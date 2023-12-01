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
    """A protocol for waitable primitives."""

    def wait(self) -> Any:
        """Wait."""
        pass  # pragma: no cover

    def wait_for(self, predicate: Callable[[], bool]) -> Any:
        """Wait for the predicate to hold ``True``."""
        pass  # pragma: no cover

    def notify(self) -> Any:
        """notify one."""
        pass  # pragma: no cover

    def notify_all(self) -> Any:
        """notify all."""
        pass  # pragma: no cover


@runtime_checkable
class SAcquirable(Protocol):
    """A protocol for shared acquiarables."""

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


@runtime_checkable
class SWaitable(SAcquirable, Protocol):
    """A protocol for shared waitable primitives."""

    def wait_read(self) -> Any:
        """Wait for reading."""
        pass  # pragma: no cover

    def wait_for_read(self, predicate: Callable[[], bool]) -> Any:
        """Wait for the predicate to hold ``True`` for reading."""
        pass  # pragma: no cover

    def notify_read(self) -> Any:
        """notify one for reading."""
        pass  # pragma: no cover

    def notify_all_read(self) -> Any:
        """notify all for reading."""
        pass  # pragma: no cover

    def wait_write(self) -> Any:
        """Wait for writing."""
        pass  # pragma: no cover

    def wait_for_write(self, predicate: Callable[[], bool]) -> Any:
        """Wait for the predicate to hold ``True`` for writing."""
        pass  # pragma: no cover

    def notify_write(self) -> Any:
        """notify one for writing."""
        pass  # pragma: no cover

    def notify_all_write(self) -> Any:
        """notify all for writing."""
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
    """The class for asynchronous read-preferring shared locks.

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
    """The class for asynchronous write-preferring shared locks.

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


@dataclass
class SCondition:
    """The class for shared condition variables.

    This class is designed to be used for asynchronous prgramming.
    """

    _s: SAcquirable
    _a: Waitable

    def acquire_read(self) -> None:
        self._s.acquire_read()

    def release_read(self) -> None:
        self._s.release_read()

    def wait_read(self) -> None:
        self._a.acquire()
        self._s.release_read()
        self._a.wait()
        self._s.acquire_read()
        self._a.release()

    def wait_for_read(self, predicate: Callable[[], bool]) -> None:
        self._a.acquire()
        self._s.release_read()
        self._a.wait_for(predicate)
        self._s.acquire_read()
        self._a.release()

    def notify_read(self) -> None:
        self._a.acquire()
        self._s.release_read()
        self._a.notify()
        self._s.acquire_read()
        self._a.release()

    def notify_all_read(self) -> None:
        self._a.acquire()
        self._s.release_read()
        self._a.notify_all()
        self._s.acquire_read()
        self._a.release()

    def acquire_write(self) -> None:
        self._s.acquire_write()

    def release_write(self) -> None:
        self._s.release_write()

    def wait_write(self) -> None:
        self._a.acquire()
        self._s.release_write()
        self._a.wait()
        self._s.acquire_write()
        self._a.release()

    def wait_for_write(self, predicate: Callable[[], bool]) -> None:
        self._a.acquire()
        self._s.release_write()
        self._a.wait_for(predicate)
        self._s.acquire_write()
        self._a.release()

    def notify_write(self) -> None:
        self._a.acquire()
        self._s.release_write()
        self._a.notify()
        self._s.acquire_write()
        self._a.release()

    def notify_all_write(self) -> None:
        self._a.acquire()
        self._s.release_write()
        self._a.notify_all()
        self._s.acquire_write()
        self._a.release()


@dataclass
class AsyncSCondition:
    """The class for asynchronous shared condition variables.

    This class is designed to be used for asynchronous prgramming.
    """

    _s: SAcquirable
    _a: Waitable

    async def acquire_read(self) -> None:
        await await_if_awaitable(self._s.acquire_read())

    async def release_read(self) -> None:
        await await_if_awaitable(self._s.release_read())

    async def wait_read(self) -> None:
        await await_if_awaitable(self._a.acquire())
        await await_if_awaitable(self._s.release_read())
        await await_if_awaitable(self._a.wait())
        await await_if_awaitable(self._s.acquire_read())
        await await_if_awaitable(self._a.release())

    async def wait_for_read(self, predicate: Callable[[], bool]) -> None:
        await await_if_awaitable(self._a.acquire())
        await await_if_awaitable(self._s.release_read())
        await await_if_awaitable(self._a.wait_for(predicate))
        await await_if_awaitable(self._s.acquire_read())
        await await_if_awaitable(self._a.release())

    async def notify_read(self) -> None:
        await await_if_awaitable(self._a.acquire())
        await await_if_awaitable(self._s.release_read())
        await await_if_awaitable(self._a.notify())
        await await_if_awaitable(self._s.acquire_read())
        await await_if_awaitable(self._a.release())

    async def notify_all_read(self) -> None:
        await await_if_awaitable(self._a.acquire())
        await await_if_awaitable(self._s.release_read())
        await await_if_awaitable(self._a.notify_all())
        await await_if_awaitable(self._s.acquire_read())
        await await_if_awaitable(self._a.release())

    async def acquire_write(self) -> None:
        await await_if_awaitable(self._s.acquire_write())

    async def release_write(self) -> None:
        await await_if_awaitable(self._s.release_write())

    async def wait_write(self) -> None:
        await await_if_awaitable(self._a.acquire())
        await await_if_awaitable(self._s.release_write())
        await await_if_awaitable(self._a.wait())
        await await_if_awaitable(self._s.acquire_write())
        await await_if_awaitable(self._a.release())

    async def wait_for_write(self, predicate: Callable[[], bool]) -> None:
        await await_if_awaitable(self._a.acquire())
        await await_if_awaitable(self._s.release_write())
        await await_if_awaitable(self._a.wait_for(predicate))
        await await_if_awaitable(self._s.acquire_write())
        await await_if_awaitable(self._a.release())

    async def notify_write(self) -> None:
        await await_if_awaitable(self._a.acquire())
        await await_if_awaitable(self._s.release_write())
        await await_if_awaitable(self._a.notify())
        await await_if_awaitable(self._s.acquire_write())
        await await_if_awaitable(self._a.release())

    async def notify_all_write(self) -> None:
        await await_if_awaitable(self._a.acquire())
        await await_if_awaitable(self._s.release_write())
        await await_if_awaitable(self._a.notify_all())
        await await_if_awaitable(self._s.acquire_write())
        await await_if_awaitable(self._a.release())
