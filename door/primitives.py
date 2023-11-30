""":mod:`door.primitives` defines the primitives."""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from door.utilities import await_if_awaitable


@runtime_checkable
class Acquirable(Protocol):
    """A protocol for acquirable primitives."""

    def acquire(self) -> Any:
        """Acquire the primitive."""
        pass  # pragma: no cover

    def release(self) -> Any:
        """Release the primitive. """
        pass  # pragma: no cover


@runtime_checkable
class Waitable(Acquirable, Protocol):
    """A protocol for acquirable primitives."""

    def wait(self) -> Any:
        """Wait."""
        pass  # pragma: no cover

    def wait_for(self, predicate: Callable[[], bool]) -> Any:
        """Wait."""
        pass  # pragma: no cover

    def notify(self) -> Any:
        """notify one."""
        pass  # pragma: no cover

    def notify_all(self) -> Any:
        """notify all."""
        pass  # pragma: no cover


@runtime_checkable
class SAcquirable(Protocol):
    """A protocol for shared primitives."""

    def acquire_read(self) -> Any:
        """Acquire the primitive for reading."""
        pass  # pragma: no cover

    def release_read(self) -> Any:
        """Release the primitive for reading."""
        pass  # pragma: no cover

    def acquire_write(self) -> Any:
        """Acquire the primitive for writing (and reading)."""
        pass  # pragma: no cover

    def release_write(self) -> Any:
        """Release the primitive for writing (and reading)."""
        pass  # pragma: no cover


@dataclass
class RSLock:
    """The class for read-preferring shared locks.

    The implementations in this library is read-preferring and follow
    the pseudocode in Concurrent Programming: Algorithms, Principles,
    and Foundations by Michel Raynal.
    """

    _r: Acquirable
    _g: Acquirable
    _b: int = field(default=0, init=False)

    def acquire_read(self) -> None:
        self._r.acquire()

        self._b += 1

        if self._b == 1:
            self._g.acquire()

        self._r.release()

    def release_read(self) -> None:
        self._r.acquire()

        self._b -= 1

        if self._b == 0:
            self._g.release()

        self._r.release()

    def acquire_write(self) -> None:
        self._g.acquire()

    def release_write(self) -> None:
        self._g.release()


@dataclass
class AsyncRSLock:
    """The base class for asynchronous read-preferring shared locks.

    This class is designed to be used for asynchronous prgramming.

    The implementations in this library is read-preferring and follow
    the pseudocode in Concurrent Programming: Algorithms, Principles,
    and Foundations by Michel Raynal.
    """

    _r: Acquirable
    _g: Acquirable
    _b: int = field(default=0, init=False)

    async def acquire_read(self) -> None:
        await await_if_awaitable(self._r.acquire())

        self._b += 1

        if self._b == 1:
            await await_if_awaitable(self._g.acquire())

        await await_if_awaitable(self._r.release())

    async def release_read(self) -> None:
        await await_if_awaitable(self._r.acquire())

        self._b -= 1

        if self._b == 0:
            self._g.release()

        await await_if_awaitable(self._r.release())

    async def acquire_write(self) -> None:
        await await_if_awaitable(self._g.acquire())

    async def release_write(self) -> None:
        await await_if_awaitable(self._g.release())


@dataclass
class WSLock:
    """The class for write-preferring shared locks."""

    _g: Waitable
    _num_writers_waiting: int = field(default=0, init=False)
    _writer_active: bool = field(default=False, init=False)
    _num_readers_active: int = field(default=0, init=False)

    def acquire_read(self) -> None:
        self._g.acquire()

        while self._num_writers_waiting > 0 or self._writer_active:
            self._g.wait()

        self._num_readers_active += 1

        self._g.release()

    def release_read(self) -> None:
        self._g.acquire()

        self._num_readers_active -= 1

        if self._num_readers_active == 0:
            self._g.notify_all()

        self._g.release()

    def acquire_write(self) -> None:
        self._g.acquire()

        self._num_writers_waiting += 1

        while self._num_readers_active > 0 or self._writer_active:
            self._g.wait()

        self._num_writers_waiting -= 1
        self._writer_active = True

        self._g.release()

    def release_write(self) -> None:
        self._g.acquire()

        self._writer_active = False

        self._g.notify_all()
        self._g.release()


@dataclass
class AsyncWSLock:
    """The base class for asynchronous write-preferring shared locks.

    This class is designed to be used for asynchronous prgramming.
    """

    _g: Waitable
    _num_writers_waiting: int = field(default=0, init=False)
    _writer_active: bool = field(default=False, init=False)
    _num_readers_active: int = field(default=0, init=False)

    async def acquire_read(self) -> None:
        await await_if_awaitable(self._g.acquire())

        while self._num_writers_waiting > 0 or self._writer_active:
            await await_if_awaitable(self._g.wait())

        self._num_readers_active += 1

        await await_if_awaitable(self._g.release())

    async def release_read(self) -> None:
        await await_if_awaitable(self._g.acquire())

        self._num_readers_active -= 1

        if self._num_readers_active == 0:
            await await_if_awaitable(self._g.notify_all())

        await await_if_awaitable(self._g.release())

    async def acquire_write(self) -> None:
        await await_if_awaitable(self._g.acquire())

        self._num_writers_waiting += 1

        while self._num_readers_active > 0 or self._writer_active:
            await await_if_awaitable(self._g.wait())

        self._num_writers_waiting -= 1
        self._writer_active = True

        await await_if_awaitable(self._g.release())

    async def release_write(self) -> None:
        await await_if_awaitable(self._g.acquire())

        self._writer_active = False

        await await_if_awaitable(self._g.notify_all())
        await await_if_awaitable(self._g.release())
