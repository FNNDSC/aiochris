import abc
import os
from typing import Optional, Generic, Callable

import aiohttp
from async_property import async_cached_property

from chris.client.base import L, CSelf
from chris.client.base import BaseChrisClient
from chris.link import http
from chris.models.logged_in import Plugin, File
from chris.models.public import User
from chris.util.errors import IncorrectLoginError, raise_for_status
from chris.models.types import ChrisURL, Username, Password
from chris.util.search import Search


class AuthenticatedClient(BaseChrisClient[L, CSelf], Generic[L, CSelf], abc.ABC):
    """
    An authenticated ChRIS client.
    """

    @classmethod
    async def from_login(
        cls,
        url: str | ChrisURL,
        username: str | Username,
        password: str | Password,
        max_search_requests: int = 100,
        connector: Optional[aiohttp.TCPConnector] = None,
        connector_owner: bool = True,
    ) -> CSelf:
        """
        Get authentication token using username and password, then construct the client.
        """
        async with aiohttp.ClientSession(
            connector=connector, connector_owner=False
        ) as session:
            try:
                c = await cls.__from_login_with(
                    url=url,
                    username=username,
                    password=password,
                    max_search_requests=max_search_requests,
                    session=session,
                    connector_owner=connector_owner,
                )
            except BaseException as e:
                if connector is None:
                    await session.connector.close()
                raise e
        return c

    @classmethod
    async def __from_login_with(
        cls,
        url: str | ChrisURL,
        username: Username,
        password: Password,
        max_search_requests: int,
        session: aiohttp.ClientSession,
        connector_owner: bool,
    ) -> CSelf:
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
            max_search_requests=max_search_requests,
            connector=session.connector,
            connector_owner=connector_owner,
        )

    @classmethod
    async def from_token(
        cls,
        url: str | ChrisURL,
        token: str,
        max_search_requests: int,
        connector: Optional[aiohttp.TCPConnector] = None,
        connector_owner: Optional[bool] = True,
    ) -> CSelf:
        """
        Construct an authenticated client using the given token.
        """
        return await cls.new(
            url=url,
            max_search_requests=max_search_requests,
            connector=connector,
            connector_owner=connector_owner,
            session_modifier=cls.__curry_token(token),
        )

    @staticmethod
    def __curry_token(token: str) -> Callable[[aiohttp.ClientSession], None]:
        def add_token_to(session: aiohttp.ClientSession) -> None:
            session.headers.update({"Authorization": "Token " + token})

        return add_token_to

    # ============================================================
    # CUBE API methods
    # ============================================================

    @http.search("plugins")
    def search_plugins(self, **query) -> Search[Plugin]:
        """
        Search for plugins.
        """
        ...

    def upload(self, local_file: str | os.PathLike, upload_path: str) -> File:
        """
        Upload a local file to *ChRIS*.

        Examples
        --------

        Upload a single file:

        ```python
        chris = await ChrisClient.from_login(
            username='chris',
            password='chris1234',
            url='https://cube.chrisproject.org/api/v1/'
        )
        file = await chris.upload("./my_data.dat", 'dir/my_data.dat')
        assert file.fname == 'chris/uploads/dir/my_data.dat'
        ```

        Upload (in parallel) all `*.txt` files in a directory
        `'incoming'` to `chris/uploads/big_folder`:

        ```python
        upload_jobs = (
            chris.upload(p, f'big_folder/{p}')
            for p in Path('incoming')
        )
        await asyncio.gather(upload_jobs)
        ```

        Parameters
        ----------
        local_file
            Path of an existing local file to upload.
        upload_path
            A subpath of `{username}/uploads/` where to upload the file to in *CUBE*
        """
        if not str(upload_path).startswith(""):
            ...
        raise NotImplementedError()

    @http.get("user")
    async def user(self) -> User:
        """Gets the user's information."""
        ...

    @async_cached_property
    async def _user(self) -> User:
        return await self.user()

    async def username(self) -> Username:
        """
        Gets the username. In contrast to `self.user`, this method will use a cached API call.
        """
        user = await self._user  # this is weird
        return user.username
