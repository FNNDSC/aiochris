"""
Subclasses of classes from `aiochris.models.data` which are returned
from an `aiochris.client.authed.AuthenticatedClient`.
These classes may have read-write functionality on the *ChRIS* API.
"""
import asyncio
import time
from dataclasses import dataclass
from typing import Optional, Sequence

from serde import deserialize

from aiochris.link import http
from aiochris.link.linked import LinkedModel
from aiochris.models.data import PluginInstanceData, FeedData, UserData, FeedNoteData
from aiochris.enums import PluginType, Status
from aiochris.models.public import PublicPlugin
from aiochris.types import *


@deserialize
@dataclass(frozen=True)
class User(UserData, LinkedModel):
    pass  # TODO change_email, change_password


@deserialize
@dataclass(frozen=True)
class File(LinkedModel):
    """
    A file in CUBE.
    """

    url: str
    fname: FileFname
    fsize: int
    file_resource: FileResourceUrl

    @property
    def parent(self) -> str:
        """
        Get the parent (directory) of a file.

        Examples
        --------

        ```python
        assert file.fname == 'chris/feed_4/pl-dircopy_7/data/hello-world.txt'
        assert file.parent == 'chris/feed_4/pl-dircopy_7/data'
        ```
        """
        split = self.fname.split("/")
        if len(split) <= 1:
            return self.fname
        return "/".join(split[:-1])

    # TODO download methods


@deserialize
@dataclass(frozen=True)
class PACSFile(File):
    """
    A file from a PACS server which was pushed into ChRIS.
    A PACSFile is usually a DICOM file.

    See https://github.com/FNNDSC/ChRIS_ultron_backEnd/blob/a1bf499144df79622eb3f8a459cdb80d8e34cb04/chris_backend/pacsfiles/models.py#L16-L33
    """

    PatientID: str
    PatientName: str
    PatientBirthDate: str
    PatientAge: int
    PatientSex: str
    StudyDate: str  # TODO deserialize
    AccessionNumber: str
    Modality: str
    ProtocolName: str
    StudyInstanceUID: str
    StudyDescription: str
    SeriesInstanceUID: str
    SeriesDescription: str
    pacs_identifier: str


@deserialize
@dataclass(frozen=True)
class PluginInstance(PluginInstanceData):
    @http.get("feed")
    async def get_feed(self) -> "Feed":
        """Get the feed this plugin instance belongs to."""
        ...

    @http.put("url")
    async def get(self) -> "PluginInstance":
        """
        Get this plugin's state (again).
        """
        ...

    @http.put("url")
    async def set(
        self, title: Optional[str] = None, status: Optional[str] = None
    ) -> "PluginInstance":
        """
        Set the title or status of this plugin instance.
        """
        ...

    @http.delete("url")
    async def delete(self) -> None:
        """Delete this plugin instance."""
        ...

    async def wait(
        self,
        status: Status
        | Sequence[Status] = (
            Status.finishedSuccessfully,
            Status.finishedWithError,
            Status.cancelled,
        ),
        timeout: float = 300,
        interval: float = 5,
    ) -> tuple[float, "PluginInstance"]:
        """
        Wait until this plugin instance finishes (or some other desired status).

        Parameters
        ----------
        status
            Statuses to wait for
        timeout
            Number of seconds to wait for before giving up
        interval
            Number of seconds to wait between checking on status

        Returns
        -------
        Returns the number of seconds elapsed and the last state of the plugin instance.
        This function will return for one of two reasons: either the plugin instance finished,
        or this function timed out. Make sure you check the plugin instance's final status!
        """
        if status is Status:
            status = (status,)
        if self.status in status:
            return 0.0, self
        timeout_ns = timeout * 1e9
        start = time.monotonic_ns()
        while (cur := await self.get()).status not in status:
            elapsed = time.monotonic_ns() - start
            if elapsed > timeout_ns:
                return elapsed / 1e9, cur
            await asyncio.sleep(interval)
        return (time.monotonic_ns() - start) / 1e9, cur


@deserialize
@dataclass(frozen=True)
class FeedNote(FeedNoteData):
    @http.get("feed")
    async def get_feed(self) -> "Feed":
        """Get the feed this note belongs to."""
        ...

    @http.put("url")
    async def set(
        self, title: Optional[str] = None, content: Optional[str] = None
    ) -> "FeedNote":
        """Change this note."""
        ...


@deserialize
@dataclass(frozen=True)
class Feed(FeedData):
    """
    A feed of a logged in user.
    """

    @http.put("url")
    async def set(
        self, name: Optional[str] = None, owner: Optional[str | Username] = None
    ) -> "Feed":
        """
        Change the name or the owner of this feed.

        Parameters
        ----------
        name
            new name for this feed
        owner
            new owner for this feed
        """
        ...

    @http.get("note")
    async def get_note(self) -> FeedNote:
        ...


@deserialize
@dataclass(frozen=True)
class Plugin(PublicPlugin):
    """
    A ChRIS plugin. Create a plugin instance of this plugin to run it.
    """

    instances: ApiUrl

    @http.post("instances")
    async def _create_instance_raw(self, **kwargs) -> PluginInstance:
        ...

    async def create_instance(
        self, previous: Optional[PluginInstance] = None, **kwargs
    ) -> PluginInstance:
        """
        Create a plugin instance, i.e. "run" this plugin.

        Parameters common to all plugins are described below.
        Not all valid parameters are listed, since each plugin's parameters are different.
        Some plugins have required parameters too.
        To list all possible parameters, make a GET request to the specific plugin's instances link.

        Parameters
        ----------
        previous: chris.models.data.PluginInstanceData
            Previous plugin instance
        previous_id: int
            Previous plugin instance ID number (conflicts with `previous`)
        compute_resource_name: Optional[str]
            Name of compute resource to use
        memory_limit: Optional[str]
            Memory limit. Format is *x*Mi or *x*Gi where x is an integer.
        cpu_limit: Optional[str]
            CPU limit. Format is *x*m for *x* is an integer in millicores.
        gpu_limit: Optional[int]
            GPU limit.
        """
        if previous is not None:
            if "previous_id" in kwargs:
                raise ValueError("Cannot give both previous and previous_id.")
            if not isinstance(previous, PluginInstance):
                raise TypeError(f"{previous} is not a PluginInstance")
            kwargs["previous_id"] = previous.id
        if self.plugin_type is PluginType.fs:
            if "previous_id" in kwargs:
                raise ValueError(
                    "Cannot create plugin instance of a fs-type plugin with a previous plugin instance."
                )
        elif "previous_id" not in kwargs:
            raise ValueError(
                f'Plugin type is "{self.plugin_type.value}" so previous is a required parameter.'
            )
        return await self._create_instance_raw(**kwargs)
