"""
Common connection and authentication logic between _ChRIS_ store
and _ChRIS_ backends.

Beware code smells! To work around limitations of frozen dataclasses
and async object creation, while trying to achieve code reuse between
`AnonymousChrisStoreClient`, `ChrisStoreClient`, and `ChrisClient`,
I'm doing some unorthodox things in "constructor" class methods.

If using more than one client in an application, it's more efficient
to use the same
[connector](https://docs.aiohttp.org/en/stable/client_advanced.html#connectors).

```python
import aiohttp
from chris import ChrisStoreClient, ChrisClient

with aiohttp.TCPConnector() as connector:
    store_client = await ChrisStoreClient.from_url(
        url='https://example.com/cube/api/v1/',
        connector=connector,
        connector_owner=False
    )
    cube_client = await ChrisClient.from_login(
        url='https://example.com/cube/api/v1/',
        username='storeuser',
        password='storepassword',
        connector=connector,
        connector_owner=False
    )
    ...
```
"""

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
from serde.json import from_json

from chris.common.atypes import CommonCollectionLinks, AuthenticatedCollectionLinks
from chris.common.models import Plugin, CreatedUser
from chris.common.errors import IncorrectLoginError, raise_for_status
from chris.common.search import get_paginated, PaginatedUrl, T
from chris.common.types import ChrisURL, ChrisUsername, ChrisPassword, ChrisToken

_B = TypeVar("_B", bound="BaseClient")
_A = TypeVar("_A", bound="AnonymousClient")
_C = TypeVar("_C", bound="AuthenticatedClient")
_L = TypeVar("_L", bound=CommonCollectionLinks)
_UL = TypeVar("_UL", bound=AuthenticatedCollectionLinks)
P = TypeVar("P", bound=Plugin)


@dataclass(frozen=True)
class AbstractClient(Generic[_L, P], abc.ABC):
    """
    Common data between clients for the _ChRIS_ backend and _ChRIS_ store backend.
    It is simply a wrapper around a
    [aiohttp.ClientSession](https://docs.aiohttp.org/en/stable/client_advanced.html#client-session)
    and also has the `collection_links` object from the base URL.
    """

    collection_links: _L
    s: aiohttp.ClientSession
    url: PaginatedUrl

    async def close(self):
        """
        Close the HTTP session used by this client.
        """
        await self.s.close()

    async def get_first_plugin(self, **query) -> Optional[P]:
        """
        Get the first plugin from a search.

        Parameters are not documented, and possible key-value pairs are different
        between the _ChRIS_ store and _CUBE_.

        - https://github.com/FNNDSC/ChRIS_store/blob/8f4fc98b3d87dc9aa3f7fbb314684021680a5945/store_backend/plugins/models.py#L203-L261
        - https://github.com/FNNDSC/ChRIS_ultron_backEnd/blob/1ea8fc0ce6c6c1be6d67be21cf235ea07d8a9aa7/chris_backend/plugins/models.py#L212-L248
        """
        search_results = self.search_plugins(limit=1, max_requests=1, **query)
        return await anext(search_results, None)

    def search_plugins(self, max_requests=100, **query) -> AsyncIterator[P]:
        return self.search(
            url=self.collection_links.plugins,
            query=query,
            element_type=generic_of(self.__class__, Plugin),
            max_requests=max_requests,
        )

    def search(
        self, url: str, query: dict, element_type: Type[T], max_requests: int = 100
    ) -> AsyncIterator[T]:
        qs = self._join_qs(query)
        return get_paginated(
            session=self.s,
            url=PaginatedUrl(f"{url}search?{qs}"),
            element_type=element_type,
            max_requests=max_requests,
        )

    @staticmethod
    def _join_qs(query: dict) -> str:
        return "&".join(f"{k}={v}" for k, v in query.items() if v)


