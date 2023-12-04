""":mod:`door.multiprocessing2` defines utilities for multiprocessing."""

from dataclasses import dataclass, field
from multiprocessing import Condition, Lock, RLock
from typing import TypeVar

from door.doors import (
    AcquirableDoor as SyncAcquirableDoor,
    HandledDoor,
    SAcquirableDoor as SyncSAcquirableDoor,
    SWaitableDoor as SyncSWaitableDoor,
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
from door.utilities import Handle as Handle, ValueCounter   # noqa: F401

_T = TypeVar('_T')


@dataclass
class RSLock(SyncRSLock):
    """The class for read-preferring shared locks.

    This class is designed to be used for multiprocessing.

    The implementations in this library is read-preferring and follow
    the pseudocode in Concurrent Programming: Algorithms, Principles,
    and Foundations by Michel Raynal.
    """

    _r: Acquirable = field(default_factory=Lock)
    _g: Acquirable = field(default_factory=Lock)
    _b: ValueCounter = field(default_factory=ValueCounter, init=False)


@dataclass
class WSLock(SyncWSLock):
    """The class for write-preferring shared locks.

    This class is designed to be used for multiprocessing.
    """

    _g: Waitable = field(default_factory=Condition)
    _num_writers_waiting: ValueCounter = field(
        default_factory=ValueCounter,
        init=False,
    )
    _writer_active: ValueCounter = field(
        default_factory=ValueCounter,
        init=False,
    )
    _num_readers_active: ValueCounter = field(
        default_factory=ValueCounter,
        init=False,
    )


@dataclass
class RSCondition(SyncSCondition):
    """The class for read-preferring shared condition variables.

    This class is designed to be used for multiprocessing.
    """

    _s: SAcquirable = field(default_factory=RSLock)
    _a: Waitable = field(default_factory=Condition)


@dataclass
class WSCondition(SyncSCondition):
    """The class for write-preferring shared condition variables.

    This class is designed to be used for multiprocessing.
    """

    _s: SAcquirable = field(default_factory=WSLock)
    _a: Waitable = field(default_factory=Condition)


@dataclass
class AcquirableDoor(HandledDoor[_T], SyncAcquirableDoor[_T]):
    """The class for acquirable doors.

    This class is designed to be used for multiprocessing.

    The door is initialized with the resource and corresponding
    primitive.

    The door can give access to the resource based on the desired
    operation.  When the user attempts to access the resource in a
    forbidden way or after its access is expired, an exception will
    be raised.
    """

    _primitive: Acquirable = field(default_factory=RLock)


@dataclass
class WaitableDoor(HandledDoor[_T], SyncWaitableDoor[_T]):
    """The class for waitable doors.

    This class is designed to be used for multiprocessing.

    The door is initialized with the resource and corresponding
    primitive.

    The door can give access to the resource based on the desired
    operation.  When the user attempts to access the resource in a
    forbidden way or after its access is expired, an exception will
    be raised.
    """

    _primitive: Waitable = field(default_factory=Condition)


@dataclass
class SAcquirableDoor(HandledDoor[_T], SyncSAcquirableDoor[_T]):
    """The class for shared acquirable doors.

    This class is designed to be used for multiprocessing.

    The door is initialized with the resource and corresponding
    primitive.

    The door can give access to the resource based on the desired
    operation.  When the user attempts to access the resource in a
    forbidden way or after its access is expired, an exception will
    be raised.
    """

    _primitive: SAcquirable = field(default_factory=WSLock)


@dataclass
class SWaitableDoor(HandledDoor[_T], SyncSWaitableDoor[_T]):
    """The class for shared waitable doors.

    This class is designed to be used for multiprocessing.

    The door is initialized with the resource and corresponding
    primitive.

    The door can give access to the resource based on the desired
    operation.  When the user attempts to access the resource in a
    forbidden way or after its access is expired, an exception will
    be raised.
    """

    _primitive: SWaitable = field(default_factory=WSCondition)
