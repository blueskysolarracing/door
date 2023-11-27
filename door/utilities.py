from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager, closing, contextmanager
from dataclasses import dataclass
from enum import auto, Flag
from typing import Any, cast, Generic, TypeVar

from door.primitives import (
    AsyncPrimitive,
    FineGrainedAsyncPrimitive,
    FineGrainedPrimitive,
    Primitive,
)

_T = TypeVar('_T')


@dataclass(repr=False)
class Resource(Generic[_T]):
    """The class for resources.

    >>> @dataclass
    ... class X:
    ...     a: str = 'a'
    ...     b: str = 'b'
    ...
    >>> x = X()
    >>> x
    X(a='a', b='b')
    >>> x.a
    'a'
    >>> x.b
    'b'

    >>> resource = Resource(x, Resource.Mode.READ)
    >>> resource.a
    'a'
    >>> resource.a = 'A'
    Traceback (most recent call last):
        ...
    ValueError: no write permission
    >>> resource.close()
    >>> resource.a
    Traceback (most recent call last):
        ...
    ValueError: no read permission
    >>> resource.a = 'A'
    Traceback (most recent call last):
        ...
    ValueError: no write permission

    >>> resource = Resource(x, Resource.Mode.WRITE)
    >>> resource.b = 'B'
    >>> resource.b
    Traceback (most recent call last):
        ...
    ValueError: no read permission
    >>> resource.close()

    >>> resource = Resource(x, Resource.Mode.READ | Resource.Mode.WRITE)
    >>> resource.b
    'B'
    >>> resource.a
    'a'
    >>> resource.a = 'A'
    >>> resource.a
    'A'
    >>> resource.close()
    >>> x
    X(a='A', b='B')
    >>> x.a
    'A'
    >>> x.b
    'B'
    """

    class Mode(Flag):
        """The flag for modes."""

        READ = auto()
        WRITE = auto()

    __initialized = False
    __raw: _T
    __mode: Mode

    def __post_init__(self) -> None:
        self.__initialized = True

    def __getattr__(self, name: str) -> Any:
        try:
            value = self.__getattribute__(name)
        except AttributeError:
            if self.Mode.READ not in self.__mode:
                raise ValueError('no read permission')

            value = getattr(self.__raw, name)

        return value

    def __setattr__(self, name: str, value: Any) -> None:
        if not self.__initialized:
            super().__setattr__(name, value)

        try:
            self.__getattribute__(name)
        except AttributeError:
            if self.Mode.WRITE not in self.__mode:
                raise ValueError('no write permission')

            setattr(self.__raw, name, value)
        else:
            super().__setattr__(name, value)

    def close(self) -> None:
        """Close the resource.

        The raw resource becomes inaccessible.

        :return: ``None``.
        """
        self.__mode = self.Mode(0)


@dataclass
class Door(Generic[_T]):
    """The class for doors.

    The door is initialized with the raw resource and corresponding
    primitive.

    The door can give access to the raw resource based on the desired
    operation. When the user attempts to access the raw resource in a
    forbidden way or after its access is expired, an exception will be
    raised.

    >>> @dataclass
    ... class X:
    ...     a: str = 'a'
    ...     b: str = 'b'
    ...
    >>> x = X()
    >>> x
    X(a='a', b='b')
    >>> x.a
    'a'
    >>> x.b
    'b'

    >>> from threading import RLock
    >>> door = Door(x, RLock())

    >>> with door.read() as resource:
    ...     resource.a
    ...
    'a'
    >>> resource.a
    Traceback (most recent call last):
        ...
    ValueError: no read permission
    >>> resource.a = 'A'
    Traceback (most recent call last):
        ...
    ValueError: no write permission
    >>> with door.read() as resource:
    ...     resource.a = 'A'
    ...
    Traceback (most recent call last):
        ...
    ValueError: no write permission

    >>> with door.write() as resource:
    ...     resource.b = 'B'
    ...     resource.b
    ...     resource.a
    ...     resource.a = 'A'
    ...     resource.a
    ...
    'B'
    'a'
    'A'

    >>> x
    X(a='A', b='B')
    >>> x.a
    'A'
    >>> x.b
    'B'
    """

    raw_resource: _T
    """The raw resource to be accessed."""
    primitive: Primitive | FineGrainedPrimitive
    """The synchronization primitive."""

    @contextmanager
    def read(self) -> Iterator[_T]:
        """Return the context manager for the resource in read mode.

        After the resource is released, the raw resource becomes
        inaccessible.

        :return: The context manager for the resource.
        """
        if isinstance(self.primitive, FineGrainedPrimitive):
            self.primitive.acquire_read()
        else:
            self.primitive.acquire()

        try:
            resource = Resource(self.raw_resource, Resource.Mode.READ)

            with closing(resource):
                yield cast(_T, resource)
        finally:
            if isinstance(self.primitive, FineGrainedPrimitive):
                self.primitive.release_read()
            else:
                self.primitive.release()

    @contextmanager
    def write(self) -> Iterator[_T]:
        """Return the context manager for the resource in write (and
        read) mode.

        After the resource is released, the raw resource becomes
        inaccessible.

        :return: The context manager for the resource.
        """
        if isinstance(self.primitive, FineGrainedPrimitive):
            self.primitive.acquire_write()
        else:
            self.primitive.acquire()

        try:
            resource = Resource(
                self.raw_resource,
                Resource.Mode.READ | Resource.Mode.WRITE,
            )

            with closing(resource):
                yield cast(_T, resource)
        finally:
            if isinstance(self.primitive, FineGrainedPrimitive):
                self.primitive.release_write()
            else:
                self.primitive.release()


@dataclass
class AsyncDoor(Generic[_T]):
    """The class for doors.

    This class is designed to be used for asynchronous prgramming.

    The door is initialized with the raw resource and corresponding
    primitive.

    The door can give access to the raw resource based on the desired
    operation. When the user attempts to access the raw resource in a
    forbidden way or after its access is expired, an exception will be
    raised.
    """

    raw_resource: _T
    """The raw resource to be accessed."""
    primitive: AsyncPrimitive | FineGrainedAsyncPrimitive
    """The synchronization primitive."""

    @asynccontextmanager
    async def read(self) -> AsyncIterator[_T]:
        """Return the asynchronous context manager for the resource in
        read mode.

        After the resource is released, the raw resource becomes
        inaccessible.

        :return: The context manager for the resource.
        """
        if isinstance(self.primitive, FineGrainedAsyncPrimitive):
            await self.primitive.acquire_read()
        else:
            await self.primitive.acquire()

        try:
            resource = Resource(self.raw_resource, Resource.Mode.READ)

            with closing(resource):
                yield cast(_T, resource)
        finally:
            if isinstance(self.primitive, FineGrainedAsyncPrimitive):
                await self.primitive.release_read()
            else:
                self.primitive.release()

    @asynccontextmanager
    async def write(self) -> AsyncIterator[_T]:
        """Return the asynchronous context manager for the resource in
        write (and read) mode.

        After the resource is released, the raw resource becomes
        inaccessible.

        :return: The context manager for the resource.
        """
        if isinstance(self.primitive, FineGrainedAsyncPrimitive):
            await self.primitive.acquire_write()
        else:
            await self.primitive.acquire()

        try:
            resource = Resource(
                self.raw_resource,
                Resource.Mode.READ | Resource.Mode.WRITE,
            )

            with closing(resource):
                yield cast(_T, resource)
        finally:
            if isinstance(self.primitive, FineGrainedAsyncPrimitive):
                await self.primitive.release_write()
            else:
                self.primitive.release()
