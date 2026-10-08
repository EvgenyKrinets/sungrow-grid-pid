"""Sungrow Grid PID: install native HA helpers and editable automation."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event

from .const import DOMAIN
from .frontend import async_register_frontend
from .installer import install

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    return True


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate earlier config entries without deleting user data."""
    from .config_flow import DEFAULTS, SungrowGridPidConfigFlow

    target_version = SungrowGridPidConfigFlow.VERSION
    if entry.version > target_version:
        _LOGGER.error("Unsupported newer Sungrow Grid PID config entry version: %s", entry.version)
        return False
    if entry.version == target_version:
        return True

    data = {**DEFAULTS, **entry.data}
    # Earlier releases stored the same entity selections in options.
    # Preserve user configuration, including options, across upgrades.
    hass.config_entries.async_update_entry(
        entry, data=data, version=target_version
    )
    _LOGGER.info("Migrated Sungrow Grid PID config entry from old version to %s", target_version)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    try:
        if not hass.data.get(f"{DOMAIN}_frontend_registered"):
            await async_register_frontend(hass)
            hass.data[f"{DOMAIN}_frontend_registered"] = True
    except Exception:
        _LOGGER.exception("Card registration failed; automation installer will continue")

    try:
        result, restart_needed = await install(hass, entry)
    except Exception:
        _LOGGER.exception("Cannot install Sungrow Grid PID automation")
        raise

    _LOGGER.info("Sungrow Grid PID automation: %s; helper restart required: %s", result, restart_needed)

    @callback
    def on_automation_state(event):
        new = event.data.get("new_state")
        old = event.data.get("old_state")
        if new is None or new.state != "on" or (old and old.state == "on"):
            return
        scene = entry.options.get("scene_entity", entry.data.get("scene_entity", ""))
        if scene and hass.states.get(scene):
            hass.async_create_task(
                hass.services.async_call("scene", "turn_on", {"entity_id": scene}, blocking=True)
            )

    entry.async_on_unload(async_track_state_change_event(
        hass, ["automation.simple_grid_battery_controller"], on_automation_state
    ))
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    return True


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # Automation and helpers are first-class user-editable items. Do not delete
    # user-owned YAML or storage records implicitly on integration removal.
    return True
