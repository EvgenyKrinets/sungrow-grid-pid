"""Sungrow Grid PID: install native HA helpers and editable automation."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.const import EVENT_STATE_CHANGED

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

    _LOGGER.info("Sungrow Grid PID automation: %s; restart required: %s", result, restart_needed)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    async def activate_selected_scene(automation_entity: str) -> None:
        scene = entry.options.get("scene_entity", entry.data.get("scene_entity", ""))
        if not scene:
            _LOGGER.warning("PID enabled via %s but no scene is configured", automation_entity)
            return
        if hass.states.get(scene) is None:
            _LOGGER.error("PID enabled via %s but selected scene %s does not exist", automation_entity, scene)
            return
        try:
            await hass.services.async_call(
                "scene", "turn_on", {"entity_id": scene}, blocking=True
            )
            _LOGGER.info("Activated PID startup scene %s for %s", scene, automation_entity)
        except Exception:
            _LOGGER.exception("Failed activating PID startup scene %s for %s", scene, automation_entity)

    @callback
    def on_automation_state(event):
        new = event.data.get("new_state")
        old = event.data.get("old_state")
        if new is None or new.state != "on" or (old and old.state == "on"):
            return
        entity_id = event.data.get("entity_id", "")
        if not entity_id.startswith("automation."):
            return
        # The YAML automation often has no ID, so HA may assign a different
        # entity_id. Resolve by friendly name just as the dashboard card does.
        expected = "automation.simple_grid_battery_controller"
        friendly = str(new.attributes.get("friendly_name", "")).strip().lower()
        if entity_id != expected and friendly != "simple grid battery controller":
            return
        hass.async_create_task(activate_selected_scene(entity_id))

    # Listen even if the user's YAML automation is loaded after this integration.
    entry.async_on_unload(hass.bus.async_listen(EVENT_STATE_CHANGED, on_automation_state))
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    return True


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # Preserve normal user-editable automation/helpers; release the snapshot sensor.
    return await hass.config_entries.async_unload_platforms(entry, ["sensor"])
