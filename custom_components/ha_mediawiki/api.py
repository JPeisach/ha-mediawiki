"""MediaWiki API Client."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

import pywikibot
from pywikibot.login import ClientLoginManager

if TYPE_CHECKING:
    import aiohttp
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
    def _getPage(self) -> BasePage | None:
        if self._site is not None:
            p = pywikibot.Page(self._site, "Test")
            return p
        return None

    # FIXME: should this be a public interface?
    def site(self) -> BaseSite:
        return self._site

    def user(self) -> pywikibot.User:
        # For quick reference
        return self._user

    def __init__(
        self,
        username: str,
        password: str,
        site_url: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """MediaWiki API Client."""
        self._username = username
        self._password = password
        self._session = session
        self._site_url = site_url
        self._logged_in = False

    # TODO: make sure we only define what we need
    async def login(self):
        """Login to the MediaWiki instance."""
        # yep.. each of these are like this - and they have to be this way
        # so we can assign them their private vars, because
        # *I think* we can't assign fields in code that is running in
        # executor
        self._site = await asyncio.get_running_loop().run_in_executor(
            None, lambda: pywikibot.Site(url=self._site_url)
        )
        self._login_mgr = await asyncio.get_running_loop().run_in_executor(
            None,
            lambda: ClientLoginManager(
                user=self._username, password=self._password, site=self._site
            ),
        )
        self._logged_in = await asyncio.get_running_loop().run_in_executor(
            None, self._login_mgr.login
        )
        self._user = await asyncio.get_running_loop().run_in_executor(
            None, lambda: pywikibot.User(self._login_mgr.site, self._username)
        )

    async def async_get_userinfo(self) -> Any:
        """Get userinfo per site."""
        if self._logged_in:
            return self._login_mgr.site.userinfo
        return ""

    # TODO: Across the entire file, fix types and returns
    async def async_get_user_contributions(self) -> Any:
        if self._logged_in:
            return await asyncio.get_running_loop().run_in_executor(
                None, self._user.contributions
            )
        return ""

    def _count_user_contribs(
        self,
    ) -> int:
        j = 0
        for _ in self._user.contributions():
            j += 1
        return j

    # TODO: deduplicate from above?
    async def async_get_user_contributions_count(self) -> int:
        return await asyncio.get_running_loop().run_in_executor(
            None, self._count_user_contribs
        )

    async def async_get_globaluserinfo(self) -> dict:
        if self._logged_in:
            return await asyncio.get_running_loop().run_in_executor(
                None,
                lambda: self._login_mgr.site.get_globaluserinfo(user=self._username),
            )
        return {}
