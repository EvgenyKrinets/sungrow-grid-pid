from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import UnitOfPower

from .const import DEFAULT_MAX_TARGET, DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    controller = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([GridTargetNumber(controller)])


class GridTargetNumber(NumberEntity):
    _attr_name = "PID Grid Target"
    _attr_unique_id = "sungrow_grid_pid_target"
    _attr_icon = "mdi:transmission-tower-export"
    _attr_native_min_value = 0
    _attr_native_max_value = DEFAULT_MAX_TARGET
    _attr_native_step = 1000
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_mode = NumberMode.SLIDER

    def __init__(self, controller):
        self.controller = controller

    @property
    def native_value(self):
        return self.controller.target

    async def async_set_native_value(self, value):
        self.controller.target = float(value)
        self.async_write_ha_state()
