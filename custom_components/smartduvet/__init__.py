"""
Custom integration to integrate SmartDuvet with Home Assistant.

For more details about this integration, please refer to
https://github.com/smartduvet-ha-integration
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import CONF_HOST, Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
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
    hass: HomeAssistant,  # noqa: ARG001
    entry: SmartDuvetConfigEntry,
) -> None:
    """Handle removal of a config entry."""
    # Home Assistant automatically removes entities from the registry when a config entry is removed.
    # This function can be used for additional cleanup if needed (e.g., removing files, cleaning up external resources).
    LOGGER.info("SmartDuvet integration removed for device at %s", entry.data.get(CONF_HOST, "unknown"))


async def async_reload_entry(
    hass: HomeAssistant,
    entry: SmartDuvetConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
