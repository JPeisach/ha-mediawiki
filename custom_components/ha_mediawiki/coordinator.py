"""DataUpdateCoordinator for ha_mediawiki."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    MediaWikiApiClient,
    MediaWikiApiClientAuthenticationError,
    MediaWikiApiClientError,
)

if TYPE_CHECKING:
    import pywikibot
    from homeassistant.core import HomeAssistant
    from pywikibot import User
    from pywikibot.site import APISite

    from .data import MediaWikiConfigEntry

_LOGGER = logging.getLogger(__name__)


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class MediaWikiDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: MediaWikiConfigEntry
    global_userinfo: dict
    site: APISite
    sitename: str
    user: User
    userinfo: dict
    edit_count: Any  # TODO: What's the type?
    user_contributions_count: int
    last_edit_page: str | None
    last_edit_time: pywikibot.Timestamp | None
    last_edit_msg: str | None

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: MediaWikiConfigEntry,
        api: MediaWikiApiClient,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass, _LOGGER, name="MediaWiki API Coordinator", config_entry=config_entry
        )
        self.config_entry = config_entry
        self.api = api

    def get_user_contributions_count(self) -> int:
        return self.user_contributions_count

    async def async_get_page_extract(self, page: str) -> str:
        return await self.api.async_get_page_extract(page)

    async def _async_setup(self) -> None:
        await self.api.login()

        # Direct references
        self.site = self.api.site()  # type: ignore  # noqa: PGH003
        self.user = self.api.user()
        self.userinfo = await self.api.async_get_userinfo()
        self.watched_pages = await self.api.async_get_watched_pages()
        last_edit = await self.api.async_get_last_edit()
        if last_edit is not None:
            self.last_edit_page = last_edit[0].title()
            self.last_edit_time = last_edit[2]
            self.last_edit_msg = last_edit[3]
        self.sitename = await self.api.async_get_sitename()

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            self.global_userinfo = await self.api.async_get_globaluserinfo()
            self.edit_count = await self.api.async_get_user_edit_count()
        except MediaWikiApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except MediaWikiApiClientError as exception:
            raise UpdateFailed(exception) from exception
