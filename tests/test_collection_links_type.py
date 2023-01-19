"""
Assert metaprogramming helpers work on the public classes of this package.
"""
from chris import AnonChrisClient, ChrisClient, ChrisAdminClient
from chris.models.collection_links import (
    AnonymousCollectionLinks,
    CollectionLinks,
    AdminCollectionLinks,
)


def test_collection_links_type():
    assert AnonChrisClient._collection_type() is AnonymousCollectionLinks
    assert ChrisClient._collection_type() is CollectionLinks
    assert ChrisAdminClient._collection_type() is AdminCollectionLinks
