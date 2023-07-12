"""
.. include:: ./home.md

.. include:: ./examples.md
"""

import aiochris.client
import aiochris.models
import aiochris.util
from aiochris.util.search import Search, acollect
from aiochris.client.normal import ChrisClient
from aiochris.client.anon import AnonChrisClient
from aiochris.client.admin import ChrisAdminClient
from aiochris.enums import Status, ParameterTypeName

__all__ = [
    "AnonChrisClient",
    "ChrisClient",
    "ChrisAdminClient",
    "Search",
    "acollect",
    "Status",
    "ParameterTypeName",
    "client",
    "models",
    "util",
    "errors",
    "types",
]
