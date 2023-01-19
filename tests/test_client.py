import functools
import time
from pathlib import Path
from typing import Callable, Awaitable

import pytest
from aiohttp.client_exceptions import ClientConnectorError

from chris import AnonChrisClient, ChrisClient, ChrisAdminClient
from chris.models.logged_in import Plugin, PluginInstance, Feed
from chris.models.public import ComputeResource
from chris.models.types import Username, Password
from chris.util.errors import IncorrectLoginError
from chris.util.search import ManySearchError, NoneSearchError
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
    admin_client: ChrisAdminClient, normal_client: ChrisClient, now_str: str
) -> ComputeResource:
    """
    Create a compute resource as the admin user, then check that it exists as the normal user.
    """
    created_compute_resource = await admin_client.create_compute_resource(
        name=f"test-aiochris-{now_str}-cr",
        compute_url=f"http://localhost:56965/does-not-exist/api/v1/",
        compute_user=f"pfcon",
        compute_password=f"pfcon1234",
        description="a fake compute resource for testing aiochris.",
    )
    search = await normal_client.search_compute_resources(
        name=created_compute_resource.name
    ).first()
    assert search.id == created_compute_resource.id
    assert created_compute_resource in await normal_client.get_all_compute_resources()
    return created_compute_resource


async def test_search_only_wrong(anon_client: AnonChrisClient):
    with pytest.raises(ManySearchError):
        await anon_client.search_plugins(name="pl-").get_only()
    with pytest.raises(NoneSearchError):
        await anon_client.search_plugins(name_exact="dne").get_only()


@pytest.fixture(scope="session")
async def dircopy(normal_client: ChrisClient):
    return await normal_client.search_plugins(name_exact="pl-dircopy").first()


@pytest.fixture(scope="session")
async def simpledsapp(normal_client: ChrisClient):
    return await normal_client.search_plugins(name_exact="pl-simpledsapp").first()


@pytest.fixture(scope="session")
async def dircopy_instance(
    dircopy: Plugin, normal_client: ChrisClient, tmp_path_factory
) -> PluginInstance:
    example_file_path = tmp_path_factory.mktemp("aiochris-test") / "hello_aiochris.txt"
    example_file_path.write_text("testing is good fun")

    upload_subpath = f"aiochris-test-upload-{now_str}/hello_aiochris.txt"
    uploaded_file = await normal_client.upload_file(example_file_path, upload_subpath)
    assert uploaded_file.fname.endswith("hello_aiochris.txt")

    plinst = await dircopy.create_instance(
        dir=uploaded_file.parent, compute_resource_name="host"
    )
    assert plinst.plugin_id == dircopy.id
    return plinst


async def test_plugin_instances(
    normal_client: ChrisClient, dircopy_instance: PluginInstance
):
    changed_inst = await dircopy_instance.set(
        title="i am a unit test called test_plugin_instances"
    )
    assert changed_inst.id == dircopy_instance.id
    found_plinst = await normal_client.plugin_instances(id=changed_inst.id).get_only()
    assert found_plinst.title == changed_inst.title


async def test_feed(dircopy_instance: PluginInstance):
    feed = await dircopy_instance.get_feed()
    feed_name = f"aiochris test feed: now_str={now_str}"
    changed_feed = await feed.set(name=feed_name)
    assert changed_feed.name == feed_name
    note = await feed.get_note()
    note_title = "howdy, partner"
    note_content = "i reckon this is a good enough test."
    changed_note = await note.set(title=note_title, content=note_content)
    assert changed_note.title == note_title
    assert changed_note.content == note_content
    assert changed_note.id == note.id


async def test_create_instance_checks_previous_type(
    dircopy: Plugin, simpledsapp: Plugin, dircopy_instance: PluginInstance
):
    with pytest.raises(TypeError, match="4 is not a PluginInstance"):
        await simpledsapp.create_instance(previous=4)  # type: ignore
    with pytest.raises(ValueError, match="Cannot give both previous and previous_id."):
        await simpledsapp.create_instance(previous=dircopy_instance, previous_id=4)
    e = "Cannot create plugin instance of a fs-type plugin with a previous plugin instance."
    with pytest.raises(ValueError, match=e):
        await dircopy.create_instance(previous=dircopy_instance)
    e = 'Plugin type is "ds" so previous is a required parameter.'
    with pytest.raises(ValueError, match=e):
        await simpledsapp.create_instance()
