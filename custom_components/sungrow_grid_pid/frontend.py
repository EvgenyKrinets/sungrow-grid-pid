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
CARD_STATIC_URL = f"/sungrow_grid_pid/{VERSION}/sungrow-grid-pid-card.js"
CARD_URL = f"{CARD_STATIC_URL}?v={VERSION}"
MORE_INFO_PATH = Path(__file__).parent / "frontend" / "vendor" / "custom-more-info.js"
MORE_INFO_STATIC_URL = f"/sungrow_grid_pid/{VERSION}/custom-more-info.js"
MORE_INFO_URL = f"{MORE_INFO_STATIC_URL}?v={VERSION}"


async def _try_register_resource(hass: HomeAssistant) -> bool:
    """Register our card and vendored more-info JS, respecting a HACS copy."""
    lovelace = hass.data.get(LOVELACE_DATA)
    if lovelace is None:
        return False
    resources = lovelace.resources
    if not getattr(resources, "loaded", True):
        return False
    if not hasattr(resources, "async_create_item"):
        return False

    items = list(resources.async_items())
    card_resource = next(
        (item for item in items
         if str(item.get("url", "")).split("?")[0].endswith("/sungrow-grid-pid-card.js")),
        None,
    )
    if card_resource is None:
        await resources.async_create_item({"res_type": "module", "url": CARD_URL})
    elif card_resource.get("url") != CARD_URL:
        await resources.async_update_item(
            card_resource["id"], {"res_type": "module", "url": CARD_URL}
        )

    # If Custom More Info has already been installed by the user through
    # HACS, don't load our bundled copy in parallel.
    items = list(resources.async_items())
    upstream_exists = any(
        "custom-more-info" in str(item.get("url", "")).lower()
        and not str(item.get("url", "")).split("?")[0].startswith("/sungrow_grid_pid/")
        for item in items
    )
    own_resource = next(
        (item for item in items if str(item.get("url", "")).split("?")[0].startswith("/sungrow_grid_pid/")
         and str(item.get("url", "")).split("?")[0].endswith("/custom-more-info.js")),
        None,
    )
    if upstream_exists:
        if own_resource is not None:
            await resources.async_delete_item(own_resource["id"])
        _LOGGER.info("Custom More Info already installed; using the existing HACS resource")
    elif own_resource is None:
        await resources.async_create_item({"res_type": "module", "url": MORE_INFO_URL})
        _LOGGER.info("Automatically registered bundled Custom More Info resource")
    elif own_resource.get("url") != MORE_INFO_URL:
        await resources.async_update_item(
            own_resource["id"], {"res_type": "module", "url": MORE_INFO_URL}
        )
    return True


async def async_register_frontend(hass: HomeAssistant) -> None:
    """Serve the card and reliably register it after Lovelace is ready."""
    await hass.http.async_register_static_paths(
        [StaticPathConfig(CARD_STATIC_URL, str(CARD_PATH), False),
         StaticPathConfig(MORE_INFO_STATIC_URL, str(MORE_INFO_PATH), False)]
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
            # Do not use a fallback for the optional plugin: duplicate loading
            # is worse than requiring the Lovelace resource registry.

    await _register()
