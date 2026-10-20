"""Persist native SEM switches across Home Assistant restarts and reloads."""
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.restore_state import RestoreEntity
from .const import DOMAIN


class ManagerSwitch(SwitchEntity, RestoreEntity):
    _attr_should_poll = False
    _attr_has_entity_name = False

    def __init__(self, manager, morning=False):
        self.manager, self.morning = manager, morning
        self._attr_name = "SEM Morning Discharge" if morning else "SEM Grid Target"
        self._attr_unique_id = (
            "sungrow_energy_manager_morning" if morning
            else "sungrow_energy_manager_grid_target"
        )
        self.entity_id = (
            "switch.sem_morning_discharge" if morning
            else "switch.sem_grid_target"
        )
        # The manager reads its durable storage BEFORE adding platforms.
        self._attr_is_on = (
            manager.morning_enabled if morning else manager.enabled
        )

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        # Migration from v4.0.4: the manager's Store did not contain these
        # switches, so use RestoreEntity for the first upgrade only.
        saved = (
            self.manager._saved_morning_enabled if self.morning
            else self.manager._saved_enabled
        )
        if saved is None:
            previous = await self.async_get_last_state()
            saved = bool(previous and previous.state == "on")
        self._attr_is_on = saved
        if self.morning:
            self.manager.morning_enabled = saved
        else:
            self.manager.enabled = saved

    async def async_turn_on(self, **kwargs):
        if self.morning:
            self.manager.morning_enabled = True
            await self.manager.persist()
            self.manager.notify()
        else:
            await self.manager.start()
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        if self.morning:
            self.manager.morning_enabled = False
            self.manager.exit_requested = self.manager.forced
            await self.manager.persist()
            if self.manager.forced:
                await self.manager.finish_forced()
            self.manager.notify()
        else:
            await self.manager.stop()
        self._attr_is_on = False
        self.async_write_ha_state()


async def async_setup_entry(hass, entry, async_add_entities):
    manager = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ManagerSwitch(manager), ManagerSwitch(manager, True)])
