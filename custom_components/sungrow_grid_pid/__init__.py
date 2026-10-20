"""Sungrow Grid PID: install native HA helpers and editable automation."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.const import EVENT_STATE_CHANGED

from .const import DOMAIN
from .frontend import async_register_frontend
from .installer import install
from .manager import setup_manager

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
    manager, unsub = await setup_manager(hass, entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = manager
    entry.async_on_unload(unsub)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "number", "switch", "time"])

    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    return True


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # Preserve normal user-editable automation/helpers; release the snapshot sensor.
    success = await hass.config_entries.async_unload_platforms(entry, ["sensor", "number", "switch", "time"])
    if success:
        # ConfigEntry invokes callbacks registered with async_on_unload itself
        # after async_unload_entry returns True. Do not call an internal/manual
        # callback-unload method here: it can break options reloads.
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    else:
        _LOGGER.error("SEM could not unload its entity platforms; options reload aborted")
    return success
