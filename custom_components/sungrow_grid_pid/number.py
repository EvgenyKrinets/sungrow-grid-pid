"""Editable Sungrow Energy Manager parameters, restored across restarts."""
from __future__ import annotations
from homeassistant.components.number import NumberEntity
from homeassistant.helpers.restore_state import RestoreEntity
from .const import DOMAIN

PARAMETERS = {
    "export_target": ("Export Target SP", 0, 17000, 100, "W", 10000),
    "dead_band": ("Export Dead Band", 0, 10000, 100, "W", 1000),
    "delay": ("Export Delay Time", 0, 86400, 1, "s", 600),
    "charge_gain": ("Charge Gain SP", 1, 25000, 100, "W", 3000),
    "empty_soc": ("Empty SOC SP", 0, 100, 1, "%", 30),
    "discharge_power": ("Battery Forced Discharge Power", 0, 25000, 100, "W", 8000),
}

class Parameter(NumberEntity, RestoreEntity):
    _attr_should_poll = False
    _attr_has_entity_name = False

    def __init__(self, manager, key, setting):
        self.manager, self.key = manager, key
        label, low, high, step, unit, default = setting
        self._attr_name = "SEM " + label
        self._attr_unique_id = "sungrow_energy_manager_" + key
        self.entity_id = "number.sem_" + key
        self._attr_native_min_value = low
        self._attr_native_max_value = high
        self._attr_native_step = step
        self._attr_native_unit_of_measurement = unit
        self._attr_native_value = default

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        prior = await self.async_get_last_state()
        if prior:
            try:
                value = float(prior.state)
                if self.native_min_value <= value <= self.native_max_value:
                    self._attr_native_value = value
            except (ValueError, TypeError):
                pass
        self.manager.params[self.key] = self._attr_native_value

    async def async_set_native_value(self, value):
        self._attr_native_value = value
        self.manager.params[self.key] = value
        self.async_write_ha_state()
        self.manager.notify()

async def async_setup_entry(hass, entry, async_add_entities):
    manager = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([Parameter(manager, key, value) for key, value in PARAMETERS.items()])
