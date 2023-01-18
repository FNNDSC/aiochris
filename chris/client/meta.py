import abc
from typing import Final, Any, Optional, Callable, Type

from chris.link.metaprog import generic_of
from chris.models.collection_links import AbstractCollectionLinks


class CollectionClientMeta(abc.ABCMeta):
    """
    A metaclass for `chris.client.base.AbstractChrisClient`
    which sets the class attribute `collection_links_type`
    and performs validation on any methods decorated by
    `chris.util.collection.post` at the time of class definition.
    """

    _DECORATED_METHOD_MARK: Final = "_collection_name"
    """
    An attribute name which is set on functions decorated by the
    method decorators in this module.
    """

    def __new__(mcs, name, bases, dct):
        c = super().__new__(mcs, name, bases, dct)
        if abc.ABC in bases:
            c.collection_links_type = AbstractCollectionLinks
            return c
        c.collection_links_type: Type[AbstractCollectionLinks] = generic_of(
            c, AbstractCollectionLinks
        )
        mcs._validate_collection_names(dct, c.collection_links_type)
        return c

    @classmethod
    def _validate_collection_names(
        mcs, dct, collection_links_type: Type[AbstractCollectionLinks]
    ):
        """
        Check that every method marked by `mark_to_check` was given a collection name
        which exists as a field in the class's associated
        `chris.models.collection_links.AbstractCollectionLinks` type.
        """
        marked_methods = filter(None, map(mcs._get_marked, dct.values()))
        for collection_name, method in marked_methods:
            if not collection_links_type.has_field(collection_name):
                raise TypeError(
                    f'Method {method} requests collection_link "{collection_name}" '
                    f"which is not defined in {collection_links_type}"
                )

    @classmethod
    def _get_marked(mcs, method: Any) -> Optional[tuple[str, Callable]]:
        if not callable(method):
            return None
        if hasattr(method, mcs._DECORATED_METHOD_MARK):
            val = getattr(method, mcs._DECORATED_METHOD_MARK)
            return val, method
        return None

    @classmethod
    def mark_to_check(mcs, method: Callable, collection_name: str) -> None:
        """
        Indicate that the given method has a data dependency on the
        class to have a member in its `collection_links` by a given name.
        """
        if not callable(method):
            raise TypeError("method must be callable")
        setattr(method, mcs._DECORATED_METHOD_MARK, collection_name)
