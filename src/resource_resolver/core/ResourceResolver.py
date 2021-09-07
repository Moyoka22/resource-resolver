from __future__ import annotations

from io import StringIO
from pathlib import Path
from typing import Dict, IO, Literal, Optional, Union, overload

from .errors import ResourceResolverError
from .ResourceProxy import ResourceProxy

instance = None


class ResourceResolver:
    """Resolves resources by name. Resources must be stored and retrieved
    as strings.

    Currently supported formats for resource:
    - IO[str]: Any object of type IO which returns a string (a file like object).
    - Path: Any subclass of pathlib.Path.
    - file url: Matches ^file:///.* .
    """

    def __init__(self):
        self._resource_map: Dict[str, ResourceProxy] = {}

    @staticmethod
    def get_instance() -> ResourceResolver:
        global instance
        if not instance:
            instance = ResourceResolver()
        return instance

    def clear(self):
        """Removes all resources from the resolver."""
        self._resource_map.clear()

    def has(self, key: str) -> bool:
        """Returns true if the key is defined in the resolver."""
        return self.__contains__(key)

    @overload
    def get(self, key: str, as_a: Literal['str']) -> str:
        ...
    @overload
    def get(self, key: str, as_a: Literal['buffer']) -> StringIO:
        ...
    @overload
    def get(self, key: str, as_a: Literal['file_handle']) -> IO[str]:
        ...
    @overload
    def get(self, key: str) -> str:
        ...
    def get(self, key: str, as_a: str = 'str'):
        """Return the requested resource as a string or string buffer."""

        if not key in self._resource_map:
            raise ResourceResolverError.UndefinedResource(key=key)
        proxy = self._resource_map[key]
        return proxy.get(as_a=as_a)

    def define(self, key: str,
               location: Optional[Union[str, IO[str], Path]] = None,
               overwrite=False,
               read_only=False,
               **kwargs) -> None:
        """Defines a resource url for a given key.

        :param key: The name of the resource which is being defined.
        :param location: A location from an attempt will be made to load the
        resource. If not supplied, an empty, in-memory buffer is created.
        :param overwrite: Required to be true if defining a resource with an
        existing key; if not true, an error will be thrown on attempted
        redefinition.
        :param read_only: Can be used to specify a resource is read-only.
        If read_only is passed as true, any attempts 
        to write to the resource will throw an error.

        :returns: None
        """
        if key in self._resource_map and not overwrite:
            raise ResourceResolverError.DuplicateKey(key=key)
        if not location:
            location = f'tmp://{key}'
        self._resource_map[key] = self._create_resource_io(location,
                                                            read_only,
                                                           **kwargs)

    def save(self, key: str, data: Union[str, IO[str]]) -> None:
        """Saves the string or string buffer argument passed
        to the given resource.
        """
        if not key in self._resource_map:
            raise ResourceResolverError.UndefinedResource(key=key)

        resource_io = self._resource_map[key]

        resource_io.put(data)

    def _create_resource_io(self, location: Union[str, IO[str], Path],
                            read_only: bool,
                            **kwargs) -> ResourceProxy:
        return ResourceProxy(location, read_only, **kwargs)

    def __contains__(self, key: str) -> bool:
        return key in self._resource_map
    
    def __getitem__(self, key: str) -> IO[str]:
        return self.get(key, as_a='file_handle')
       
        


def get_resource_resolver() -> ResourceResolver:
    """Returns a singleton instance of the resource resolver."""
    return ResourceResolver.get_instance()
