<div align="center">

# ☀️ Sungrow Grid PID

### Smart grid export control for Home Assistant

**Use excess solar energy to charge your battery while regulating power exported to the grid.**

![Sungrow Grid PID — illustrated system overview](docs/images/sungrow_grid_pid_energy_infographic.png)

[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Custom%20Integration-18BCF2?logo=homeassistant&logoColor=white)](https://www.home-assistant.io/)
[![HACS](https://img.shields.io/badge/HACS-Compatible-41BDF5)](https://hacs.xyz/)
[![Latest release](https://img.shields.io/github/v/release/EvgenyKrinets/sungrow-grid-pid?label=Release)](https://github.com/EvgenyKrinets/sungrow-grid-pid/releases)
[![GitHub license](https://img.shields.io/github/license/EvgenyKrinets/sungrow-grid-pid)](LICENSE)

[**Installation**](#-installation) · [**How it works**](#-how-it-works) · [**Configuration**](#-configuration) · [**Troubleshooting**](#-troubleshooting)

</div>

---

## ⚡ What is Sungrow Grid PID?

**Sungrow Grid PID** is a community-built Home Assistant integration that helps regulate grid export by adjusting the inverter's **maximum battery charging power**. It compares your current export reading with the desired grid export target, then changes the charge-power command to reduce the difference.

This is useful for a Sungrow hybrid inverter when solar energy can be divided between the home, grid export, and battery charging.

> **Note:** The illustration above is a conceptual example. Displayed power values are illustrative, not live readings or guarantees of inverter output. This is a simple integral-based controller, not a full proportional–integral–derivative implementation.

## ✨ Features

| Feature | Description |
| --- | --- |
| 🎯 **Grid export target** | Set the desired export power with a slider |
| 🔋 **Battery charging control** | Updates the maximum charge-power entity in Home Assistant |
| 🔁 **One-second adjustment** | Original, user-editable Home Assistant automation |
| 🧩 **Native helpers** | Uses standard `input_number` entities |
| ⏯️ **PID ON/OFF** | Toggle the Home Assistant automation directly from the Lovelace card |
| 🔧 **Editable entities** | Choose the export sensor, battery charge control, and Sungrow scene |
| 🏠 **Local automation** | Runs inside your own Home Assistant instance |
| 📦 **HACS installation** | Install integration files using HACS |

## 🧠 How it works

```text
Solar PV ───┬──► Home consumption
            ├──► Grid export ──► sensor.export_power
            └──► Battery charging ◄── number.battery_max_charge_power
                                          ▲
                                          │
Target (input_number.pid_grid_target) ──► PID automation
                                          ▲
                                          │
Memory (input_number.pid_integral) ◄──────┘
```

Every second, the automation reads the grid export and target:

```text
error      = actual_grid_export - export_target
new_output = previous_output + error × 0.10
new_output = clamp(new_output, 0, 25000)
```

It writes `new_output` to the configured charging-power `number` entity and also stores it in `input_number.pid_integral`.

- **Actual export above target:** battery charge-power command increases.
- **Actual export below target:** battery charge-power command decreases.
- **PID off:** the automation stops changing the charging-power command; turning it off does **not** automatically reset charging power to zero.

The controller's behavior depends on the sign convention and response of the selected export sensor and charge-power entity. Verify those before enabling.

## 📦 Installation

1. In **HACS**, add `https://github.com/EvgenyKrinets/sungrow-grid-pid` as a custom **Integration** repository (if it is not already available).
2. Install **Sungrow Grid PID** and **restart Home Assistant**.
3. Go to **Settings → Devices & services → Add integration → Sungrow Grid PID**.
4. Confirm the pre-filled entity IDs or choose matching entities from the selectors.
5. Complete setup. Existing native PID helpers are preserved; missing ones are set up by the installer.
6. If helpers were newly created, **restart Home Assistant once more** to make them available.
7. Find **Simple Grid Battery Controller** under **Settings → Automations & scenes**, and the **Sungrow Grid PID** dashboard/card in Home Assistant.

**Before enabling:** verify the automation is loaded, the export reading is valid, the target is within the permitted export limit, and no second PID automation is controlling the same charge-power entity.

### ⚙️ Configuration

Default values match the original Sungrow setup and can be changed through integration settings:

| Setting | Default |
| --- | --- |
| Grid export sensor | `sensor.export_power` |
| Maximum battery charge power | `number.battery_max_charge_power` |
| Scene activated on PID enable | `scene.self_consumption_mode_max_battery_discharge` |
| Grid target helper | `input_number.pid_grid_target` |
| PID integral helper | `input_number.pid_integral` |
| Target range | 0–17,000 W, 1,000 W step |
| Output range | 0–25,000 W |
| Feedback gain | 0.10 |
| Update interval | 1 second |

The integration uses an **ordinary editable Home Assistant automation** named `Simple Grid Battery Controller`. It does **not** run the PID calculation through a separate background Python PID loop.

### 🎛️ Dashboard card

The compact `custom:sungrow-grid-pid-card` displays:

- **PID automation** — ON/OFF switch, linked to `automation.simple_grid_battery_controller` by default
- **Grid export target** — slider linked to `input_number.pid_grid_target`
- **Actual grid export** — from `sensor.export_power`
- **Battery charge command** — from `number.battery_max_charge_power`

If your automation has a different entity ID, select the correct `automation.*` entity in the card editor. The same applies to the other entities.

## 🔧 Charge power limits (min / max / step)

The PID now reads the selected `number.battery_max_charge_power` entity's `min`, `max`, and `step` attributes during each update. For example, a Sungrow charge-power control may report **min 10 W, max 25,000 W, step 100 W**.

- On a large export shortfall (2,000 W or more), the command becomes the **minimum supported value** (for example **10 W**), not an invalid **0 W**.
- In normal conditions, the requested output is bounded by the entity's supported limits and the PID's 25,000 W ceiling, and aligned to the entity's step starting from its minimum.
- `input_number.pid_integral` is updated with the same accepted **requested** setpoint, avoiding buildup of an unattainable internal 0 W target.
- **This is a command limit, not a guarantee of actual battery charge current.** Sungrow may impose other control restrictions.

On upgrading, the installer safely updates the two **unchanged integration-generated PID formulas** from earlier releases, creating an `automations.yaml.sungrow-grid-pid.bak` backup before changing the file. Custom manual formulas are not overwritten, and a manually created automation with the same alias is preserved. Verify the actual YAML in **Settings → Automations & scenes** after upgrade and ensure no second automation is controlling the same charge limit.

## ☁️ Fast response to sudden clouds

The standard feedback formula changes battery charge power gradually. When PV power drops suddenly, its stored integral can keep a positive charge command for several seconds.

The updated generated automation adds **rapid cutoff**:

```text
error = grid_export - grid_target
if error <= -2000 W:
    battery_charge_command = device_minimum (for example 10 W)
else:
    battery_charge_command = clamp(integral + error × 0.10, 0, 25000 W)
```

Example: export target **15 kW**, measured export suddenly drops to **8 kW**. The charge command is set to the **device minimum** on the next one-second automation run. The inverter may take additional time to respond. This is a simple cutoff strategy, not a certified grid protection.

On update, the installer replaces **only the original unmodified generated formula** in its own `automations.yaml` entry (ID `sungrow_grid_pid_simple_controller`). Before modifying it, it makes a backup next to `automations.yaml` ending in `.sungrow-grid-pid.bak`. **Existing manual automations and previously modified formulas are not overwritten**; update those manually if desired.

## 🗒️ Hide Activity entries while keeping the history graph

On initial setup or restart, the integration **automatically adds** these three Logbook-only exclusions to simple `configuration.yaml` configurations (and creates `configuration.yaml.sungrow-grid-pid.bak` before making changes). Home Assistant must restart once more for the new Logbook filter to take effect. For complex YAML configurations (including external includes) the installer leaves the file untouched and explains why in the logs. To **keep the Battery max charge power graph** but hide frequent **Activity / Logbook** entries, the configuration is:

```yaml
logbook:
  exclude:
    entities:
      - number.battery_max_charge_power
      - input_number.pid_integral
      - automation.simple_grid_battery_controller
```

Merge this into an existing `logbook:` section if you already have one. Check configuration and restart Home Assistant. Recorder will continue storing the sensor's history, and its history graph will remain available. The installer deliberately does not alter Recorder include/exclude filters, since altering them may remove the graph. This does **not** reduce Recorder database size; it filters Activity/Logbook entries. Older already-open Activity results may require a page refresh.

**Do not put this entity under `recorder.exclude` if you want to preserve the graph.**

## 🛟 Troubleshooting

| Problem | What to check |
| --- | --- |
| Card says **automation not found** | Confirm the automation exists and its real entity ID matches the card configuration |
| Integration shows a red error | Open **Settings → System → Logs** and check entries mentioning `sungrow_grid_pid` |
| Card still looks old after HACS update | Restart Home Assistant and hard-refresh the browser (Ctrl+Shift+R) |
| No helpers visible | Restart HA after first-time helper creation |
| Automation not loaded | Check that `configuration.yaml` includes `automation: !include automations.yaml` and review automation errors |
| PID seems to work in the wrong direction | Verify that positive `sensor.export_power` means exporting power |

## ⚠️ Safety and limitations

- **Always obey your utility export limit** and inverter/battery charging specifications. This software is not an export-limit protection system or certified grid control.
- PID uses frequent entity updates; recorder/history load can grow if the integral helper changes every second.
- If the controller is disabled or Home Assistant goes offline, the last inverter charge limit may remain active.
- The current installer preserves pre-existing helpers and automations instead of deleting or overwriting user-maintained configuration.
- Actual integration behavior can vary with Home Assistant releases and specific Sungrow integrations. Test with supervision before relying on automatic charging decisions.

## 🗑️ Uninstall

Remove **Sungrow Grid PID** from **Settings → Devices & services**, then uninstall its files in **HACS**. Native helpers and editable automations may remain intentionally; remove those separately after ensuring nothing else uses them.

## ❤️ Community

Issues, bug reports, and contributions are welcome:

- [Report an issue](https://github.com/EvgenyKrinets/sungrow-grid-pid/issues)
- [View releases](https://github.com/EvgenyKrinets/sungrow-grid-pid/releases)

---

<div align="center"><sub>Community project for Home Assistant. Not an official Sungrow or Home Assistant product.</sub></div>
