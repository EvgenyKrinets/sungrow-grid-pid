from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

from .const import VERSION

_LOGGER = logging.getLogger(__name__)

CARD_PATH = Path(__file__).parent / "frontend" / "sungrow-grid-pid-card.js"
CARD_STATIC_URL = "/sungrow_grid_pid/sungrow-grid-pid-card.js"
CARD_URL = f"{CARD_STATIC_URL}?v={VERSION}"


async def _register_lovelace_resource(hass: HomeAssistant) -> bool:
    """Register the card in Lovelace storage resources when writable."""
    try:
        lovelace = hass.data.get("lovelace")
        resources = getattr(lovelace, "resources", None)
        if resources is None or not hasattr(resources, "async_create_item"):
            return False

        items = resources.async_items()
        for item in items:
            url = str(item.get("url", ""))
            if url.startswith(CARD_STATIC_URL):
                if url != CARD_URL and hasattr(resources, "async_update_item"):
                    item_id = item.get("id")
                    if item_id:
                        await resources.async_update_item(item_id, {"res_type": "module", "url": CARD_URL})
                return True

        await resources.async_create_item({"res_type": "module", "url": CARD_URL})
        return True
    except Exception:
        _LOGGER.exception("Unable to register Sungrow Grid PID as Lovelace resource")
        return False


async def async_register_frontend(hass: HomeAssistant) -> None:
    """Serve the card and register it as a Lovelace module."""
    await hass.http.async_register_static_paths(
        [StaticPathConfig(CARD_STATIC_URL, str(CARD_PATH), False)]
    )

    # Preferred path: Lovelace resource collection. It loads after HA's
    # custom-element registry is ready and therefore appears reliably in picker.
    if not await _register_lovelace_resource(hass):
        # Fallback for YAML/read-only resource mode.
        add_extra_js_url(hass, CARD_URL)
