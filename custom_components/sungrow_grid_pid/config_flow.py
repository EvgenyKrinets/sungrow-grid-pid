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
            return await self.async_step_remove()

        if user_input is not None:
            return self.async_create_entry(title="Sungrow Grid PID", data={})

        return self.async_show_form(step_id="user", data_schema=vol.Schema({}))

    async def async_step_remove(self, user_input=None):
        """Recovery wizard for an orphaned/hidden configuration entry.

        Home Assistant may still have an entry even when the integration is not
        visible among loaded integrations. Only delete after explicit confirmation.
        """
        if user_input is None:
            return self.async_show_form(
                step_id="remove",
                data_schema=vol.Schema({vol.Required("confirm", default=False): bool}),
            )

        if not user_input.get("confirm"):
            return self.async_abort(reason="removal_cancelled")

        entries = self._async_current_entries()
        for entry in entries:
            await self.hass.config_entries.async_remove(entry.entry_id)
        return self.async_abort(reason="removed_successfully")

    @staticmethod
    def async_get_options_flow(config_entry):
        return SungrowGridPidOptionsFlow(config_entry)


class SungrowGridPidOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            if (user_input["target_max"] <= user_input["target_min"] or user_input["target_step"] <= 0):
                return self.async_show_form(step_id="init", data_schema=self._schema(), errors={"base": "invalid_slider_range"})
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(step_id="init", data_schema=self._schema())

    def _schema(self):
        current = self.config_entry.options
        return vol.Schema({
            vol.Required("export_entity", default=current.get("export_entity", DEFAULT_EXPORT_ENTITY)): str,
            vol.Required("charge_entity", default=current.get("charge_entity", DEFAULT_CHARGE_ENTITY)): str,
            vol.Required("scene_entity", default=current.get("scene_entity", DEFAULT_SCENE_ENTITY)): str,
            vol.Required("target_min", default=current.get("target_min", DEFAULT_TARGET_MIN)): vol.Coerce(float),
            vol.Required("target_max", default=current.get("target_max", DEFAULT_TARGET_MAX)): vol.Coerce(float),
            vol.Required("target_step", default=current.get("target_step", DEFAULT_TARGET_STEP)): vol.Coerce(float),
        })
