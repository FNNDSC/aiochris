import abc
from typing import Optional, Generic, Callable

import aiohttp

from chris.client.base import L, CSelf
from chris.client.chris import AbstractChrisClient
from chris.helper.errors import IncorrectLoginError, raise_for_status
from chris.models.types import ChrisURL, Username, Password


class AuthenticatedClient(AbstractChrisClient[L, CSelf], Generic[L, CSelf], abc.ABC):
    """
    An authenticated ChRIS client.
    """

    @classmethod
    async def from_login(
        cls,
        url: str | ChrisURL,
        username: str | Username,
        password: str | Password,
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
        url: str | ChrisURL,
        username: Username,
        password: Password,
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
            connector=session.connector,
            connector_owner=connector_owner,
        )

    @classmethod
    async def from_token(
        cls,
        url: str | ChrisURL,
        token: str,
        connector: Optional[aiohttp.TCPConnector] = None,
        connector_owner: Optional[bool] = True,
    ) -> CSelf:
        """
        Construct an authenticated client using the given token.
        """
        return await cls.new(
            url, connector, connector_owner, session_modifier=cls.__curry_token(token)
        )

    @staticmethod
    def __curry_token(token: str) -> Callable[[aiohttp.ClientSession], None]:
        def add_token_to(session: aiohttp.ClientSession) -> None:
            session.headers.update({"Authorization": "Token " + token})

        return add_token_to
