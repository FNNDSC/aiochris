from aiochris.link.metaprog import get_return_hint


class ExampleClient:
    def example_method_one(self) -> list:
        ...

    def example_method_two(self) -> bool:
        ...


def test_get_return_hint():
    assert get_return_hint(ExampleClient.example_method_one) is list
    assert get_return_hint(ExampleClient.example_method_two) is bool
