from chris import AnonChrisClient, ChrisClient, ChrisAdminClient
from chris.helper.collection import has_collection
from chris.helper.metaprog import get_class_of_method, get_return_hint
from chris.models.collection_links import (
    AnonymousCollectionLinks,
    CollectionLinks,
    AdminCollectionLinks,
)


class ExampleClass:
    def method(self) -> frozenset:
        ...


def test_get_class_of_method():
    assert get_class_of_method(ExampleClass.method) is ExampleClass


def test_get_return_hint():
    assert get_return_hint(ExampleClass.method) is frozenset


def test_has_collection():
    assert has_collection(AnonChrisClient, "plugins")
    assert has_collection(ChrisClient, "plugins")
    assert has_collection(ChrisAdminClient, "plugins")

    assert not has_collection(AnonChrisClient, "user")
    assert has_collection(ChrisClient, "user")
    assert has_collection(ChrisAdminClient, "user")

    assert not has_collection(AnonChrisClient, "admin")
    assert not has_collection(ChrisClient, "admin")
    assert has_collection(ChrisAdminClient, "admin")


def test_collection_links_type():
    assert AnonChrisClient.collection_links_type is AnonymousCollectionLinks
    assert ChrisClient.collection_links_type is CollectionLinks
    assert ChrisAdminClient.collection_links_type is AdminCollectionLinks
