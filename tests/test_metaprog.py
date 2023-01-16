"""
Testing metaprogramming without using any of the public classes of this package
nor any real HTTP requests.
"""
import typing
import json
from dataclasses import dataclass
from typing import AsyncIterator

import aiohttp
import pytest
from pytest_mock import MockerFixture

from chris.client.base import AbstractClient
from chris.helper.metaprog import get_return_hint, get_return_item_type
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
    def example_search(self, **kwargs) -> AsyncIterator[str]:
        ...


def test_get_return_hint():
    assert get_return_hint(ExampleClient.example_method) is list


def test_get_return_item_of():
    def example_search() -> AsyncIterator[str]:
        ...

    assert get_return_item_type(example_search) is str


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
    example_client.s.get.assert_not_called()
    assert await anext(search) == "yellowfin"
    expected_uri = "https://example.com/something/search/?animal=fish&edible=yes"
    example_client.s.get.assert_called_once_with(expected_uri)
    example_client.s.get.reset_mock()
    mock_response.text.reset_mock()
    assert await anext(search) == "tuna"
    example_client.s.get.assert_not_called()
    assert await anext(search) == "salmon"
    example_client.s.get.assert_not_called()

    second_res = {
        "count": 5,
        "next": None,
        "previous": "https://example.com/something/search/?animal=fish&edible=yes?limit=3&offset=0",
        "results": ["flounder", "swordfish"],
    }
    mock_response.text = mocker.AsyncMock(return_value=json.dumps(second_res))
    assert await anext(search) == "flounder"
    example_client.s.get.assert_called_once_with(first_res["next"])
    example_client.s.get.reset_mock()
    assert await anext(search) == "swordfish"
    assert await anext(search, None) is None
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
