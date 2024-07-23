"""
Test workaround for a pyserde/beartype bug.

- https://github.com/beartype/beartype/issues/410
"""

import typing
from beartype import beartype
from aiochris.models import PluginInstance, Feed
from aiochris.link.linked import _beartype_workaround410  # noqa


@beartype
class BeartypedClass:
    def bear_method(self) -> "DummyReturn":
        ...


class DummyReturn:
    pass


def test_beartype_workaround_minimalcase():
    method_return_type = typing.get_type_hints(BeartypedClass.bear_method)['return']
    assert _beartype_workaround410(method_return_type) is DummyReturn


def test_beartype_workaround410_real():
    method_return_type = typing.get_type_hints(PluginInstance.get_feed)['return']
    assert _beartype_workaround410(method_return_type) is Feed
