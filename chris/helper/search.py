import copy
import logging
from dataclasses import dataclass
from typing import (
    Optional,
    TypeVar,
    AsyncGenerator,
    Type,
    AsyncIterable,
    Any,
    Generic,
    AsyncIterator,
)

import aiohttp
import yarl
from serde import deserialize
from serde.json import from_json

from chris.helper._de_connected import deserialize_connected

logger = logging.getLogger(__name__)

T = TypeVar("T")


@deserialize
class _Paginated:
    """
    Response from a paginated endpoint.
    """

    count: int
    next: Optional[str]
    previous: Optional[str]
    results: list[Any]


@dataclass
class Search(Generic[T], AsyncIterable[T]):
    """
    Search result.
    """

    base_url: str
    params: dict[str, Any]
    s: aiohttp.ClientSession
    Item: Type[T]
    max_requests: int = 100

    def __aiter__(self) -> AsyncIterator[T]:
        return self._paginate(self.url)

    async def first(self) -> Optional[T]:
        """
        Get the first item.
        """
        return await anext(self._first_aiter(), None)

    async def count(self) -> int:
        """
        Get the number of items in this collection search.
        """
        async with self.s.get(self._first_url) as res:
            data: _Paginated = from_json(_Paginated, await res.text())
        return data.count

    def _paginate(self, url: yarl.URL) -> AsyncIterator[T]:
        return _get_paginated(
            session=self.s, url=url, item_type=self.Item, max_requests=self.max_requests
        )

    @property
    def url(self) -> yarl.URL:
        return self._search_url_with(self.params)

    def _first_aiter(self) -> AsyncIterator[T]:
        return self._paginate(self._first_url)

    @property
    def _first_url(self) -> yarl.URL:
        params = copy.copy(self.params)
        params["limit"] = 1
        params["offset"] = 0
        return self._search_url_with(params)

    @property
    def _search_url(self) -> yarl.URL:
        return yarl.URL(self.base_url) / "search/"

    def _search_url_with(self, query: dict[str, Any]):
        return yarl.URL(self._search_url).with_query(query)


async def _get_paginated(
    session: aiohttp.ClientSession,
    url: yarl.URL | str,
    item_type: Type[T],
    max_requests: int = 100,
) -> AsyncGenerator[T, None]:
    """
    Make HTTP GET requests to a paginated endpoint. Further requests to the
    "next" URL are made in the background as needed.
    """
    logger.debug("GET, max_requests=%d, --> %s", max_requests, url)
    if max_requests <= 0:
        raise TooMuchPaginationException()
    async with session.get(url) as res:  # N.B. not checking for 4XX, 5XX statuses
        data: _Paginated = from_json(_Paginated, await res.text())
        for element in data.results:
            yield deserialize_connected(session, item_type, element)
    if data.next is not None:
        next_results = _get_paginated(session, data.next, item_type, max_requests - 1)
        async for next_element in next_results:
            yield next_element


async def acollect(async_iterable: AsyncIterable[T]) -> list[T]:
    # nb: using tuple here causes
    #     TypeError: 'async_generator' object is not iterable
    # return tuple(e async for e in async_iterable)
    return [e async for e in async_iterable]


class TooMuchPaginationException(Exception):
    pass
