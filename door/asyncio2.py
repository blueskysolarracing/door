""":mod:`door.asyncio` defines utilities for asynchronous programming."""

from asyncio import Lock
from dataclasses import dataclass, field

from door.primitives import AsyncPrimitive, AsyncSLock


@dataclass
class SLock(AsyncSLock):
    """The class for shared locks.

    This class is designed to be used for asynchronous programming.

    The implementations in this library is read-preferring and follow
    the pseudocode in Concurrent Programming: Algorithms, Principles,
    and Foundations by Michel Raynal.
    """

    _r: AsyncPrimitive = field(default_factory=Lock, init=False)
    _g: AsyncPrimitive = field(default_factory=Lock, init=False)
