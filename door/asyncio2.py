""":mod:`door.asyncio2` defines utilities for asynchronous programming."""

from asyncio import Lock
from dataclasses import dataclass, field

from door.primitives import Acquirable, AsyncSLock


@dataclass
class SLock(AsyncSLock):
    """The class for shared locks.

    This class is designed to be used for asynchronous programming.

    The implementations in this library is read-preferring and follow
    the pseudocode in Concurrent Programming: Algorithms, Principles,
    and Foundations by Michel Raynal.
    """

    _r: Acquirable = field(default_factory=Lock, init=False)
    _g: Acquirable = field(default_factory=Lock, init=False)
