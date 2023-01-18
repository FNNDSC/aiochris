"""
NewTypes for ChRIS models.
"""

from typing import NewType, Union

Username = NewType("ChrisUsername", str)
Password = NewType("ChrisPassword", str)
ChrisURL = NewType("ChrisURL", str)

ApiUrl = NewType("ApiUrl", str)
"""URL which I am too lazy to be more specific about."""
ResourceId = NewType("ResourceId", int)
"""ID number which I am too lazy to be more specific about."""
PluginName = NewType("PluginName", str)
ImageTag = NewType("ImageTag", str)
PluginVersion = NewType("PluginVersion", str)

PluginUrl = NewType("PluginUrl", str)
PluginSearchUrl = NewType("PluginSearchUrl", str)

PluginId = NewType("PluginId", int)

UserUrl = NewType("UserUrl", str)
UserId = NewType("UserId", int)

AdminUrl = NewType("AdminUrl", str)
"""A admin resource URL ending with `/chris-admin/api/v1/`"""
ComputeResourceName = NewType("ComputeResourceName", str)
ComputeResourceId = NewType("ComputeResourceId", str)

PfconUrl = NewType("PfconUrl", str)

FeedId = NewType("FeedId", str)


CubeFilePath = NewType("CubeFilePath", str)


CUBEErrorCode = NewType("CUBEErrorCode", str)

ContainerImageTag = NewType("ContainerImageTag", str)

PipingId = NewType("PipingId", int)
PipelineId = NewType("PipelineId", int)


ParameterName = NewType("ParameterName", str)
ParameterType = Union[str, int, float, bool]

PipelineParameterId = NewType("ParameterLocalId", int)
PluginParameterId = NewType("ParameterGlobalId", int)
PluginInstanceId = NewType("PluginInstanceId", int)

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
NoteUrl = NewType("NoteUrl", str)
"""A feed's note."""
PluginParametersUrl = NewType("PluginParametersUrl", str)
TagsUrl = NewType("TagsUrl", str)
TaggingsUrl = NewType("TaggingsUrl", str)
CommentsUrl = NewType("CommentsUrl", str)
