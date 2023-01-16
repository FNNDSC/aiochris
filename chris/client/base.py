import abc
import functools
from dataclasses import dataclass
from typing import (
    Optional,
    TypeVar,
    Generic,
    AsyncContextManager,
    AsyncIterator,
    Type,
    ForwardRef,
    Callable,
)

import aiohttp
import typing_inspect
from serde import from_dict

from chris.helper.metaprog import generic_of
from chris.models.collection_links import AnonymousCollectionLinks
from chris.models.res import Plugin
from chris.helper.search import get_paginated, T

# in Python 3.11 we will be able to use Self!
CSelf = TypeVar("CSelf", bound="AbstractChrisClient")

_C = TypeVar("_C", bound="AuthenticatedClient")
L = TypeVar("L", bound=AnonymousCollectionLinks)


class CollectionClientMeta(abc.ABCMeta):
    """
    A metaclass for `AbstractChrisClient` which sets the class attribute `collection_links_type`.
    """

    def __new__(mcs, name, bases, dct):
        c = super().__new__(mcs, name, bases, dct)
        c.collection_links_type: Type[AnonymousCollectionLinks] = generic_of(  # noqa
            c, AnonymousCollectionLinks
        )
        return c


@dataclass(frozen=True)
class AbstractChrisClient(
    Generic[L, CSelf],
    AsyncContextManager[CSelf],
    abc.ABC,
    metaclass=CollectionClientMeta,
):
    """
    Provides the implementation for most of the read-only GET resources of ChRIS
    and functions related to the client object's own usage.
    """

    collection_links: L
    s: aiohttp.ClientSession
    url: str
    max_requests: int = 1000
    """
    Maximum number of requests to make for pagination.
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

    async def get_first_plugin(self, **query) -> Optional[Plugin]:
        """
        Get the first plugin from a search.
        """
        search_results = self.search_plugins(limit=1, max_requests=1, **query)
        return await anext(search_results, None)

    def search_plugins(self, max_requests=100, **query) -> AsyncIterator[Plugin]:
        """
        Search for plugins.
        """
        return self.search(
            url=self.collection_links.plugins,
            query=query,
            element_type=Plugin,
            max_requests=max_requests,
        )

    def search(
        self, url: str, query: dict, element_type: Type[T], max_requests: int = 100
    ) -> AsyncIterator[T]:
        qs = self._join_qs(query)
        return get_paginated(
            session=self.s,
            url=f"{url}search?{qs}",
            element_type=element_type,
            max_requests=max_requests,
        )

    @staticmethod
    def _join_qs(query: dict) -> str:
        return "&".join(f"{k}={v}" for k, v in query.items() if v)
