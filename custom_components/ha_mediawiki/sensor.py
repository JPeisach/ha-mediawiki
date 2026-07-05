"""Sensor platform for ha_mediawiki."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

import voluptuous as vol
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.core import ServiceCall, ServiceResponse, SupportsResponse, callback
from homeassistant.helpers import selector

from custom_components.ha_mediawiki.const import DOMAIN

from .entity import MediaWikiEntity

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers import entity_platform
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

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
        value_fn=lambda a: a.coordinator.edit_count,
    ),
    MediaWikiSensorEntityDescription(
        key="last_edit_page_title",
        name="Last Edit Page Title",
        value_fn=lambda a: a.coordinator.last_edit_page,  # type: ignore
    ),
    MediaWikiSensorEntityDescription(
        key="last_edit_timestamp",
        name="Last Edit Time",
        value_fn=lambda a: a.coordinator.last_edit_time,  # type: ignore
    ),
    MediaWikiSensorEntityDescription(
        key="last_edit_msg",
        name="Last Edit Message",
        value_fn=lambda a: a.coordinator.last_edit_msg,  # type: ignore
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: ConfigEntry,
    async_add_entities: Callable[[list[SensorEntity]], None],
) -> None:
    """Set up the sensor platform."""

    @callback
    async def async_get_page_extract(call: ServiceCall) -> ServiceResponse:
        """Get page extract"""
        page = call.data.get("page_name")
        extract = await entry.runtime_data.async_get_page_extract(page)
        return {"message": extract}

    hass.services.async_register(
        DOMAIN,
        service="get_page_extract",
        schema=vol.Schema(
            {
                vol.Required("page_name"): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.URL,
                    ),
                )
            }
        ),
        service_func=async_get_page_extract,
        supports_response=SupportsResponse.OPTIONAL,
    )

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
