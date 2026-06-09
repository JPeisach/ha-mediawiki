"""DataUpdateCoordinator for ha_mediawiki."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    MediaWikiApiClient,
    MediaWikiApiClientAuthenticationError,
    MediaWikiApiClientError,
)

if TYPE_CHECKING:
    from .data import MediaWikiConfigEntry

_LOGGER = logging.getLogger(__name__)


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class MediaWikiDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: MediaWikiConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: MediaWikiConfigEntry,
        api: MediaWikiApiClient,
    ):
        super().__init__(
            hass, _LOGGER, name="MediaWiki API Coordinator", config_entry=config_entry
        )
        self.api = api

    async def _async_setup(self):
        await self.api.login()

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            return await self.api.async_get_data()
        except MediaWikiApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except MediaWikiApiClientError as exception:
            raise UpdateFailed(exception) from exception
