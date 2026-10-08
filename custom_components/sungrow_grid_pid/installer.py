"""Install editable Home Assistant helpers and a normal YAML automation.

A restart is needed after creating input_number storage helpers because HA owns
their in-memory storage collection. Existing helpers are never overwritten.
"""
from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.helpers.storage import Store
from homeassistant.util.file import write_utf8_file_atomic
from homeassistant.util.yaml import dump, load_yaml

_LOGGER = logging.getLogger(__name__)
AUTOMATION_ID = "sungrow_grid_pid_simple_controller"
HELPERS = (
    ("input_number.pid_grid_target", {"name": "PID Grid Target", "min": 0, "max": 17000, "step": 1000, "mode": "box", "unit_of_measurement": "W"}),
    ("input_number.pid_integral", {"name": "PID Integral", "min": 0, "max": 25000, "step": 1, "mode": "box", "unit_of_measurement": "W"}),
)


def make_automation(export_entity, charge_entity, scene_entity):
    automation = {
        "id": AUTOMATION_ID,
        "alias": "Simple Grid Battery Controller",
        "description": "Installed by Sungrow Grid PID; editable in Home Assistant.",
        "triggers": [{"trigger": "time_pattern", "seconds": "/1"}],
        "conditions": [{"condition": "template", "value_template":
            "{{ is_number(states('" + export_entity + "')) and is_number(states('input_number.pid_grid_target')) and is_number(states('input_number.pid_integral')) }}"}],
        "actions": [
            {"variables": {
                "grid": "{{ states('" + export_entity + "') | float }}",
                "target": "{{ states('input_number.pid_grid_target') | float }}",
                "output_old": "{{ states('input_number.pid_integral') | float }}",
            }},
            {"variables": {"error": "{{ grid - target }}"}},
            {"variables": {"output_new": "{% set x = output_old + (error * 0.10) %} {{ [[x, 0] | max, 25000] | min | round(0) }}"}},
            {"action": "number.set_value", "target": {"entity_id": charge_entity}, "data": {"value": "{{ output_new }}"}},
            {"action": "input_number.set_value", "target": {"entity_id": "input_number.pid_integral"}, "data": {"value": "{{ output_new }}"}},
        ],
        "mode": "single",
        "max_exceeded": "silent",
        "initial_state": False,
    }
    # Optional scene is run only when a user turns on the automation,
    # handled by a state-change listener in the integration.
    return automation


def write_automation(path, automation):
    path = Path(path)
    content = load_yaml(str(path)) if path.exists() else []
    if content is None:
        content = []
    if not isinstance(content, list):
        raise ValueError("automations.yaml must contain a list; no files changed")
    found = next((i for i, a in enumerate(content) if isinstance(a, dict) and a.get("id") == AUTOMATION_ID), None)
    if found is None:
        # Preserve an existing manually-authored automation with the same name.
        if any(isinstance(a, dict) and a.get("alias") == automation["alias"] for a in content):
            return "existing_manual"
        content.append(automation)
        write_utf8_file_atomic(str(path), dump(content))
        return "created"
    # User edits are preserved on subsequent starts.
    return "existing"


async def install_helpers(hass):
    """Seed official input_number storage without touching existing data."""
    missing = [h for h, _ in HELPERS if hass.states.get(h) is None]
    if not missing:
        return False
    store = Store(hass, 1, "input_number")
    current = await store.async_load() or {"items": []}
    items = current.setdefault("items", [])
    known = {str(item.get("id", "")) for item in items}
    pending = []
    for entity, data in HELPERS:
        key = entity.split(".", 1)[1]
        if hass.states.get(entity) is not None or key in known:
            continue
        pending.append({"id": key, **data})
    if not pending:
        return False
    # Storage is independently owned by HA. Installation changes become
    # available on next core restart, rather than mutating a live collection.
    items.extend(pending)
    await store.async_save(current)
    _LOGGER.warning("Created input_number helper definitions: %s. Restart Home Assistant to load them.", [x["id"] for x in pending])
    return True


async def install_dashboard(hass):
    """Create a dedicated dashboard containing the PID controller card."""
    from homeassistant.components import frontend
    from homeassistant.components.lovelace import dashboard
    from homeassistant.components.lovelace.const import LOVELACE_DATA

    data = hass.data.get(LOVELACE_DATA)
    if data is None or "sungrow-grid-pid" in data.dashboards:
        return

    dashboards = dashboard.DashboardsCollection(hass)
    await dashboards.async_load()
    if any(item.get("url_path") == "sungrow-grid-pid" for item in dashboards.async_items()):
        return

    item = await dashboards.async_create_item({
        "url_path": "sungrow-grid-pid",
        "title": "Sungrow Grid PID",
        "icon": "mdi:solar-power",
        "show_in_sidebar": True,
        "require_admin": False,
    })
    page = dashboard.LovelaceStorage(hass, item)
    await page.async_save({
        "title": "Sungrow Grid PID",
        "views": [{
            "title": "PID",
            "path": "pid",
            "cards": [{"type": "custom:sungrow-grid-pid-card"}],
        }],
    })
    data.dashboards["sungrow-grid-pid"] = page
    if not frontend.async_panel_exists(hass, "sungrow-grid-pid"):
        frontend.async_register_built_in_panel(
            hass, "lovelace", frontend_url_path="sungrow-grid-pid",
            require_admin=False, show_in_sidebar=True,
            sidebar_title="Sungrow Grid PID", sidebar_icon="mdi:solar-power",
            config={"mode": "storage"},
        )


async def install(hass, entry):
    created_helpers = await install_helpers(hass)
    automation = make_automation(
        entry.options.get("export_entity", entry.data.get("export_entity", "sensor.export_power")),
        entry.options.get("charge_entity", entry.data.get("charge_entity", "number.battery_max_charge_power")),
        entry.options.get("scene_entity", entry.data.get("scene_entity", "scene.self_consumption_mode_max_battery_discharge")),
    )
    result = await hass.async_add_executor_job(write_automation, hass.config.path("automations.yaml"), automation)
    if result in ("created", "existing_manual", "existing"):
        await hass.services.async_call("automation", "reload", {}, blocking=True)
    candidates = [(entity_id, state.attributes.get("friendly_name")) for entity_id, state in hass.states.async_all("automation") if "grid" in entity_id.lower() or "pid" in entity_id.lower() or "battery" in entity_id.lower()]
    if not candidates:
        _LOGGER.error("Sungrow Grid PID: automation not found after reload. Installer status=%s. Confirm configuration.yaml includes automation: !include automations.yaml and check automation errors in Home Assistant logs.", result)
    else:
        _LOGGER.info("Available battery/PID automations: %s", candidates)
    try:
        await install_dashboard(hass)
    except Exception:
        _LOGGER.exception("Dashboard creation failed; helpers and automation remain installed")
    return result, created_helpers
