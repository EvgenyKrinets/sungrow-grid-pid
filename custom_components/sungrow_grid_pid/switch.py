"""Switches for Grid Target control and scheduled morning discharge."""
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.restore_state import RestoreEntity
from .const import DOMAIN

class ManagerSwitch(SwitchEntity, RestoreEntity):
    _attr_should_poll = False
    _attr_has_entity_name = False

    def __init__(self, manager, morning=False):
        self.manager, self.morning = manager, morning
        self._attr_name = "SEM Morning Discharge" if morning else "SEM Grid Target"
        self._attr_unique_id = "sungrow_energy_manager_morning" if morning else "sungrow_energy_manager_grid_target"
        self.entity_id = "switch.sem_morning_discharge" if morning else "switch.sem_grid_target"
        self._attr_is_on = False

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        old = await self.async_get_last_state()
        if old and old.state == "on":
            if self.morning:
                self.manager.morning_enabled = True
                self._attr_is_on = True
            else:
                # Do not automatically command the battery after Home Assistant restarts.
                # User must explicitly reactivate Grid Target.
                self._attr_is_on = False

    async def async_turn_on(self, **kwargs):
        if self.morning:
            self.manager.morning_enabled = True
        else:
            await self.manager.start()
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        if self.morning:
            self.manager.morning_enabled = False
        else:
            await self.manager.stop()
        self._attr_is_on = False
        self.async_write_ha_state()

async def async_setup_entry(hass, entry, async_add_entities):
    manager = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ManagerSwitch(manager), ManagerSwitch(manager, True)])
