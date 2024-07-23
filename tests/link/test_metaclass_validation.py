import pytest
import yarl

from aiochris.link.linked import Linked
from aiochris.link import http


def test_metaclass_validates_links():
    expected_msg = (
        r"Method .+BadClient.bad_method.+ needs link "
        r"\"a_name_that_dne\" but .*BadClient.* does not have it"
    )
    with pytest.raises(TypeError, match=expected_msg) as e:

        class BadClient(Linked):
            @classmethod
            def _has_link(cls, name: str) -> bool:
                return False

            def _get_link(self, name: str) -> yarl.URL:
                raise pytest.fail(f'should not have link "{name}"')

            @http.post("a_name_that_dne")
            async def bad_method(self, a_param: str) -> list: ...
