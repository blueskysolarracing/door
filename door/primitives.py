""":mod:`door.primitives` defines the primitive protocols."""

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@runtime_checkable
class Primitive(Protocol):
    """A protocol for primitives."""

    def acquire(self) -> bool:
        """Acquire the primitive.

        :return: ``True`` if acquired, otherwise ``False``.
        """
        pass  # pragma: no cover

    def release(self) -> None:
        """Release the primitive.

        :return: ``None``.
        """
        pass  # pragma: no cover


@runtime_checkable
class AsyncPrimitive(Protocol):
    """A protocol for asynchronous primitives."""

    async def acquire(self) -> bool:
        """Acquire the primitive.

        :return: ``True`` if acquired, otherwise ``False``.
        """
        pass  # pragma: no cover

    def release(self) -> None:
        """Release the primitive.

        :return: ``None``.
        """
        pass  # pragma: no cover


@runtime_checkable
class FineGrainedPrimitive(Protocol):
    """A protocol for fine-grained primitives."""

    def acquire_read(self) -> bool:
        """Acquire the primitive for reading.

        :return: ``True`` if acquired, otherwise ``False``.
        """
        pass  # pragma: no cover

    def release_read(self) -> None:
        """Release the primitive for reading.

        :return: ``None``.
        """
        pass  # pragma: no cover

    def acquire_write(self) -> bool:
        """Acquire the primitive for writing (and reading).

        :return: ``True`` if acquired, otherwise ``False``.
        """
        pass  # pragma: no cover

    def release_write(self) -> None:
        """Release the primitive for writing (and reading).

        :return: ``None``.
        """
        pass  # pragma: no cover


@runtime_checkable
class FineGrainedAsyncPrimitive(Protocol):
    """A protocol for fine-grained asynchronous primitives."""

    async def acquire_read(self) -> bool:
        """Acquire the primitive for reading.

        :return: ``True`` if acquired, otherwise ``False``.
        """
        pass  # pragma: no cover

    async def release_read(self) -> None:
        """Release the primitive for reading.

        :return: ``None``.
        """
        pass  # pragma: no cover

    async def acquire_write(self) -> bool:
        """Acquire the primitive for writing (and reading).

        :return: ``True`` if acquired, otherwise ``False``.
        """
        pass  # pragma: no cover

    async def release_write(self) -> None:
        """Release the primitive for writing (and reading).

        :return: ``None``.
        """
        pass  # pragma: no cover


@dataclass
class SLock:
    """The class for shared locks.

    The implementations in this library is read-preferring and follow
    the pseudocode in Concurrent Programming: Algorithms, Principles,
    and Foundations by Michel Raynal.
    """

    _r: Primitive
    _g: Primitive
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

    _r: AsyncPrimitive
    _g: AsyncPrimitive
    _b: int = field(default=0, init=False)

    async def acquire_read(self) -> bool:
        await self._r.acquire()

        self._b += 1

        if self._b == 1:
            await self._g.acquire()

        self._r.release()

        return True

    async def release_read(self) -> None:
        await self._r.acquire()

        self._b -= 1

        if self._b == 0:
            self._g.release()

        self._r.release()

    async def acquire_write(self) -> bool:
        await self._g.acquire()

        return True

    async def release_write(self) -> None:
        self._g.release()
