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

import yarl
from serde import deserialize
from serde.json import from_json

from aiochris.link.linked import deserialize_linked, Linked
from aiochris.errors import (
    BaseClientError,
    raise_for_status,
    NonsenseResponseError,
)

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
    Abstraction over paginated collection responses from *CUBE*.
    `Search` objects are returned by methods for search endpoints of the *CUBE* API.
    It is an [asynchronous iterable](https://docs.python.org/3/glossary.html#term-asynchronous-iterable)
    which produces items from responses that return multiple results.
    HTTP requests are fired as-neede, they happen in the background during iteration.
    No request is made before the first time a `Search` object is called.

    .. note:: Pagination is handled internally and automatically.
             The query parameters `limit` and `offset` can be explicitly given, but they shouldn't.

    Examples
    --------

    Use an `async for` loop to print the name of every feed:

    ```python
    all_feeds = chris.search_feeds()  # returns a Search[Feed]
    async for feed in all_feeds:
        print(feed.name)
    ```
    """

    base_url: str
    params: dict[str, Any]
    client: Linked
    Item: Type[T]
    max_requests: int = 100
    subpath: str = "search/"

    def __aiter__(self) -> AsyncIterator[T]:
        return self._paginate(self.url)

    async def first(self) -> Optional[T]:
        """
        Get the first item.

        See also
        --------
        `get_only` : similar use, but more strict
        """
        return await anext(self._first_aiter(), None)

    async def get_only(self, allow_multiple=False) -> T:
        """
        Get the *only* item from a search with one result.

        Examples
        --------

        This method is very commonly used for getting "one thing" from CUBE.

        ```python
        await chris.search_plugins(name_exact="pl-dircopy", version="2.1.1").get_only()
        ```

        In the example above, a search for plugins given (`name_exact`, `version`)
        is guaranteed to return either 0 or 1 result.

        Raises
        ------
        aiochris.util.search.NoneSearchError
            If this search is empty.
        aiochris.util.search.ManySearchError
            If this search has more than one item and `allow_multiple` is `False`

        See also
        --------
        `first` : does the same thing but without checks.

        Parameters
        ----------
        allow_multiple: bool
            if `True`, do not raise `ManySearchError` if `count > 1`
        """
        one = await self._get_one()
        if one.count == 0:
            raise NoneSearchError(self.url)
        if not allow_multiple and one.count > 1:
            raise ManySearchError(self.url)
        if len(one.results) < 1:
            raise NonsenseResponseError(
                f"Response has count={one.count} but the results are empty.", one
            )
        return deserialize_linked(self.client, self.Item, one.results[0])

    async def count(self) -> int:
        """
        Get the number of items in this collection search.

        Examples
        --------

        `count` is useful for rendering a progress bar. TODO example with files
        """
        one = await self._get_one()
        return one.count

    async def _get_one(self) -> _Paginated:
        async with self.client.s.get(self._first_url) as res:
            await raise_for_status(res)
            return from_json(_Paginated, await res.text())

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
        return yarl.URL(self.base_url) / self.subpath

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


class TooMuchPaginationError(BaseClientError):
    """Specified maximum number of requests exceeded while retrieving results from a paginated resource."""

    pass


class GetOnlyError(BaseClientError):
    """Search does not have exactly one result."""

    pass


class NoneSearchError(GetOnlyError):
    """A search expected to have at least one element, has none."""

    pass


class ManySearchError(GetOnlyError):
    """A search expected to have only one result, has several."""

    pass
