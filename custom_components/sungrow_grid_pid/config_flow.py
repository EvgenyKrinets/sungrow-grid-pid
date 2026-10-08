from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries

from .const import (
    DEFAULT_CHARGE_ENTITY,
    DEFAULT_EXPORT_ENTITY,
    DEFAULT_SCENE_ENTITY,
    DEFAULT_TARGET_MAX,
    DEFAULT_TARGET_MIN,
    DEFAULT_TARGET_STEP,
    DOMAIN,
)


class SungrowGridPidConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 2

    async def async_step_user(self, user_input=None):
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(title="Sungrow Grid PID", data={})

        return self.async_show_form(step_id="user", data_schema=vol.Schema({}))

    @staticmethod
    def async_get_options_flow(config_entry):
        return SungrowGridPidOptionsFlow(config_entry)


class SungrowGridPidOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self.config_entry.options
        schema = vol.Schema({
            vol.Required("export_entity", default=current.get("export_entity", DEFAULT_EXPORT_ENTITY)): str,
            vol.Required("charge_entity", default=current.get("charge_entity", DEFAULT_CHARGE_ENTITY)): str,
            vol.Required("scene_entity", default=current.get("scene_entity", DEFAULT_SCENE_ENTITY)): str,
            vol.Required("target_min", default=current.get("target_min", DEFAULT_TARGET_MIN)): vol.Coerce(float),
            vol.Required("target_max", default=current.get("target_max", DEFAULT_TARGET_MAX)): vol.Coerce(float),
            vol.Required("target_step", default=current.get("target_step", DEFAULT_TARGET_STEP)): vol.Coerce(float),
        })
        return self.async_show_form(step_id="init", data_schema=schema)
