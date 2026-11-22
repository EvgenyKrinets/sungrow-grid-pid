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
        self.manager.last_attempt_minute = None
        self.manager.morning_status = "Scheduled for " + value.strftime("%H:%M")
        self.manager.notify()
        self.async_write_ha_state()

class TariffTime(TimeEntity, RestoreEntity):
    """User-adjustable discount start/end time, kept across restarts."""
    _attr_should_poll = False
    _attr_has_entity_name = False
    _attr_icon = "mdi:clock-time-four-outline"

    def __init__(self, manager, starting):
        self.manager, self.starting = manager, starting
        self._attr_name = "SEM Night Tariff Start" if starting else "SEM Night Tariff End"
        self._attr_unique_id = (
            "sungrow_energy_manager_tariff_start" if starting
            else "sungrow_energy_manager_tariff_end"
        )
        self.entity_id = (
            "time.sem_tariff_start" if starting
            else "time.sem_tariff_end"
        )
        self._attr_native_value = time(23, 0) if starting else time(7, 0)

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        old = await self.async_get_last_state()
        if old and old.state not in ("unknown", "unavailable"):
            try:
                self._attr_native_value = time.fromisoformat(old.state)
            except ValueError:
                pass
        if self.starting:
            self.manager.tariff_start = self._attr_native_value
        else:
            self.manager.tariff_end = self._attr_native_value

    async def async_set_value(self, value):
        self._attr_native_value = value
        if self.starting:
            self.manager.tariff_start = value
        else:
            self.manager.tariff_end = value
        self.manager.tariff_schedule_changed()
        self.async_write_ha_state()


async def async_setup_entry(hass, entry, async_add_entities):
    manager = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MorningTime(manager), TariffTime(manager, True), TariffTime(manager, False)])
