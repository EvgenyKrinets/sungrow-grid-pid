"""Safely add the optional Logbook-only entity exclusion.

Never touches Recorder: the history graph remains available.
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

from homeassistant.util.file import write_utf8_file_atomic

ENTITY = "number.battery_max_charge_power"


def ensure_logbook_exclusion(config_file: str) -> str:
    """Edit only a simple YAML logbook section; back up before writing.

    Complex/includes configs are left untouched rather than risking damage.
    A Home Assistant restart is required after changing configuration.yaml.
    """
    path = Path(config_file)
    if not path.exists():
        return "missing_configuration"
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)
    # Never act if the entity already appears anywhere in the Logbook config.
    headers = [i for i, line in enumerate(lines) if re.match(r"^logbook\s*:\s*(?:#.*)?$", line)]
    if len(headers) > 1:
        return "multiple_logbook_sections"
    if not headers:
        # If an unusual logbook mapping is present, avoid a duplicate YAML key.
        if re.search(r"^logbook\s*:", original, flags=re.M):
            return "complex_configuration"
        updated = original.rstrip("\r\n") + "\n\nlogbook:\n  exclude:\n    entities:\n      - " + ENTITY + "\n"
    else:
        start = headers[0]
        end = next((i for i in range(start + 1, len(lines)) if re.match(r"^[A-Za-z_][A-Za-z0-9_]*\s*:", lines[i])), len(lines))
        block = "".join(lines[start:end])
        if ENTITY in block:
            return "already_configured"
        # Only modify simple nesting; no includes, aliases or inline maps.
        if any(tok in block for tok in ("!include", "<<:", "{", "}")):
            return "complex_configuration"
        exclude = next((i for i in range(start + 1, end) if re.match(r"^  exclude\s*:\s*(?:#.*)?$", lines[i])), None)
        if exclude is None:
            lines.insert(end, "  exclude:\n    entities:\n      - " + ENTITY + "\n")
        else:
            entities = next((i for i in range(exclude + 1, end) if re.match(r"^    entities\s*:\s*(?:#.*)?$", lines[i])), None)
            if entities is None:
                lines.insert(exclude + 1, "    entities:\n      - " + ENTITY + "\n")
            else:
                # Guard against comma-separated or inline entity lists.
                if not re.match(r"^    entities\s*:\s*(?:#.*)?$", lines[entities]):
                    return "complex_configuration"
                lines.insert(entities + 1, "      - " + ENTITY + "\n")
        updated = "".join(lines)
    if updated == original:
        return "already_configured"
    shutil.copy2(path, path.with_name(path.name + ".sungrow-grid-pid.bak"))
    write_utf8_file_atomic(str(path), updated)
    return "updated_restart_required"
