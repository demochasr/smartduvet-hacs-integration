"""
Custom integration to integrate SmartDuvet with Home Assistant.

For more details about this integration, please refer to
https://github.com/smartduvet-ha-integration
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import CONF_HOST, Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import async_get as async_get_device_registry
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from homeassistant.loader import async_get_loaded_integration

from .api import SmartDuvetApiClient
from .const import LOGGER
from .coordinator import SmartDuvetDataUpdateCoordinator
from .data import SmartDuvetData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import SmartDuvetConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.CLIMATE,
    Platform.LIGHT,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: SmartDuvetConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    # Initialize the API client
    client = SmartDuvetApiClient(
        host=entry.data[CONF_HOST],
        session=async_get_clientsession(hass),
    )
    
    # Store runtime data
    entry.runtime_data = SmartDuvetData(
        client=client,
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=None,  # Will be set below
    )
    
    # Initialize the coordinator with proper configuration
    coordinator = SmartDuvetDataUpdateCoordinator(
        hass=hass,
        config_entry=entry,
    )
    
    # Update the runtime data with the coordinator
    entry.runtime_data.coordinator = coordinator

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    LOGGER.info("SmartDuvet integration setup completed for device at %s", entry.data[CONF_HOST])
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: SmartDuvetConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_entry(
    hass: HomeAssistant,
    entry: SmartDuvetConfigEntry,
) -> None:
    """Handle removal of a config entry."""
    # Get both registries
    entity_registry = async_get_entity_registry(hass)
    device_registry = async_get_device_registry(hass)
    
    # Find all entities associated with this config entry
    entities_to_remove = [
        entity_entry.entity_id
        for entity_entry in entity_registry.entities.values()
        if entity_entry.config_entry_id == entry.entry_id
    ]
    
    # Find all devices associated with this config entry
    devices_to_remove = [
        device_entry.id
        for device_entry in device_registry.devices.values()
        if entry.entry_id in device_entry.config_entries
    ]
    
    # Remove each entity from the registry
    for entity_id in entities_to_remove:
        LOGGER.debug("Removing entity %s from registry", entity_id)
        entity_registry.async_remove(entity_id)
    
    # Remove each device from the registry
    for device_id in devices_to_remove:
        LOGGER.debug("Removing device %s from registry", device_id)
        device_registry.async_remove_device(device_id)
    
    LOGGER.info(
        "Removed SmartDuvet integration for device at %s (%d entities, %d devices removed)", 
        entry.data.get(CONF_HOST, "unknown"),
        len(entities_to_remove),
        len(devices_to_remove)
    )


async def async_reload_entry(
    hass: HomeAssistant,
    entry: SmartDuvetConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
