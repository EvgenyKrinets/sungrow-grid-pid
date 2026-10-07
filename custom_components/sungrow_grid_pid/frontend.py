from __future__ import annotations

from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

from .const import VERSION

CARD_URL = f"/sungrow_grid_pid/sungrow-grid-pid-card.js?v={VERSION}"
CARD_PATH = Path(__file__).parent / "frontend" / "sungrow-grid-pid-card.js"


async def async_register_frontend(hass: HomeAssistant) -> None:
    """Serve and load the bundled Lovelace card."""
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                "/sungrow_grid_pid/sungrow-grid-pid-card.js",
                str(CARD_PATH),
                False,
            )
        ]
    )
    add_extra_js_url(hass, CARD_URL)
