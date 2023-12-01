""":mod:`door.multiprocessing2` defines utilities for multiprocessing."""

from dataclasses import dataclass, field
from multiprocessing import Condition, Lock

from door.primitives import (
    Acquirable,
    RSLock as SyncRSLock,
    SAcquirable,
    SCondition as SyncSCondition,
    Waitable,
    WSLock as SyncWSLock,
)


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


@dataclass
class WSLock(SyncWSLock):
    """The class for write-preferring shared locks.

    This class is designed to be used for multiprocessing.
    """

    _g: Waitable = field(default_factory=Condition)


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
