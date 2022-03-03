from __future__ import annotations

import logging
import re
import shutil
import tempfile
from abc import ABCMeta, abstractmethod, abstractstaticmethod
from io import TextIOBase
from pathlib import Path
from typing import Any, IO, List, Optional, Type, Union, cast
from weakref import finalize, proxy

logger = logging.getLogger(__name__)


class ManagerRegistry:
    _Managers: List[Type[ResourceManagerBase]] = []

    @staticmethod
    def register_manager(manager: Type[ResourceManagerBase]):
        """
        Registers a manager in the manager registry.
        """
        logger.debug(f'Registering manager {manager}.')
        ManagerRegistry._Managers.append(manager)

    @staticmethod
    def get_manager(location: Any) -> Optional[Type[ResourceManagerBase]]:
        """
        Retrieves the appropriate manager for a location.

        Calls the test method of each Manager in an effort to locate an
        appropriate manager for an object.
        """
        if issubclass(type(location), TextIOBase):
            location = cast(IO[str], location)
            return TempManager
        for Manager in ManagerRegistry._Managers:
            if Manager.test(location):
                return Manager
        logger.warning(
            f'Location {location} failed test for all managers '
            f'in {[ klass.__name__ for klass in ManagerRegistry._Managers]}.')
        return None


class ResourceManagerMeta(ABCMeta):
    """
    Implements auto-registration of ResourceManagerBase subsclasses into the 
    manager registry.
    """

    def __init__(self, name, bases, namespace):
        if not name == 'ResourceManagerBase':
            ManagerRegistry.register_manager(self)  # type: ignore


class ResourceManagerBase(metaclass=ResourceManagerMeta):

    def __init__(self, location: Any):
        self._finalizer = finalize(self, self.close)
        ...

    @abstractstaticmethod
    def test(location: Any) -> bool:
        """
        Returns true if the location defines a locatinon which this manager
        can handle.
        """
        ...

    @abstractmethod
    def put(self, data: IO[str]) -> None:
        """
        Overwrites the current data stored at the location with the supplied
         data.
        """
        ...

    @abstractmethod
    def append(self, data: IO[str]) -> None:
        """
        Appends the supplied data to the current data stored at the location.
        """
        ...

    @abstractmethod
    def get(self) -> IO[str]:
        """
        Returns a stream which can be used to get the data stored at the
        location.
        """
        ...

    @abstractmethod
    def close(self) -> None:
        """
        Performs any shutdown functionality required to close the stream from
        the location.
        """
        ...


class FileManager(ResourceManagerBase):
    """
    Implements management of a file resource.
    """

    def __init__(self, location: Union[str, Path]):
        super().__init__(location)
        if issubclass(type(location), Path):
            self._path = cast(Path, location)
        else:
            url = cast(str, location)
            self._url = url[7:]  # Removes file:// from path
            self._path = Path(self._url)

        self._fp = self._path.open(mode='a+', encoding='utf-8')

    @staticmethod
    def test(location: Any) -> bool:
        if isinstance(location, Path):
            return True

        if not isinstance(location, str):
            return False

        url = cast(str, location)
        pattern = r'^file://'
        match = re.match(pattern, url)

        return bool(match)

    def put(self, data: IO[str]) -> None:
        self._fp.seek(0, 0)
        data.seek(0, 0)
        self._fp.truncate()
        shutil.copyfileobj(data, self._fp)

    def append(self, data: IO[str]) -> None:
        data.seek(0, 0)
        shutil.copyfileobj(data, self._fp)

    def get(self) -> IO[str]:
        self._fp.seek(0, 0)
        return proxy(self._fp)

    def close(self):
        try:
            self._fp.close()
        except Exception as e:
            logging.exception(e)


class TempManager(ResourceManagerBase):
    """
    Implements management of a temporary resource. The backing IO for a 
    temporary resource is not guaranteed to be fixed.
    """

    def __init__(self, location: Any):
        super().__init__(location)
        self._fp = tempfile.TemporaryFile(mode='w+', encoding='utf-8')

        if issubclass(type(location), TextIOBase):
            location.seek(0, 0)
            shutil.copyfileobj(location, self._fp)

    @staticmethod
    def test(location: Any) -> bool:
        if not isinstance(location, str):
            return False

        url = cast(str, location)
        pattern = r'^tmp://'
        match = re.match(pattern, url)

        return bool(match)

    def put(self, data: IO[str]) -> None:
        self._fp.seek(0, 0)
        data.seek(0, 0)
        self._fp.truncate()
        shutil.copyfileobj(data, self._fp)

    def append(self, data: IO[str]) -> None:
        data.seek(0, 0)
        shutil.copyfileobj(data, self._fp)

    def get(self) -> IO[str]:
        self._fp.seek(0, 0)
        return proxy(self._fp)

    def close(self):
        try:
            self._fp.close()
        except Exception as e:
            logging.exception(e)
