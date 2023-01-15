from dataclasses import dataclass

from serde import deserialize

from chris.common.atypes import CommonCollectionLinks, AuthenticatedCollectionLinks
from chris.common.types import ApiUrl


@deserialize
@dataclass(frozen=True)
class AnonymousCollectionLinks(CommonCollectionLinks):
    plugin_stars: ApiUrl


@deserialize
@dataclass(frozen=True)
class StoreCollectionLinks(AuthenticatedCollectionLinks):
    favorite_plugin_metas: ApiUrl
    collab_plugin_metas: ApiUrl


@deserialize
@dataclass(frozen=True)
class AnonymousHome:
    collection_links: AnonymousCollectionLinks


# plugin upload response
# {
#     "url": "http://localhost:8010/api/v1/plugins/1/",
#     "id": 1,
#     "creation_date": "2022-02-19T13:48:32.099324-05:00",
#     "name": "pl-copy",
#     "version": "1.0.0",
#     "dock_image": "localhost/fnndsc/pl-copy:1.0.0",
#     "public_repo": "https://github.com/FNNDSC",
#     "icon": "",
#     "type": "ds",
#     "stars": 0,
#     "authors": "FNNDSC <dev@babyMRI.org>",
#     "title": "simple-copy",
#     "category": "",
#     "description": "A ChRIS ds plugin that copies data",
#     "documentation": "https://github.com/FNNDSC/chris_plugin/tree/master/examples/pl-copy",
#     "license": "MIT",
#     "execshell": "/usr/local/bin/python",
#     "selfpath": "/usr/local/bin",
#     "selfexec": "simple_copy",
#     "min_number_of_workers": 1,
#     "max_number_of_workers": 1,
#     "min_cpu_limit": 1000,
#     "max_cpu_limit": 2147483647,
#     "min_memory_limit": 200,
#     "max_memory_limit": 2147483647,
#     "min_gpu_limit": 0,
#     "max_gpu_limit": 0,
#     "parameters": "http://localhost:8010/api/v1/plugins/1/parameters/",
#     "meta": "http://localhost:8010/api/v1/1/"
# }
