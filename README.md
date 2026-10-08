# Sungrow Grid PID v3.0.0

Home Assistant / HACS integration that installs an ordinary editable Home Assistant automation and two native input_number Helpers.

## Installation

1. Install this repository as a HACS integration.
2. Restart Home Assistant.
3. Settings → Devices & services → Add integration → Sungrow Grid PID.
4. Default entities are pre-filled; change if your setup differs:
   - Export sensor: `sensor.export_power`
   - Battery charge power: `number.battery_max_charge_power`
   - Self-consumption scene: `scene.self_consumption_mode_max_battery_discharge`
5. Submit. Integration checks these entities before creating anything.
6. **Restart Home Assistant one more time if Helpers were missing.** This is needed for Home Assistant to load the freshly stored input_number helpers.

The installer retains existing `input_number.pid_grid_target` (0..17000 W, step 1000) and `input_number.pid_integral` (0..25000 W, step 1), and creates only missing entries.

## What gets installed

- A regular editable automation in `automations.yaml` with ID `sungrow_grid_pid_simple_controller` and alias `Simple Grid Battery Controller`.
- The original one-second PID algorithm (error = grid - target, integrator += error * 0.10, output 0..25000).
- A dedicated sidebar dashboard **Sungrow Grid PID** with one Lovelace card displaying target slider and automation ON/OFF switch.
- An editable setup form allowing choosing export/charge/scene entity IDs.

**Safety:** the automation is initially off. Turn it on from its dashboard after checking helper values and entity assignments. Existing automations with alias `Simple Grid Battery Controller` are never overwritten; use them instead or rename/remove an old duplicate first. Changes made to installed automation YAML are not overwritten on integration restart.

**Uninstall:** Home Assistant config-entry removal does not erase editable automation YAML or native Helpers, to prevent accidental user data loss. Remove those separately if desired. HACS uninstall removes integration code.

**Requirements:** standard `automation: !include automations.yaml` in configuration.yaml for the installed automation to be active and UI editable. Other nonstandard automation YAML layouts might require manual adaptation.

## Advanced notes

Some newly created Helpers become visible only after HA restart. In an existing system with both helpers already present (like the original setup) no extra restart is required. The new implementation **does not use** the old Python PID controller, custom Number/Sensor/Switch platforms, or its previous service loop.
