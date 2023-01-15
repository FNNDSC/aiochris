# aiochris

[_ChRIS_](https://chrisproject.org) Python client library built on
[aiohttp](https://github.com/aio-libs/aiohttp) (async HTTP client) and
[pyserde](https://github.com/yukinarit/pyserde)
([dataclasses](https://docs.python.org/3/library/dataclasses.html) deserializer).

## Developing

Requires [Poetry](https://python-poetry.org/) version 1.3.1.

### Setup

```shell
git clone git@github.com:FNNDSC/aiochris.git
cd aiochris
poetry install --with=dev
```

### Testing

1. Start up [miniCHRIS](https://github.com/FNNDSC/miniChRIS-docker)
2. `poetry run pytest`
