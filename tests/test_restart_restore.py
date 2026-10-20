"""Standalone restart-state tests; no Home Assistant installation required."""
from __future__ import annotations
import asyncio
import importlib.util
from pathlib import Path
import sys
import types
import unittest

ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "sungrow_grid_pid"


def install_stubs():
    for name in (
        "homeassistant", "homeassistant.core", "homeassistant.components",
        "homeassistant.components.switch", "homeassistant.helpers",
        "homeassistant.helpers.event", "homeassistant.helpers.storage",
        "homeassistant.helpers.restore_state",
    ):
        sys.modules[name] = types.ModuleType(name)
    sys.modules["homeassistant.core"].callback = lambda fn: fn
    sys.modules["homeassistant.helpers.event"].async_track_time_interval = (
        lambda hass, fn, interval: (lambda: None)
    )

    class Store:
        def __init__(self, hass, version, key):
            self.hass, self.key = hass, key
        async def async_load(self):
            return dict(self.hass.persisted.get(self.key, {}))
        async def async_save(self, value):
            self.hass.persisted[self.key] = dict(value)
    sys.modules["homeassistant.helpers.storage"].Store = Store

    class SwitchEntity:
        async def async_added_to_hass(self):
            pass
        def async_write_ha_state(self):
            pass
    class RestoreEntity:
        async def async_get_last_state(self):
            return getattr(self, "last_state", None)
    sys.modules["homeassistant.components.switch"].SwitchEntity = SwitchEntity
    sys.modules["homeassistant.helpers.restore_state"].RestoreEntity = RestoreEntity

    pkg = types.ModuleType("sungrow_grid_pid")
    pkg.__path__ = [str(ROOT)]
    sys.modules["sungrow_grid_pid"] = pkg
    const = types.ModuleType("sungrow_grid_pid.const")
    const.DOMAIN = "sungrow_grid_pid"
    sys.modules["sungrow_grid_pid.const"] = const

    def load(module_name, filename):
        spec = importlib.util.spec_from_file_location(module_name, ROOT / filename)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    return load("sungrow_grid_pid.manager", "manager.py"), load("sungrow_grid_pid.switch", "switch.py")


manager_module, switch_module = install_stubs()
STORE_KEY = "sungrow_energy_manager_test-entry"


class FakeState:
    def __init__(self, state, attrs=None, entity_id=""):
        self.state = str(state)
        self.attributes = attrs or {}
        self.entity_id = entity_id


class FakeStates:
    def __init__(self):
        self.values = {
            "scene.self": FakeState("2026-10-20T05:00:00"),
            "scene.forced": FakeState("2026-10-20T06:00:00"),
            "sensor.soc": FakeState("71.5"),
            "number.reserve": FakeState("20", {"min": 0, "max": 100}),
            "number.charge": FakeState("1000", {"min": 10, "max": 25000, "step": 10}),
            "number.forced_power": FakeState("2000", {"min": 0, "max": 25000}),
            "sensor.export": FakeState("5000"),
        }
    def get(self, key):
        return self.values.get(key)
    def async_all(self, domain=None):
        return [s for name,s in self.values.items() if domain is None or name.startswith(domain + ".")]


class FakeServices:
    def __init__(self):
        self.calls = []
    async def async_call(self, domain, service, data, blocking=False):
        self.calls.append((domain, service, data))


class FakeHass:
    def __init__(self, saved=None):
        self.persisted = {STORE_KEY: dict(saved or {})}
        self.states = FakeStates()
        self.services = FakeServices()
        self.config = types.SimpleNamespace(time_zone="UTC")
        self.loop = asyncio.get_running_loop()
    def async_create_task(self, coro):
        return self.loop.create_task(coro)


class FakeEntry:
    entry_id = "test-entry"
    data = {
        "scene_entity": "scene.self",
        "forced_scene_entity": "scene.forced",
        "export_entity": "sensor.export",
        "charge_entity": "number.charge",
        "soc_entity": "sensor.soc",
        "reserve_soc_entity": "number.reserve",
        "forced_power_entity": "number.forced_power",
    }
    options = {}


class RestartTests(unittest.IsolatedAsyncioTestCase):
    async def build(self, saved=None, old_grid=None, old_morning=None):
        hass = FakeHass(saved)
        manager, unsubscribe = await manager_module.setup_manager(hass, FakeEntry())
        main = switch_module.ManagerSwitch(manager)
        morning = switch_module.ManagerSwitch(manager, morning=True)
        if old_grid is not None:
            main.last_state = FakeState("on" if old_grid else "off")
        if old_morning is not None:
            morning.last_state = FakeState("on" if old_morning else "off")
        await main.async_added_to_hass()
        await morning.async_added_to_hass()
        return hass, manager, main, morning

    async def test_grid_and_schedule_survive_restart(self):
        hass, mgr, main, morning = await self.build(
            {"enabled": True, "morning_enabled": True, "forced": False}
        )
        await mgr.resume_after_restore()
        self.assertTrue(mgr.enabled)
        self.assertTrue(mgr.morning_enabled)
        self.assertTrue(main._attr_is_on)
        self.assertTrue(morning._attr_is_on)
        self.assertIn(("scene", "turn_on", {"entity_id": "scene.self"}), hass.services.calls)
        self.assertTrue(hass.persisted[STORE_KEY]["enabled"])
        self.assertTrue(hass.persisted[STORE_KEY]["morning_enabled"])

    async def test_active_forced_discharge_kept_when_safe(self):
        hass, mgr, main, morning = await self.build(
            {"enabled": True, "morning_enabled": True, "forced": True}
        )
        await mgr.resume_after_restore()
        self.assertTrue(mgr.forced)
        self.assertTrue(mgr.enabled)
        self.assertEqual(hass.services.calls, [])  # Do not reset to Self-Consumption.
        self.assertIn("Resumed", mgr.morning_status)

    async def test_forced_discharge_stops_at_reserve_on_restart(self):
        hass, mgr, main, morning = await self.build(
            {"enabled": True, "morning_enabled": True, "forced": True}
        )
        hass.states.values["sensor.soc"].state = "19"
        await mgr.resume_after_restore()
        self.assertFalse(mgr.forced)
        self.assertIn(("scene", "turn_on", {"entity_id": "scene.self"}), hass.services.calls)

    async def test_migrate_old_switch_states(self):
        hass, mgr, main, morning = await self.build(
            {"forced": False}, old_grid=True, old_morning=True
        )
        await mgr.resume_after_restore()
        self.assertTrue(mgr.enabled)
        self.assertTrue(mgr.morning_enabled)
        self.assertTrue(hass.persisted[STORE_KEY]["enabled"])

    async def test_stop_switch_is_stored(self):
        hass, mgr, main, morning = await self.build(
            {"enabled": True, "morning_enabled": True, "forced": False}
        )
        await mgr.resume_after_restore()
        await main.async_turn_off()
        await morning.async_turn_off()
        self.assertFalse(hass.persisted[STORE_KEY]["enabled"])
        self.assertFalse(hass.persisted[STORE_KEY]["morning_enabled"])

    async def test_schedule_turn_off_stops_active_forced_mode(self):
        hass, mgr, main, morning = await self.build(
            {"enabled": True, "morning_enabled": True, "forced": True}
        )
        await mgr.resume_after_restore()
        await morning.async_turn_off()
        self.assertFalse(mgr.forced)
        self.assertFalse(mgr.morning_enabled)
        self.assertIn(("scene", "turn_on", {"entity_id": "scene.self"}), hass.services.calls)


if __name__ == "__main__":
    unittest.main()
