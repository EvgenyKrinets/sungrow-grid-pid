from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import UnitOfPower
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    DEFAULT_MAX_CHARGE,
    DEFAULT_TARGET,
    DEFAULT_TARGET_MAX,
    DEFAULT_TARGET_MIN,
    DEFAULT_TARGET_STEP,
    DOMAIN,
)


async def async_setup_entry(hass, entry, async_add_entities):
    controller = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        GridTargetNumber(controller, entry),
        PidIntegralNumber(controller),
    ])


class GridTargetNumber(NumberEntity, RestoreEntity):
    _attr_name = "PID Grid Target"
    _attr_unique_id = "sungrow_grid_pid_target"
    _attr_icon = "mdi:transmission-tower-export"
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_mode = NumberMode.SLIDER

    def __init__(self, controller, entry):
        self.controller = controller
        self.entry = entry
        controller.add_listener(self._update)

    @property
    def native_min_value(self):
        return float(self.entry.options.get("target_min", DEFAULT_TARGET_MIN))

    @property
    def native_max_value(self):
        return float(self.entry.options.get("target_max", DEFAULT_TARGET_MAX))

    @property
    def native_step(self):
        return float(self.entry.options.get("target_step", DEFAULT_TARGET_STEP))

    @property
    def native_value(self):
        return self.controller.target

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        if (state := await self.async_get_last_state()) is not None:
            try:
                value = float(state.state)
                self.controller.target = max(self.native_min_value, min(self.native_max_value, value))
            except (TypeError, ValueError):
                self.controller.target = DEFAULT_TARGET
        self.async_write_ha_state()

    async def async_set_native_value(self, value):
        self.controller.target = max(self.native_min_value, min(self.native_max_value, float(value)))
        self.async_write_ha_state()
        self.controller.notify()

    def _update(self):
        if self.hass:
            self.async_write_ha_state()


class PidIntegralNumber(NumberEntity, RestoreEntity):
    _attr_name = "PID Integral"
    _attr_unique_id = "sungrow_grid_pid_integral"
    _attr_icon = "mdi:integral-box"
    _attr_native_min_value = 0
    _attr_native_max_value = DEFAULT_MAX_CHARGE
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_mode = NumberMode.BOX

    def __init__(self, controller):
        self.controller = controller
        controller.add_listener(self._update)

    @property
    def native_value(self):
        return self.controller.integral

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        if (state := await self.async_get_last_state()) is not None:
            try:
                self.controller.integral = max(0.0, min(DEFAULT_MAX_CHARGE, float(state.state)))
                self.controller.output = self.controller.integral
            except (TypeError, ValueError):
                pass
        self.async_write_ha_state()

    async def async_set_native_value(self, value):
        self.controller.integral = max(0.0, min(DEFAULT_MAX_CHARGE, float(value)))
        self.controller.output = self.controller.integral
        self.async_write_ha_state()
        self.controller.notify()

    def _update(self):
        if self.hass:
            self.async_write_ha_state()
