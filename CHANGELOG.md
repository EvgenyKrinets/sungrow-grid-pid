# Changelog — Sungrow Energy Manager

The latest stable release is documented in [GitHub Releases](https://github.com/EvgenyKrinets/sungrow-grid-pid/releases). This project retains the historical domain `sungrow_grid_pid` for upgrade compatibility.

## v4.0.9 — Product documentation and image refresh

- Regenerated the high-resolution product banner with a Night Tariff feature panel, keeping the original marketing image archived.
- Updated README, product illustrations, and the three-mode architecture diagram.
- Added a detailed Night Tariff setup/verification guide.
- Reviewed HACS naming, integration entity listings, and user-facing documentation.
- No changes to inverter or battery control algorithms.

## v4.0.8 — Night Tariff Mode

**Automatically use the cheaper night tariff without discharging the battery.** Enable the independent **Night Tariff Mode** switch on the SEM dashboard.

- **Default discount:** 23:00–07:00, Sunday–Thursday *starting nights* (Home Assistant local time). A Thursday night continues through Friday 07:00; Friday and Saturday nights are excluded.
- During discount SEM activates the selected **Self-Consumption Mode (no battery discharge)** scene. Outside discount it activates the usual **Self-Consumption Mode (max battery discharge)** scene.
- The tariff has its **own ON/OFF switch** and works even if Grid Target is STOP. Its state survives Home Assistant restarts.
- Edit **Discount Start** and **Discount End** directly on the dashboard using native Home Assistant time entities. Defaults: 23:00 and 07:00.
- **One command per transition**, not once a second. If an entity/service is temporarily unavailable the controller reports a diagnostic and retries.
- **Morning Forced Discharge takes priority** when active. After its reserved SOC threshold is reached, SEM returns to the tariff-appropriate scene, not blindly to max-discharge mode.
- Disabling Night Tariff returns to normal Self-Consumption when SEM has previously applied a tariff scene, except when Forced Discharge is running.
- An additional integration option selects **Night tariff — no battery discharge scene** (automatically suggested when a unique scene with that friendly name exists).
- New entities: `switch.sem_night_tariff`, `time.sem_tariff_start`, `time.sem_tariff_end`, `sensor.sem_night_tariff_status`.

**Important hardware verification:** In the example screenshot, the scene called **Self-Consumption Mode (no battery discharge)** displays **Battery max discharge power = 25,000 W**. That value alone does **not** disable battery discharge. Check that activating the scene actually makes the home draw energy from the grid while PV is insufficient. Adjust the scene in Sungrow/Home Assistant if necessary. SEM switches scenes; it cannot guarantee the effect of a misconfigured scene.

**Tariff calendar assumption:** The selected nights begin Sunday, Monday, Tuesday, Wednesday and Thursday. The Thursday 23:00 → Friday 07:00 window **is included**; Friday 23:00 and Saturday 23:00 starts are excluded. Confirm this matches your utility's contract. No special public-holiday calendar is included.

## v4.0.7 — Reliable Start Time picker

- Fix the **Morning Discharge → Start Time** clock popup sometimes disappearing while Home Assistant updates live export power and battery status.
- The Lovelace card now updates values, status labels, and buttons **in place** instead of replacing the entire card after each HA state event.
- While the native browser time picker is open, its draft value and DOM element remain intact. The selected time is saved using the existing `time.set_value` service.
- Includes a JavaScript regression test simulating 1,000 consecutive Home Assistant state updates with an open picker.
- No changes to export control, charge limits, battery discharge or the morning schedule logic.

## v4.0.6 — HACS presentation update

- The HACS repository display name is now **Sungrow Energy Manager**, matching the Home Assistant integration.
- The release includes the full product-style README and uploaded high-resolution showcase banner so HACS can render the updated documentation when this version is selected.
- No change to grid or battery control logic since v4.0.5.

## v4.0.5 — Reliable restart recovery

- Both **Grid Target (START/STOP)** and **Battery Morning Discharge (ON/OFF)** remember their previous positions after a Home Assistant restart and normal integration reload.
- Active Morning Forced Discharge is **no longer cancelled unconditionally** during SEM startup. SEM resumes monitoring it when both switches were enabled and valid SOC is above the configured backup reserve.
- If reserve is reached, required SOC data are invalid/unavailable, or the controller was disabled, SEM attempts to exit Forced Discharge via its configured Self-Consumption scene rather than leaving forced discharge unmanaged.
- Existing installations are upgraded in place. For the first upgrade from older versions, SEM attempts to migrate the last saved native switch states; thereafter it stores the intended ON/OFF values independently.
- **After upgrading from v4.0.4 or earlier, verify the two switches once.** If their previous ON states were not saved by Home Assistant, turn them on once. Future restarts will remember them.
- Normal battery and inverter protections remain authoritative. Reissuing a scene or service command does not confirm the physical inverter mode; monitor it during the first reboot test.

