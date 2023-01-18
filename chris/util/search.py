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

from chris.link.linked import deserialize_linked, Linked

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

    Examples
    --------

    Use with an `async for` loop:

    TODO example with plugin instances

    ```python
    finished_freesurfer: Search = chris.plugin_instances(plugin_name_exact='pl-fshack', status='finishedSuccessfully')
    async for p in chris.plugin_instances(

    ```
    """

    base_url: str
    params: dict[str, Any]
    client: Linked
    Item: Type[T]
    max_requests: int = 100

    def __aiter__(self) -> AsyncIterator[T]:
        return self._paginate(self.url)

    async def first(self) -> Optional[T]:
        """
        Get the first item.

        Examples
        --------

        This function is commonly used to "get one thing" from CUBE.

        ```python
        await chris.search_plugins(name_exact="pl-dircopy").first()
        """
        return await anext(self._first_aiter(), None)

    async def count(self) -> int:
        """
        Get the number of items in this collection search.

        Examples
        --------

        `count` is useful for rendering a progress bar. TODO example with files
        """
        async with self.client.s.get(self._first_url) as res:
            data: _Paginated = from_json(_Paginated, await res.text())
        return data.count

    def _paginate(self, url: yarl.URL) -> AsyncIterator[T]:
        return _get_paginated(
            client=self.client,
            url=url,
            item_type=self.Item,
            max_requests=self.max_requests,
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
    client: Linked,
    url: yarl.URL | str,
    item_type: Type[T],
    max_requests: int,
) -> AsyncGenerator[T, None]:
    """
    Make HTTP GET requests to a paginated endpoint. Further requests to the
    "next" URL are made in the background as needed.
    """
    logger.debug("GET, max_requests=%d, --> %s", max_requests, url)
    if max_requests != -1 and max_requests == 0:
        raise TooMuchPaginationError(
            f"too many requests made to {url}. "
            f"If this is expected, then pass the argument max_search_requests=-1 to "
            f"the client constructor classmethod."
        )
    async with client.s.get(url) as res:  # N.B. not checking for 4XX, 5XX statuses
        data: _Paginated = from_json(_Paginated, await res.text())
        for element in data.results:
            yield deserialize_linked(client, item_type, element)
    if data.next is not None:
        next_results = _get_paginated(client, data.next, item_type, max_requests - 1)
        async for next_element in next_results:
            yield next_element


async def acollect(async_iterable: AsyncIterable[T]) -> list[T]:
    """
    Simple helper to convert a `Search` to a [`list`](https://docs.python.org/3/library/stdtypes.html#list).

    Using this function is not recommended unless you can assume the collection is small.
    """
    # nb: using tuple here causes
    #     TypeError: 'async_generator' object is not iterable
    # return tuple(e async for e in async_iterable)
    return [e async for e in async_iterable]


class TooMuchPaginationError(Exception):
    """ """

    pass
