""":mod:`door.asyncio2` defines utilities for asynchronous programming."""

from asyncio import Condition, Lock
from dataclasses import dataclass, field

from door.primitives import Acquirable, AsyncRSLock, AsyncWSLock, Waitable


@dataclass
class RSLock(AsyncRSLock):
    """The class for asynchronous read-preferring shared locks.

    This class is designed to be used for asynchronous programming.

    The implementations in this library is read-preferring and follow
    the pseudocode in Concurrent Programming: Algorithms, Principles,
    and Foundations by Michel Raynal.
    """

    _r: Acquirable = field(default_factory=Lock, init=False)
    _g: Acquirable = field(default_factory=Lock, init=False)


@dataclass
class WSLock(AsyncWSLock):
    """The class for asynchronous write-preferring shared locks.

    This class is designed to be used for asynchronous programming.
    """

    _g: Waitable = field(default_factory=Condition, init=False)
