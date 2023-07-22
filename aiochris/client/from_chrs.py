"""
Interoperability with [`chrs`](https://crates.io/crates/chrs) version 0.2.4.

The functions of this module uses dynamic importing of extras from the `chrs` group.
"""
import dataclasses
from pathlib import Path

import serde
from typing import Optional, Literal
from aiochris.types import Username, ChrisURL
import functools

_SERVICE = "org.chrisproject.chrs"
"""
Keyring service name used by `chrs`.

https://github.com/FNNDSC/chrs/blob/v0.2.4/chrs/src/login/saved.rs#L14
"""


@functools.cache
def _get_keyring():
    import keyring

    return keyring.get_keyring()


@serde.deserialize
@dataclasses.dataclass(frozen=True)
class StoredToken:
    """
    https://github.com/FNNDSC/chrs/blob/v0.2.4/chrs/src/login/tokenstore.rs#L18-L24
    """

    # note: we can't do @serde.deserialize(tagging=serde.AdjacentTagging('store', 'value'))
    # See https://github.com/yukinarit/pyserde/issues/411
    store: Literal["Text", "Keyring"]
    value: Optional[str] = None

    def __post_init__(self):
        if self.store not in ("Text", "Keyring"):
            raise ValueError()
        if self.store == "Text" and self.store is None:
            raise ValueError()


@dataclasses.dataclass(frozen=True)
class ChrsLogin:
    """
    A login saved by `chrs`.

    https://github.com/FNNDSC/chrs/blob/v0.2.4/chrs/src/login/tokenstore.rs#L18-L34
    """

    address: ChrisURL
    username: Username
    store: StoredToken

    def token(self) -> str:
        if self.store.value is not None:
            return self.store.value
        return self._get_token_from_keyring()

    def is_for(self, address: Optional[ChrisURL], username: Optional[Username]) -> bool:
        """
        Returns `True` if this login is for the specified _ChRIS_ user account.
        """
        if address is None and username is None:
            return True
        if address is None and username == self.username:
            return True
        if username is None and address == self.address:
            return True
        if address == self.address and username == self.username:
            return True
        return False

    def to_keyring_username(self) -> str:
        """
        Produce the username for this login in the keyring.

        https://github.com/FNNDSC/chrs/blob/v0.2.4/chrs/src/login/tokenstore.rs#L3
        """
        return f"{self.username}@{self.address}"

    def _get_token_from_keyring(self) -> str:
        """
        https://github.com/FNNDSC/chrs/blob/v0.2.4/chrs/src/login/tokenstore.rs#L110-L112
        """
        if self.store.store != "Keyring":
            raise ChrsKeyringError(
                "chrs login config is not valid: "
                f"for address={self.address} and username={self.username}"
                f"expected store=Keyring, got store={self.store.store}"
            )
        keyring_username = self.to_keyring_username()
        token = _get_keyring().get_password(_SERVICE, keyring_username)
        if token is None:
            raise ChrsKeyringError(f"No keyring password for {keyring_username}")
        return token


@dataclasses.dataclass(frozen=True)
class ChrsLogins:
    """
    Logins saved by `chrs`.

    https://github.com/FNNDSC/chrs/blob/v0.2.4/chrs/src/login/saved.rs#L18-L22
    """

    cubes: list[ChrsLogin]
    """Saved logins in reverse order of preference."""

    @classmethod
    def load(cls, path: Path) -> "ChrsLogins":
        import serde.toml

        return serde.toml.from_toml(cls, path.expanduser().read_text())

    def get_token_for(
        self,
        address: Optional[str | ChrisURL] = None,
        username: Optional[str | Username] = None,
    ) -> Optional[tuple[ChrisURL, str]]:
        """
        Get token for a login.
        """
        for login in reversed(self.cubes):
            if login.is_for(address, username):
                if (token := login.token()) is not None:
                    return login.address, token
        return None


class ChrsKeyringError(Exception):
    """Error interacting with Keyring."""

    pass
