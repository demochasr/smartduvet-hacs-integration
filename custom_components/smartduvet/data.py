"""Custom types for SmartDuvet."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import SmartDuvetApiClient
    from .coordinator import SmartDuvetDataUpdateCoordinator


type SmartDuvetConfigEntry = ConfigEntry[SmartDuvetData]


@dataclass
class SmartDuvetData:
    """Data for the SmartDuvet integration."""

    client: SmartDuvetApiClient
    coordinator: SmartDuvetDataUpdateCoordinator
    integration: Integration
