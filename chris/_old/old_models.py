from dataclasses import dataclass

from serde import deserialize
from chris.models.types import ApiUrl
from chris.models.res import Plugin
from chris._old.types import ComputeResourceName, ComputeResourceId, PfconUrl


@deserialize
@dataclass(frozen=True)
class CubePlugin(Plugin):
    compute_resources: PaginatedUrl


# {
#     "url": "http://localhost:8000/api/v1/plugins/5/",
#     "id": 5,
#     "creation_date": "2022-02-22T13:45:19.869011-05:00",
#     "name": "pl-fshack",
#     "version": "1.2.0",
#     "dock_image": "fnndsc/pl-fshack:version-1.2.2",
#     "public_repo": "https://github.com/FNNDSC/pl-fshack",
#     "icon": "",
#     "type": "ds",
#     "stars": 0,
#     "authors": "FNNDSC (dev@babyMRI.org)",
#     "title": "A quick-n-dirty attempt at hacking a FreeSurfer ChRIS plugin",
#     "category": "",
#     "description": "This app houses a complete FreeSurfer distro and exposes some\n        FreeSurfer apps at the level of the plugin CLI.'",
#     "documentation": "https://github.com/FNNDSC/pl-fshack",
#     "license": "Opensource (MIT)",
#     "execshell": "python3",
#     "selfpath": "/usr/src/fshack",
#     "selfexec": "fshack.py",
#     "min_number_of_workers": 1,
#     "max_number_of_workers": 1,
#     "min_cpu_limit": 1000,
#     "max_cpu_limit": 2147483647,
#     "min_memory_limit": 200,
#     "max_memory_limit": 2147483647,
#     "min_gpu_limit": 0,
#     "max_gpu_limit": 0,
#     "meta": "http://localhost:8000/api/v1/plugins/metas/5/",
#     "parameters": "http://localhost:8000/api/v1/plugins/5/parameters/",
#     "instances": "http://localhost:8000/api/v1/plugins/5/instances/",
#     "compute_resources": "http://localhost:8000/api/v1/plugins/5/computeresources/"
# }


@deserialize
@dataclass(frozen=True)
class ComputeResource:
    url: ApiUrl
    id: ComputeResourceId
    creation_date: str
    modification_date: str
    name: ComputeResourceName
    compute_url: PfconUrl
    compute_auth_url: str
    description: str
    max_job_exec_seconds: int
