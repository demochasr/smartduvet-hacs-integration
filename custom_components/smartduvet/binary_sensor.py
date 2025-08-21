"""Binary sensor platform for SmartDuvet."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .entity import SmartDuvetEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .data import SmartDuvetConfigEntry

ENTITY_DESCRIPTIONS = (
    BinarySensorEntityDescription(
        key="wifi_sta_connected",
        name="WiFi",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        icon="mdi:wifi",
    ),
    BinarySensorEntityDescription(
        key="schedule_onoff",
        name="Schedule Active",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon="mdi:calendar-clock",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SmartDuvetConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    async_add_entities(
        SmartDuvetBinarySensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class SmartDuvetBinarySensor(SmartDuvetEntity, BinarySensorEntity):
    """SmartDuvet binary_sensor class."""

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary_sensor is on."""
        if self.coordinator.data:
            return self.coordinator.data.get(self.entity_description.key, False)
        return None
