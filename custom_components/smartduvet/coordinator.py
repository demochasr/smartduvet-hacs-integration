"""DataUpdateCoordinator for SmartDuvet."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    SmartDuvetApiClientAuthenticationError,
    SmartDuvetApiClientCommunicationError,
    SmartDuvetApiClientError,
)
from .const import DEFAULT_UPDATE_INTERVAL, LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import SmartDuvetConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class SmartDuvetDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the SmartDuvet API."""

    config_entry: SmartDuvetConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: SmartDuvetConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        self.config_entry = config_entry
        super().__init__(
            hass,
            LOGGER,
            name=f"SmartDuvet {config_entry.title}",
            update_interval=timedelta(seconds=DEFAULT_UPDATE_INTERVAL),
            always_update=False,
        )

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            LOGGER.debug("Fetching SmartDuvet device data from %s", self.config_entry.runtime_data.client._host)
            data = await self.config_entry.runtime_data.client.async_get_info()
            
            # Validate that we got the expected data structure
            if not isinstance(data, dict):
                raise UpdateFailed(f"Invalid data format from SmartDuvet: expected dict, got {type(data)}")
            
            # Log device status for debugging
            if LOGGER.isEnabledFor(10):  # DEBUG level
                wifi_connected = data.get("wifi_sta_connected", False)
                device_ip = data.get("sta_ip", "unknown")
                LOGGER.debug(
                    "SmartDuvet status: WiFi=%s, IP=%s, Temp L/R=%s/%s, Light=%s",
                    wifi_connected,
                    device_ip,
                    data.get("temp_left", "?"),
                    data.get("temp_right", "?"),
                    data.get("light_onoff", "?"),
                )
            
            return data
            
        except SmartDuvetApiClientAuthenticationError as exception:
            # Authentication errors should reload the config entry
            LOGGER.error("SmartDuvet authentication failed: %s", exception)
            raise ConfigEntryAuthFailed(exception) from exception
        except SmartDuvetApiClientCommunicationError as exception:
            # Communication errors (timeout, network issues) make entities unavailable
            LOGGER.warning("SmartDuvet communication error: %s", exception)
            raise UpdateFailed(f"SmartDuvet connection failed: {exception}") from exception
        except SmartDuvetApiClientError as exception:
            # Other API errors also make entities unavailable
            LOGGER.error("SmartDuvet API error: %s", exception)
            raise UpdateFailed(f"SmartDuvet API error: {exception}") from exception
        except Exception as exception:
            # Catch any unexpected errors
            LOGGER.exception("Unexpected error fetching SmartDuvet data: %s", exception)
            raise UpdateFailed(f"Unexpected error: {exception}") from exception
