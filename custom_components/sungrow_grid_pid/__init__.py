from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    CHARGE_CANDIDATES, DOMAIN, EXPORT_CANDIDATES, FORCED_DISCHARGE_OPTIONS,
    GAIN, INTERVAL_SECONDS, MODE_CANDIDATES,
)
from .frontend import async_register_frontend

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["number", "sensor", "switch"]


def _find_entity(hass: HomeAssistant, candidates: tuple[str, ...], keywords: tuple[str, ...]) -> str | None:
    for entity_id in candidates:
        if hass.states.get(entity_id) is not None:
            return entity_id
    for state in hass.states.async_all():
        eid = state.entity_id.lower()
        if all(k in eid for k in keywords):
            return state.entity_id
    return None


def discover_entities(hass: HomeAssistant) -> dict[str, str | None]:
    return {
        "export": _find_entity(hass, EXPORT_CANDIDATES, ("export", "power")),
        "charge": _find_entity(hass, CHARGE_CANDIDATES, ("charge", "power")),
        "mode": _find_entity(hass, MODE_CANDIDATES, ("battery", "mode"))
            or _find_entity(hass, MODE_CANDIDATES, ("forced", "charge", "discharge")),
    }


class GridPidController:
    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self.entities = discover_entities(hass)
        self.enabled = False
        self.target = 15000.0
        self.output = 0.0
        self.error = 0.0
        self.previous_mode: str | None = None
        self._cancel = None
        self.listeners: list[Any] = []

    def add_listener(self, callback):
        self.listeners.append(callback)

    def notify(self):
        for callback in list(self.listeners):
            callback()

    async def enable(self) -> None:
        if self.enabled:
            return
        self.entities = discover_entities(self.hass)
        mode_id = self.entities["mode"]
        if mode_id:
            state = self.hass.states.get(mode_id)
            if state:
                self.previous_mode = state.state
                options = state.attributes.get("options", [])
                option = next((x for x in FORCED_DISCHARGE_OPTIONS if x in options), None)
                if option:
                    await self.hass.services.async_call(
                        "select", "select_option",
                        {"entity_id": mode_id, "option": option}, blocking=True
                    )
        charge_id = self.entities["charge"]
        if charge_id:
            state = self.hass.states.get(charge_id)
            try:
                self.output = float(state.state) if state else 0.0
            except (TypeError, ValueError):
                self.output = 0.0
        self.enabled = True
        self._cancel = async_track_time_interval(
            self.hass, self._tick, timedelta(seconds=INTERVAL_SECONDS)
        )
        self.notify()

    async def disable(self) -> None:
        if self._cancel:
            self._cancel()
            self._cancel = None
        self.enabled = False
        mode_id = self.entities.get("mode")
        if mode_id and self.previous_mode:
            state = self.hass.states.get(mode_id)
            options = state.attributes.get("options", []) if state else []
            if self.previous_mode in options:
                await self.hass.services.async_call(
                    "select", "select_option",
                    {"entity_id": mode_id, "option": self.previous_mode}, blocking=True
                )
        self.previous_mode = None
        self.notify()

    async def _tick(self, _now=None) -> None:
        if not self.enabled:
            return
        export_id = self.entities.get("export")
        charge_id = self.entities.get("charge")
        if not export_id or not charge_id:
            return
        try:
            grid = float(self.hass.states[export_id].state)
        except (KeyError, TypeError, ValueError):
            return
        self.error = grid - self.target
        self.output = max(0.0, min(25000.0, self.output + self.error * GAIN))
        await self.hass.services.async_call(
            "number", "set_value",
            {"entity_id": charge_id, "value": round(self.output)}, blocking=False
        )
        self.notify()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if not hass.data.get(f"{DOMAIN}_frontend_registered"):
        await async_register_frontend(hass)
        hass.data[f"{DOMAIN}_frontend_registered"] = True
    controller = GridPidController(hass)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = controller
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    controller = hass.data[DOMAIN][entry.entry_id]
    if controller.enabled:
        await controller.disable()
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return ok
