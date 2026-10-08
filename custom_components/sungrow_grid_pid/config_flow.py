"""Config flow with prefilled Sungrow entities and validation."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN

DEFAULTS = {
    "export_entity": "sensor.export_power",
    "charge_entity": "number.battery_max_charge_power",
    "scene_entity": "scene.self_consumption_mode_max_battery_discharge",
}


def schema(data):
    return vol.Schema({
        vol.Required("export_entity", default=data.get("export_entity", DEFAULTS["export_entity"])): str,
        vol.Required("charge_entity", default=data.get("charge_entity", DEFAULTS["charge_entity"])): str,
        vol.Required("scene_entity", default=data.get("scene_entity", DEFAULTS["scene_entity"])): str,
    })


def verify(hass, values):
    if not values["export_entity"].startswith("sensor.") or hass.states.get(values["export_entity"]) is None:
        return {"export_entity": "entity_not_found"}
    if not values["charge_entity"].startswith("number.") or hass.states.get(values["charge_entity"]) is None:
        return {"charge_entity": "entity_not_found"}
    scene = values["scene_entity"]
    if scene and (not scene.startswith("scene.") or hass.states.get(scene) is None):
        return {"scene_entity": "entity_not_found"}
    return {}


class SungrowGridPidConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 3

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
