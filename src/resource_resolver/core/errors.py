from __future__ import annotations

from typing import Any, List


class ResourceResolverError(Exception):
    """
    Encapsulates errors generated by the ResourceResolver class.
    """

    @classmethod
    def DuplicateKey(cls, key: str) -> ResourceResolverError:
        return cls(f"Cannot define key '{key}' since key already exists.")

    @classmethod
    def InvalidUrl(cls, url: str) -> ResourceResolverError:
        return cls(f"Url '{url}' is not valid.")

    @classmethod
    def ReadOnly(cls, location: Any) -> ResourceResolverError:
        return cls(f"Attempted to write to a read only resource at location"
                   f" {location}."
                   )

    @classmethod
    def UnsupportedGetAsFormat(cls, format: Any, GET_AS_FORMATS: List[str]):
        return cls(f"Invalid format '{format}' requested from get. "
                   f"Format must be one of [{', '.join(GET_AS_FORMATS)}].")

    @classmethod
    def UnsupportedProtocol(cls, location: Any) -> ResourceResolverError:
        return cls(f"The location '{location}' is not a supported. "
                   "Resolver must be passed a supported location.")

    @classmethod
    def UnsupportedWriteType(cls, t: Any) -> ResourceResolverError:
        return cls(f"Cannot write type '{type(t)}'. "
                   "Only string data is supported.")

    @classmethod
    def UndefinedResource(cls, key: str) -> ResourceResolverError:
        return cls(f"Resource '{key}' not defined.")
