""":mod:`door.doors` defines the doors."""

from abc import ABC
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager, closing, contextmanager
from dataclasses import dataclass, field
from typing import cast, Generic, TypeVar

from door.primitives import Acquirable, SAcquirable, SWaitable, Waitable
from door.utilities import await_if_awaitable, Handle, Proxy

_T = TypeVar('_T')


@dataclass
class Door(Generic[_T], ABC):
    """The abstract base class for doors.

    This class is designed to be used for threading, asynchronous
    programming, and multiprocessing.
    """

    _resource_or_handle: _T | Handle[_T]

    def _setup(self, mode: Proxy.Mode) -> Proxy[_T]:
        return Proxy(self._resource_or_handle, mode)

    def _close(self) -> None:
        pass

    def _open(self) -> None:
        pass


@dataclass
class AcquirableDoor(Door[_T]):
    """The class for acquirable doors.

    This class is designed to be used for threading and multiprocessing.

    The door is initialized with the resource and corresponding
    primitive.

    The door can give access to the resource based on the desired
    operation.  When the user attempts to access the resource in a
    forbidden way or after its access is expired, an exception will
    be raised.

    >>> @dataclass
    ... class Resource:
    ...     key: str = 'value'
    ...
    >>> resource = Resource()
    >>> resource
    Resource(key='value')
    >>> resource.key
    'value'

    >>> door = AcquirableDoor(resource)
    >>> with door() as proxy:
    ...     proxy.key
    ...     proxy.key = 'VALUE'
    ...     proxy.key
    ...
    'value'
    'VALUE'

    >>> proxy.key
    Traceback (most recent call last):
        ...
    ValueError: no read permission
    >>> proxy.key = 'value'
    Traceback (most recent call last):
        ...
    ValueError: no write permission

    >>> resource
    Resource(key='VALUE')
    >>> resource.key
    'VALUE'
    """

    _primitive: Acquirable

    @contextmanager
    def __call__(self) -> Iterator[_T]:
        """Return the context manager for the resource.

        After the resource is released, the resource becomes
        inaccessible.

        :return: The context manager for the resource.
        """
        self._primitive.acquire()

        try:
            proxy = self._setup(Proxy.Mode.READ | Proxy.Mode.WRITE)

            with closing(proxy):
                yield cast(_T, proxy)
        finally:
            self._primitive.release()


@dataclass
class AsyncAcquirableDoor(Door[_T]):
    """The class for asynchronous acquirable doors.

    This class is designed to be used for asynchronous prgramming.

    The door is initialized with the resource and corresponding
    primitive.

    The door can give access to the resource based on the desired
    operation. When the user attempts to access the resource in a
    forbidden way or after its access is expired, an exception will be
    raised.
    """

    _primitive: Acquirable

    @asynccontextmanager
    async def __call__(self) -> AsyncIterator[_T]:
        """Return the asynchronous context manager for the resource.

        After the resource is released, the resource becomes
        inaccessible.

        :return: The context manager for the resource.
        """
        await await_if_awaitable(self._primitive.acquire())

        try:
            proxy = self._setup(Proxy.Mode.READ | Proxy.Mode.WRITE)

            with closing(proxy):
                yield cast(_T, proxy)
        finally:
            await await_if_awaitable(self._primitive.release())


@dataclass
class WaitableDoor(AcquirableDoor[_T]):
    """The class for waitable doors.

    This class is designed to be used for threading and multiprocessing.

    The door is initialized with the resource and corresponding
    primitive.

    The door can give access to the resource based on the desired
    operation.  When the user attempts to access the resource in a
    forbidden way or after its access is expired, an exception will
    be raised.
    """

    _primitive: Waitable

    def wait(self) -> None:
        """Wait.

        :return: ``None``.
        """
        self._close()
        self._primitive.wait()
        self._open()

    def notify(self) -> None:
        """Notify one.

        :return: ``None``.
        """
        self._close()
        self._primitive.notify()
        self._open()

    def notify_all(self) -> None:
        """Notify all.

        :return: ``None``.
        """
        self._close()
        self._primitive.notify_all()
        self._open()


