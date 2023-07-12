from contextlib import asynccontextmanager
from typing import Optional

import aiohttp
from serde.json import from_json

from aiochris.client.authed import AuthenticatedClient
from aiochris.errors import raise_for_status
from aiochris.models.collection_links import CollectionLinks
from aiochris.models.data import UserData
from aiochris.types import ChrisURL, Username, Password


class ChrisClient(AuthenticatedClient[CollectionLinks, "ChrisClient"]):
    """
    A normal user *ChRIS* client, who may upload files and create plugin instances.
    """

    @classmethod
    async def create_user(
        cls,
        url: ChrisURL | str,
        username: Username | str,
        password: Password | str,
        email: str,
        session: Optional[aiohttp.ClientSession],
    ) -> UserData:
        payload = {
            "template": {
                "data": [
                    {"name": "email", "value": email},
                    {"name": "username", "value": username},
                    {"name": "password", "value": password},
                ]
            }
        }
        headers = {
            "Content-Type": "application/vnd.collection+json",
            "Accept": "application/json",
        }
        async with _optional_session(session) as session:
            res = await session.post(url + "users/", json=payload, headers=headers)
            await raise_for_status(res)
            return from_json(UserData, await res.text())


@asynccontextmanager
async def _optional_session(session: Optional[aiohttp.ClientSession]):
    if session is not None:
        yield session
        return
    async with aiohttp.ClientSession() as session:
        yield session