class BaseClient(AbstractClient[_L, P], AsyncContextManager[_B], abc.ABC):
    """
    Provides the `BaseClient.new` constructor. Subclasses which make
    use of `BaseClient.new` may not have any extra fields.
    """

    @classmethod
    async def new(
        cls,
        url: ChrisURL,
        connector: Optional[aiohttp.BaseConnector] = None,
        connector_owner: bool = True,
        session_modifier: Optional[Callable[[aiohttp.ClientSession], None]] = None,
    ) -> _B:
        """
        A constructor which creates the session for the `AbstractClient`
        and makes an initial request to populate `collection_links`.

        If this `BaseClient` is working with an API that requires authentication,
        then it is necessary to define `session_modifier` to add authentication
        headers to the session.
        """
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
        links_type = generic_of(cls, CommonCollectionLinks)
        links = from_dict(links_type, body["collection_links"])

        return cls(url=PaginatedUrl(url), s=session, collection_links=links)

    async def __aenter__(self) -> _B:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class AnonymousClient(BaseClient[_L, P, _A]):
    @classmethod
    async def from_url(
        cls,
        url: str | ChrisURL,
        connector: Optional[aiohttp.BaseConnector] = None,
        connector_owner: bool = True,
    ) -> _A:
        """
        Create an anonymous client for the given backend URL.
        """
        return await cls.new(url, connector, connector_owner)


class AuthenticatedClient(BaseClient[_UL, P, _C], abc.ABC):
    @classmethod
    async def from_login(
        cls,
        url: str | ChrisURL,
        username: str | ChrisUsername,
        password: str | ChrisPassword,
        connector: Optional[aiohttp.TCPConnector] = None,
        connector_owner: bool = True,
    ) -> _C:
        """
        Get authentication token using username and password, then construct the client.
        """
        async with aiohttp.ClientSession(
            connector=connector, connector_owner=False
        ) as session:
            try:
                c = await cls.__from_login_with(
                    url, username, password, session, connector_owner
                )
            except BaseException as e:
                if connector is None:
                    await session.connector.close()
                raise e
        return c

    @classmethod
    async def __from_login_with(
        cls,
        url: ChrisURL,
        username: ChrisUsername,
        password: ChrisPassword,
        session: aiohttp.ClientSession,
        connector_owner: bool,
    ) -> _C:
        """
        Get authentication token using the given session, and then construct the client.
        """
        payload = {"username": username, "password": password}
        login = await session.post(url + "auth-token/", json=payload)
        if login.status == 400:
            raise IncorrectLoginError(await login.text())
        await raise_for_status(login)
        data = await login.json()
        return await cls.from_token(
            url=url,
            token=data["token"],
            connector=session.connector,
            connector_owner=connector_owner,
        )

    @classmethod
    async def from_token(
        cls,
        url: ChrisURL,
        token: ChrisToken,
        connector: Optional[aiohttp.TCPConnector] = None,
        connector_owner: Optional[bool] = True,
    ) -> _C:
        """
        Construct an authenticated client using the given token.
        """
        return await cls.new(
            url, connector, connector_owner, session_modifier=cls.__curry_token(token)
        )

    @staticmethod
    def __curry_token(token: ChrisToken) -> Callable[[aiohttp.ClientSession], None]:
        def add_token_to(session: aiohttp.ClientSession) -> None:
            session.headers.update({"Authorization": "Token " + token})

        return add_token_to

    @classmethod
    async def create_user(
        cls,
        url: ChrisURL | str,
        username: ChrisUsername | str,
        password: ChrisPassword | str,
        email: str,
        session: aiohttp.ClientSession,
    ) -> CreatedUser:
        payload = {
            "template": {
                "data": [
                    {"name": "email", "value": email},
                    {"name": "username", "value": username},
                    {"name": "password", "value": password},
                ]
            }
        }
        headers = {
            "Content-Type": "application/vnd.collection+json",
            "Accept": "application/json",
        }
        res = await session.post(url + "users/", json=payload, headers=headers)
        await raise_for_status(res)
        return from_json(CreatedUser, await res.text())


_T = TypeVar("_T")


@functools.cache
def generic_of(c: type, t: Type[_T], subclass=False) -> Optional[Type[_T]]:
    """
    Get the actual class represented by a bound TypeVar of a generic.
    """
    for generic_type in typing_inspect.get_args(c):
        if isinstance(generic_type, (str, ForwardRef, TypeVar)):
            continue
        if issubclass(generic_type, t):
            return generic_type

    if hasattr(c, "__orig_bases__"):
        for subclass in c.__orig_bases__:
            subclass_generic = generic_of(subclass, t, subclass=True)
            if subclass_generic is not None:
                return subclass_generic
    if not subclass:
        raise ValueError("Superclass does not inherit BaseClient")
    return None
