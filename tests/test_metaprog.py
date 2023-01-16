"""
Testing metaprogramming without using any of the public classes of this package
nor any real HTTP requests.
"""
import json
from dataclasses import dataclass

import yarl
import aiohttp
import pytest
from pytest_mock import MockerFixture

from chris.client.base import AbstractClient
from chris.helper.metaprog import get_return_hint
from chris.helper.search import Search
from chris.models.collection_links import AbstractCollectionLinks

from chris.models.types import ApiUrl
from chris.helper import collection


@dataclass(frozen=True)
class ExampleCollectionLinks(AbstractCollectionLinks):
    example_collection_name: ApiUrl
    another_name: ApiUrl


class ExampleClient(AbstractClient[ExampleCollectionLinks]):
    @collection.post("example_collection_name")
    async def example_method(self, a_param: str) -> list:
        ...

    @collection.search("another_name")
    def example_search(self, **kwargs) -> Search[str]:
        ...


def test_get_return_hint():
    assert get_return_hint(ExampleClient.example_method) is list


@pytest.fixture
def example_client(mocker: MockerFixture) -> ExampleClient:
    link = ApiUrl("https://example.com/post_to_link")
    another_link = ApiUrl("https://example.com/something/")
    links = ExampleCollectionLinks(
        example_collection_name=link, another_name=another_link
    )
    return ExampleClient(
        url="https://example.com",
        collection_links=links,
        s=mocker.MagicMock(spec_set=aiohttp.ClientSession),
    )


async def test_request_to_collection_link(
    example_client: ExampleClient, mocker: MockerFixture
):
    mock_response = mocker.AsyncMock()
    mock_response.raise_for_status = mocker.MagicMock()
    mock_response.status = 200
    mock_response.text = mocker.AsyncMock(return_value="[3, 4, 5]")
    example_client.s.post = mocker.AsyncMock(return_value=mock_response)

    res = await example_client.example_method(a_param="hello")
    assert res == [3, 4, 5]
    example_client.s.post.assert_called_once_with(
        example_client.collection_links.example_collection_name,
        json={"a_param": "hello"},
        raise_for_status=mocker.ANY,
    )


async def test_search(example_client: ExampleClient, mocker: MockerFixture):
    first_res = {
        "count": 5,
        "next": "https://example.com/something/search/?limit=3&offset=3",
        "previous": None,
        "results": ["yellowfin", "tuna", "salmon"],
    }
    mock_response = mocker.MagicMock()
    mock_response.status = 200
    mock_response.text = mocker.AsyncMock(return_value=json.dumps(first_res))
    example_client.s.get = mocker.AsyncMock(return_value=mock_response)
    search = example_client.example_search(animal="fish", edible="yes")
    assert search.Item is str
    example_client.s.get.assert_not_called()

    assert await search.count() == first_res["count"]
    example_client.s.get.assert_called_once()
    called_url: yarl.URL = example_client.s.get.call_args.args[0]
    assert "limit=1" in called_url.query_string
    assert "offset=0" in called_url.query_string
    assert called_url.query_string.count("limit") == 1
    assert called_url.query_string.count("offset") == 1
    example_client.s.get.reset_mock()

    search_iter = aiter(search)
    assert await anext(search_iter) == "yellowfin"
    expected_uri = "https://example.com/something/search/?animal=fish&edible=yes"
    example_client.s.get.assert_called_once_with(yarl.URL(expected_uri))
    example_client.s.get.reset_mock()
    mock_response.text.reset_mock()
    assert await anext(search_iter) == "tuna"
    example_client.s.get.assert_not_called()
    assert await anext(search_iter) == "salmon"
    example_client.s.get.assert_not_called()

    second_res = {
        "count": 5,
        "next": None,
        "previous": "https://example.com/something/search/?animal=fish&edible=yes?limit=3&offset=0",
        "results": ["flounder", "swordfish"],
    }
    mock_response.text = mocker.AsyncMock(return_value=json.dumps(second_res))
    assert await anext(search_iter) == "flounder"
    example_client.s.get.assert_called_once_with(first_res["next"])
    example_client.s.get.reset_mock()
    assert await anext(search_iter) == "swordfish"
    assert await anext(search_iter, None) is None
    example_client.s.get.assert_not_called()


def test_metaclass_validates_links():
    expected_msg = (
        r"Method .+BadClient.bad_method.+ requests collection_link "
        r"\"a_name_that_dne\" which is not defined in .+ExampleCollectionLinks.*"
    )
    with pytest.raises(TypeError, match=expected_msg) as e:

        class BadClient(AbstractClient[ExampleCollectionLinks]):
            @collection.post("a_name_that_dne")
            async def bad_method(self, a_param: str) -> list:
                ...
