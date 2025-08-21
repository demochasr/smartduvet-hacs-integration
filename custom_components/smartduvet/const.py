"""Constants for SmartDuvet integration."""

from __future__ import annotations

from logging import Logger, getLogger
from typing import Final

LOGGER: Logger = getLogger(__package__)

# Integration details
DOMAIN: Final = "smartduvet"
NAME: Final = "SmartDuvet"
MANUFACTURER: Final = "SmartDuvet"
MODEL: Final = "SmartDuvet Bed Controller"
ATTRIBUTION: Final = "Data provided by SmartDuvet Local API"

# Configuration constants
CONF_DEVICE_NAME: Final = "device_name"
DEFAULT_NAME: Final = "SmartDuvet"
DEFAULT_UPDATE_INTERVAL: Final = 60  # seconds
CONNECTION_TIMEOUT: Final = 10  # seconds

# Default SmartDuvet hotspot details (for documentation)
DEFAULT_SSID: Final = "SmartDuvet"
DEFAULT_PASSWORD: Final = "smduvet@2011"
DEFAULT_AP_IP: Final = "192.168.4.1"

# API endpoints
API_INFO: Final = "/api/info"
API_SCANWIFI: Final = "/api/scanwifi"
API_WIFISTA: Final = "/api/wifista"
API_LIGHT: Final = "/api/light"
API_TEMP_LEFT: Final = "/api/temp/left"
API_TEMP_RIGHT: Final = "/api/temp/right"
API_MAKBED: Final = "/api/makbednow"
API_SCHEDULE: Final = "/api/schedule"
API_BOXSETTINGS: Final = "/api/boxsettings"
API_GETTIMESYSTEM: Final = "/api/gettimesystem"

# Device level constants (1-11 scale)
DEVICE_LEVEL_MIN: Final = 1
DEVICE_LEVEL_MAX: Final = 11
DEVICE_LEVEL_NEUTRAL: Final = 6


# Home Assistant temperature mapping (°C)
HA_TEMP_MIN: Final = 20  # Maps to device level 1
HA_TEMP_MAX: Final = 29  # Maps to device level 11
HA_TEMP_NEUTRAL: Final = 25  # Maps to device level 6

# Entity key constants
ENTITY_LIGHT: Final = "light"
ENTITY_TEMP_LEFT: Final = "temp_left"
ENTITY_TEMP_RIGHT: Final = "temp_right"
ENTITY_MAKEBED: Final = "makebed"
ENTITY_WIFI: Final = "wifi_sta_connected"
ENTITY_SCHEDULE: Final = "schedule_onoff"

# Device info field mappings
DEVICE_INFO_MAC: Final = "macAddress"
DEVICE_INFO_SERIAL: Final = "serialId"
DEVICE_INFO_IP: Final = "sta_ip"
DEVICE_INFO_WIFI_VERSION: Final = "wifi_version"
DEVICE_INFO_WIFI_SSID: Final = "ssid_wifi"

# Success indicators for HTML responses
SUCCESS_INDICATORS: Final = [
    "successfully",
    "success",
    "ok", 
    "done",
    "complete",
    "post",
]
