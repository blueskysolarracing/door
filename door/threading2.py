""":mod:`door.threading2` defines utilities for threading."""

from dataclasses import dataclass, field
from threading import Condition, Lock, RLock
from typing import TypeVar

from door.doors import (
    AcquirableDoor as SyncAcquirableDoor,
    SAcquirableDoor as SyncSAcquirableDoor,
    SWaitableDoor as SyncSWaitableDoor,
    UnhandledDoor,
    WaitableDoor as SyncWaitableDoor,
)
from door.primitives import (
    Acquirable,
    RSLock as SyncRSLock,
    SAcquirable,
    SCondition as SyncSCondition,
    SWaitable,
    Waitable,
    WSLock as SyncWSLock,
)
from door.utilities import IntCounter

_T = TypeVar('_T')


@dataclass
class RSLock(SyncRSLock):
    """The class for read-preferring shared locks.

    This class is designed to be used for threading.

    The implementations in this library is read-preferring and follow
    the pseudocode in Concurrent Programming: Algorithms, Principles,
    and Foundations by Michel Raynal.
    """

    _r: Acquirable = field(default_factory=Lock)
    _g: Acquirable = field(default_factory=Lock)
    _b: IntCounter = field(default_factory=IntCounter, init=False)


@dataclass
class WSLock(SyncWSLock):
    """The class for write-preferring shared locks.

    This class is designed to be used for threading.
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
class RSCondition(SyncSCondition):
    """The class for read-preferring shared condition variables.

    This class is designed to be used for threading.
    """

    _s: SAcquirable = field(default_factory=RSLock)
    _a: Waitable = field(default_factory=Condition)


@dataclass
class WSCondition(SyncSCondition):
    """The class for write-preferring shared condition variables.

    This class is designed to be used for threading.
    """

    _s: SAcquirable = field(default_factory=WSLock)
    _a: Waitable = field(default_factory=Condition)


@dataclass
class AcquirableDoor(UnhandledDoor[_T], SyncAcquirableDoor[_T]):
    """The class for acquirable doors.

    This class is designed to be used for threading.

    The door is initialized with the resource and corresponding
    primitive.

    The door can give access to the resource based on the desired
    operation.  When the user attempts to access the resource in a
    forbidden way or after its access is expired, an exception will
    be raised.
    """

    _primitive: Acquirable = field(default_factory=RLock)


@dataclass
class WaitableDoor(UnhandledDoor[_T], SyncWaitableDoor[_T]):
    """The class for waitable doors.

    This class is designed to be used for threading.

    The door is initialized with the resource and corresponding
    primitive.

    The door can give access to the resource based on the desired
    operation.  When the user attempts to access the resource in a
    forbidden way or after its access is expired, an exception will
    be raised.
    """

    _primitive: Waitable = field(default_factory=Condition)


@dataclass
class SAcquirableDoor(UnhandledDoor[_T], SyncSAcquirableDoor[_T]):
    """The class for shared acquirable doors.

    This class is designed to be used for threading.

    The door is initialized with the resource and corresponding
    primitive.

    The door can give access to the resource based on the desired
    operation.  When the user attempts to access the resource in a
    forbidden way or after its access is expired, an exception will
    be raised.
    """

    _primitive: SAcquirable = field(default_factory=WSLock)


@dataclass
class SWaitableDoor(UnhandledDoor[_T], SyncSWaitableDoor[_T]):
    """The class for shared waitable doors.

    This class is designed to be used for threading.

    The door is initialized with the resource and corresponding
    primitive.

    The door can give access to the resource based on the desired
    operation.  When the user attempts to access the resource in a
    forbidden way or after its access is expired, an exception will
    be raised.
    """

    _primitive: SWaitable = field(default_factory=WSCondition)
