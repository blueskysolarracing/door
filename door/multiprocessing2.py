""":mod:`door.multiprocessing2` defines utilities for multiprocessing."""

from dataclasses import dataclass, field
from multiprocessing import Condition, RLock

from door.primitives import (
    Acquirable,
    RSLock as SyncRSLock,
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

    _r: Acquirable = field(default_factory=RLock, init=False)
    _g: Acquirable = field(default_factory=RLock, init=False)


@dataclass
class WSLock(SyncWSLock):
    """The class for write-preferring shared locks.

    This class is designed to be used for multiprocessing.
    """

    _g: Waitable = field(default_factory=Condition, init=False)
