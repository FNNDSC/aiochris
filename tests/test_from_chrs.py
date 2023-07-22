import pytest
from aiochris.client.from_chrs import ChrsLogins, _SERVICE
from pathlib import Path


_example_path = Path("examples/example_logins.toml")
expected_password = "i am from a keyring"


@pytest.fixture(scope="session")
def keyring():
    try:
        import keyring as keyring_lib

        return keyring_lib.get_keyring()
    except ModuleNotFoundError:
        pytest.skip("keyring not installed. Please run poetry install --all-extras")


@pytest.fixture(scope="session")
def logins(keyring) -> ChrsLogins:
    l = ChrsLogins.load(_example_path)
    # simulate running `chrs login` by adding passwords to keyring
    keyring_usernames = [
        login.to_keyring_username()
        for login in l.cubes
        if login.store.store == "Keyring"
    ]
    for u in keyring_usernames:
        keyring.set_password(_SERVICE, u, expected_password)
    try:
        return l
    except Exception:
        # clean up
        for u in keyring_usernames:
            keyring.delete_password(_SERVICE, u)
        raise


@pytest.mark.parametrize(
    "username, address, expected_address, expected_token",
    [
        (
            "celery",
            "https://one.example.com/api/v1/",
            "https://one.example.com/api/v1/",
            "abcdefghijklmnopqrstuvwxyz",
        ),
        (
            None,
            "https://one.example.com/api/v1/",
            "https://one.example.com/api/v1/",
            "abcdefghijklmnopqrstuvwxyz",
        ),
        ("okra", None, "https://two.example.com/api/v1/", "qwertyuiopasdfghjklzxcvbnm"),
        (None, None, "https://two.example.com/api/v1/", expected_password),
    ],
)
def test_chrs_logins(username, address, expected_address, expected_token, logins):
    address, token = logins.get_token_for(address, username)
    assert token == expected_token
    assert address == expected_address
