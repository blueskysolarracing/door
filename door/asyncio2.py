""":mod:`door.asyncio2` defines utilities for asynchronous programming."""

from asyncio import Condition, Lock
from dataclasses import dataclass, field
from typing import TypeVar

from door.doors import (
    AsyncAcquirableDoor,
    AsyncWaitableDoor,
    AsyncSAcquirableDoor,
    AsyncSWaitableDoor,
    UnhandledDoor,
)
from door.primitives import (
    Acquirable,
    AsyncRSLock,
    AsyncSCondition,
    AsyncWSLock,
    SAcquirable,
    SWaitable,
    Waitable,
)
from door.utilities import IntCounter

_T = TypeVar('_T')


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
    _b: IntCounter = field(default_factory=IntCounter, init=False)


@dataclass
class WSLock(AsyncWSLock):
    """The class for asynchronous write-preferring shared locks.

    This class is designed to be used for asynchronous programming.
    """

    _g: Waitable = field(default_factory=Condition)
    _num_writers_waiting: IntCounter = field(
        default_factory=IntCounter,
        init=False,
    )
    _writer_active: IntCounter = field(default_factory=IntCounter, init=False)
    _num_readers_active: IntCounter = field(
        default_factory=IntCounter,
        init=False,
    )


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


@dataclass
class AcquirableDoor(UnhandledDoor[_T], AsyncAcquirableDoor[_T]):
    """The class for asynchronous acquirable doors.

    This class is designed to be used for asynchronous programming.

    The door is initialized with the resource and corresponding
    primitive.

    The door can give access to the resource based on the desired
    operation. When the user attempts to access the resource in a
    forbidden way or after its access is expired, an exception will be
    raised.
    """

    _primitive: Acquirable = field(default_factory=Lock)


@dataclass
class WaitableDoor(UnhandledDoor[_T], AsyncWaitableDoor[_T]):
    """The class for asynchronous waitable doors.

    This class is designed to be used for asynchronous programming.

    The door is initialized with the resource and corresponding
    primitive.

    The door can give access to the resource based on the desired
    operation. When the user attempts to access the resource in a
    forbidden way or after its access is expired, an exception will be
    raised.
    """

    _primitive: Waitable = field(default_factory=Condition)


@dataclass
class SAcquirableDoor(UnhandledDoor[_T], AsyncSAcquirableDoor[_T]):
    """The class for asynchronous shared acquirable doors.

    This class is designed to be used for asynchronous programming.

    The door is initialized with the resource and corresponding
    primitive.

    The door can give access to the resource based on the desired
    operation. When the user attempts to access the resource in a
    forbidden way or after its access is expired, an exception will be
    raised.
    """

    _primitive: SAcquirable = field(default_factory=WSLock)


@dataclass
class SWaitableDoor(UnhandledDoor[_T], AsyncSWaitableDoor[_T]):
    """The class for asynchronous shared waitable doors.

    This class is designed to be used for asynchronous programming.

    The door is initialized with the resource and corresponding
    primitive.

    The door can give access to the resource based on the desired
    operation. When the user attempts to access the resource in a
    forbidden way or after its access is expired, an exception will be
    raised.
    """

    _primitive: SWaitable = field(default_factory=WSCondition)
