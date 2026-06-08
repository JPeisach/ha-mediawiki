"""Sample API Client."""

from __future__ import annotations

import asyncio
import socket
from typing import Any

import aiohttp
import async_timeout
import pywikibot
import pywikibot.data
import pywikibot.data.api
from pywikibot.page import BasePage
from pywikibot.site import BaseSite


class MediaWikiApiClientError(Exception):
    """Exception to indicate a general API error."""


class MediaWikiApiClientCommunicationError(
    MediaWikiApiClientError,
):
    """Exception to indicate a communication error."""


class MediaWikiApiClientAuthenticationError(
    MediaWikiApiClientError,
):
    """Exception to indicate an authentication error."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise MediaWikiApiClientAuthenticationError(
            msg,
        )
    response.raise_for_status()


class MediaWikiApiClient:
    """Sample API Client."""

    # It's probably better to just use the pretty output from
    # pywikibot, but we need to ensure we don't make blocking calls
    # so each possible call gets its function instead of a generic
    # wrapper
    def _getPage(self) -> BasePage:
        p = pywikibot.Page(pywikibot.Site(self._site), "Test")
        return p

    def __init__(
        self,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Sample API Client."""
        self._username = username
        self._password = password
        self._session = session
        # for now, lets just use test wikipedia *only*
        self._site = "wikipedia:test"

    async def async_get_data(self) -> Any:
        """Get data from the API."""
        return await asyncio.get_running_loop().run_in_executor(
            None,
            # pywikibot.data.api.Request(
            #     self._site, action=action, **params
            # ).submit,
            self._getPage,
        )