@dataclass
class AsyncWaitableDoor(AsyncAcquirableDoor[_T]):
    """The class for asynchronous waitable doors.

    This class is designed to be used for asynchronous prgramming.

    The door is initialized with the resource and corresponding
    primitive.

    The door can give access to the resource based on the desired
    operation. When the user attempts to access the resource in a
    forbidden way or after its access is expired, an exception will be
    raised.
    """

    _primitive: Waitable

    async def wait(self) -> None:
        """Wait.

        :return: ``None``.
        """
        self._close()
        await await_if_awaitable(self._primitive.wait())
        self._open()

    async def notify(self) -> None:
        """Notify one.

        :return: ``None``.
        """
        self._close()
        await await_if_awaitable(self._primitive.notify())
        self._open()

    async def notify_all(self) -> None:
        """Notify all.

        :return: ``None``.
        """
        self._close()
        await await_if_awaitable(self._primitive.notify_all())
        self._open()


@dataclass
class SAcquirableDoor(Door[_T]):
    """The class for shared acquirable doors.

    This class is designed to be used for threading and multiprocessing.

    The door is initialized with the resource and corresponding
    primitive.

    The door can give access to the resource based on the desired
    operation.  When the user attempts to access the resource in a
    forbidden way or after its access is expired, an exception will
    be raised.

    >>> @dataclass
    ... class Resource:
    ...     key: str = 'value'
    ...
    >>> resource = Resource()
    >>> resource
    Resource(key='value')
    >>> resource.key
    'value'

    >>> door = SAcquirableDoor(resource)
    >>> with door.read() as proxy:
    ...     proxy.key
    ...
    'value'

    >>> with door.read() as proxy:
    ...     proxy.key = 'VALUE'
    ...
    Traceback (most recent call last):
        ...
    ValueError: no write permission

    >>> with door.write() as proxy:
    ...     proxy.key
    ...     proxy.key = 'VALUE'
    ...     proxy.key
    ...
    'value'
    'VALUE'

    >>> proxy.key
    Traceback (most recent call last):
        ...
    ValueError: no read permission
    >>> proxy.key = 'value'
    Traceback (most recent call last):
        ...
    ValueError: no write permission

    >>> resource
    Resource(key='VALUE')
    >>> resource.key
    'VALUE'
    """

    _primitive: SAcquirable

    @contextmanager
    def read(self) -> Iterator[_T]:
        """Return the context manager for the resource in read mode.

        After the resource is released, the resource becomes
        inaccessible.

        :return: The context manager for the resource.
        """
        self._primitive.acquire_read()

        try:
            proxy = self._setup(Proxy.Mode.READ)

            with closing(proxy):
                yield cast(_T, proxy)
        finally:
            self._primitive.release_read()

    @contextmanager
    def write(self) -> Iterator[_T]:
        """Return the context manager for the resource in write (and
        read) mode.

        After the resource is released, the resource becomes
        inaccessible.

        :return: The context manager for the resource.
        """
        self._primitive.acquire_write()

        try:
            proxy = self._setup(Proxy.Mode.READ | Proxy.Mode.WRITE)

            with closing(proxy):
                yield cast(_T, proxy)
        finally:
            self._primitive.release_write()


@dataclass
class AsyncSAcquirableDoor(Door[_T]):
    """The class for asynchronous shared acquirable doors.

    This class is designed to be used for asynchronous prgramming.

    The door is initialized with the resource and corresponding
    primitive.

    The door can give access to the resource based on the desired
    operation. When the user attempts to access the resource in a
    forbidden way or after its access is expired, an exception will be
    raised.
    """

    _primitive: SAcquirable

    @asynccontextmanager
    async def read(self) -> AsyncIterator[_T]:
        """Return the asynchronous context manager for the resource in
        read mode.

        After the resource is released, the resource becomes
        inaccessible.

        :return: The context manager for the resource.
        """
        await await_if_awaitable(self._primitive.acquire_read())

        try:
            proxy = self._setup(Proxy.Mode.READ)

            with closing(proxy):
                yield cast(_T, proxy)
        finally:
            await await_if_awaitable(self._primitive.release_read())

    @asynccontextmanager
    async def write(self) -> AsyncIterator[_T]:
        """Return the asynchronous context manager for the resource in
        write (and read) mode.

        After the resource is released, the resource becomes
        inaccessible.

        :return: The context manager for the resource.
        """
        await await_if_awaitable(self._primitive.acquire_write())

        try:
            proxy = self._setup(Proxy.Mode.READ | Proxy.Mode.WRITE)

            with closing(proxy):
                yield cast(_T, proxy)
        finally:
            await await_if_awaitable(self._primitive.release_write())


