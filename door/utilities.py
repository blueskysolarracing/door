""":mod:`door.utilities` defines the utilities."""

from collections.abc import Awaitable
from dataclasses import dataclass
from enum import auto, Flag
from functools import partial
from types import BuiltinMethodType, MethodType
from typing import Any, Generic, TypeVar

_T = TypeVar('_T')


@dataclass(repr=False)
class Proxy(Generic[_T]):
    """The class for resource proxies.

    >>> @dataclass
    ... class Resource:
    ...     key: Any = 'value'
    ...
    >>> resource = Resource()
    >>> resource
    Resource(key='value')
    >>> resource.key
    'value'

    >>> proxy = Proxy(resource, Proxy.Mode.READ)
    >>> proxy.key
    'value'
    >>> proxy.key = 'VALUE'
    Traceback (most recent call last):
        ...
    ValueError: no write permission
    >>> proxy.close()

    >>> proxy = Proxy(resource, Proxy.Mode.WRITE)
    >>> proxy.key = 'VALUE'
    >>> proxy.key
    Traceback (most recent call last):
        ...
    ValueError: no read permission
    >>> proxy.close()

    >>> proxy = Proxy(resource, Proxy.Mode.READ | Proxy.Mode.WRITE)
    >>> proxy.key
    'VALUE'
    >>> proxy.key = 'value'
    >>> proxy.key
    'value'
    >>> proxy.close()

    >>> proxy.key
    Traceback (most recent call last):
        ...
    ValueError: no read permission
    >>> proxy.key = 'VALUE'
    Traceback (most recent call last):
        ...
    ValueError: no write permission

    >>> resource
    Resource(key='value')
    >>> resource.key
    'value'
    """

    class Mode(Flag):
        """The flag for modes."""

        READ = auto()
        WRITE = auto()

    __initialized = False
    __resource: _T
    __mode: Mode

    def __post_init__(self) -> None:
        self.__initialized = True

    def __getattr__(self, name: str) -> Any:
        try:
            value = self.__getattribute__(name)
        except AttributeError:
            if self.Mode.READ not in self.__mode:
                raise ValueError('no read permission')

            value = getattr(self.__resource, name)

        if isinstance(value, MethodType):
            value = partial(value.__func__, self)
        elif isinstance(value, BuiltinMethodType):
            raise ValueError('builtin method type not supported')

        return value

    def __setattr__(self, name: str, value: Any) -> None:
        if not self.__initialized:
            super().__setattr__(name, value)

        try:
            self.__getattribute__(name)
        except AttributeError:
            if self.Mode.WRITE not in self.__mode:
                raise ValueError('no write permission')

            setattr(self.__resource, name, value)
        else:
            super().__setattr__(name, value)

    def close(self) -> None:
        """Close the resource.

        The resource becomes inaccessible.

        :return: ``None``.
        """
        self.__mode = self.Mode(0)


async def await_if_awaitable(awaitable: Any) -> None:
    if isinstance(awaitable, Awaitable):
        await awaitable
