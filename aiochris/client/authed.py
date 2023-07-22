import abc
import os
from pathlib import Path
from typing import Optional, Generic, Callable, Sequence

import aiohttp
from async_property import async_cached_property

from aiochris.client.base import BaseChrisClient
from aiochris.client.base import L, CSelf
from aiochris.link import http
from aiochris.link.linked import deserialize_res
from aiochris.models.logged_in import Plugin, File, User, PluginInstance, Feed, PACSFile
from aiochris.models.public import ComputeResource
from aiochris.types import ChrisURL, Username, Password
from aiochris.errors import IncorrectLoginError, raise_for_status
from aiochris.util.search import Search, acollect
from aiochris.client.from_chrs import ChrsLogins


class AuthenticatedClient(BaseChrisClient[L, CSelf], Generic[L, CSelf], abc.ABC):
    """
    An authenticated ChRIS client.
    """

    @classmethod
    async def from_login(
        cls,
        url: str | ChrisURL,
        username: str | Username,
        password: str | Password,
        max_search_requests: int = 100,
        connector: Optional[aiohttp.TCPConnector] = None,
        connector_owner: bool = True,
    ) -> CSelf:
        """
        Get authentication token using username and password, then construct the client.

        See `aiochris.client.base.BaseChrisClient.new` for parameter documentation.
        """
        async with aiohttp.ClientSession(
            connector=connector, connector_owner=False
        ) as session:
            try:
                c = await cls.__from_login_with(
                    url=url,
                    username=username,
                    password=password,
                    max_search_requests=max_search_requests,
                    session=session,
                    connector_owner=connector_owner,
                )
            except BaseException as e:
                if connector is None:
                    await session.connector.close()
                raise e
        return c

    @classmethod
    async def __from_login_with(
        cls,
        url: str | ChrisURL,
        username: Username,
        password: Password,
        max_search_requests: int,
        session: aiohttp.ClientSession,
        connector_owner: bool,
    ) -> CSelf:
        """
        Get authentication token using the given session, and then construct the client.
        """
        payload = {"username": username, "password": password}
        login = await session.post(url + "auth-token/", json=payload)
        if login.status == 400:
            raise IncorrectLoginError(await login.text())
        await raise_for_status(login)
        data = await login.json()
        return await cls.from_token(
            url=url,
            token=data["token"],
            max_search_requests=max_search_requests,
            connector=session.connector,
            connector_owner=connector_owner,
        )

    @classmethod
    async def from_token(
        cls,
        url: str | ChrisURL,
        token: str,
        max_search_requests: int = 100,
        connector: Optional[aiohttp.TCPConnector] = None,
        connector_owner: Optional[bool] = True,
    ) -> CSelf:
        """
        Construct an authenticated client using the given token.

        See `aiochris.client.base.BaseChrisClient.new` for parameter documentation.
        """
        return await cls.new(
            url=url,
            max_search_requests=max_search_requests,
            connector=connector,
            connector_owner=connector_owner,
            session_modifier=cls.__curry_token(token),
        )

    @classmethod
    async def from_chrs(
        cls,
        url: Optional[str | ChrisURL] = None,
        username: Optional[str | Username] = None,
        max_search_requests: int = 100,
        connector: Optional[aiohttp.TCPConnector] = None,
        connector_owner: Optional[bool] = True,
        config_file: Path = Path("~/.config/chrs/login.toml"),
    ) -> CSelf:
        """
        Log in using [`chrs`](https://crates.io/crates/chrs).
        *ChRIS* logins can be saved with the `chrs login` command.

        In order to call this function, `aiochris` must be installed with the extras `from-chrs`.
        Using pip:

        ```shell
        pip install aiochris[chrs]
        ```

        Or using Poetry:

        ```shell
        poetry add -E chrs aiochris
        ```

        `from_chrs` makes it easy to use `aiochris` in Jupyter Notebook or IPython,
        especially since it saves you from having to write your password in a notebook
        that you want to share with others. Both Jupyter and IPython support top-level `await`.

        ```python
        from aiochris import ChrisClient, acollect

        chris = await ChrisClient.from_chrs()
        await acollect(chris.search_plugins())
        ```

        When `from_chrs` is called with no parameters, it uses the "preferred account"
        i.e. the most recently added account, the same _ChRIS_ account and server as
        `chrs` would when called without options. The "preferred account" can be changed
        by running `chrs switch`.
        """
        logins = ChrsLogins.load(config_file)
        if (t := logins.get_token_for(url, username)) is None:
            raise IncorrectLoginError("No chrs login found.")
        url, token = t
        return await cls.from_token(
            url=url,
            token=token,
            max_search_requests=max_search_requests,
            connector=connector,
            connector_owner=connector_owner,
        )

    @staticmethod
    def __curry_token(token: str) -> Callable[[aiohttp.ClientSession], None]:
        def add_token_to(session: aiohttp.ClientSession) -> None:
            session.headers.update({"Authorization": "Token " + token})

        return add_token_to

    # ============================================================
    # CUBE API methods
    # ============================================================

    @http.search(".")
    def search_feeds(self, **query) -> Search[Feed]:
        """
        Search for feeds.
        """
        ...

    @http.search("plugins")
    def search_plugins(self, **query) -> Search[Plugin]:
        """
        Search for plugins.
        """
        ...

    @http.search("plugin_instances")
    def plugin_instances(self, **query) -> Search[PluginInstance]:
        """
        Search for plugin instances.
        """
        ...

    async def upload_file(
        self, local_file: str | os.PathLike, upload_path: str
    ) -> File:
        """
        Upload a local file to *ChRIS*.

        .. warning:: Uses non-async code.
                     The file is read using non-async code.
                     Performance will suffer with large files and hard drives.
                     See [aiolibs/aiohttp#7174](https://github.com/aio-libs/aiohttp/issues/7174)

        Examples
        --------

        Upload a single file:

        ```python
        aiochris = await ChrisClient.from_login(
            username='chris',
            password='chris1234',
            url='https://cube.chrisproject.org/api/v1/'
        )
        file = await aiochris.upload_file("./my_data.dat", 'dir/my_data.dat')
        assert file.fname == 'aiochris/uploads/dir/my_data.dat'
        ```

        Upload (in parallel) all `*.txt` files in a directory
        `'incoming'` to `aiochris/uploads/big_folder`:

        ```python
        upload_jobs = (
            aiochris.upload_file(p, f'big_folder/{p}')
            for p in Path('incoming')
        )
        await asyncio.gather(upload_jobs)
        ```

        Parameters
        ----------
        local_file
            Path of an existing local file to upload.
        upload_path
            A subpath of `{username}/uploads/` where to upload the file to in *CUBE*
        """
        upload_path = await self._add_upload_prefix(upload_path)
        local_file = Path(local_file)
        with local_file.open("rb") as f:
            data = aiohttp.FormData()
            data.add_field("upload_path", upload_path)
            data.add_field("fname", f, filename=local_file.name)
            sent = self.s.post(self.collection_links.uploadedfiles, data=data)
            return await deserialize_res(
                sent, self, {"fname": local_file, "upload_path": upload_path}, File
            )

        # read_stream = _file_sender(local_file, chunk_size)
        # file_length = os.stat(local_file).st_size
        # return await self.upload_stream(read_stream, upload_path, str(local_file), file_length)

    # doesn't work: 411 Length Required
    # async def upload_stream(self, read_stream: AsyncIterable[bytes], upload_path: str, fname: str, length: int
    #                         ) -> File:
    #     """
    #     Stream a file upload to *ChRIS*. For a higher-level wrapper which accepts
    #     a path argument instead, see `upload`.
    #
    #     Parameters
    #     ----------
    #     read_stream
    #         bytes stream
    #     upload_path
    #         uploadedfiles path starting with `'{username}/uploads/`
    #     fname
    #         file name to use in the multipart POST request
    #     length
    #         content length
    #     """
    #     data = aiohttp.FormData()
    #     data.add_field('upload_path', upload_path)
    #     data.add_field('fname', read_stream, filename=fname)
    #     async with self.s.post(self.collection_links.uploadedfiles, data=data) as res:
    #         return serde.json.from_json(File, await res.text())
    #
    #     with aiohttp.MultipartWriter() as mpwriter:
    #         mpwriter.append_form({'upload_path': upload_path})
    #         mpwriter.append(read_stream, headers={
    #             'Content-Disposition': 'form-data; name="fname"; filename="value_goes_here"'
    #         })

    async def _add_upload_prefix(self, upload_path: str) -> str:
        upload_prefix = f"{await self.username()}/uploads/"
        if str(upload_path).startswith(upload_prefix):
            return upload_path
        return f"{upload_prefix}{upload_path}"

    @http.get("user")
    async def user(self) -> User:
        """Gets the user's information."""
        ...

    @async_cached_property
    async def _user(self) -> User:
        return await self.user()

    async def username(self) -> Username:
        """
        Gets the username. In contrast to `self.user`, this method will use a cached API call.
        """
        user = await self._user  # this is weird
        return user.username

    @http.search("compute_resources")
    def search_compute_resources(self, **query) -> Search[ComputeResource]:
        """
        Search for existing compute resources.

        See also
        --------
        `get_all_compute_resources` :
        """
        ...

    async def get_all_compute_resources(self) -> Sequence[ComputeResource]:
        """
        Get all compute resources.

        This method exists for convenience.
        The number of compute resources of a CUBE is typically small so it's ok.

        See also
        --------
        `search_compute_resources` :
        """
        return await acollect(self.search_compute_resources())

    @http.search("pacsfiles")
    def search_pacsfiles(self, **query) -> Search[PACSFile]:
        """
        Search for PACS files.
        """
        ...


# async def _file_sender(file_name: str | os.PathLike, chunk_size: int):
#     """
#     Stream the reading of a file using an asynchronous generator.
#
#     https://docs.aiohttp.org/en/stable/client_quickstart.html#streaming-uploads
#     """
#     async with aiofiles.open(file_name, 'rb') as f:
#         chunk = await f.read(chunk_size)
#         while chunk:
#             yield chunk
#             chunk = await f.read(chunk_size)
