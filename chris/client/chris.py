import abc
from typing import AsyncContextManager, Generic, Optional, Callable, AsyncIterator

import aiohttp
from serde import from_dict

from chris.client.base import CSelf, L, AbstractClient
from chris.helper import collection
from chris.models.res import Plugin


class AbstractChrisClient(
    Generic[L, CSelf],
    AbstractClient[L],
    AsyncContextManager[CSelf],
    abc.ABC,
):
    """
    Provides the implementation for most of the read-only GET resources of ChRIS
    and functions related to the client object's own usage.
    """

    @classmethod
    async def new(
        cls,
        url: str,
        connector: Optional[aiohttp.BaseConnector] = None,
        connector_owner: bool = True,
        session_modifier: Optional[Callable[[aiohttp.ClientSession], None]] = None,
    ) -> CSelf:
        """
        A constructor which creates the session for the `AbstractChrisClient`
        and makes an initial request to populate `collection_links`.

        Parameters
        ----------
        url
            ChRIS backend url, e.g. "https://cube.chrisproject.org/api/v1/"
        connector
            Connector to use.
            If creating multiple client objects in the same program,
            reusing connectors between them is more efficient.
        connector_owner
            If `True`, this client will close its `aiohttp.BaseConnector`
        session_modifier
            Called to mutate the created `aiohttp.ClientSession` for the object.
            If the client requires authentication, define `session_modifier`
            to add authentication headers to the session.
        """
        if not url.endswith("/api/v1/"):
            raise ValueError("url must end with /api/v1/")
        accept_json = {
            "Accept": "application/json",
            # 'Content-Type': 'application/vnd.collection+json',
        }
        # TODO maybe we want to wrap the session:
        # - status == 4XX --> print response text
        # - content-type: application/vnd.collection+json
        session = aiohttp.ClientSession(
            headers=accept_json,
            raise_for_status=True,
            connector=connector,
            connector_owner=connector_owner,
        )
        if session_modifier is not None:
            session_modifier(session)

        res = await session.get(url)
        body = await res.json()
        links = from_dict(cls.collection_links_type, body["collection_links"])

        return cls(url=url, s=session, collection_links=links)

    async def __aenter__(self) -> CSelf:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """
        Close the HTTP session used by this client.
        """
        await self.s.close()

    # ==================================================
    # ChRIS API functions
    # ==================================================

    async def get_first_plugin(self, **query) -> Optional[Plugin]:
        """
        Get the first plugin from a search.
        """
        search_results = self.search_plugins(limit=1, max_requests=1, **query)
        return await anext(search_results, None)

    @collection.search("plugins")
    def search_plugins(self, **query) -> AsyncIterator[Plugin]:
        """
        Search for plugins.
        """
        ...
