"""Sungrow Energy Manager: deterministic stepped export control and morning discharge."""
from __future__ import annotations

import logging
import asyncio
import math
from datetime import datetime, time, timedelta

from homeassistant.core import callback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.storage import Store

_LOGGER = logging.getLogger(__name__)
OLD_AUTOMATION = "automation.simple_grid_battery_controller"


def numeric(hass, entity):
    state = hass.states.get(entity) if entity else None
    if state is None:
        return None
    try:
        result = float(state.state)
        return result if math.isfinite(result) else None
    except (ValueError, TypeError):
        return None


class EnergyManager:
    """No direct battery control until user enables the manager switch."""

    def __init__(self, hass, entry):
        self.hass, self.entry = hass, entry
        self.enabled = False
        self.morning_enabled = False
        self.params = {
            "export_target": 10000.0,
            "dead_band": 1000.0,
            "delay": 600.0,
            "charge_gain": 3000.0,
            "empty_soc": 30.0,
            "discharge_power": 8000.0,
        }
        self.start_time = time(5, 0)
        self.direction = 0
        self.started = None
        self.last_run_date = None
        self.forced = False
        self.status = "Stopped"
        self.morning_status = "Not run yet"
        self.listeners = []
        self._tick_lock = asyncio.Lock()
        self._store = Store(hass, 1, "sungrow_energy_manager_" + entry.entry_id)

    async def persist(self):
        await self._store.async_save({"forced": self.forced, "last_run": self.last_run_date.isoformat() if self.last_run_date else None})

    def setting(self, name):
        return self.entry.options.get(name, self.entry.data.get(name, ""))

    def add_listener(self, callback_fn):
        self.listeners.append(callback_fn)

    def notify(self):
        for listener in list(self.listeners):
            listener()

    async def start(self):
        # Prevent simultaneous commands from the previous YAML-based PID.
        for state in self.hass.states.async_all("automation"):
            if state.entity_id == OLD_AUTOMATION or state.attributes.get("friendly_name", "").lower() == "simple grid battery controller":
                if state.state == "on":
                    await self.hass.services.async_call("automation", "turn_off", {"entity_id": state.entity_id}, blocking=True)
        scene = self.setting("scene_entity")
        if scene and self.hass.states.get(scene):
            await self.hass.services.async_call("scene", "turn_on", {"entity_id": scene}, blocking=True)
        self.enabled = True
        self.direction, self.started = 0, None
        self.status = "Grid Target active"
        self.notify()

    async def stop(self):
        self.enabled = False
        self.direction, self.started = 0, None
        if self.forced:
            await self.finish_forced()
        self.status = "Stopped"
        self.notify()

    async def begin_forced(self):
        soc = numeric(self.hass, self.setting("soc_entity"))
        reserved = numeric(self.hass, self.setting("reserve_soc_entity"))
        if soc is None or reserved is None:
            self.morning_status = "Cannot start: SOC or backup reserve unavailable"
            self.notify()
            return
        if soc <= self.params["empty_soc"] or soc <= reserved:
            self.morning_status = f"Skipped: SOC {soc:g}%, start threshold {self.params['empty_soc']:g}%, reserve {reserved:g}%"
            self.notify()
            return
        mode = self.setting("forced_scene_entity")
        power = self.setting("forced_power_entity")
        if not mode or not power or not self.hass.states.get(mode) or not self.hass.states.get(power):
            self.morning_status = "Not configured: choose Forced Discharge scene and power number in integration options"
            self.notify()
            return
        self.direction, self.started = 0, None
        try:
            st = self.hass.states.get(power)
            lo = float(st.attributes.get("min", 0))
            hi = float(st.attributes.get("max", 25000))
            value = max(lo, min(hi, self.params["discharge_power"]))
            await self.hass.services.async_call("number", "set_value", {"entity_id": power, "value": value}, blocking=True)
            await self.hass.services.async_call("scene", "turn_on", {"entity_id": mode}, blocking=True)
            self.forced = True
            await self.persist()
            self.status = "Battery Forced Discharge"
            self.morning_status = f"Active: forced discharge at {value:g} W limit"
            self.notify()
        except Exception:
            _LOGGER.exception("Morning forced discharge failed")
            self.status = "Morning discharge command failed"
            self.morning_status = "ERROR: service call failed; inspect HA logs"
            self.notify()

    async def finish_forced(self):
        scene = self.setting("scene_entity")
        # Keep flag set if command fails, so the next tick retries safely.
        if not scene or not self.hass.states.get(scene):
            self.status = "ERROR: recovery scene unavailable"
            return
        try:
            await self.hass.services.async_call("scene", "turn_on", {"entity_id": scene}, blocking=True)
            self.forced = False
            await self.persist()
            self.direction, self.started = 0, None
            self.status = "Grid Target active" if self.enabled else "Stopped"
            self.morning_status = "Finished: Self-Consumption restored"
            self.notify()
        except Exception:
            _LOGGER.exception("Cannot exit forced discharge")
            self.status = "ERROR: cannot exit forced discharge"

    async def tick(self, _now):
        if self._tick_lock.locked():
            return
        async with self._tick_lock:
            await self._tick_impl(_now)

    async def _tick_impl(self, _now):
        if not self.enabled:
            if self.forced:
                await self.finish_forced()
            return
        now = datetime.now(self.hass.config.time_zone and __import__("zoneinfo").ZoneInfo(self.hass.config.time_zone))
        if self.forced:
            soc = numeric(self.hass, self.setting("soc_entity"))
            reserved = numeric(self.hass, self.setting("reserve_soc_entity"))
            if soc is None or reserved is None:
                self.status = "ERROR: SOC missing; reverting mode"
                await self.finish_forced()
            elif soc <= reserved:
                await self.finish_forced()
            self.notify()
            return

        if self.morning_enabled and self.last_run_date != now.date() and now.hour == self.start_time.hour and now.minute == self.start_time.minute:
            self.last_run_date = now.date()
            await self.persist()
            await self.begin_forced()
            if self.forced:
                self.notify()
                return

        export = numeric(self.hass, self.setting("export_entity"))
        charge_entity = self.setting("charge_entity")
        charge = numeric(self.hass, charge_entity)
        if export is None or charge is None:
            self.status = "Waiting for valid export / charging power"
            self.direction, self.started = 0, None
            self.notify()
            return
        target = self.params["export_target"]
        band = self.params["dead_band"]
        direction = 1 if export > target + band else -1 if export < target - band else 0
        if direction != self.direction:
            self.direction, self.started = direction, now if direction else None
        if direction == 0:
            self.status = "Grid Target: within dead band"
        elif self.started is not None:
            elapsed = (now - self.started).total_seconds()
            remaining = max(0, self.params["delay"] - elapsed)
            self.status = f"Grid Target: {'increase' if direction > 0 else 'decrease'} in {remaining:.0f}s"
            if elapsed >= self.params["delay"]:
                state = self.hass.states.get(charge_entity)
                lo = float(state.attributes.get("min", 0))
                hi = float(state.attributes.get("max", 25000))
                step = float(state.attributes.get("step", 1)) or 1
                desired = max(lo, min(hi, charge + direction * self.params["charge_gain"]))
                desired = max(lo, min(hi, lo + round((desired - lo) / step) * step))
                if desired != charge:
                    try:
                        await self.hass.services.async_call("number", "set_value", {"entity_id": charge_entity, "value": desired}, blocking=True)
                        self.status = f"Grid Target: charge set to {desired:.0f} W"
                    except Exception:
                        _LOGGER.exception("Charge power adjustment failed")
                        self.status = "ERROR: charge adjustment failed"
                else:
                    self.status = "Grid Target: charge at limit"
                self.started = now
        self.notify()


async def setup_manager(hass, entry):
    manager = EnergyManager(hass, entry)
    prior = await manager._store.async_load() or {}
    if prior.get("last_run"):
        try:
            from datetime import date
            manager.last_run_date = date.fromisoformat(prior["last_run"])
        except (ValueError, TypeError):
            pass
    if prior.get("forced"):
        manager.forced = True
        await manager.finish_forced()
    @callback
    def schedule_tick(now):
        hass.async_create_task(manager.tick(now))
    unsub = async_track_time_interval(hass, schedule_tick, timedelta(seconds=1))
    return manager, unsub
