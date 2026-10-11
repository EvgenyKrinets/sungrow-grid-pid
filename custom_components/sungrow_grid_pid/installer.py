"""Install editable Home Assistant helpers and a normal YAML automation.

A restart is needed after creating input_number storage helpers because HA owns
their in-memory storage collection. Existing helpers are never overwritten.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
import shutil

from homeassistant.helpers.storage import Store
from homeassistant.util.file import write_utf8_file_atomic
from homeassistant.util.yaml import dump, load_yaml

from .logbook_config import ensure_logbook_exclusion

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
            {"variables": {"output_new": """{% set lo = state_attr('__CHARGE__', 'min') | float(10) %}
{% set hi = state_attr('__CHARGE__', 'max') | float(25000) %}
{% set output = output_old + error * 0.10 %}
{{ [[output, lo] | max, hi] | min | round(2) }}
""".replace("__CHARGE__", charge_entity)}},
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
    by_id = [i for i, item in enumerate(content) if isinstance(item, dict) and item.get("id") == AUTOMATION_ID]
    by_alias = [i for i, item in enumerate(content) if isinstance(item, dict) and item.get("alias") == automation["alias"]]
    # Never modify an ambiguous automation or create a second one.
    if len(by_id) > 1 or len(by_alias) > 1 or (by_id and by_alias and by_id[0] != by_alias[0]):
        _LOGGER.error("More than one PID automation exists; refusing automatic edits")
        return "ambiguous"
    found = by_id[0] if by_id else (by_alias[0] if by_alias else None)
    if found is None:
        content.append(automation)
        write_utf8_file_atomic(str(path), dump(content))
        return "created"

    item = content[found]
    actions = item.get("actions", item.get("action", []))
    if not isinstance(actions, list):
        return "existing_custom"

    def target_matches(action, service, entity):
        if not isinstance(action, dict) or action.get("action", action.get("service")) != service:
            return False
        target = action.get("target", {})
        return target.get("entity_id") == entity

    # Only migrate the original user's known automation pattern or our own ID.
    if not any(target_matches(a, "input_number.set_value", "input_number.pid_integral") for a in actions):
        return "existing_custom"
    if not any(target_matches(a, "number.set_value", automation["actions"][3]["target"]["entity_id"]) for a in actions):
        return "existing_custom"
    outputs = [a for a in actions if isinstance(a, dict) and isinstance(a.get("variables"), dict) and "output_new" in a["variables"]]
    if len(outputs) != 1:
        return "existing_custom"
    action = outputs[0]
    formula = str(action["variables"]["output_new"])
    new_formula = automation["actions"][2]["variables"]["output_new"]
    if formula.strip() == new_formula.strip():
        return "existing"

    # YAML folded > may change whitespace: match the original algorithm
    # structurally, rather than exact formatting. Do not overwrite custom PID.
    normalized = re.sub(r"\s+", " ", formula).strip()
    old_simple = (
        re.search(r"{%\s*set\s+x\s*=\s*output_old\s*\+\s*\(error\s*\*\s*0\.10\)\s*%}", normalized)
        and "[[x, 0] | max, 25000] | min" in normalized
        and "| round(0)" in normalized
    )
    old_cloud = "error <= -2000" in normalized and old_simple
    # Recognize all our previous dynamic min/max/step variants, including
    # the v3.0.13 "error < 0" forced-minimum formula.
    old_dynamic = (
        "{% set lo = state_attr(" in formula
        and "{% set aligned = lo + n * step %}" in formula
        and "{% set desired =" in formula
        and "output_old + error * 0.10" in formula
    )
    old_smooth_limited = (
        "{% set lo = state_attr(" in formula
        and "{% set output = output_old + error * 0.10 %}" in formula
        and "[state_attr(" in formula
        and "'max') | float(25000), 25000] | min" in formula
    )
    if not (old_simple or old_cloud or old_dynamic or old_smooth_limited):
        _LOGGER.warning("PID automation formula is custom; preserving it: %s", item.get("alias"))
        return "existing_custom"

    # Preserve the user's automation ID, description, enabled state and all
    # other action steps. Only replace the old supported output expression.
    if path.exists():
        shutil.copy2(path, path.with_name(path.name + ".sungrow-grid-pid.bak"))
    action["variables"]["output_new"] = new_formula
    write_utf8_file_atomic(str(path), dump(content))
    _LOGGER.info("Updated existing PID automation formula (id=%s, alias=%s)", item.get("id"), item.get("alias"))
    return "updated"

async def install_helpers(hass):
    """Create native input_number entities, persist their config and verify existence.

    Previous versions only modified the storage file, leaving the entities
    missing in the current running session. This registers the missing
    native InputNumber entities with Home Assistant immediately.
    """
    from homeassistant.components.input_number import DATA_INPUT_NUMBER, InputNumber
    from homeassistant.helpers.entity_registry import async_get as get_registry

    runtime = hass.data.get(DATA_INPUT_NUMBER)
    if runtime is None:
        raise RuntimeError("input_number is not loaded; cannot install PID helpers")

    store = Store(hass, 1, "input_number")
    stored = await store.async_load() or {"items": []}
    items = stored.setdefault("items", [])
    if not isinstance(items, list):
        raise RuntimeError("Invalid input_number storage; refusing to overwrite")
    by_id = {str(item.get("id")): item for item in items}
    registry = get_registry(hass)

    created = False
    persisted_change = False
    for entity_id, definition in HELPERS:
        if hass.states.get(entity_id) is not None:
            continue
        key = entity_id.partition(".")[2]
        data = by_id.get(key)
        if data is None:
            # Do not override any entity owned by another integration, nor
            # YAML-configured native helpers whose storage entry is absent.
            existing = registry.async_get(entity_id)
            if existing is not None:
                _LOGGER.error("PID helper %s belongs to an existing registry entry; not replacing it", entity_id)
                continue
            data = {"id": key, **definition, "initial": 15000 if key == "pid_grid_target" else 0}
            items.append(data)
            by_id[key] = data
            persisted_change = True

        # InputNumber.from_storage uses the same native entity class as the
        # input_number integration. Register it with its existing component.
        native = InputNumber.from_storage(data)
        native.entity_id = entity_id
        await runtime.component.async_add_entities([native])
        if hass.states.get(entity_id) is None:
            raise RuntimeError(f"Failed to create required native helper {entity_id}")
        _LOGGER.info("Registered native PID helper: %s", entity_id)
        created = True

    if persisted_change:
        await store.async_save(stored)

    missing = [eid for eid, _ in HELPERS if hass.states.get(eid) is None]
    if missing:
        raise RuntimeError(f"Required PID helpers remain missing: {missing}")
    return created


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
    logbook_result = await hass.async_add_executor_job(
        ensure_logbook_exclusion, hass.config.path("configuration.yaml")
    )
    if logbook_result == "updated_restart_required":
        _LOGGER.warning(
            "Sungrow Grid PID added Logbook exclusions for charge power, PID Integral and PID automation. "
            "Restart Home Assistant to hide Activity entries; Recorder graphs remain active."
        )
    elif logbook_result not in ("already_configured",):
        _LOGGER.warning(
            "Sungrow Grid PID did not modify Logbook config (%s). "
            "Review configuration.yaml manually if needed.", logbook_result
        )
    created_helpers = await install_helpers(hass)
    automation = make_automation(
        entry.options.get("export_entity", entry.data.get("export_entity", "sensor.export_power")),
        entry.options.get("charge_entity", entry.data.get("charge_entity", "number.battery_max_charge_power")),
        entry.options.get("scene_entity", entry.data.get("scene_entity", "scene.self_consumption_mode_max_battery_discharge")),
    )
    result = await hass.async_add_executor_job(write_automation, hass.config.path("automations.yaml"), automation)
    if result in ("created", "existing_manual", "existing", "updated"):
        await hass.services.async_call("automation", "reload", {}, blocking=True)
    candidates = [(state.entity_id, state.attributes.get("friendly_name")) for state in hass.states.async_all("automation") if any(term in state.entity_id.lower() for term in ("grid", "pid", "battery"))]
    if not candidates:
        _LOGGER.error("Sungrow Grid PID: automation not found after reload. Installer status=%s. Confirm configuration.yaml includes automation: !include automations.yaml and check automation errors in Home Assistant logs.", result)
    else:
        _LOGGER.info("Available battery/PID automations: %s", candidates)
    try:
        await install_dashboard(hass)
    except Exception:
        _LOGGER.exception("Dashboard creation failed; helpers and automation remain installed")
    return result, created_helpers
