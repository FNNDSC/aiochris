import functools
import time
from pathlib import Path
from typing import Callable, Awaitable

import pytest
from aiohttp.client_exceptions import ClientConnectorError

from chris import AnonChrisClient, ChrisClient, ChrisAdminClient
from chris.models.public import ComputeResource
from chris.models.types import Username, Password
from chris.util.errors import IncorrectLoginError
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
    """
    A string which is different on each test session.
    """
    return str(int(time.time()))


@pytest.fixture(scope="session")
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
async def normal_client(session, new_user_info) -> ChrisClient:
    with pytest.raises(IncorrectLoginError):
        await ChrisClient.from_login(
            url=new_user_info.url,
            username=new_user_info.username,
            password=new_user_info.password,
            connector=session.connector,
            connector_owner=False,
        )
    created_user = await ChrisClient.create_user(
        url=new_user_info.url,
        username=new_user_info.username,
        password=new_user_info.password,
        email=f"{new_user_info.username}@example.com",
        session=session,
    )
    assert created_user.username == new_user_info.username
    return await ChrisClient.from_login(
        url=new_user_info.url,
        username=new_user_info.username,
        password=new_user_info.password,
        connector=session.connector,
        connector_owner=False,
    )


async def test_get_plugin(anon_client: AnonChrisClient):
    p = await anon_client.search_plugins(name_exact="pl-dircopy").first()
    assert p.name == "pl-dircopy"


async def test_username(normal_client: ChrisClient, new_user_info):
    assert (await normal_client.username()) == new_user_info.username


async def test_get_user(normal_client: ChrisClient, new_user_info):
    assert (await normal_client.user()).username == new_user_info.username


@pytest.fixture(scope="session")
async def new_compute_resource(
    admin_client: ChrisAdminClient, now_str: str
) -> ComputeResource:
    name = f"test-aiochris-{now_str}-cr"
    created_compute_resource = await admin_client.create_compute_resource(
        name=name,
        compute_url=f"http://localhost:56965/does-not-exist/api/v1/",
        compute_user=f"pfcon",
        compute_password=f"pfcon1234",
        description="a fake compute resource for testing aiochris.",
    )
    assert created_compute_resource.name == name
    return created_compute_resource


async def test_everything(
    normal_client: ChrisClient,
    tmp_path: Path,
    now_str: str,
    new_compute_resource: ComputeResource,
):
    example_file_path = tmp_path / "hello_aiochris.txt"
    example_file_path.write_text("testing is good fun")

    upload_subpath = f"aiochris-test-upload-{now_str}/hello_aiochris.txt"
    uploaded_file = await normal_client.upload_file(example_file_path, upload_subpath)
    assert uploaded_file.fname.endswith("hello_aiochris.txt")

    plugin = await normal_client.search_plugins(name_exact="pl-dircopy").first()
    plinst = await plugin.create_instance(
        dir=uploaded_file.parent, compute_resource_name="host"
    )
    assert plinst.plugin_id == plugin.id

    # new_compute_resource.name
