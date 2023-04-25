# aiochris

[![Tests](https://github.com/FNNDSC/aiochris/actions/workflows/test.yml/badge.svg)](https://github.com/FNNDSC/aiochris/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/FNNDSC/aiochris/branch/master/graph/badge.svg?token=48EEYZ3PUU)](https://codecov.io/gh/FNNDSC/aiochris)
[![PyPI](https://img.shields.io/pypi/v/aiochris)](https://pypi.org/project/aiochris/)
[![License - MIT](https://img.shields.io/pypi/l/aiochris)](https://github.com/FNNDSC/aiochris/blob/master/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[_ChRIS_](https://chrisproject.org) Python client library built on
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

## Quick Example

```python
import asyncio
from aiochris import ChrisClient


async def readme_example():
    chris = await ChrisClient.from_login(
        username='chris',
        password='chris1234',
        url='https://cube.chrisproject.org/api/v1/'
    )
    dircopy = await chris.search_plugins(name_exact='pl-brainmgz', version='2.0.3').get_only()
    plinst = await dircopy.create_instance(compute_resource_name='host')
    feed = await plinst.get_feed()
    await feed.set(name="hello, aiochris!")
    await chris.close()  # do not forget to clean up!


asyncio.run(readme_example())
```

## Documentation Links

- Client documentation: https://fnndsc.github.io/aiochris
- Developer documentation: https://github.com/FNNDSC/aiochris/wiki