@dataclass
class SWaitableDoor(SAcquirableDoor[_T]):
    """The class for shared waitable doors.

    This class is designed to be used for threading and multiprocessing.

    The door is initialized with the resource and corresponding
    primitive.

    The door can give access to the resource based on the desired
    operation.  When the user attempts to access the resource in a
    forbidden way or after its access is expired, an exception will
    be raised.
    """

    _primitive: SWaitable

    def wait_read(self) -> None:
        """Wait for reading.

        :return: ``None``.
        """
        self._close()
        self._primitive.wait_read()
        self._open()

    def notify_read(self) -> None:
        """Notify one for reading.

        :return: ``None``.
        """
        self._close()
        self._primitive.notify_read()
        self._open()

    def notify_all_read(self) -> None:
        """Notify all for reading.

        :return: ``None``.
        """
        self._close()
        self._primitive.notify_all_read()
        self._open()

    def wait_write(self) -> None:
        """Wait for writing.

        :return: ``None``.
        """
        self._close()
        self._primitive.wait_write()
        self._open()

    def notify_write(self) -> None:
        """Notify one for writing.

        :return: ``None``.
        """
        self._close()
        self._primitive.notify_write()
        self._open()

    def notify_all_write(self) -> None:
        """Notify all for writing.

        :return: ``None``.
        """
        self._close()
        self._primitive.notify_all_write()
        self._open()


@dataclass
class AsyncSWaitableDoor(AsyncSAcquirableDoor[_T]):
    """The class for asynchronous shared waitable doors.

    This class is designed to be used for asynchronous prgramming.

    The door is initialized with the resource and corresponding
    primitive.

    The door can give access to the resource based on the desired
    operation. When the user attempts to access the resource in a
    forbidden way or after its access is expired, an exception will be
    raised.
    """

    _primitive: SWaitable

    async def wait_read(self) -> None:
        """Wait for reading.

        :return: ``None``.
        """
        self._close()
        await await_if_awaitable(self._primitive.wait_read())
        self._open()

    async def notify_read(self) -> None:
        """Notify one for reading.

        :return: ``None``.
        """
        self._close()
        await await_if_awaitable(self._primitive.notify_read())
        self._open()

    async def notify_all_read(self) -> None:
        """Notify all for reading.

        :return: ``None``.
        """
        self._close()
        await await_if_awaitable(self._primitive.notify_all_read())
        self._open()

    async def wait_write(self) -> None:
        """Wait for writing.

        :return: ``None``.
        """
        self._close()
        await await_if_awaitable(self._primitive.wait_write())
        self._open()

    async def notify_write(self) -> None:
        """Notify one for writing.

        :return: ``None``.
        """
        self._close()
        await await_if_awaitable(self._primitive.notify_write())
        self._open()

    async def notify_all_write(self) -> None:
        """Notify all for writing.

        :return: ``None``.
        """
        self._close()
        await await_if_awaitable(self._primitive.notify_all_write())
        self._open()


class UnhandledDoor(Door[_T], ABC):
    """The abstract base class for unhandled doors.

    This class is designed to be used for threading and asynchronous
    prgramming.
    """

    def __post_init__(self) -> None:
        if isinstance(self._resource_or_handle, Handle):
            raise ValueError('handle used')


class HandledDoor(Door[_T], ABC):
    """The abstract base class for handled doors.

    This class is designed to be used for multiprocessing.
    """

    _proxy: Proxy[_T] = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self._resource_or_handle, Handle):
            raise ValueError('handle not used')

    def _setup(self, mode: Proxy.Mode) -> Proxy[_T]:
        self._proxy = super()._setup(mode)

        return self._proxy

    def _close(self) -> None:
        self._proxy.close()

    def _open(self) -> None:
        self._proxy.open()
