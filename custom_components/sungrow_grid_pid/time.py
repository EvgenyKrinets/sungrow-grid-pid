"""Morning discharge start time control."""
from datetime import time
from homeassistant.components.time import TimeEntity
from homeassistant.helpers.restore_state import RestoreEntity
from .const import DOMAIN

class MorningTime(TimeEntity, RestoreEntity):
    _attr_name = "SEM Morning Discharge Start"
    _attr_unique_id = "sungrow_energy_manager_morning_start"
    _attr_should_poll = False
    _attr_has_entity_name = False

    def __init__(self, manager):
        self.manager = manager
        self.entity_id = "time.sem_morning_start"
        self._attr_native_value = time(5,0)

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        old = await self.async_get_last_state()
        if old and old.state not in ("unknown","unavailable"):
            try:
                self._attr_native_value = time.fromisoformat(old.state)
            except ValueError:
                pass
        self.manager.start_time = self._attr_native_value

    async def async_set_value(self, value):
        self._attr_native_value = value
        self.manager.start_time = value
        self.async_write_ha_state()

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([MorningTime(hass.data[DOMAIN][entry.entry_id])])
