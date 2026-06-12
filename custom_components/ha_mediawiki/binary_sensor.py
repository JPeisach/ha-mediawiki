"""Binary sensor platform for ha_mediawiki."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry

from .entity import MediaWikiEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import MediaWikiDataUpdateCoordinator
    from .data import MediaWikiConfigEntry

ENTITY_DESCRIPTIONS = (
    BinarySensorEntityDescription(
        key="ha_mediawiki",
        name="Message",
        device_class=BinarySensorDeviceClass.UPDATE,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    async_add_entities(
        MediaWikiBinarySensor(
            coordinator=entry.runtime_data,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class MediaWikiBinarySensor(MediaWikiEntity, BinarySensorEntity):
    """ha_mediawiki binary_sensor class."""

    def __init__(
        self,
        coordinator: MediaWikiDataUpdateCoordinator,
        entity_description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        return True
