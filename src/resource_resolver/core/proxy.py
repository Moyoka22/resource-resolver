import logging
import shutil
from io import StringIO, TextIOBase
from pathlib import Path
import tempfile
from typing import IO, Literal, Union, cast

from .errors import ResourceResolverError
from .managers import ManagerRegistry


class ResourceProxy:
    """
    A proxy object for resources. The proxy object provides a consistent 
    interface for resources which is independent of the type of resource which
    it is backed by.
    """
    GET_AS_FORMATS = ['str', 'buffer', 'file_handle']

    def __init__(self, location: Union[str, IO[str], Path],
                 read_only=False,
                 **kwargs):
        self._location = location
        self._read_only = read_only
        Manager = ManagerRegistry.get_manager(location)
        if not Manager:
            location = repr(location)
            raise ResourceResolverError.UnsupportedProtocol(location)
        self._manager = Manager(location, **kwargs)

    def put(self, data: Union[str, IO[str]]) -> None:
        """
        Overwrites the specified resource with the supplied data.

        Data supplied must be in the form of a raw string or a text stream.
        If the resource has previously been indicated to be read-only, a 
        ResourceResolverError will be thrown upon write attempts.
        """
        if self.is_read_only:
            raise ResourceResolverError.ReadOnly(self._location)
        if not (isinstance(data, str) or isinstance(data, TextIOBase)):
            raise ResourceResolverError.UnsupportedWriteType(data)

        if isinstance(data, str):
            data = cast(str, data)
            data = self._produce_stream_from_data(data)

        data = cast(IO[str], data)
        self._manager.put(data)

    def get(self, as_a: str) -> Union[str, IO[str], StringIO]:
        """
        Overloaded function which retrieves the resource content. The 
        contents can be returned as a raw string, a text IO buffer, or a
        text stream.
        """
        supported_formats = self.GET_AS_FORMATS
        if as_a not in supported_formats:
            raise ResourceResolverError.\
                UnsupportedGetAsFormat(as_a,
                                       supported_formats)
        if as_a == 'str':
            return self._manager.get().read()
        elif as_a == 'buffer':
            buffer = StringIO()
            data = self._manager.get()
            shutil.copyfileobj(data, buffer)
            buffer.seek(0, 0)
            return buffer
        else:
            as_a = cast(Literal['file_handle'], as_a)
            return self._manager.get()

    @property
    def is_read_only(self) -> bool:
        return self._read_only

    def _produce_stream_from_data(self, data: str) -> IO[str]:
        """
        Attempts to wrap a raw string in a buffer. If memory allocation fails 
        then a text stream is returned.
        """
        try:
            buffer: IO[str] = StringIO(data)
            buffer.seek(0, 0)
        except MemoryError:
            logging.warning('Failed to allocation memory for string. '
                            f'String has length {len(data)}.')
            fp = tempfile.TemporaryFile(mode="w+")
            fp.write(data)
            fp.seek(0, 0)
            return fp

        else:
            return buffer
