# Sungrow Grid PID

Local 1-second grid export controller for Home Assistant and Sungrow.

**Version: v1.0.0**

## Requirements
- Home Assistant
- [KRoperUK/sungrow-hass](https://github.com/KRoperUK/sungrow-hass)
- Local Sungrow/Modbus Export Power and Battery Charge Power entities

## HACS installation
1. HACS → Integrations → ⋮ → Custom repositories.
2. Add `EvgenyKrinets/sungrow-grid-pid` as **Integration**.
3. Install **Sungrow Grid PID** and restart Home Assistant.
4. Settings → Devices & services → Add integration → **Sungrow Grid PID**.
5. No entity IDs are requested: required Sungrow entities are discovered automatically.

## v1.0.0 controller
Every second:

```
error = export_power - grid_target
output = previous_output + error * 0.10
output = clamp(output, 0, 25000)
```

When PID Controller is enabled, the integration remembers the current battery mode and selects **Force discharge / Forced discharge**. When PID Controller is disabled, it restores the previous mode.

The first release intentionally matches the proven Home Assistant automation. It does not add adaptive surplus search, Import Guard, D-term, or other control logic.

## Entities
- PID Grid Controller (switch)
- PID Grid Target (number, 0–25,000 W, 1,000 W step)
- PID Output (sensor)
- PID Grid Error (sensor)
- Sungrow Grid PID Version (sensor)
