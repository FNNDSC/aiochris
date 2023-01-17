import abc
from dataclasses import dataclass

import aiohttp
from serde import deserialize, field


@deserialize
@dataclass(frozen=True)
class Connected(abc.ABC):
    s: aiohttp.ClientSession = field(deserializer=lambda s: s)
