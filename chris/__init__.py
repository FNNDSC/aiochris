"""
[*ChRIS*](https://chrisproject.org) Python client library built on
[aiohttp](https://github.com/aio-libs/aiohttp) (async HTTP client) and
[pyserde](https://github.com/yukinarit/pyserde)
([dataclasses](https://docs.python.org/3/library/dataclasses.html) deserializer).

## Efficiency with aiohttp

If using more than one client in an application, it's more efficient
to use the same
[connector](https://docs.aiohttp.org/en/stable/client_advanced.html#connectors).

```python
import aiohttp
from chris import ChrisClient

with aiohttp.TCPConnector() as connector:
    client1 = await ChrisClient.from_login(
        url='https://example.com/cube/api/v1/',
        username='user1',
        password='user1234',
        connector=connector,
        connector_owner=False
    )
    client2 = await ChrisClient.from_login(
        url='https://example.com/cube/api/v1/',
        username='user2',
        password='user4321',
        connector=connector,
        connector_owner=False
    )
    ...
```
"""

import chris.client
import chris.models
import chris.util
from chris.client.normal import ChrisClient
from chris.client.anon import AnonChrisClient
from chris.client.admin import ChrisAdminClient
from chris.models.enums import Status, ParameterTypeName

__all__ = [
    "AnonChrisClient",
    "ChrisClient",
    "ChrisAdminClient",
    "Status",
    "ParameterTypeName",
    "client",
    "models",
    "util",
]
