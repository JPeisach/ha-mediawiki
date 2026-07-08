"""
Custom integration to integrate ha_mediawiki with Home Assistant.

For more details about this integration, please refer to
https://github.com/jpeisach/ha_mediawiki
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import homeassistant
import homeassistant.helpers
import homeassistant.helpers.device_registry
import voluptuous as vol
from homeassistant.const import CONF_PASSWORD, CONF_URL, CONF_USERNAME, Platform
from homeassistant.core import (
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
    callback,
)
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.ha_mediawiki.const import DOMAIN

from .api import MediaWikiApiClient
from .coordinator import MediaWikiDataUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from .data import MediaWikiConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
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

    @callback
    async def async_get_page_extract(call: ServiceCall) -> ServiceResponse:
        """Get page extract of a MediaWiki page."""
        page_name = call.data.get("page_name")
        device_id = call.data.get("device_id")

        device_entry = homeassistant.helpers.device_registry.async_get(hass).async_get(
            str(device_id)
        )

        config_entry = hass.config_entries.async_get_known_entry(
            device_entry.primary_config_entry  # type: ignore
        )
        extract = await config_entry.runtime_data.api.async_get_page_extract(page_name)

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
                ),
                vol.Required("device_id"): selector.DeviceSelector(
                    selector.DeviceSelectorConfig(integration=DOMAIN)
                ),
            }
        ),
        service_func=async_get_page_extract,
        supports_response=SupportsResponse.OPTIONAL,
    )

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
