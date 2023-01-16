from typing import Optional

import aiohttp

from chris.client.chris import AbstractChrisClient
from chris.models.collection_links import AnonymousCollectionLinks


class AnonChrisClient(AbstractChrisClient[AnonymousCollectionLinks, "AnonChrisClient"]):
    """
    An anonymous ChRIS client. It has access to read-only GET resources,
    such as being able to search for plugins.
    """

    @classmethod
    async def from_url(
        cls,
        url: str,
        connector: Optional[aiohttp.BaseConnector] = None,
        connector_owner: bool = True,
    ) -> "AnonChrisClient":
        """
        Create an anonymous client.

        See `chris.base.AbstractChrisClient.new` for parameter documentation.
        """
        return await cls.new(url, connector, connector_owner)
