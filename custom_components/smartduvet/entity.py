"""SmartDuvetEntity class."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    DEVICE_INFO_IP,
    DEVICE_INFO_MAC,
    DEVICE_INFO_WIFI_VERSION,
    DOMAIN,
    LOGGER,
    MANUFACTURER,
    MODEL,
)
from .coordinator import SmartDuvetDataUpdateCoordinator


class SmartDuvetEntity(CoordinatorEntity[SmartDuvetDataUpdateCoordinator]):
    """SmartDuvetEntity class."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SmartDuvetDataUpdateCoordinator,
        entity_description: EntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        
        # Generate stable unique_id using config entry ID (ensures consistency across restarts)
        # This ensures entities are properly tracked in entity registry and removed when integration is deleted
        entry_id_short = coordinator.config_entry.entry_id.replace("-", "")[:8]
        self._attr_unique_id = f"{entry_id_short}_{entity_description.key}"
        
        # Set entity name according to has_entity_name = True pattern
        # Entity name should only identify the data point, not include device name
        # Home Assistant will automatically combine device.name + entity.name for friendly_name
        if entity_description.name:
            self._attr_name = entity_description.name
        else:
            # For main feature entities (like main light), use None 
            # This will make the entity use only the device name
            self._attr_name = None
        
        # Create device info using constants and proper data extraction
        self._attr_device_info = self._create_device_info(coordinator)

    def _create_device_info(self, coordinator: SmartDuvetDataUpdateCoordinator) -> DeviceInfo:
        """Create device info for the SmartDuvet device."""
        # Extract device information from coordinator data
        mac_address = None
        sta_ip = None
        wifi_version = "Unknown"
        
        if coordinator.data:
            mac_address = coordinator.data.get(DEVICE_INFO_MAC)
            sta_ip = coordinator.data.get(DEVICE_INFO_IP)
            wifi_version = str(coordinator.data.get(DEVICE_INFO_WIFI_VERSION, "Unknown"))
        
        # Create device identifiers
        identifiers = {(DOMAIN, coordinator.config_entry.entry_id)}
        if mac_address:
            identifiers.add((DOMAIN, mac_address))
        
        # Build device info dictionary
        device_info_dict = {
            "identifiers": identifiers,
            "name": coordinator.config_entry.title or "SmartDuvet",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": wifi_version,
        }
        
        # Add optional device properties
        if mac_address:
            # Add MAC address as both connection identifier and hw_version
            device_info_dict["connections"] = {("mac", mac_address.lower().replace(":", ""))}
        
        if sta_ip:
            device_info_dict["configuration_url"] = f"http://{sta_ip}/api/info"
        
        return DeviceInfo(**device_info_dict)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        # Entity is available if coordinator has successful data and is not in error state
        return self.coordinator.last_update_success and self.coordinator.data is not None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return None
        
        # Add some useful diagnostic attributes
        attributes = {}
        
        # Add last update time (if available)
        if hasattr(self.coordinator, 'last_update_success_time') and self.coordinator.last_update_success_time:
            attributes["last_update"] = self.coordinator.last_update_success_time.isoformat()
        elif hasattr(self.coordinator, 'last_update_time') and self.coordinator.last_update_time:
            attributes["last_update"] = self.coordinator.last_update_time.isoformat()
        
        # Add device IP if available
        if sta_ip := self.coordinator.data.get(DEVICE_INFO_IP):
            attributes["device_ip"] = sta_ip
        
        # Add WiFi version if available
        if wifi_version := self.coordinator.data.get(DEVICE_INFO_WIFI_VERSION):
            attributes["wifi_version"] = wifi_version
        
        return attributes if attributes else None

    async def async_will_remove_from_hass(self) -> None:
        """Entity being removed from hass."""
        # This method is called when the entity is being removed from Home Assistant
        # This ensures proper cleanup from entity registry when integration is removed
        LOGGER.debug("Entity %s is being removed from Home Assistant", self.entity_id)
        await super().async_will_remove_from_hass()
