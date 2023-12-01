""":mod:`door.doors` defines the doors."""

from collections.abc import AsyncIterator, Callable, Iterator
from contextlib import asynccontextmanager, closing, contextmanager
from dataclasses import dataclass
from typing import Any, cast, Generic, TypeVar

from door.primitives import Acquirable, SAcquirable, SWaitable, Waitable
from door.utilities import Proxy, await_if_awaitable

_T = TypeVar('_T')


@dataclass
class AcquirableDoor(Generic[_T]):
    """The class for acquirable doors.

    The door is initialized with the resource and corresponding
    primitive.

    The door can give access to the resource based on the desired
    operation.  When the user attempts to access the resource in a
    forbidden way or after its access is expired, an exception will
    be raised.

    >>> @dataclass
    ... class Resource:
    ...     key: Any = 'value'
    ...
    >>> resource = Resource()
    >>> resource
    Resource(key='value')
    >>> resource.key
    'value'

    >>> from threading import Lock
    >>> door = AcquirableDoor(resource, Lock())

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

    resource: _T
    """The resource to be accessed."""
    primitive: Acquirable
    """The synchronization primitive."""

    @contextmanager
    def __call__(self) -> Iterator[_T]:
        """Return the context manager for the resource.

        After the resource is released, the resource becomes
        inaccessible.

        :return: The context manager for the resource.
        """
        self.primitive.acquire()

        try:
            resource = Proxy(self.resource, Proxy.Mode.READ | Proxy.Mode.WRITE)

            with closing(resource):
                yield cast(_T, resource)
        finally:
            self.primitive.release()


@dataclass
class AsyncAcquirableDoor(Generic[_T]):
    """The class for asynchronous acquirable doors.

    This class is designed to be used for asynchronous prgramming.

    The door is initialized with the resource and corresponding
    primitive.

    The door can give access to the resource based on the desired
    operation. When the user attempts to access the resource in a
    forbidden way or after its access is expired, an exception will be
    raised.
    """

    resource: _T
    """The resource to be accessed."""
    primitive: Acquirable
    """The synchronization primitive."""

    @asynccontextmanager
    async def __call__(self) -> AsyncIterator[_T]:
        """Return the asynchronous context manager for the resource.

        After the resource is released, the resource becomes
        inaccessible.

        :return: The context manager for the resource.
        """
        await await_if_awaitable(self.primitive.acquire())

        try:
            resource = Proxy(self.resource, Proxy.Mode.READ | Proxy.Mode.WRITE)

            with closing(resource):
                yield cast(_T, resource)
        finally:
            await await_if_awaitable(self.primitive.release())


@dataclass
class WaitableDoor(AcquirableDoor[_T]):
    """The class for waitable doors.

    The door is initialized with the resource and corresponding
    primitive.

    The door can give access to the resource based on the desired
    operation.  When the user attempts to access the resource in a
    forbidden way or after its access is expired, an exception will
    be raised.
    """

    primitive: Waitable

    def wait(self) -> None:
        """Wait.

        :return: ``None``.
        """
        self.primitive.wait()

    def wait_for(self, predicate: Callable[[], bool]) -> None:
        """Wait for the predicate to hold ``True``.

        :return: ``None``.
        """
        self.primitive.wait_for(predicate)

    def notify(self) -> None:
        """Notify one.

        :return: ``None``.
        """
        self.primitive.notify()

    def notify_all(self) -> None:
        """Notify all.

        :return: ``None``.
        """
        self.primitive.notify_all()


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

    primitive: Waitable

    async def wait(self) -> None:
        """Wait.

        :return: ``None``.
        """
        await await_if_awaitable(self.primitive.wait())

    async def wait_for(self, predicate: Callable[[], Any]) -> None:
        """Wait for the predicate to hold ``True``.

        :return: ``None``.
        """
        await await_if_awaitable(self.primitive.wait_for(predicate))

    async def notify(self) -> None:
        """Notify one.

        :return: ``None``.
        """
        await await_if_awaitable(self.primitive.notify())

    async def notify_all(self) -> None:
        """Notify all.

        :return: ``None``.
        """
        await await_if_awaitable(self.primitive.notify_all())


@dataclass
class SAcquirableDoor(Generic[_T]):
    """The class for shared acquirable doors.

    The door is initialized with the resource and corresponding
    primitive.

    The door can give access to the resource based on the desired
    operation.  When the user attempts to access the resource in a
    forbidden way or after its access is expired, an exception will
    be raised.

    >>> @dataclass
    ... class Resource:
    ...     key: Any = 'value'
    ...
    >>> resource = Resource()
    >>> resource
    Resource(key='value')
    >>> resource.key
    'value'

    >>> from door.threading2 import RSLock
    >>> door = SAcquirableDoor(resource, RSLock())

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

    resource: _T
    """The resource to be accessed."""
    primitive: SAcquirable
    """The synchronization primitive."""

    @contextmanager
    def read(self) -> Iterator[_T]:
        """Return the context manager for the resource in read mode.

        After the resource is released, the resource becomes
        inaccessible.

        :return: The context manager for the resource.
        """
        self.primitive.acquire_read()

        try:
            resource = Proxy(self.resource, Proxy.Mode.READ)

            with closing(resource):
                yield cast(_T, resource)
        finally:
            self.primitive.release_read()

    @contextmanager
    def write(self) -> Iterator[_T]:
        """Return the context manager for the resource in write (and
        read) mode.

        After the resource is released, the resource becomes
        inaccessible.

        :return: The context manager for the resource.
        """
        self.primitive.acquire_write()

        try:
            resource = Proxy(self.resource, Proxy.Mode.READ | Proxy.Mode.WRITE)

            with closing(resource):
                yield cast(_T, resource)
        finally:
            self.primitive.release_write()


