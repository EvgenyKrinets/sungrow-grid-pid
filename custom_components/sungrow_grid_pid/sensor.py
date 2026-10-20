"""Low-frequency historical snapshot of Sungrow battery charge command."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN

HISTORY_ENTITY_ID = "sensor.sungrow_pid_charge_history"


class ChargeHistorySensor(SensorEntity, RestoreEntity):
    _attr_name = "Sungrow PID Charge History"
    _attr_unique_id = "sungrow_grid_pid_charge_history"
    _attr_native_unit_of_measurement = "W"
    _attr_icon = "mdi:battery-charging"
    _attr_should_poll = False
    _attr_state_class = "measurement"
    _attr_entity_id = HISTORY_ENTITY_ID

    def __init__(self, hass, source: str) -> None:
        self._hass = hass
        self._source = source
        self.entity_id = HISTORY_ENTITY_ID
        self._attr_native_value = None

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        old = await self.async_get_last_state()
        if old and old.state not in ("unknown", "unavailable"):
            try:
                self._attr_native_value = float(old.state)
            except (ValueError, TypeError):
                pass
        self._sample(None)
        self.async_on_remove(
            async_track_time_interval(self.hass, self._sample, timedelta(seconds=10))
        )

    @callback
    def _sample(self, _now) -> None:
        source = self._hass.states.get(self._source)
        if source is None or source.state in ("unknown", "unavailable"):
            return
        try:
            value = float(source.state)
        except (TypeError, ValueError):
            return
        # Recorder stores state changes, not repeated writes of the same value.
        if value != self._attr_native_value:
            self._attr_native_value = value
            self.async_write_ha_state()


class ManagerStatusSensor(SensorEntity):
    """Native diagnostic status of the step controller."""

    _attr_name = "SEM Manager Status"
    _attr_unique_id = "sungrow_energy_manager_status"
    _attr_should_poll = False
    _attr_icon = "mdi:information-outline"

    def __init__(self, manager):
        self.manager = manager
        self.entity_id = "sensor.sem_manager_status"

    @property
    def native_value(self):
        return self.manager.status

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self.manager.add_listener(self._notify)

    @callback
    def _notify(self):
        self.async_write_ha_state()


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    charge = entry.options.get("charge_entity", entry.data.get("charge_entity", "number.battery_max_charge_power"))
    from .const import DOMAIN
    async_add_entities([
        ChargeHistorySensor(hass, charge),
        ManagerStatusSensor(hass.data[DOMAIN][entry.entry_id]),
    ])
