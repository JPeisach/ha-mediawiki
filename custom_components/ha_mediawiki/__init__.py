"""
Custom integration to integrate ha_mediawiki with Home Assistant.

For more details about this integration, please refer to
https://github.com/ludeeus/ha_mediawiki
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_URL, CONF_USERNAME, Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_loaded_integration

from .api import MediaWikiApiClient
from .const import DOMAIN, LOGGER
from .coordinator import MediaWikiDataUpdateCoordinator
from .data import MediaWikiData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import MediaWikiConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    coordinator = MediaWikiDataUpdateCoordinator(
        hass=hass,
        config_entry=entry,
        api=MediaWikiApiClient(
            username=entry.data[CONF_USERNAME],
            password=entry.data[CONF_PASSWORD],
            site_url=entry.data[CONF_URL],
            session=async_get_clientsession(hass),
        ),
    )

    entry.runtime_data = coordinator

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: MediaWikiConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: MediaWikiConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
