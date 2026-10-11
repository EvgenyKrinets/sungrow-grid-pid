"""Safely configure native Logbook filters without disabling Recorder graphs.

Only simple configuration.yaml mappings are auto-edited. Nonstandard !include,
inline mappings or aliased YAML are left untouched with a logged explanation.
"""
from __future__ import annotations

from pathlib import Path
import re
import shutil

from homeassistant.util.file import write_utf8_file_atomic

EXCLUDED_ENTITIES = (
    "number.battery_max_charge_power",
    "input_number.pid_integral",
    "automation.simple_grid_battery_controller",
)

TOP = re.compile(r"^([a-zA-Z_][\w]*)\s*:")
PLAIN = re.compile(r"^(\s*)([a-zA-Z_][\w]*)\s*:\s*(?:#.*)?$")


def _sections(lines):
    starts = [(i, m.group(1)) for i, line in enumerate(lines) if (m := TOP.match(line))]
    sections = {}
    for n, (i, key) in enumerate(starts):
        end = starts[n + 1][0] if n + 1 < len(starts) else len(lines)
        sections.setdefault(key, []).append((i, end))
    return sections


def _simple_section(lines, bounds):
    start, end = bounds
    block = "".join(lines[start:end])
    return not any(tag in block for tag in ("!include", "<<:", "{", "}", "&", "*"))


def _add_exclusions(lines):
    """Return new text or status; never replace other users' exclusions."""
    sections = _sections(lines)
    current = sections.get("logbook", [])
    if len(current) > 1:
        return None, "duplicate_logbook"
    if not current:
        if any(line.lstrip().startswith("logbook:") for line in lines):
            return None, "complex_logbook"
        lines.extend(["\n", "logbook:\n", "  exclude:\n", "    entities:\n"])
        bounds = (len(lines) - 4, len(lines))
    else:
        bounds = current[0]
        if not _simple_section(lines, bounds):
            return None, "complex_logbook"
    start, end = bounds
    block = lines[start:end]
    exclude_idx = next((i for i, line in enumerate(block) if re.match(r"^  exclude\s*:\s*(?:#.*)?$", line)), None)
    if exclude_idx is None:
        insert = start + 1
        lines[insert:insert] = ["  exclude:\n", "    entities:\n"]
        entities_idx = insert + 1
    else:
        entities_relative = next((i for i, line in enumerate(block[exclude_idx + 1:], exclude_idx + 1) if re.match(r"^    entities\s*:\s*(?:#.*)?$", line)), None)
        if entities_relative is not None:
            entities_idx = start + entities_relative
        else:
            if any(re.match(r"^    entities\s*:", line) for line in block):
                return None, "complex_entities"
            entities_idx = start + exclude_idx + 1
            lines.insert(entities_idx, "    entities:\n")
    # Match only the actual list under logbook.exclude.entities, not unrelated keys.
    existing = set()
    for line in lines[entities_idx + 1:]:
        if re.match(r"^\S|^  \S|^    \S", line) and line.strip() and not line.lstrip().startswith("#"):
            break
        match = re.match(r"^      -\s+([^#\n]+)", line)
        if match:
            existing.add(match.group(1).strip().strip("'\""))
        elif line.strip() and not line.lstrip().startswith("#") and not line.startswith("      "):
            return None, "complex_entities"
    missing = [entity for entity in EXCLUDED_ENTITIES if entity not in existing]
    if not missing:
        return "".join(lines), "already_configured"
    lines[entities_idx + 1:entities_idx + 1] = ["      - " + entity + "\n" for entity in missing]
    return "".join(lines), "updated_restart_required"


def ensure_logbook_exclusion(config_file: str) -> str:
    """Update Logbook-only exclusion; back up original configuration first.

    Never change recorder.include or recorder.exclude: doing so could remove
    the historical graph the user wants to retain.
    """
    path = Path(config_file)
    if not path.exists():
        return "missing_configuration"
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)
    sections = _sections(lines)

    # Detect conflict and leave Recorder untouched, since an included entity
    # may otherwise disappear from the History graph.
    recorder = sections.get("recorder", [])
    if len(recorder) > 1:
        return "complex_recorder"
    if recorder and not _simple_section(lines, recorder[0]):
        return "complex_recorder"

    updated, result = _add_exclusions(lines)
    if updated is None or updated == original:
        return result
    shutil.copy2(path, path.with_name(path.name + ".sungrow-grid-pid.bak"))
    write_utf8_file_atomic(str(path), updated)
    return result
