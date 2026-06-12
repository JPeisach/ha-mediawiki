"""DataUpdateCoordinator for ha_mediawiki."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pywikibot import User
import pywikibot
import pywikibot.login
from pywikibot.pagegenerators import UserContributionsGenerator
from pywikibot.site import BaseSite

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
    global_userinfo: dict
    site: BaseSite
    user: User
    user_contributions: Any  # TODO: What's the type?
    user_contributions_count: int

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: MediaWikiConfigEntry,
        api: MediaWikiApiClient,
    ):
        super().__init__(
            hass, _LOGGER, name="MediaWiki API Coordinator", config_entry=config_entry
        )
        self.config_entry = config_entry
        self.api = api

    async def _async_setup(self):
        await self.api.login()

        # Direct references
        self.site = self.api.site()
        self.user = self.api.user()

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            self.global_userinfo = await self.api.async_get_globaluserinfo()
            self.user_contributions = await self.api.async_get_user_contributions()
            self.user_contributions_count = (
                await self.api.async_get_user_contributions_count()
            )
        except MediaWikiApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except MediaWikiApiClientError as exception:
            raise UpdateFailed(exception) from exception
