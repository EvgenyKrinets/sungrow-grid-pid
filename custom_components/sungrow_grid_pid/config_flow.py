from __future__ import annotations

from homeassistant import config_entries

from .const import DOMAIN
from . import discover_entities


class SungrowGridPidConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        sungrow_entries = self.hass.config_entries.async_entries("sungrow")
        entities = discover_entities(self.hass)
        if not sungrow_entries:
            return self.async_abort(reason="sungrow_not_found")
        if not entities["export"] or not entities["charge"]:
            return self.async_abort(reason="required_entities_not_found")

        return self.async_create_entry(title="Sungrow Grid PID", data={})
