"""Light platform for SmartDuvet."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
    LightEntityDescription,
)

from .entity import SmartDuvetEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .data import SmartDuvetConfigEntry

ENTITY_DESCRIPTIONS = (
    LightEntityDescription(
        key="light",
        name=None,  # Main feature entity - uses device name only
        icon="mdi:bed",  # Use bed icon for SmartDuvet light
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SmartDuvetConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the light platform."""
    async_add_entities(
        SmartDuvetLight(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class SmartDuvetLight(SmartDuvetEntity, LightEntity):
    """SmartDuvet light class."""

    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_color_mode = ColorMode.RGB

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        if self.coordinator.data:
            return self.coordinator.data.get("light_onoff", False)
        return None

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        """Return the rgb color value [int, int, int]."""
        if self.coordinator.data and "light_value" in self.coordinator.data:
            light_value = self.coordinator.data["light_value"]
            if isinstance(light_value, str):
                try:
                    rgba = light_value.split(" ")
                    if len(rgba) >= 3:
                        return (int(rgba[0]), int(rgba[1]), int(rgba[2]))
                except (ValueError, IndexError):
                    pass
        return None

    @property
    def brightness(self) -> int | None:
        """Return the brightness of this light between 0..255."""
        if self.coordinator.data and "light_value" in self.coordinator.data:
            light_value = self.coordinator.data["light_value"]
            if isinstance(light_value, str):
                try:
                    rgba = light_value.split(" ")
                    if len(rgba) >= 4:
                        return int(rgba[3])
                except (ValueError, IndexError):
                    pass
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        rgb_color = kwargs.get(ATTR_RGB_COLOR, self.rgb_color or (255, 255, 255))
        brightness = kwargs.get(ATTR_BRIGHTNESS, self.brightness or 255)

        # Send light command
        await self.coordinator.config_entry.runtime_data.client.async_set_light(
            light_onoff=True,
            red=rgb_color[0],
            green=rgb_color[1],
            blue=rgb_color[2],
            intensity=brightness,
        )
        
        # Refresh to validate changes were applied
        await self.coordinator.async_request_refresh()
        
        # Log validation (optional - for debugging)
        if self.coordinator.data:
            actual_state = self.coordinator.data.get("light_onoff", False)
            if not actual_state:
                from .const import LOGGER
                LOGGER.warning("Light turn_on command may have failed - device reports light_onoff: %s", actual_state)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        current_rgb = self.rgb_color or (255, 255, 255)
        current_brightness = self.brightness or 255
        
        # Send light command
        await self.coordinator.config_entry.runtime_data.client.async_set_light(
            light_onoff=False,
            red=current_rgb[0],
            green=current_rgb[1],
            blue=current_rgb[2],
            intensity=current_brightness,
        )
        
        # Refresh to validate changes were applied
        await self.coordinator.async_request_refresh()
        
        # Log validation (optional - for debugging)
        if self.coordinator.data:
            actual_state = self.coordinator.data.get("light_onoff", True)
            if actual_state:
                from .const import LOGGER
                LOGGER.warning("Light turn_off command may have failed - device reports light_onoff: %s", actual_state)