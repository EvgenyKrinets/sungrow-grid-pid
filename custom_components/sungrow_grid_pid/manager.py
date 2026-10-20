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
        self._saved_enabled = None
        self._saved_morning_enabled = None
        self._ready = False
        self._resume_scene_pending = False
        self._resume_retry_at = 0.0
        self.exit_requested = False
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
        self.last_run_time = None
        self.last_attempt_minute = None
        self.forced = False
        self.status = "Stopped"
        self.morning_status = "Not run yet"
        self.listeners = []
        self._tick_lock = asyncio.Lock()
        self._store = Store(hass, 1, "sungrow_energy_manager_" + entry.entry_id)

    async def persist(self):
        """Persist intended switch states together with ongoing discharge state."""
        await self._store.async_save({
            "enabled": self.enabled,
            "morning_enabled": self.morning_enabled,
            "forced": self.forced,
            "exit_requested": self.exit_requested,
            "last_run": self.last_run_date.isoformat() if self.last_run_date else None,
            "last_run_time": self.last_run_time,
        })

    def setting(self, name):
        return self.entry.options.get(name, self.entry.data.get(name, ""))

    def add_listener(self, callback_fn):
        self.listeners.append(callback_fn)

    def notify(self):
        for listener in list(self.listeners):
            listener()

    async def _disable_legacy(self):
        """Never allow the old PID and SEM to command the battery together."""
        for state in self.hass.states.async_all("automation"):
            if state.entity_id == OLD_AUTOMATION or state.attributes.get("friendly_name", "").lower() == "simple grid battery controller":
                if state.state == "on":
                    await self.hass.services.async_call("automation", "turn_off", {"entity_id": state.entity_id}, blocking=True)
    async def _activate_self_consumption(self):
        scene = self.setting("scene_entity")
        state = self.hass.states.get(scene) if scene else None
        if not scene or state is None or state.state == "unavailable":
            self.status = "Waiting for Self-Consumption scene"
            return False
        try:
            await self.hass.services.async_call(
                "scene", "turn_on", {"entity_id": scene}, blocking=True
            )
        except Exception:
            _LOGGER.exception("SEM could not restore Self-Consumption scene")
            self.status = "ERROR: Self-Consumption scene failed"
            return False
        self.status = "Grid Target active"
        return True

    async def start(self):
        await self._disable_legacy()
        if not self.forced:
            # On an explicit START, preserve previous behavior: activate the scene.
            if not await self._activate_self_consumption():
                raise RuntimeError("Selected Self-Consumption scene is unavailable")
        self.enabled = True
        self._resume_scene_pending = False
        self.exit_requested = False
        self.direction, self.started = 0, None
        if self.forced:
            self.status = "Battery Forced Discharge"
        await self.persist()
        self.notify()

    async def stop(self):
        self.enabled = False
        self.direction, self.started = 0, None
        self._resume_scene_pending = False
        self.exit_requested = self.forced
        await self.persist()
        if self.forced:
            await self.finish_forced()
        if not self.forced:
            self.status = "Stopped"
        self.notify()

    async def resume_after_restore(self):
        """Resume remembered modes after entity parameters and time are restored."""
        await self._disable_legacy()
        self._ready = True
        if self.forced:
            soc = numeric(self.hass, self.setting("soc_entity"))
            reserve = numeric(self.hass, self.setting("reserve_soc_entity"))
            if (
                not self.enabled or not self.morning_enabled or self.exit_requested
                or soc is None or reserve is None
                or not 0 <= soc <= 100 or not 0 <= reserve <= 100
                or soc <= reserve
            ):
                self.exit_requested = True
                self.morning_status = "Recovery: ending forced discharge (state or SOC unsafe)"
                await self.finish_forced()
                # Keep retrying the fallback until the scene can be called.
            else:
                self.status = "Battery Forced Discharge"
                self.morning_status = "Resumed: monitoring forced discharge after HA restart"
        elif self.enabled:
            # Do not accidentally reset a running forced-discharge mode.
            # Resume Self-Consumption when no forced discharge was recorded.
            self._resume_scene_pending = True
            await self._resume_self_consumption()
        else:
            self.status = "Stopped"
        await self.persist()
        self.notify()

    async def _resume_self_consumption(self):
        if not self._resume_scene_pending:
            return
        if self.hass.loop.time() < self._resume_retry_at:
            return
        await self._disable_legacy()
        if await self._activate_self_consumption():
            self._resume_scene_pending = False
        else:
            # No rapid retries when Modbus/scene entities are not yet ready.
            self._resume_retry_at = self.hass.loop.time() + 30



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
            self.exit_requested = False
            self.last_run_date = datetime.now(__import__("zoneinfo").ZoneInfo(self.hass.config.time_zone)).date()
            self.last_run_time = self.start_time.strftime("%H:%M")
            await self.persist()
            self.status = "Battery Forced Discharge"
            self.morning_status = f"Active: forced discharge at {value:g} W limit"
            self.notify()
        except Exception:
            _LOGGER.exception("Morning forced discharge failed")
            self.status = "Morning discharge command failed"
            self.morning_status = "ERROR: service call failed; inspect HA logs"
            self.notify()

    async def update_forced_power(self, requested):
        """Apply changed discharge power only while forced mode is active."""
        if not self.forced:
            return
        async with self._tick_lock:
            power = self.setting("forced_power_entity")
            st = self.hass.states.get(power) if power else None
            if st is None or not power.startswith("number."):
                self.morning_status = "ERROR: Forced Discharge power entity unavailable"
                self.notify()
                raise ValueError(self.morning_status)
            soc = numeric(self.hass, self.setting("soc_entity"))
            reserve = numeric(self.hass, self.setting("reserve_soc_entity"))
            if soc is None or reserve is None or not 0 <= reserve <= 100 or soc <= reserve:
                self.morning_status = "ERROR: unsafe SOC/reserve; discharge power not changed"
                self.notify()
                raise ValueError(self.morning_status)
            low = float(st.attributes.get("min", 0))
            high = float(st.attributes.get("max", 25000))
            step = float(st.attributes.get("step", 1)) or 1
            if not low <= requested <= high:
                self.morning_status = f"ERROR: requested power outside {low:g}–{high:g} W"
                self.notify()
                raise ValueError(self.morning_status)
            applied = max(low, min(high, low + round((requested - low) / step) * step))
            try:
                await self.hass.services.async_call(
                    "number", "set_value", {"entity_id": power, "value": applied}, blocking=True
                )
            except Exception:
                self.morning_status = "ERROR: failed to update Forced Discharge power"
                self.notify()
                _LOGGER.exception("Failed to change forced discharge limit")
                raise
            self.morning_status = f"Active: forced discharge limit set to {applied:g} W"
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
            self.exit_requested = False
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
        if not self._ready:
            return
        if not self.enabled:
            if self.forced:
                self.exit_requested = True
                await self.finish_forced()
            return
        if self._resume_scene_pending and not self.forced:
            await self._resume_self_consumption()
            self.notify()
            return
        now = datetime.now(self.hass.config.time_zone and __import__("zoneinfo").ZoneInfo(self.hass.config.time_zone))
        if self.forced:
            soc = numeric(self.hass, self.setting("soc_entity"))
            reserved = numeric(self.hass, self.setting("reserve_soc_entity"))
            if self.exit_requested or not self.morning_enabled:
                self.exit_requested = True
                await self.finish_forced()
            elif (
                soc is None or reserved is None
                or not 0 <= soc <= 100 or not 0 <= reserved <= 100
            ):
                self.status = "ERROR: SOC unavailable/invalid; reverting mode"
                self.exit_requested = True
                await self.finish_forced()
            elif soc <= reserved:
                self.exit_requested = True
                await self.finish_forced()
            self.notify()
            return

        scheduled_minute = self.start_time.strftime("%H:%M")
        scheduled_now = now.hour == self.start_time.hour and now.minute == self.start_time.minute
        attempt_key = (now.date(), scheduled_minute)
        already_completed = self.last_run_date == now.date() and self.last_run_time == scheduled_minute
        if self.morning_enabled and scheduled_now and not already_completed and self.last_attempt_minute != attempt_key:
            # Never consume the whole day's scheduled run on a failed attempt.
            # Attempt at most once during each scheduled minute, avoiding
            # hammering the inverter with repeated service calls every second.
            self.last_attempt_minute = attempt_key
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
        # Do not run or reset a pointless delay when charging is already at
        # the boundary in the requested direction. Re-arm the full delay only
        # after the value leaves that boundary (or the direction reverses).
        charge_state = self.hass.states.get(charge_entity)
        charge_min = float(charge_state.attributes.get("min", 0))
        charge_max = float(charge_state.attributes.get("max", 25000))
        charge_step = float(charge_state.attributes.get("step", 1)) or 1
        at_limit = (
            (direction > 0 and charge >= charge_max - charge_step / 2)
            or (direction < 0 and charge <= charge_min + charge_step / 2)
        )
        if at_limit:
            self.direction, self.started = 0, None
            self.status = (
                "Grid Target: charge at maximum"
                if direction > 0 else "Grid Target: charge at minimum"
            )
        elif direction != self.direction:
            self.direction, self.started = direction, now if direction else None
        if at_limit:
            pass
        elif direction == 0:
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
    manager.last_run_time = prior.get("last_run_time")
    # Existing v4.0.4 storage holds only forced/last_run. In that case,
    # switch RestoreEntity recovers ON/OFF from the previous HA state.
    manager._saved_enabled = prior.get("enabled") if isinstance(prior.get("enabled"), bool) else None
    manager._saved_morning_enabled = (
        prior.get("morning_enabled") if isinstance(prior.get("morning_enabled"), bool) else None
    )
    manager.enabled = manager._saved_enabled is True
    manager.morning_enabled = manager._saved_morning_enabled is True
    manager.forced = prior.get("forced") is True
    manager.exit_requested = prior.get("exit_requested") is True
    # A forced mode must NOT automatically be switched off during setup.
    # Wait until sensors, switches, numbers and scheduled time are restored,
    # then check backup SOC before allowing the forced mode to continue.
    @callback
    def schedule_tick(now):
        hass.async_create_task(manager.tick(now))
    unsub = async_track_time_interval(hass, schedule_tick, timedelta(seconds=1))
    return manager, unsub
