""":mod:`door.doors` defines the doors."""

from collections.abc import AsyncIterator, Callable, Iterator
from contextlib import asynccontextmanager, closing, contextmanager
from dataclasses import dataclass
from functools import partial
from typing import Any, cast, Generic, TypeVar

from door.primitives import Acquirable, SAcquirable, Waitable
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

    >>> with door.acquire() as proxy:
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
    def acquire(self) -> Iterator[_T]:
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
    async def acquire(self) -> AsyncIterator[_T]:
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

    def wait_for(self, predicate: Callable[[_T], bool]) -> None:
        """Wait for the predicate to hold ``True``.

        :return: ``None``.
        """
        self.primitive.wait_for(partial(predicate, self.resource))

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

    >>> with door.acquire_read() as proxy:
    ...     proxy.key
    ...
    'value'

    >>> with door.acquire_read() as proxy:
    ...     proxy.key = 'VALUE'
    ...
    Traceback (most recent call last):
        ...
    ValueError: no write permission

    >>> with door.acquire_write() as proxy:
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
    def acquire_read(self) -> Iterator[_T]:
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
    def acquire_write(self) -> Iterator[_T]:
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
    async def acquire_read(self) -> AsyncIterator[_T]:
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
    async def acquire_write(self) -> AsyncIterator[_T]:
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
