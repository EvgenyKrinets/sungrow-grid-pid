"""Tests for discounted tariff night windows and control priority."""
from datetime import datetime, time
import types
import unittest

from test_restart_restore import FakeHass, FakeEntry, FakeState, manager_module
from sungrow_grid_pid.tariff import is_discount_time


class NightWindowTests(unittest.TestCase):
    def test_only_sunday_through_thursday_starting_nights(self):
        # Sun Nov 22 through Sat Nov 28, 2026 (local datetime).
        assert is_discount_time(datetime(2026, 11, 22, 23, 0))
        assert is_discount_time(datetime(2026, 11, 23, 6, 59))
        assert not is_discount_time(datetime(2026, 11, 23, 7, 0))
        assert not is_discount_time(datetime(2026, 11, 23, 22, 59))
        assert is_discount_time(datetime(2026, 11, 26, 23, 15))
        assert is_discount_time(datetime(2026, 11, 27, 6, 59))
        assert not is_discount_time(datetime(2026, 11, 27, 23, 15))
        assert not is_discount_time(datetime(2026, 11, 28, 6, 59))
        assert not is_discount_time(datetime(2026, 11, 28, 23, 15))
        assert not is_discount_time(datetime(2026, 11, 22, 6, 59))

    def test_custom_times_are_used(self):
        start, end = time(22, 0), time(8, 30)
        assert is_discount_time(datetime(2026, 11, 23, 22, 0), start, end)
        assert is_discount_time(datetime(2026, 11, 24, 8, 29), start, end)
        assert not is_discount_time(datetime(2026, 11, 24, 8, 30), start, end)
        assert not is_discount_time(datetime(2026, 11, 23, 21, 59), start, end)
        assert not is_discount_time(datetime(2026, 11, 23, 23, 0), start, start)


class NightManagerTests(unittest.IsolatedAsyncioTestCase):
    async def make_manager(self, initial=None):
        hass = FakeHass(initial or {"tariff_enabled": True, "enabled": False})
        hass.states.values["scene.discount"] = FakeState("2026-11-20T23:00:00")
        entry = types.SimpleNamespace(
            entry_id=FakeEntry.entry_id,
            data={**FakeEntry.data, "discount_scene_entity": "scene.discount"},
            options={},
        )
        manager, unsub = await manager_module.setup_manager(hass, entry)
        return hass, manager

    async def test_restart_restores_tariff_even_if_grid_target_off(self):
        hass, manager = await self.make_manager()
        manager._tariff_now = lambda: datetime(2026, 11, 22, 23, 10)
        await manager.resume_after_restore()
        self.assertTrue(manager.tariff_enabled)
        self.assertFalse(manager.enabled)
        self.assertIn(("scene", "turn_on", {"entity_id": "scene.discount"}), hass.services.calls)
        self.assertEqual(manager._tariff_applied_mode, "discount")

    async def test_one_scene_call_per_boundary(self):
        hass, manager = await self.make_manager()
        manager._ready = True
        manager.tariff_enabled = True
        sun = datetime(2026, 11, 22, 23, 10)
        monday = datetime(2026, 11, 23, 7, 0)
        self.assertTrue(await manager.apply_tariff(sun))
        self.assertTrue(await manager.apply_tariff(sun))
        self.assertEqual(len(hass.services.calls), 1)
        self.assertEqual(hass.services.calls[0][2]["entity_id"], "scene.discount")
        self.assertTrue(await manager.apply_tariff(monday))
        self.assertEqual(len(hass.services.calls), 2)
        self.assertEqual(hass.services.calls[1][2]["entity_id"], "scene.self")
        self.assertTrue(await manager.apply_tariff(monday))
        self.assertEqual(len(hass.services.calls), 2)

    async def test_forced_discharge_priority_and_correct_exit_scene(self):
        hass, manager = await self.make_manager()
        manager.tariff_enabled = True
        manager.enabled = True
        manager.morning_enabled = True
        manager.forced = True
        manager._tariff_now = lambda: datetime(2026, 11, 22, 23, 10)
        self.assertTrue(await manager.apply_tariff(force=True))
        self.assertEqual(hass.services.calls, [])
        self.assertIn("Paused", manager.tariff_status)
        await manager.finish_forced()
        self.assertFalse(manager.forced)
        self.assertEqual(hass.services.calls[-1][2]["entity_id"], "scene.discount")

    async def test_toggling_tariff_off_restores_normal_scene(self):
        hass, manager = await self.make_manager({"enabled": False, "tariff_enabled": False})
        manager._tariff_now = lambda: datetime(2026, 11, 22, 23, 10)
        await manager.set_tariff(True)
        self.assertTrue(hass.persisted["sungrow_energy_manager_test-entry"]["tariff_enabled"])
        self.assertEqual(hass.services.calls[-1][2]["entity_id"], "scene.discount")
        await manager.set_tariff(False)
        self.assertFalse(hass.persisted["sungrow_energy_manager_test-entry"]["tariff_enabled"])
        self.assertEqual(hass.services.calls[-1][2]["entity_id"], "scene.self")

    async def test_missing_discount_scene_rejects_enable(self):
        hass, manager = await self.make_manager({"tariff_enabled": False})
        hass.states.values.pop("scene.discount")
        with self.assertRaises(ValueError):
            await manager.set_tariff(True)
        self.assertFalse(manager.tariff_enabled)


if __name__ == "__main__":
    unittest.main()
