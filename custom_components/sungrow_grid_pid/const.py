DOMAIN = "sungrow_grid_pid"
VERSION = "1.3.0"

DEFAULT_TARGET = 15000
DEFAULT_MAX_TARGET = 25000
DEFAULT_MAX_CHARGE = 25000
GAIN = 0.10
INTERVAL_SECONDS = 1

EXPORT_CANDIDATES = (
    "sensor.export_power",
    "sensor.sungrow_export_power",
)
CHARGE_CANDIDATES = (
    "number.battery_max_charge_power",
    "number.sungrow_battery_max_charge_power",
    "number.sungrow_charge_discharge_power",
)
MODE_CANDIDATES = (
    "select.battery_forced_charge_discharge",
    "select.sungrow_battery_forced_charge_discharge",
    "select.sungrow_battery_mode",
)
FORCED_DISCHARGE_OPTIONS = (
    "Forced discharge",
    "Force discharge",
    "Discharge",
    "discharge",
    "force_discharge",
)
