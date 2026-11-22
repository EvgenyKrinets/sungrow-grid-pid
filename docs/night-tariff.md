# Night Tariff Mode — configuration and verification

[← Sungrow Energy Manager](../README.md) · [Version history](../CHANGELOG.md)

## Purpose

Night Tariff Mode is an **optional, independent** Home Assistant switch in Sungrow Energy Manager (SEM). During selected discounted hours it activates the Sungrow **Self-Consumption Mode (no battery discharge)** scene. When the discount ends it activates **Self-Consumption Mode (max battery discharge)**. It does not directly operate Modbus registers; it triggers the scenes already provided by your Sungrow Home Assistant integration.

It is intended for an electricity tariff with cheaper electricity from **23:00 until 07:00**, on nights starting **Sunday through Thursday**, excluding nights starting **Friday and Saturday**. Confirm these assumptions against your own tariff contract; holidays are **not** currently handled specially.

## Weekly example (Home Assistant local time)

| Starting evening | Time interval | Night Tariff action |
|---|---|---|
| Sunday | 23:00 → Monday 07:00 | No battery discharge |
| Monday | 23:00 → Tuesday 07:00 | No battery discharge |
| Tuesday | 23:00 → Wednesday 07:00 | No battery discharge |
| Wednesday | 23:00 → Thursday 07:00 | No battery discharge |
| Thursday | 23:00 → Friday 07:00 | No battery discharge |
| Friday | 23:00 → Saturday 07:00 | Not discounted |
| Saturday | 23:00 → Sunday 07:00 | Not discounted |

The schedule follows the **local time zone configured in Home Assistant**. Its starting/ending times are editable; its allowed starting days are currently fixed.

## Setup

1. In **Settings → Devices & Services → Sungrow Energy Manager → Configure**, set **Self-Consumption Mode scene (start and return)** to the *max battery discharge* scene. This is the normal scene already required by Grid Target.
2. Set **Night tariff — no battery discharge scene** to **Self-Consumption Mode (no battery discharge)**. SEM proposes it automatically when there is exactly one suitable scene by that name.
3. In the SEM dashboard, locate **Night Tariff Mode**. Confirm **Discount Start = 23:00** and **Discount End = 07:00**, then toggle **ON**.
4. Check `sensor.sem_night_tariff_status`, the configured scene state, Sungrow **EMS mode**, and actual battery power. Verify the result with power flowing to the home while solar PV is low.
5. Set the switch to **OFF** to disable this schedule. The switch position survives HA restarts, so after first configuration you should not have to re-enable it daily.

### The scene must actually stop discharging

**Critical:** A scene with the label *no battery discharge* may not actually prevent discharge. In a supplied Sungrow example, its visible settings included **Battery max discharge power = 25,000 W**. That limit does **not** by itself forbid discharging.

The SEM scheduler only calls the selected scene. If it still allows the battery to discharge, **fix that scene or the Sungrow setting it controls before relying on tariff switching**. Do not assume an accepted `scene.turn_on` service call proves the inverter changed physical operating mode.

## Coordination with other SEM functions

- **Grid Target** works independently. Its charging-limit controller can remain ON while Night Tariff is ON.
- **Morning Discharge** takes priority. SEM does not overwrite an active **Battery Forced Discharge** scene at a tariff boundary. When forced discharge completes or returns to the reserved SOC threshold, SEM selects whichever self-consumption scene the tariff schedule calls for at that moment.
- **Scene commands** are sent when the desired tariff period changes, or after enabling/editing the tariff schedule, not every second. Temporarily unavailable scenes trigger diagnostic messages and retries.
- **Startup:** the Night Tariff switch is restored after HA restarts and the current period is evaluated using the restored schedule. This does not provide a fallback while HA or the Sungrow integration is offline.

## Native entities

| Entity | Function |
|---|---|
| `switch.sem_night_tariff` | Enable or disable tariff switching |
| `time.sem_tariff_start` | Discount begins (default 23:00) |
| `time.sem_tariff_end` | Discount ends (default 07:00) |
| `sensor.sem_night_tariff_status` | Status/diagnostic for last requested scene |

## Troubleshooting

**Night Tariff ON but battery still discharging:** Activate the chosen no-discharge scene manually in Developer Tools and check whether the battery stops discharging. If not, the scene or actual inverter settings require attention.

**Tariff panel says scene missing:** Ensure **Night tariff — no battery discharge scene** is populated in integration Configure and points to a real `scene.*` entity. If the scene was renamed, reselect it.

**Discount doesn't start on Friday night:** Expected with this calendar: Friday and Saturday *starting nights* are excluded. Thursday 23:00 → Friday 07:00 remains discounted.

**Forcing discharge at the tariff boundary:** Morning Forced Discharge has higher priority until its completion. SEM will then restore the appropriate scene.

**Unexpected switching after HA restart:** Verify the system's time zone under **Settings → System → General**, both start and end times, and the restored Night Tariff ON/OFF state. Consult `sensor.sem_night_tariff_status`.

---

⚠️ **Safety:** SEM is a community Home Assistant integration, not an approved inverter/grid protection. Inverter export limits, BMS safeguards and the reserve SOC must remain configured independently.
