"""Constants for the Felicity (local Wi-Fi) integration."""
from __future__ import annotations

DOMAIN = "felicity_local"
DEFAULT_PORT = 53970
DEFAULT_SCAN_INTERVAL = 10  # seconds
MIN_SCAN_INTERVAL = 5

CONF_SCAN_INTERVAL = "scan_interval"

CMD_REAL = b"wifilocalMonitor:get dev real infor"
CMD_BASIC = b"wifilocalMonitor:get dev basice infor"  # sic — the firmware spells it "basice"
CMD_SETTINGS = b"wifilocalMonitor:get dev set infor"

# Bstate / Estate codes seen in the wild
BMS_STATES = {
    320: "full",
    960: "standby",
    9152: "charging",
    5056: "discharging",
}
