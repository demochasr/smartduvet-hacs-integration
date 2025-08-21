"""Button platform for SmartDuvet."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription

from .entity import SmartDuvetEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .data import SmartDuvetConfigEntry

ENTITY_DESCRIPTIONS = (
    ButtonEntityDescription(
        key="makebed",
        name="Make bed",
        icon="mdi:bed",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SmartDuvetConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    async_add_entities(
        SmartDuvetButton(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class SmartDuvetButton(SmartDuvetEntity, ButtonEntity):
    """SmartDuvet button class."""

    async def async_press(self) -> None:
        """Handle the button press."""
        if self.entity_description.key == "makebed":
            from .const import LOGGER
            
            # Send make bed command
            LOGGER.info("Make bed button pressed - sending command to SmartDuvet")
            await self.coordinator.config_entry.runtime_data.client.async_make_bed()
            
            # Refresh to validate command was received
            await self.coordinator.async_request_refresh()
            
            # Note: Make bed action doesn't have a status field to validate
            # But we log the action for debugging purposes
            LOGGER.info("Make bed command sent successfully")