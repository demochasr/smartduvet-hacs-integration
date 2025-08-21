"""Sensor platform for SmartDuvet."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import EntityCategory

from .entity import SmartDuvetEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .data import SmartDuvetConfigEntry

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="macAddress",
        name="MAC Address",
        icon="mdi:network-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="serialId",
        name="Serial ID",
        icon="mdi:identifier",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="ssid_wifi",
        name="WiFi SSID",
        icon="mdi:wifi",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="schedule_value",
        name="Schedule Time",
        icon="mdi:clock-time-four",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SmartDuvetConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        SmartDuvetSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class SmartDuvetSensor(SmartDuvetEntity, SensorEntity):
    """SmartDuvet Sensor class."""

    @property
    def native_value(self) -> str | int | None:
        """Return the native value of the sensor."""
        if self.coordinator.data:
            value = self.coordinator.data.get(self.entity_description.key)
            if value is not None:
                # Handle empty strings for IP address
                if self.entity_description.key == "sta_ip" and value == "":
                    return None
                return value
        return None