@dataclass
class AsyncSAcquirableDoor(Generic[_T]):
    """The class for asynchronous shared acquirable doors.

    This class is designed to be used for asynchronous prgramming.

    The door is initialized with the resource and corresponding
    primitive.

    The door can give access to the resource based on the desired
    operation. When the user attempts to access the resource in a
    forbidden way or after its access is expired, an exception will be
    raised.
    """

    resource: _T
    """The resource to be accessed."""
    primitive: SAcquirable
    """The synchronization primitive."""

    @asynccontextmanager
    async def read(self) -> AsyncIterator[_T]:
        """Return the asynchronous context manager for the resource in
        read mode.

        After the resource is released, the resource becomes
        inaccessible.

        :return: The context manager for the resource.
        """
        await await_if_awaitable(self.primitive.acquire_read())

        try:
            resource = Proxy(self.resource, Proxy.Mode.READ)

            with closing(resource):
                yield cast(_T, resource)
        finally:
            await await_if_awaitable(self.primitive.release_read())

    @asynccontextmanager
    async def write(self) -> AsyncIterator[_T]:
        """Return the asynchronous context manager for the resource in
        write (and read) mode.

        After the resource is released, the resource becomes
        inaccessible.

        :return: The context manager for the resource.
        """
        await await_if_awaitable(self.primitive.acquire_write())

        try:
            resource = Proxy(self.resource, Proxy.Mode.READ | Proxy.Mode.WRITE)

            with closing(resource):
                yield cast(_T, resource)
        finally:
            await await_if_awaitable(self.primitive.release_write())


@dataclass
class SWaitableDoor(SAcquirableDoor[_T]):
    """The class for shared waitable doors.

    The door is initialized with the resource and corresponding
    primitive.

    The door can give access to the resource based on the desired
    operation.  When the user attempts to access the resource in a
    forbidden way or after its access is expired, an exception will
    be raised.
    """

    primitive: SWaitable

    def wait_read(self) -> None:
        """Wait for reading.

        :return: ``None``.
        """
        self.primitive.wait_read()

    def wait_for_read(self, predicate: Callable[[], bool]) -> None:
        """Wait for the predicate to hold ``True`` for reading.

        :return: ``None``.
        """
        self.primitive.wait_for_read(predicate)

    def notify_read(self) -> None:
        """Notify one for reading.

        :return: ``None``.
        """
        self.primitive.notify_read()

    def notify_all_read(self) -> None:
        """Notify all for reading.

        :return: ``None``.
        """
        self.primitive.notify_all_read()

    def wait_write(self) -> None:
        """Wait for writing.

        :return: ``None``.
        """
        self.primitive.wait_write()

    def wait_for_write(self, predicate: Callable[[], bool]) -> None:
        """Wait for the predicate to hold ``True`` for writing.

        :return: ``None``.
        """
        self.primitive.wait_for_write(predicate)

    def notify_write(self) -> None:
        """Notify one for writing.

        :return: ``None``.
        """
        self.primitive.notify_write()

    def notify_all_write(self) -> None:
        """Notify all for writing.

        :return: ``None``.
        """
        self.primitive.notify_all_write()


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

    primitive: SWaitable

    async def wait_read(self) -> None:
        """Wait for reading.

        :return: ``None``.
        """
        await await_if_awaitable(self.primitive.wait_read())

    async def wait_for_read(self, predicate: Callable[[], Any]) -> None:
        """Wait for the predicate to hold ``True`` for reading.

        :return: ``None``.
        """
        await await_if_awaitable(self.primitive.wait_for_read(predicate))

    async def notify_read(self) -> None:
        """Notify one for reading.

        :return: ``None``.
        """
        await await_if_awaitable(self.primitive.notify_read())

    async def notify_all_read(self) -> None:
        """Notify all for reading.

        :return: ``None``.
        """
        await await_if_awaitable(self.primitive.notify_all_read())

    async def wait_write(self) -> None:
        """Wait for writing.

        :return: ``None``.
        """
        await await_if_awaitable(self.primitive.wait_write())

    async def wait_for_write(self, predicate: Callable[[], Any]) -> None:
        """Wait for the predicate to hold ``True`` for writing.

        :return: ``None``.
        """
        await await_if_awaitable(self.primitive.wait_for_write(predicate))

    async def notify_write(self) -> None:
        """Notify one for writing.

        :return: ``None``.
        """
        await await_if_awaitable(self.primitive.notify_write())

    async def notify_all_write(self) -> None:
        """Notify all for writing.

        :return: ``None``.
        """
        await await_if_awaitable(self.primitive.notify_all_write())
