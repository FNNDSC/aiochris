from typing import Optional

import aiohttp

from aiochris.client.base import BaseChrisClient
from aiochris.link import http
from aiochris.models.collection_links import AnonymousCollectionLinks
from aiochris.models.public import PublicPlugin
from aiochris.util.search import Search


class AnonChrisClient(BaseChrisClient[AnonymousCollectionLinks, "AnonChrisClient"]):
    """
    An anonymous ChRIS client. It has access to read-only GET resources,
    such as being able to search for plugins.
    """

    @classmethod
    async def from_url(
        cls,
        url: str,
        max_search_requests: int = 100,
        connector: Optional[aiohttp.BaseConnector] = None,
        connector_owner: bool = True,
    ) -> "AnonChrisClient":
        """
        Create an anonymous client.

        See `aiochris.client.base.BaseChrisClient.new` for parameter documentation.
        """
        return await cls.new(
            url=url,
            max_search_requests=max_search_requests,
            connector=connector,
            connector_owner=connector_owner,
        )

    @http.search("plugins")
    def search_plugins(self, **query) -> Search[PublicPlugin]:
        """
        Search for plugins.

        Since this client is not logged in, you cannot create plugin instances using this client.
        """
        ...
