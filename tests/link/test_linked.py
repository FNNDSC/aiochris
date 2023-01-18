import dataclasses

import aiohttp
import pytest
import serde
import yarl

from chris.link.linked import Linked, LinkedModel, deserialize_linked


@serde.deserialize
@dataclasses.dataclass(frozen=True)
class ExampleLinkedModel(LinkedModel):
    a_name: str
    a_num: int


@serde.deserialize
@dataclasses.dataclass(frozen=True)
class ExampleUnlinkedModel:
    food: str
    taste: str


class ExampleClient(Linked):
    def _get_link(self, name: str) -> yarl.URL:
        raise NotImplementedError()

    @classmethod
    def _has_link(cls, name: str) -> bool:
        raise NotImplementedError()


@pytest.fixture(scope="session")
def example_linked_client(session: aiohttp.ClientSession):
    return ExampleClient(s=session, max_search_requests=10)


def test_deserialize_linked(example_linked_client):
    data = {"a_name": "ellen", "a_num": -4}
    o = deserialize_linked(example_linked_client, ExampleLinkedModel, data)
    assert isinstance(o, ExampleLinkedModel)
    assert o.s is example_linked_client.s
    assert o.a_name == data["a_name"]
    assert o.a_num == data["a_num"]


def test_deserialize_unlinked(example_linked_client):
    data = {"food": "fries", "taste": "salty"}
    o = deserialize_linked(example_linked_client, ExampleUnlinkedModel, data)
    assert isinstance(o, ExampleUnlinkedModel)
    assert o == ExampleUnlinkedModel(**data)
