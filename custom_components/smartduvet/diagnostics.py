"""Diagnostics support for SmartDuvet."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.diagnostics import async_redact_data


if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

CONF_TO_REDACT = {
    "ssid_wifi",
    "macAddress", 
    "serialId",
    "sta_ip",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry  # noqa: ARG001
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = config_entry.runtime_data.coordinator
    
    diagnostics_data = {
        "config_entry": {
            "title": config_entry.title,
            "version": config_entry.version,
            "domain": config_entry.domain,
            "source": config_entry.source,
            "state": config_entry.state.value,
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "last_exception": str(coordinator.last_exception) if coordinator.last_exception else None,
            "update_interval": coordinator.update_interval.total_seconds() if coordinator.update_interval else None,
            "name": coordinator.name,
        },
        "device_data": coordinator.data if coordinator.data else {},
        "api_client": {
            "host": coordinator.config_entry.runtime_data.client._host,
            "base_url": coordinator.config_entry.runtime_data.client._base_url,
        },
    }
    
    # Redact sensitive information
    return async_redact_data(diagnostics_data, CONF_TO_REDACT)


async def async_get_device_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry, device  # noqa: ARG001
) -> dict[str, Any]:
    """Return diagnostics for a device entry."""
    coordinator = config_entry.runtime_data.coordinator
    
    device_diagnostics = {
        "device_info": {
            "identifiers": list(device.identifiers),
            "manufacturer": device.manufacturer,
            "model": device.model,
            "name": device.name,
            "sw_version": device.sw_version,
            "hw_version": device.hw_version,
        },
        "device_data": coordinator.data if coordinator.data else {},
        "coordinator_status": {
            "available": coordinator.last_update_success,
            "last_update": (
                coordinator.last_update_success_time.isoformat() 
                if hasattr(coordinator, 'last_update_success_time') and coordinator.last_update_success_time 
                else (
                    coordinator.last_update_time.isoformat() 
                    if hasattr(coordinator, 'last_update_time') and coordinator.last_update_time 
                    else None
                )
            ),
            "update_interval": coordinator.update_interval.total_seconds() if coordinator.update_interval else None,
        },
    }
    
    # Add device-specific diagnostics if data is available
    if coordinator.data:
        device_diagnostics["device_status"] = {
            "wifi_connected": coordinator.data.get("wifi_sta_connected", False),
            "wifi_version": coordinator.data.get("wifi_version", "unknown"),
            "light_status": coordinator.data.get("light_onoff", False),
            "light_value": coordinator.data.get("light_value", "unknown"),
            "temperature_left": coordinator.data.get("temp_left", 0),
            "temperature_right": coordinator.data.get("temp_right", 0),
            "schedule_active": coordinator.data.get("schedule_onoff", False),
            "schedule_time": coordinator.data.get("schedule_value", "unknown"),
        }
    
    # Redact sensitive information
    return async_redact_data(device_diagnostics, CONF_TO_REDACT)