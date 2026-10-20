## v4.0.2 — Reload and charge-boundary fixes

- Correctly delegate config-entry unload callbacks to Home Assistant when saving new integration options. This prevents the previous invalid manual callback-unload call.
- Grid Target no longer starts or repeatedly resets the adjustment countdown when the charge limit is already at the minimum and the controller wants to decrease it, or at the maximum and it wants to increase it. A new direction or a move away from the limit re-arms the configured delay.
- No changes to the configured symmetric Dead Band, Delay, or Gain policy.

## v4.0.1 — Morning Discharge schedule fix

- Failed or skipped scheduled discharge no longer marks the entire day completed.
- The schedule registers one attempt per configured minute; changing the start time allows another attempt at the new time. A successful activation persists its date and scheduled start time.
- Battery Morning Discharge remains optional and requires four configured Sungrow entities and an active Grid Target controller.
- Persistent `sensor.sem_morning_discharge_status` reports failures, missing entities and SOC threshold skips.
- Numeric parameters on the dashboard display whole watts, seconds and percent values.
- Configuration field names and detailed help are translated into Russian, English and Hebrew.
- The optional **Test Discharge Now** button is not included.

