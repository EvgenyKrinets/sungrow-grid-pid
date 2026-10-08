from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    DEFAULT_CHARGE_ENTITY,
    DEFAULT_EXPORT_ENTITY,
    DEFAULT_MAX_CHARGE,
    DEFAULT_SCENE_ENTITY,
    DEFAULT_TARGET,
    DOMAIN,
    GAIN,
    INTERVAL_SECONDS,
)
from .frontend import async_register_frontend

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["number", "sensor", "switch"]


class GridPidController:
    """Exact Home Assistant automation logic, packaged as an integration."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.enabled = False
        self.target = DEFAULT_TARGET
        self.integral = 0.0
        self.output = 0.0
        self.error = 0.0
        self.grid = 0.0
        self._cancel = None
        self._tick_running = False
        self.listeners: list[Any] = []

    @property
    def export_entity(self) -> str:
        return self.entry.options.get("export_entity", DEFAULT_EXPORT_ENTITY)

    @property
    def charge_entity(self) -> str:
        return self.entry.options.get("charge_entity", DEFAULT_CHARGE_ENTITY)

    @property
    def scene_entity(self) -> str:
        return self.entry.options.get("scene_entity", DEFAULT_SCENE_ENTITY)

    def add_listener(self, callback):
        self.listeners.append(callback)

    def notify(self):
        for callback in list(self.listeners):
            callback()

    async def enable(self) -> None:
        if self.enabled:
            return

        scene_id = self.scene_entity
        if scene_id:
            if self.hass.states.get(scene_id) is None:
                _LOGGER.warning("PID start: configured Sungrow scene %s not found", scene_id)
            else:
                try:
                    await self.hass.services.async_call(
                        "scene", "turn_on", {"entity_id": scene_id}, blocking=True
                    )
                except Exception:
                    _LOGGER.exception("PID start failed to activate Sungrow scene %s", scene_id)
                    raise

        # Same starting point as input_number.pid_integral in the original automation.
        self.output = float(self.integral)
        self.enabled = True
        self._cancel = async_track_time_interval(
            self.hass, self._tick, timedelta(seconds=INTERVAL_SECONDS)
        )
        _LOGGER.info("Sungrow Grid PID enabled with export=%s charge=%s scene=%s", self.export_entity, self.charge_entity, scene_id)
        self.notify()

    async def disable(self) -> None:
        if self._cancel:
            self._cancel()
            self._cancel = None
        self.enabled = False
        self.notify()

    async def _tick(self, _now=None) -> None:
        # Faithful equivalent of automation mode: single / max_exceeded: silent.
        if not self.enabled or self._tick_running:
            return

        self._tick_running = True
        try:
            export_state = self.hass.states.get(self.export_entity)
            charge_state = self.hass.states.get(self.charge_entity)
            if export_state is None or charge_state is None:
                return

            try:
                grid = float(export_state.state)
                target = float(self.target)
                integral = float(self.integral)
            except (TypeError, ValueError):
                return

            self.grid = grid
            self.error = grid - target
            output_new = integral + (self.error * GAIN)
            output_new = round(max(0.0, min(DEFAULT_MAX_CHARGE, output_new)))

            # Exact order from the original automation:
            # 1) write battery max charge power
            # 2) store the same value as the new integral/output
            await self.hass.services.async_call(
                "number",
                "set_value",
                {"entity_id": self.charge_entity, "value": output_new},
                blocking=True,
            )
            self.output = float(output_new)
            self.integral = float(output_new)
            self.notify()
        finally:
            self._tick_running = False


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    if not hass.data.get(f"{DOMAIN}_frontend_registered"):
        try:
            await async_register_frontend(hass)
            hass.data[f"{DOMAIN}_frontend_registered"] = True
        except Exception:
            _LOGGER.exception("Unable to register PID frontend; integration remains manageable")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if not hass.data.get(f"{DOMAIN}_frontend_registered"):
        await async_register_frontend(hass)
        hass.data[f"{DOMAIN}_frontend_registered"] = True

    controller = GridPidController(hass, entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = controller
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    controller = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if controller is not None and controller.enabled:
        await controller.disable()
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return ok
