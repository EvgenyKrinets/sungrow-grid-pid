"""Guarded manual morning-discharge test button."""
from homeassistant.components.button import ButtonEntity
from .const import DOMAIN

class TestMorningDischarge(ButtonEntity):
    _attr_name = "SEM Test Morning Discharge"
    _attr_unique_id = "sungrow_energy_manager_test_discharge"
    _attr_icon = "mdi:battery-arrow-down-outline"
    _attr_has_entity_name = False

    def __init__(self, manager):
        self.manager = manager
        self.entity_id = "button.sem_test_morning_discharge"

    async def async_press(self):
        await self.manager.manual_morning_test()

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([TestMorningDischarge(hass.data[DOMAIN][entry.entry_id])])
