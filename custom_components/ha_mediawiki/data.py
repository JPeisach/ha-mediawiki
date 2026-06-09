"""Custom types for ha_mediawiki."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import MediaWikiApiClient
    from .coordinator import MediaWikiDataUpdateCoordinator


type MediaWikiConfigEntry = ConfigEntry[MediaWikiData]


@dataclass
class MediaWikiData:
    """Data for the Blueprint integration."""

    client: MediaWikiApiClient
    coordinator: MediaWikiDataUpdateCoordinator
    integration: Integration
