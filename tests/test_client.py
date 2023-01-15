import pytest
from chris import AnonChrisClient, ChrisClient
from chris.helper.search import acollect
from typing import Type, Callable, Awaitable
import functools
from aiohttp.client_exceptions import ClientConnectorError


def skip_if_not_connected(f: Callable[[...], Awaitable]):
    @functools.wraps(f)
    async def wrapper(*args, **kwargs):
        try:
            return await f(*args, **kwargs)
        except ClientConnectorError:
            pytest.skip("backend is not running")

    return wrapper


@pytest.fixture(scope="session")
@skip_if_not_connected
async def anon(session, credentials) -> AnonChrisClient:
    return await AnonChrisClient.from_url(
        url=credentials.url, connector=session.connector, connector_owner=False
    )


@pytest.fixture(scope="session")
@skip_if_not_connected
async def chris(session, credentials) -> ChrisClient:
    return await ChrisClient.from_login(
        url=credentials.url,
        username=credentials.username,
        password=credentials.password,
        connector=session.connector,
        connector_owner=False,
    )


async def test_get_plugin(anon: AnonChrisClient):
    p = await anon.get_first_plugin(name_exact="pl-dircopy")
    assert p.name == "pl-dircopy"
