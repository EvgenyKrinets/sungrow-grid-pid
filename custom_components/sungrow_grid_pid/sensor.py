from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import UnitOfPower

from .const import DOMAIN, VERSION


async def async_setup_entry(hass, entry, async_add_entities):
    c = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        PidSensor(c, "PID Output", "output", "mdi:battery-arrow-down", "output"),
        PidSensor(c, "PID Grid Error", "error", "mdi:delta", "error"),
        VersionSensor(c),
    ])


class PidSensor(SensorEntity):
    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.WATT

    def __init__(self, controller, name, attr, icon, uid):
        self.controller = controller
        self._attr_name = name
        self.attr = attr
        self._attr_icon = icon
        self._attr_unique_id = f"sungrow_grid_pid_{uid}"
        controller.add_listener(self._update)

    @property
    def native_value(self):
        return round(getattr(self.controller, self.attr))

    def _update(self):
        if self.hass:
            self.async_write_ha_state()


class VersionSensor(SensorEntity):
    _attr_name = "Sungrow Grid PID Version"
    _attr_unique_id = "sungrow_grid_pid_version"
    _attr_icon = "mdi:information-outline"

    def __init__(self, controller):
        self.controller = controller

    @property
    def native_value(self):
        return VERSION
