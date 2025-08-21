"""Climate platform for SmartDuvet."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityDescription,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature

from .const import (
    DEVICE_LEVEL_MAX,
    DEVICE_LEVEL_MIN,
    DEVICE_LEVEL_NEUTRAL,
    HA_TEMP_MAX,
    HA_TEMP_MIN,
    HA_TEMP_NEUTRAL,
)
from .entity import SmartDuvetEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .data import SmartDuvetConfigEntry

ENTITY_DESCRIPTIONS = (
    ClimateEntityDescription(
        key="temp_left",
        name="Left",
        icon="mdi:bed-single-outline",
    ),
    ClimateEntityDescription(
        key="temp_right",
        name="Right", 
        icon="mdi:bed-single-outline",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SmartDuvetConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the climate platform."""
    async_add_entities(
        SmartDuvetClimate(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class SmartDuvetClimate(SmartDuvetEntity, ClimateEntity):
    """SmartDuvet climate class."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.COOL, HVACMode.HEAT]
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_min_temp = HA_TEMP_MIN  # Coolest temperature (maps to level 1)
    _attr_max_temp = HA_TEMP_MAX  # Warmest temperature (maps to level 11)
    _attr_target_temperature_step = 1

    def _temp_to_level(self, temperature: float) -> int:
        """Convert Home Assistant temperature (20-29°C) to SmartDuvet level (1-11, skip 6)."""
        temp = int(round(temperature))
        
        if temp <= HA_TEMP_MIN:
            return DEVICE_LEVEL_MIN  # Coolest
        elif temp <= 24:
            return temp - 19  # 21→2, 22→3, 23→4, 24→5
        elif temp >= HA_TEMP_MAX:
            return DEVICE_LEVEL_MAX  # Warmest
        else:
            # 25→7, 26→8, 27→9, 28→10, 29→11 (skip level 6)
            return temp - 18

    def _level_to_temp(self, level: int) -> float:
        """Convert SmartDuvet level (1-11) to Home Assistant temperature (20-29°C)."""
        if level == 0 or level == 6:
            return HA_TEMP_NEUTRAL  # Neutral/Off represented as 25°C
        elif level <= 5:
            return float(HA_TEMP_MIN - 1 + level)  # 1→20, 2→21, 3→22, 4→23, 5→24
        else:
            return float(HA_TEMP_MIN - 2 + level)  # 7→25, 8→26, 9→27, 10→28, 11→29

    @property
    def hvac_mode(self) -> HVACMode:
        """Return hvac operation ie. heat, cool mode."""
        if self.coordinator.data and self.entity_description.key in self.coordinator.data:
            level = self.coordinator.data.get(self.entity_description.key, 6)
            if level == 0 or level == 6:
                return HVACMode.OFF
            elif level <= 5:
                return HVACMode.COOL
            else:
                return HVACMode.HEAT
        return HVACMode.OFF

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        if self.coordinator.data and self.entity_description.key in self.coordinator.data:
            level = self.coordinator.data.get(self.entity_description.key, 6)
            return self._level_to_temp(level)
        return None

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVACMode.OFF:
            # Set to level 6 (neutral/off)
            await self._async_set_level(DEVICE_LEVEL_NEUTRAL)
        elif hvac_mode == HVACMode.COOL:
            # Set to level 5 (24°C - coolest comfortable setting)
            await self._async_set_level(5)
        elif hvac_mode == HVACMode.HEAT:
            # Set to level 7 (25°C - warmest comfortable setting)  
            await self._async_set_level(7)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is not None:
            level = self._temp_to_level(temperature)
            await self._async_set_level(level)

    async def _async_set_level(self, level: int) -> None:
        """Set SmartDuvet level for the appropriate side."""
        # Send temperature command
        if self.entity_description.key == "temp_left":
            await self.coordinator.config_entry.runtime_data.client.async_set_temp_left(level)
        elif self.entity_description.key == "temp_right":
            await self.coordinator.config_entry.runtime_data.client.async_set_temp_right(level)
        
        # Refresh to validate changes were applied
        await self.coordinator.async_request_refresh()
        
        # Log validation (optional - for debugging)
        if self.coordinator.data:
            actual_level = self.coordinator.data.get(self.entity_description.key, 0)
            if actual_level != level:
                from .const import LOGGER
                LOGGER.warning(
                    "Temperature command may have failed - requested %s level: %d (%.0f°C), device reports level: %d (%.0f°C)",
                    self.entity_description.key,
                    level,
                    self._level_to_temp(level),
                    actual_level,
                    self._level_to_temp(actual_level)
                )