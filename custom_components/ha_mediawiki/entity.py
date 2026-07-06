"""MediaWikiEntity class."""

from __future__ import annotations

from homeassistant.const import CONF_NAME, CONF_URL, CONF_USERNAME
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import MediaWikiDataUpdateCoordinator


class MediaWikiEntity(CoordinatorEntity[MediaWikiDataUpdateCoordinator]):
    """MediaWikiEntity class."""

    def __init__(self, coordinator: MediaWikiDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    coordinator.config_entry.domain,
                    coordinator.config_entry.entry_id,
                ),
            },
            configuration_url=coordinator.config_entry.data[CONF_URL],
            model=coordinator.sitename,
            model_id=coordinator.config_entry.data[CONF_USERNAME],
            name=coordinator.config_entry.data[CONF_NAME],
        )

    @property
    def unique_id(self) -> str:
        """Generate a unique ID for this entity."""
        if self.entity_description is not None:
            return f"{self.coordinator.sitename}_{self.coordinator.config_entry.data[CONF_USERNAME]}_{self.entity_description.key}"
        return f"{self.coordinator.sitename}_{self.name}"
