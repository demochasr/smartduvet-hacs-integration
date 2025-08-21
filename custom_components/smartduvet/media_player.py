"""Media player platform for SmartDuvet."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityDescription,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)

from .const import LOGGER
from .entity import SmartDuvetEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .data import SmartDuvetConfigEntry

ENTITY_DESCRIPTIONS = (
    MediaPlayerEntityDescription(
        key="settings",
        name="Settings",
        icon="mdi:cog",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: SmartDuvetConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the media player platform."""
    async_add_entities(
        SmartDuvetMediaPlayer(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class SmartDuvetMediaPlayer(SmartDuvetEntity, MediaPlayerEntity):
    """SmartDuvet media player class for configuration commands."""

    _attr_supported_features = MediaPlayerEntityFeature.PLAY_MEDIA
    _attr_state = MediaPlayerState.IDLE

    @property
    def state(self) -> MediaPlayerState:
        """Return the state of the media player."""
        return MediaPlayerState.IDLE if self.available else MediaPlayerState.OFF

    async def async_play_media(
        self, media_type: str, media_id: str, **kwargs: Any
    ) -> None:
        """Send configuration commands via media player interface.
        
        media_type: Command (wifista, boxsettings)
        media_id: JSON parameters for the command
        """
        LOGGER.debug("SmartDuvet media player received: media_type=%s, media_id=%s", media_type, media_id)
        
        try:
            # Parse JSON parameters from media_id
            try:
                params = json.loads(media_id) if media_id.strip() else {}
            except json.JSONDecodeError as exception:
                LOGGER.error("Invalid JSON in media_id: %s - %s", media_id, exception)
                return
            
            # Execute command based on media_type
            if media_type == "wifista":
                await self._handle_wifista_command(params)
            elif media_type == "scanwifi":
                await self._handle_scanwifi_command(params)
            elif media_type == "boxsettings":
                await self._handle_boxsettings_command(params)
            else:
                LOGGER.error("Unknown command: %s. Supported commands: wifista, scanwifi, boxsettings", media_type)
                
        except Exception as exception:
            LOGGER.error("Error executing media player command %s: %s", media_type, exception)

    async def _handle_wifista_command(self, params: dict[str, Any]) -> None:
        """Handle WiFi station configuration command.
        
        Expected params: {
            "ssid": "NetworkName", 
            "password": "NetworkPassword",
            "scan": true  # Optional: trigger scan after setting credentials (default: true)
        }
        """
        try:
            ssid = params.get("ssid")
            password = params.get("password")
            auto_scan = params.get("scan", True)  # Default to True for backward compatibility
            
            if not ssid or not password:
                LOGGER.error("WiFi command requires 'ssid' and 'password' parameters")
                return
            
            LOGGER.info("Setting WiFi credentials: SSID=%s", ssid)
            # Step 1: Send WiFi credentials
            await self.coordinator.config_entry.runtime_data.client.async_set_wifi_credentials(ssid, password)
            
            # Step 2: Optional scan after wifista to actually connect
            if auto_scan:
                LOGGER.info("Triggering WiFi scan to connect to network")
                await self.coordinator.config_entry.runtime_data.client.async_scan_wifi()
            else:
                LOGGER.info("Skipping automatic WiFi scan (scan=false)")
            
            # Step 3: Refresh coordinator data to get updated connection status
            await self.coordinator.async_request_refresh()
            
        except Exception as exception:
            LOGGER.error("Error setting WiFi credentials: %s", exception)
            raise

    async def _handle_scanwifi_command(self, params: dict[str, Any]) -> None:
        """Handle WiFi scan command.
        
        Expected params: {} (no parameters needed)
        Triggers WiFi scan and refreshes wifi_available in /api/info
        """
        try:
            LOGGER.info("Scanning for available WiFi networks")
            # This returns HTML "Scanning Wifi" but triggers scan
            result = await self.coordinator.config_entry.runtime_data.client.async_scan_wifi()
            
            LOGGER.info("WiFi scan triggered: %s", result)
            
            # Refresh coordinator data to get updated wifi_available
            await self.coordinator.async_request_refresh()
            
        except Exception as exception:
            LOGGER.error("Error scanning WiFi networks: %s", exception)
            raise

    async def _handle_boxsettings_command(self, params: dict[str, Any]) -> None:
        """Handle box settings configuration command.
        
        Expected params: {"mac": "1A:2B:3C:4D:5E:6F", "serial_id": "defaultboard2"}
        If mac or serial_id not provided, uses current values from /api/info
        Processes MAC address and Serial ID according to SmartDuvet format
        """
        try:
            # Get user-provided values or use current device values
            mac = params.get("mac")
            serial_id = params.get("serial_id")
            
            # Use current device info if not provided by user
            if not mac and self.coordinator.data:
                mac = self.coordinator.data.get("macAddress")
                LOGGER.info("Using current MAC address from device: %s", mac)
            
            if not serial_id and self.coordinator.data:
                serial_id = self.coordinator.data.get("serialId")
                LOGGER.info("Using current Serial ID from device: %s", serial_id)
            
            # Final validation
            if not mac or not serial_id:
                LOGGER.error("Box settings command requires 'mac' and 'serial_id' parameters or available device data")
                return
            
            # Process MAC address to hex int array (same as HTML implementation)
            def hex_string_to_int_array(hex_str: str) -> list[int]:
                """Convert hex string to array of integers."""
                clean_hex = hex_str.replace(":", "")
                return [int(clean_hex[i:i+2], 16) for i in range(0, len(clean_hex), 2)]
            
            # Process Serial ID (same as HTML implementation)
            def process_serial_id(serial: str) -> str:
                """Process serial ID to SmartDuvet format."""
                return f"{len(serial):02d}06B_SERIAL:{serial}B_PASS:123456"
            
            # Convert MAC address
            mac_int = hex_string_to_int_array(mac)
            
            if len(mac_int) != 6:
                LOGGER.error("Invalid MAC address format. Expected 6 hex pairs, got %d", len(mac_int))
                return
            
            # Build box settings payload (same structure as HTML)
            box_settings = {
                "Mac_add_1": mac_int[0],
                "Mac_add_2": mac_int[1], 
                "Mac_add_3": mac_int[2],
                "Mac_add_4": mac_int[3],
                "Mac_add_5": mac_int[4],
                "Mac_add_6": mac_int[5],
                "serialId": process_serial_id(serial_id)
            }
            
            LOGGER.info("Sending box settings: MAC=%s, Serial=%s", mac, serial_id)
            LOGGER.debug("Box settings payload: %s", box_settings)
            
            # Send to /api/boxsettings endpoint
            await self.coordinator.config_entry.runtime_data.client._api_wrapper(
                method="post",
                url=self.coordinator.config_entry.runtime_data.client._base_url + "/api/boxsettings",
                data=box_settings,
            )
            
            # Refresh coordinator data after command
            await self.coordinator.async_request_refresh()
            
        except Exception as exception:
            LOGGER.error("Error setting box settings: %s", exception)
            raise