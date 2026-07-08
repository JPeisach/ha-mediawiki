"""Sensor platform for ha_mediawiki."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)

from .entity import MediaWikiEntity

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from .coordinator import MediaWikiDataUpdateCoordinator

from homeassistant.helpers.typing import StateType


# thanks pantherale0 for doing this with wiiu-smarthome, it's cool
@dataclass(frozen=True, kw_only=True)
class MediaWikiSensorEntityDescription(SensorEntityDescription):
    """Class describing MediaWiki entities."""

    value_fn: Callable[[MediaWikiEntity], None]


ENTITY_DESCRIPTIONS: list[MediaWikiSensorEntityDescription] = [
    MediaWikiSensorEntityDescription(
        key="contributions",
        name="Contributions",
        icon="mdi:format-quote-close",
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda entity: entity.coordinator.edit_count,
    ),
    MediaWikiSensorEntityDescription(
        key="last_edit_page_title",
        name="Last Edit Page Title",
        value_fn=lambda entity: entity.coordinator.last_edit_page,  # type: ignore
    ),
    MediaWikiSensorEntityDescription(
        key="last_edit_timestamp",
        name="Last Edit Time",
        value_fn=lambda entity: entity.coordinator.last_edit_time,  # type: ignore
    ),
    MediaWikiSensorEntityDescription(
        key="last_edit_msg",
        name="Last Edit Message",
        value_fn=lambda entity: entity.coordinator.last_edit_msg,  # type: ignore
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: ConfigEntry,
    async_add_entities: Callable[[list[SensorEntity]], None],
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        [
            MediaWikiSensor(
                coordinator=entry.runtime_data,
                entity_description=entity_description,
            )
            for entity_description in ENTITY_DESCRIPTIONS
        ]
    )


class MediaWikiSensor(MediaWikiEntity, SensorEntity):
    """ha_mediawiki Sensor class."""

    entity_description: MediaWikiSensorEntityDescription

    def __init__(
        self,
        coordinator: MediaWikiDataUpdateCoordinator,
        entity_description: MediaWikiSensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description: MediaWikiSensorEntityDescription = entity_description

    @property
    def native_value(self) -> StateType:
        """Count contributions."""
        return self.entity_description.value_fn(self)
