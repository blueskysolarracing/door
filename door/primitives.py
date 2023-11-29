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
class SLock:
    """The class for shared locks.

    The implementations in this library is read-preferring and follow
    the pseudocode in Concurrent Programming: Algorithms, Principles,
    and Foundations by Michel Raynal.
    """

    _r: Acquirable
    _g: Acquirable
    _b: int = field(default=0, init=False)

    def acquire_read(self) -> bool:
        self._r.acquire()

        self._b += 1

        if self._b == 1:
            self._g.acquire()

        self._r.release()

        return True

    def release_read(self) -> None:
        self._r.acquire()

        self._b -= 1

        if self._b == 0:
            self._g.release()

        self._r.release()

    def acquire_write(self) -> bool:
        self._g.acquire()

        return True

    def release_write(self) -> None:
        self._g.release()


@dataclass
class AsyncSLock:
    """The abstract base class for shared locks.

    This class is designed to be used for asynchronous prgramming.

    The implementations in this library is read-preferring and follow
    the pseudocode in Concurrent Programming: Algorithms, Principles,
    and Foundations by Michel Raynal.
    """

    _r: Acquirable
    _g: Acquirable
    _b: int = field(default=0, init=False)

    async def acquire_read(self) -> bool:
        await await_if_awaitable(self._r.acquire())

        self._b += 1

        if self._b == 1:
            await await_if_awaitable(self._g.acquire())

        await await_if_awaitable(self._r.release())

        return True

    async def release_read(self) -> None:
        await await_if_awaitable(self._r.acquire())

        self._b -= 1

        if self._b == 0:
            self._g.release()

        await await_if_awaitable(self._r.release())

    async def acquire_write(self) -> bool:
        await await_if_awaitable(self._g.acquire())

        return True

    async def release_write(self) -> None:
        await await_if_awaitable(self._g.release())
