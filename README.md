# aiochris

[![Tests](https://github.com/FNNDSC/aiochris/actions/workflows/test.yml/badge.svg)](https://github.com/FNNDSC/chris_plugin/actions/workflows/test.yml)
[![PyPI](https://img.shields.io/pypi/v/aiochris)](https://pypi.org/project/aiochris/)
[![License - MIT](https://img.shields.io/pypi/l/aiochris)](https://github.com/FNNDSC/aiochris/blob/master/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

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

### Code Formatting

```shell
poetry run pre-commit run --all-files
```
