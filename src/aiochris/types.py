"""
NewTypes for _ChRIS_ models.
"""

from typing import NewType, Union, Literal

Username = NewType("Username", str)
"""ChRIS user account username"""
Password = NewType("Password", str)
"""ChRIS user account password"""
ChrisURL = NewType("ChrisURL", str)
"""ChRIS backend API base URL"""

ApiUrl = NewType("ApiUrl", str)
"""Any CUBE URL which I am too lazy to be more specific about."""
ResourceId = NewType("ResourceId", int)
"""ID number which I am too lazy to be more specific about."""
PluginName = NewType("PluginName", str)
"""Name of a ChRIS plugin"""
ImageTag = NewType("ImageTag", str)
"""OCI image tag (informally, a Docker Image name)"""
PluginVersion = NewType("PluginVersion", str)
"""Version string of a ChRIS plugin"""

PluginUrl = NewType("PluginUrl", str)
"""
URL of a ChRIS plugin.

## Examples

- https://chrisstore.co/api/v1/plugins/5/
- https://cube.chrisproject.org/api/v1/plugins/6/
"""
PluginSearchUrl = NewType("PluginSearchUrl", str)

PluginId = NewType("PluginId", int)

UserUrl = NewType("UserUrl", str)
UserId = NewType("UserId", int)

AdminUrl = NewType("AdminUrl", str)
"""A admin resource URL ending with `/chris-admin/api/v1/`"""
ComputeResourceName = NewType("ComputeResourceName", str)
ComputeResourceId = NewType("ComputeResourceId", int)

PfconUrl = NewType("PfconUrl", str)

FeedId = NewType("FeedId", int)


CubeFilePath = NewType("CubeFilePath", str)


CUBEErrorCode = NewType("CUBEErrorCode", str)

ContainerImageTag = NewType("ContainerImageTag", str)

PipingId = NewType("PipingId", int)
PipelineId = NewType("PipelineId", int)

ParameterName = NewType("ParameterName", str)
ParameterValue = Union[str, int, float, bool]
ParameterType = Literal["boolean", "integer", "float", "string", "path", "unextpath"]

PluginInstanceParameterUrl = NewType("PluginInstanceParameterUrl", str)
PluginInstanceParameterId = NewType("PluginInstanceParameterId", int)

PipelineParameterId = NewType("ParameterLocalId", int)
PluginParameterId = NewType("ParameterGlobalId", int)
PluginInstanceId = NewType("PluginInstanceId", int)

FileFname = NewType("FileFname", str)
FileResourceName = NewType("FileResourceName", str)
FileId = NewType("FileId", int)

FilesUrl = NewType("FilesUrl", str)
FileResourceUrl = NewType("FileResourceUrl", str)
PipelineUrl = NewType("PipelineUrl", str)
PipingsUrl = NewType("PipingsUrl", str)
PipelinePluginsUrl = NewType("PipelinePluginsUrl", str)
PipelineDefaultParametersUrl = NewType("PipelineDefaultParametersUrl", str)
PipingUrl = NewType("PipingUrl", str)

PipelineParameterUrl = NewType("PipingParameterUrl", str)
PluginInstanceUrl = NewType("PluginInstanceUrl", str)
PluginInstancesUrl = NewType("PluginInstancesUrl", str)
DescendantsUrl = NewType("DescendantsUrl", str)
PipelineInstancesUrl = NewType("PipelineInstancesUrl", str)
PluginInstanceParamtersUrl = NewType("PluginInstanceParametersUrl", str)
ComputeResourceUrl = NewType("ComputeResourceUrl", str)
SplitsUrl = NewType("SplitsUrl", str)
FeedUrl = NewType("FeedUrl", str)
NoteId = NewType("NoteId", int)
"""A feed note's ID number."""
NoteUrl = NewType("NoteUrl", str)
"""
A feed's note URL.

## Examples

- https://cube.chrisproject.org/api/v1/note4/
"""
PluginParametersUrl = NewType("PluginParametersUrl", str)
TagsUrl = NewType("TagsUrl", str)
TaggingsUrl = NewType("TaggingsUrl", str)
CommentsUrl = NewType("CommentsUrl", str)

PluginParameterUrl = NewType("PluginParameterUrl", str)

PacsFileId = NewType("PacsFileId", int)
