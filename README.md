# Sungrow Grid PID

Local 1-second grid export controller for Home Assistant and Sungrow.

**Version: v1.1.0**

## Requirements
- Home Assistant
- [KRoperUK/sungrow-hass](https://github.com/KRoperUK/sungrow-hass)
- Local Sungrow/Modbus Export Power and Battery Charge Power entities

## HACS installation
1. HACS → Integrations → ⋮ → Custom repositories.
2. Add `EvgenyKrinets/sungrow-grid-pid` as **Integration**.
3. Install/update **Sungrow Grid PID** and restart Home Assistant.
4. Settings → Devices & services → Add integration → **Sungrow Grid PID**.
5. No entity IDs are requested: required Sungrow entities are discovered automatically.

## Lovelace card — v1.1.0
The integration now bundles and automatically loads its own **Sungrow Grid PID** dashboard card.

After restart:
1. Open any dashboard.
2. Edit dashboard → Add card.
3. Search for **Sungrow Grid PID**.
4. Add it. No YAML or entity IDs are required.

The card includes:
- PID Controller ON/OFF
- Grid Target slider
- current Grid Export
- PID Output
- Grid Error
- Battery Charge Command
- Running/Stopped status
- integration version

## Controller
Every second:

```
error = export_power - grid_target
output = previous_output + error * 0.10
output = clamp(output, 0, 25000)
```

When PID Controller is enabled, the integration remembers the current battery mode and selects **Force discharge / Forced discharge**. When PID Controller is disabled, it restores the previous mode.

This release intentionally keeps the proven controller logic. It does not add adaptive surplus search, Import Guard, D-term, or other control logic.

## Entities
- PID Grid Controller (switch)
- PID Grid Target (number, 0–25,000 W, 1,000 W step)
- PID Output (sensor)
- PID Grid Error (sensor)
- Sungrow Grid PID Version (sensor)
