""":mod:`door.utilities` defines the utilities."""

from collections.abc import Awaitable
from dataclasses import dataclass, field, InitVar
from enum import auto, Flag
from functools import partial
from multiprocessing import Value
from multiprocessing.shared_memory import SharedMemory
from pickle import dumps, loads
from types import BuiltinMethodType, MethodType
from typing import (
    Any,
    cast,
    ClassVar,
    Generic,
    Protocol,
    runtime_checkable,
    TypeVar,
)

_T = TypeVar('_T')


@runtime_checkable
class Counter(Protocol):
    """The protocol for counters."""

    def increment(self) -> None:
        """Increment.

        :return: ``None``.
        """
        pass  # pragma: no cover

    def decrement(self) -> None:
        """Decrement.

        :return: ``None``.
        """
        pass  # pragma: no cover

    def __bool__(self) -> bool:
        """Check the non-zero status.

        :return: The non-zero status.
        """
        pass  # pragma: no cover


@dataclass
class IntCounter(Counter):
    """The class for ``int`` counters.

    This class is designed to be used for asynchronous programming.
    """

    __value: int = field(default=0, init=False)

    def increment(self) -> None:
        self.__value += 1

    def decrement(self) -> None:
        self.__value -= 1

    def __bool__(self) -> bool:
        return bool(self.__value)


@dataclass
class ValueCounter(Counter):
    """The class for ``Value`` counters.

    This class is designed to be used for multiprocessing.
    """

    __value: Any = field(
        default_factory=partial(Value, 'Q', lock=False),
        init=False,
    )

    def increment(self) -> None:
        self.__value.value += 1

    def decrement(self) -> None:
        self.__value.value -= 1

    def __bool__(self) -> bool:
        return bool(self.__value.value)


@dataclass
class Handle(Generic[_T]):
    """The class for handles.

    All handles should be unlinked when no longer used by calling
    :meth:`Handle.unlink` only once across all processes.

    >>> handle = Handle([1, 2, 3])
    >>> handle.get()
    [1, 2, 3]
    >>> handle.set(3)
    >>> handle.get()
    3
    >>> handle.unlink()
    """

    NAME_MAX: ClassVar[int] = 255
    """The maximum size of the name."""
    resource: InitVar[_T]
    """The shared resource."""
    __name: str = field(init=False)

    def __post_init__(self, resource: _T) -> None:
        data = dumps(resource)
        shm_data = SharedMemory(create=True, size=len(data))
        shm_data.buf[:] = data
        shm_name = SharedMemory(create=True, size=self.NAME_MAX)
        shm_name.buf[:len(shm_data.name)] = shm_data.name.encode()
        self.__name = shm_name.name

        shm_data.close()
        shm_name.close()

    def get(self) -> _T:
        """Get the shared resource.

        :return: The shared resource.
        """
        shm_name = SharedMemory(self.__name)
        shm_data = SharedMemory(shm_name.buf.tobytes().rstrip(b'\0').decode())
        data = shm_data.buf.tobytes()

        shm_name.close()
        shm_data.close()

        return cast(_T, loads(data))

    def set(self, value: _T) -> None:
        """Set the shared resource.

        :param value: The new value.
        :return: ``None``.
        """
        data = dumps(value)
        shm_name = SharedMemory(self.__name)
        shm_data = SharedMemory(shm_name.buf.tobytes().rstrip(b'\0').decode())

        if shm_data.buf != data:
            if len(shm_data.buf) != len(data):
                shm_data.close()
                shm_data.unlink()

                shm_data = SharedMemory(create=True, size=len(data))
                shm_name.buf[:] = b'\0' * shm_name.size
                shm_name.buf[:len(shm_data.name)] = shm_data.name.encode()

            shm_data.buf[:] = data

        shm_name.close()
        shm_data.close()

    def unlink(self) -> None:
        """Unlink the shared resource.

        This must be called only once across all processes.

        :return: ``None``.
        """
        shm_name = SharedMemory(self.__name)
        shm_data = SharedMemory(shm_name.buf.tobytes().rstrip(b'\0').decode())

        shm_name.close()
        shm_name.unlink()
        shm_data.close()
        shm_data.unlink()


@dataclass
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
    resource_or_handle: InitVar[_T | Handle[_T]]
    """The resource or handle."""
    __mode: Mode
    __resource: _T = field(init=False)
    __handle: Handle[_T] | None = field(init=False)
    __status: bool = field(default=False, init=False)

    def __post_init__(self, resource_or_handle: _T | Handle[_T]) -> None:
        if isinstance(resource_or_handle, Handle):
            self.__handle = resource_or_handle
        else:
            self.__resource = resource_or_handle
            self.__handle = None

        self.open()

        self.__initialized = True

    def __repr__(self) -> str:
        return repr(self.__resource)

    def __eq__(self, other: object) -> bool:
        return self.__resource == other

    def __getattr__(self, name: str) -> Any:
        if not self.__initialized:
            return self.__getattribute__(name)

        try:
            value = self.__getattribute__(name)
        except AttributeError:
            if not self.__status or self.Mode.READ not in self.__mode:
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
            if not self.__status or self.Mode.WRITE not in self.__mode:
                raise ValueError('no write permission')

            setattr(self.__resource, name, value)
        else:
            super().__setattr__(name, value)

    def open(self) -> None:
        """Close.

        :return: ``None``.
        """
        if self.__handle is not None:
            self.__resource = self.__handle.get()

        self.__status = True

    def close(self) -> None:
        """Close.

        :return: ``None``.
        """
        if self.__handle is not None and self.Mode.WRITE in self.__mode:
            self.__handle.set(self.__resource)

        self.__status = False


async def await_if_awaitable(awaitable: Any) -> None:
    """Await if awaitable.

    :return: ``None``.
    """
    if isinstance(awaitable, Awaitable):
        await awaitable
