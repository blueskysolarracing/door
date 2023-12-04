""":mod:`door.primitives` defines the primitives."""

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from door.utilities import await_if_awaitable, Counter


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

    def notify(self) -> Any:
        """Notify one."""
        pass  # pragma: no cover

    def notify_all(self) -> Any:
        """Notify all."""
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

    def notify_read(self) -> Any:
        """Notify one for reading."""
        pass  # pragma: no cover

    def notify_all_read(self) -> Any:
        """Notify all for reading."""
        pass  # pragma: no cover

    def wait_write(self) -> Any:
        """Wait for writing."""
        pass  # pragma: no cover

    def notify_write(self) -> Any:
        """Notify one for writing."""
        pass  # pragma: no cover

    def notify_all_write(self) -> Any:
        """Notify all for writing."""
        pass  # pragma: no cover


@dataclass
class RSLock:
    """The class for read-preferring shared locks.

    This class is designed to be used for threading and multiprocessing.

    The implementations in this library is read-preferring and follow
    the pseudocode in Concurrent Programming: Algorithms, Principles,
    and Foundations by Michel Raynal.
    """

    _r: Acquirable
    _g: Acquirable
    _b: Counter = field(init=False)

    def acquire_read(self) -> None:
        self._r.acquire()

        if not self._b:
            self._g.acquire()

        self._b.increment()
        self._r.release()

    def release_read(self) -> None:
        self._r.acquire()
        self._b.decrement()

        if not self._b:
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
    _b: Counter = field(init=False)

    async def acquire_read(self) -> None:
        await await_if_awaitable(self._r.acquire())

        if not self._b:
            await await_if_awaitable(self._g.acquire())

        self._b.increment()

        await await_if_awaitable(self._r.release())

    async def release_read(self) -> None:
        await await_if_awaitable(self._r.acquire())

        self._b.decrement()

        if not self._b:
            self._g.release()

        await await_if_awaitable(self._r.release())

    async def acquire_write(self) -> None:
        await await_if_awaitable(self._g.acquire())

    async def release_write(self) -> None:
        await await_if_awaitable(self._g.release())


@dataclass
class WSLock:
    """The class for write-preferring shared locks.

    This class is designed to be used for threading and multiprocessing.
    """

    _g: Waitable
    _num_writers_waiting: Counter = field(init=False)
    _writer_active: Counter = field(init=False)
    _num_readers_active: Counter = field(init=False)

    def acquire_read(self) -> None:
        self._g.acquire()

        while self._num_writers_waiting or self._writer_active:
            self._g.wait()

        self._num_readers_active.increment()
        self._g.release()

    def release_read(self) -> None:
        self._g.acquire()
        self._num_readers_active.decrement()

        if not self._num_readers_active:
            self._g.notify_all()

        self._g.release()

    def acquire_write(self) -> None:
        self._g.acquire()
        self._num_writers_waiting.increment()

        while self._num_readers_active or self._writer_active:
            self._g.wait()

        self._num_writers_waiting.decrement()
        self._writer_active.increment()
        self._g.release()

    def release_write(self) -> None:
        self._g.acquire()
        self._writer_active.decrement()
        self._g.notify_all()
        self._g.release()


@dataclass
class AsyncWSLock:
    """The class for asynchronous write-preferring shared locks.

    This class is designed to be used for asynchronous prgramming.
    """

    _g: Waitable
    _num_writers_waiting: Counter = field(init=False)
    _writer_active: Counter = field(init=False)
    _num_readers_active: Counter = field(init=False)

    async def acquire_read(self) -> None:
        await await_if_awaitable(self._g.acquire())

        while self._num_writers_waiting or self._writer_active:
            await await_if_awaitable(self._g.wait())

        self._num_readers_active.increment()

        await await_if_awaitable(self._g.release())

    async def release_read(self) -> None:
        await await_if_awaitable(self._g.acquire())

        self._num_readers_active.decrement()

        if not self._num_readers_active:
            await await_if_awaitable(self._g.notify_all())

        await await_if_awaitable(self._g.release())

    async def acquire_write(self) -> None:
        await await_if_awaitable(self._g.acquire())

        self._num_writers_waiting.increment()

        while self._num_readers_active or self._writer_active:
            await await_if_awaitable(self._g.wait())

        self._num_writers_waiting.decrement()
        self._writer_active.increment()

        await await_if_awaitable(self._g.release())

    async def release_write(self) -> None:
        await await_if_awaitable(self._g.acquire())

        self._writer_active.decrement()

        await await_if_awaitable(self._g.notify_all())
        await await_if_awaitable(self._g.release())


@dataclass
class SCondition:
    """The class for shared condition variables.

    This class is designed to be used for threading and multiprocessing.
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
