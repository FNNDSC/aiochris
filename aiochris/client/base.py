import abc
from typing import AsyncContextManager, Generic, Optional, Callable, TypeVar

import aiohttp
from serde import from_dict

from aiochris import Search
from aiochris.link.collection_client import L, CollectionJsonApiClient
from aiochris.models.public import PublicPlugin
from aiochris.errors import raise_for_status

CSelf = TypeVar(
    "CSelf", bound="BaseChrisClient"
)  # can't wait for `Self` in Python 3.11!


class BaseChrisClient(
    Generic[L, CSelf],
    CollectionJsonApiClient[L],
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
        max_search_requests: int = 100,
        connector: Optional[aiohttp.BaseConnector] = None,
        connector_owner: bool = True,
        session_modifier: Optional[Callable[[aiohttp.ClientSession], None]] = None,
    ) -> CSelf:
        """
        A constructor which creates the session for the `BaseChrisClient`
        and makes an initial request to populate `collection_links`.

        Parameters
        ----------
        url
            ChRIS backend url, e.g. "https://cube.chrisproject.org/api/v1/"
        max_search_requests
            Maximum number of HTTP requests to make while retrieving items from a
            paginated endpoint before raising `aiochris.util.search.TooMuchPaginationError`.
            Use `max_search_requests=-1` to allow for "infinite" pagination
            (well, you're still limited by Python's stack).
        connector
            [`aiohttp.BaseConnector`](https://docs.aiohttp.org/en/v3.8.3/client_advanced.html#connectors) to use.
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
            raise_for_status=False,
            connector=connector,
            connector_owner=connector_owner,
        )
        if session_modifier is not None:
            session_modifier(session)
        try:
            async with session.get(url) as res:
                await raise_for_status(res)
                body = await res.json()
        except Exception:
            await session.close()
            raise
        links = from_dict(cls._collection_type(), body["collection_links"])
        return cls(
            url=url,
            s=session,
            collection_links=links,
            max_search_requests=max_search_requests,
        )

    async def __aenter__(self) -> CSelf:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """
        Close the HTTP session used by this client.
        """
        await self.s.close()

    @abc.abstractmethod
    def search_plugins(self, **query) -> Search[PublicPlugin]:
        """
        Search for plugins.
        """
        ...
