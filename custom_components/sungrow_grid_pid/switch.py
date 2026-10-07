from homeassistant.components.switch import SwitchEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    controller = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([GridPidSwitch(controller)])


class GridPidSwitch(SwitchEntity):
    _attr_name = "PID Grid Controller"
    _attr_unique_id = "sungrow_grid_pid_controller"
    _attr_icon = "mdi:tune-variant"

    def __init__(self, controller):
        self.controller = controller
        controller.add_listener(self._update)

    @property
    def is_on(self):
        return self.controller.enabled

    async def async_turn_on(self, **kwargs):
        await self.controller.enable()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self.controller.disable()
        self.async_write_ha_state()

    def _update(self):
        if self.hass:
            self.async_write_ha_state()
