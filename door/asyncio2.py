""":mod:`door.asyncio2` defines utilities for asynchronous programming."""

from asyncio import Condition, Lock
from dataclasses import dataclass, field

from door.primitives import (
    Acquirable,
    AsyncRSLock,
    AsyncSCondition,
    AsyncWSLock,
    SAcquirable,
    Waitable,
)


@dataclass
class RSLock(AsyncRSLock):
    """The class for asynchronous read-preferring shared locks.

    This class is designed to be used for asynchronous programming.

    The implementations in this library is read-preferring and follow
    the pseudocode in Concurrent Programming: Algorithms, Principles,
    and Foundations by Michel Raynal.
    """

    _r: Acquirable = field(default_factory=Lock)
    _g: Acquirable = field(default_factory=Lock)


@dataclass
class WSLock(AsyncWSLock):
    """The class for asynchronous write-preferring shared locks.

    This class is designed to be used for asynchronous programming.
    """

    _g: Waitable = field(default_factory=Condition)


@dataclass
class RSCondition(AsyncSCondition):
    """The class for asynchronous read-preferring shared condition variables.

    This class is designed to be used for asynchronous programming.
    """

    _s: SAcquirable = field(default_factory=RSLock)
    _a: Waitable = field(default_factory=Condition)


@dataclass
class WSCondition(AsyncSCondition):
    """The class for asynchronous write-preferring shared condition variables.

    This class is designed to be used for asynchronous programming.
    """

    _s: SAcquirable = field(default_factory=WSLock)
    _a: Waitable = field(default_factory=Condition)
