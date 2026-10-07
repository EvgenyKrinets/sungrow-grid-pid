from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace import LOVELACE_DATA
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_call_later

from .const import VERSION

_LOGGER = logging.getLogger(__name__)
CARD_PATH = Path(__file__).parent / "frontend" / "sungrow-grid-pid-card.js"
CARD_STATIC_URL = "/sungrow_grid_pid/sungrow-grid-pid-card.js"
CARD_URL = f"{CARD_STATIC_URL}?v={VERSION}"


async def _try_register_resource(hass: HomeAssistant) -> bool:
    """Register/update the JS module in Lovelace storage resources."""
    lovelace = hass.data.get(LOVELACE_DATA)
    if lovelace is None:
        return False
    resources = lovelace.resources
    if not getattr(resources, "loaded", True):
        return False
    if not hasattr(resources, "async_create_item"):
        return False

    for item in resources.async_items():
        url = str(item.get("url", ""))
        if url.split("?")[0] == CARD_STATIC_URL:
            if url != CARD_URL and hasattr(resources, "async_update_item"):
                await resources.async_update_item(
                    item["id"], {"res_type": "module", "url": CARD_URL}
                )
            return True

    await resources.async_create_item({"res_type": "module", "url": CARD_URL})
    return True


async def async_register_frontend(hass: HomeAssistant) -> None:
    """Serve the card and reliably register it after Lovelace is ready."""
    await hass.http.async_register_static_paths(
        [StaticPathConfig(CARD_STATIC_URL, str(CARD_PATH), False)]
    )

    attempts = 0

    async def _register(_now=None) -> None:
        nonlocal attempts
        attempts += 1
        try:
            if await _try_register_resource(hass):
                _LOGGER.info("Sungrow Grid PID Lovelace card registered: %s", CARD_URL)
                return
        except Exception:
            _LOGGER.exception("Unable to register Sungrow Grid PID Lovelace resource")

        # Lovelace may initialize after custom integrations. Retry instead of
        # permanently falling back too early.
        if attempts < 12:
            async_call_later(hass, 5, _register)
        else:
            _LOGGER.warning("Lovelace storage resources unavailable; using frontend fallback")
            add_extra_js_url(hass, CARD_URL)

    await _register()
