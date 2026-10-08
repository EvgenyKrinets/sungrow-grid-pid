"""Config flow: native entity dropdowns with Sungrow defaults and validation."""
from __future__ import annotations

import math
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import DOMAIN

DEFAULTS = {
    "export_entity": "sensor.export_power",
    "charge_entity": "number.battery_max_charge_power",
    "scene_entity": "scene.self_consumption_mode_max_battery_discharge",
}


def schema(values):
    """HA entity selectors show searchable entity pickers instead of free text."""
    return vol.Schema({
        vol.Required("export_entity", default=values.get("export_entity", DEFAULTS["export_entity"])):
            selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
        vol.Required("charge_entity", default=values.get("charge_entity", DEFAULTS["charge_entity"])):
            selector.EntitySelector(selector.EntitySelectorConfig(domain="number")),
        vol.Required("scene_entity", default=values.get("scene_entity", DEFAULTS["scene_entity"])):
            selector.EntitySelector(selector.EntitySelectorConfig(domain="scene")),
    })


def verify(hass, values):
    """Reject wrong domains, absent/unavailable or nonnumeric power entities."""
    errors = {}
    for key, domain in (
        ("export_entity", "sensor"),
        ("charge_entity", "number"),
        ("scene_entity", "scene"),
    ):
        entity = values.get(key, "")
        state = hass.states.get(entity)
        if not entity.startswith(domain + ".") or state is None:
            errors[key] = "entity_not_found"
        elif state.state in ("unknown", "unavailable") and key != "scene_entity":
            errors[key] = "entity_unavailable"
        elif key == "export_entity":
            try:
                if not math.isfinite(float(state.state)):
                    errors[key] = "entity_not_numeric"
            except (ValueError, TypeError):
                errors[key] = "entity_not_numeric"
        elif key == "charge_entity":
            try:
                minimum = float(state.attributes.get("min", 0))
                maximum = float(state.attributes.get("max", 0))
                if not (math.isfinite(minimum) and math.isfinite(maximum) and maximum >= 25000):
                    errors[key] = "charge_range"
            except (ValueError, TypeError):
                errors[key] = "charge_range"
    return errors


class SungrowGridPidConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 4

    async def async_step_user(self, user_input=None):
        if self._async_current_entries():
            return await self.async_step_remove()
        if user_input is not None:
            errors = verify(self.hass, user_input)
            if not errors:
                return self.async_create_entry(title="Sungrow Grid PID", data=user_input)
            return self.async_show_form(step_id="user", data_schema=schema(user_input), errors=errors)
        return self.async_show_form(step_id="user", data_schema=schema({}))

    async def async_step_remove(self, user_input=None):
        if user_input is None:
            return self.async_show_form(step_id="remove", data_schema=vol.Schema({
                vol.Required("confirm", default=False): bool
            }))
        if not user_input.get("confirm"):
            return self.async_abort(reason="removal_cancelled")
        for entry in self._async_current_entries():
            await self.hass.config_entries.async_remove(entry.entry_id)
        return self.async_abort(reason="removed_successfully")

    @staticmethod
    def async_get_options_flow(config_entry):
        return SungrowGridPidOptionsFlow()


class SungrowGridPidOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            errors = verify(self.hass, user_input)
            if not errors:
                return self.async_create_entry(title="", data=user_input)
            return self.async_show_form(step_id="init", data_schema=schema(user_input), errors=errors)
        return self.async_show_form(step_id="init", data_schema=schema({
            **self.config_entry.data, **self.config_entry.options
        }))
