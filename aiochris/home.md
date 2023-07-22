[//]: # (this file is included by pdoc)

[*ChRIS*](https://chrisproject.org) Python client library built on
[aiohttp](https://github.com/aio-libs/aiohttp) (async HTTP client) and
[pyserde](https://github.com/yukinarit/pyserde)
([dataclasses](https://docs.python.org/3/library/dataclasses.html) deserializer).

## Installation

Requires Python 3.10 or 3.11.

```shell
pip install aiochris
# or
poetry add aiochris
```

## Brief Example

```python
from aiochris import ChrisClient

chris = await ChrisClient.from_login(
    username='chris',
    password='chris1234',
    url='https://cube.chrisproject.org/api/v1/'
)
dircopy = await chris.search_plugins(name_exact='pl-brainmgz', version='2.0.3').get_only()
plinst = await dircopy.create_instance(compute_resource_name='host')
await plinst.set(title="copies brain image files into feed")
```

## Introduction

`aiochris` provides three core classes: `AnonChrisClient`, `ChrisClient`, and `ChrisAdminClient`.
These clients differ in permissions.

<details>
<summary>Methods are only defined for what the client has permission to see or do.</summary>

```python
anon_client = await AnonChrisClient.from_url('https://cube.chrisproject.org/api/v1/')
# ok: can search for plugins without logging in...
plugin = await anon_client.search_plugins(name_exact='pl-mri10yr06mo01da_normal').first()
# IMPOSSIBLE! AnonChrisClient.create_instance not defined...
await plugin.create_instance()

# IMPOSSIBLE! authentication required for ChrisClient
authed_client = await ChrisClient.from_url('https://cube.chrisproject.org/api/v1/')
authed_client = await ChrisClient.from_login(
    url='https://cube.chrisproject.org/api/v1/',
    username='chris',
    password='chris1234'
)
# authenticated client can also search for plugins
plugin = await authed_client.search_plugins(name_exact='pl-mri10yr06mo01da_normal').first()
await plugin.create_instance()  # works!
```

</details>


### Client Constructors

- `AnonChrisClient.from_url`: create a *CUBE* client without logging in.
- `ChrisClient.from_login`: create a *CUBE* client using a username and password.
- `ChrisClient.from_token`: create a *CUBE* client using a token from `/api/v1/auth-token/`.
- `ChrisClient.from_chrs`: create a *CUBE* client using logins saved by [`chrs`](https://crates.io/crates/chrs).
- `ChrisAdminClient.from_login`: create an *admin* client using a username and password.
- `ChrisAdminClient.from_token`: create an *admin* client using a token from `/api/v1/auth-token/`.

### aiochris in Jupyter Notebook

Jupyter and IPython support top-level `await`. This, in conjunction with `ChrisClient.from_chrs`,
make `aiochris` a great way to use _ChRIS_ interactively with code.

For a walkthrough, see https://github.com/FNNDSC/aiochris/blob/master/examples/aiochris_as_a_shell.ipynb

### Working with aiohttp

`aiochris` hides the implementation detail that it is built upon `aiohttp`,
however one thing is important to keep in mind:
be sure to call `ChrisClient.close` at the end of your program.

```python
chris = await ChrisClient.from_login(...)
# -- snip --
await chris.close()
```

You can also use an
[asynchronous context manager](https://docs.python.org/3/glossary.html#term-asynchronous-context-manager).

```python
async with (await ChrisClient.from_login(...)) as chris:
    await chris.upload_file('./something.dat', 'something.dat')
    ...
```

### Efficiency with Multiple Clients

If using more than one `aiohttp` client in an application, it's more efficient
to use the same
[connector](https://docs.aiohttp.org/en/stable/client_advanced.html#connectors).
One connector instance should be shared among every client object,
including all `aiochris` clients and other `aiohttp` clients.

<details>
<summary>Example: efficiently using multiple aiohttp clients</summary>

```python
import aiohttp
from aiochris import ChrisClient

with aiohttp.TCPConnector() as connector:
    chris_client1 = await ChrisClient.from_login(
        url='https://example.com/cube/api/v1/',
        username='user1',
        password='user1234',
        connector=connector,
        connector_owner=False
    )
    chris_client2 = await ChrisClient.from_login(
        url='https://example.com/cube/api/v1/',
        username='user2',
        password='user4321',
        connector=connector,
        connector_owner=False
    )
    plain_http_client = aiohttp.ClientSession(connector=connector, connector_owner=False)
```

</details>

### Advice for Getting Started

Searching for things (plugins, plugin instances, files) in *CUBE* is a common task,
and *CUBE* often returns multiple items per response.
Hence, it is important to understand how the `Search` helper class works.
It simplifies how we interact with paginated collection responses from *CUBE*.

When performing batch operations, use
[`asyncio.gather`](https://docs.python.org/3/library/asyncio-task.html#running-tasks-concurrently)
to run async functions concurrently.

`aiochris` uses many generic types, so it is recommended you use an IDE
with good support for type hints, such as
[PyCharm](https://www.jetbrains.com/pycharm/download/)
or [VSCodium](https://vscodium.com) with
[Pylance](https://github.com/microsoft/pylance-release/issues/483) configured.
