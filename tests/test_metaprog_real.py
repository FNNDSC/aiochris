"""
Assert metaprogramming on the public classes of this package.
"""
from chris import AnonChrisClient, ChrisClient, ChrisAdminClient
from chris.models.collection_links import (
    AnonymousCollectionLinks,
    CollectionLinks,
    AdminCollectionLinks,
)


def test_collection_links_type():
    assert AnonChrisClient.collection_links_type is AnonymousCollectionLinks
    assert ChrisClient.collection_links_type is CollectionLinks
    assert ChrisAdminClient.collection_links_type is AdminCollectionLinks


def test_has_collection():
    assert AnonChrisClient.has_collection("plugins")
    assert ChrisClient.has_collection("plugins")
    assert ChrisAdminClient.has_collection("plugins")

    assert not AnonChrisClient.has_collection("user")
    assert ChrisClient.has_collection("user")
    assert ChrisAdminClient.has_collection("user")

    assert not AnonChrisClient.has_collection("admin")
    assert not ChrisClient.has_collection("admin")
    assert ChrisAdminClient.has_collection("admin")
