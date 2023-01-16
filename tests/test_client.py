import functools
import time
from typing import Callable, Awaitable

import pytest
from aiohttp.client_exceptions import ClientConnectorError

from chris import AnonChrisClient, ChrisClient, ChrisAdminClient
from chris.models.types import Username, Password
from tests.conftest import UserCredentials


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
async def anon_client(session, admin_credentials) -> AnonChrisClient:
    return await AnonChrisClient.from_url(
        url=admin_credentials.url, connector=session.connector, connector_owner=False
    )


@pytest.fixture(scope="session")
def now_str() -> str:
    return str(int(time.time()))


@pytest.fixture
def new_user_info(now_str, admin_credentials) -> UserCredentials:

    return UserCredentials(
        username=Username(f"test-user-{now_str}"),
        password=Password(f"chris1234{now_str}"),
        url=admin_credentials.url,
    )


@pytest.fixture(scope="session")
async def admin_client(session, admin_credentials) -> ChrisAdminClient:
    return await ChrisAdminClient.from_login(
        url=admin_credentials.url,
        username=admin_credentials.username,
        password=admin_credentials.password,
        connector=session.connector,
        connector_owner=False,
    )


@pytest.fixture(scope="session")
@skip_if_not_connected
async def normal_client(session, admin_credentials) -> ChrisClient:
    return await ChrisClient.from_login(
        url=admin_credentials.url,
        username=admin_credentials.username,
        password=admin_credentials.password,
        connector=session.connector,
        connector_owner=False,
    )


async def test_get_plugin(anon_client: AnonChrisClient):
    p = await anon_client.get_first_plugin(name_exact="pl-dircopy")
    assert p.name == "pl-dircopy"
