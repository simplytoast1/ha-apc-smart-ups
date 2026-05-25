"""Constants for the APC Smart-UPS (NMC) integration."""
from __future__ import annotations

from datetime import timedelta

DOMAIN = "apc_smart_ups"

CONF_COMMUNITY = "community"

DEFAULT_PORT = 161
DEFAULT_COMMUNITY = "public"

# Polling cadence (configurable from the integration's Configure dialog).
DEFAULT_SCAN_INTERVAL = 10  # seconds
MIN_SCAN_INTERVAL = 5
MAX_SCAN_INTERVAL = 300
UPDATE_INTERVAL = timedelta(seconds=DEFAULT_SCAN_INTERVAL)

MANUFACTURER = "APC by Schneider Electric"
