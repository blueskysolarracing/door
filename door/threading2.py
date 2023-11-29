""":mod:`door.threading2` defines utilities for multithreading."""

from dataclasses import dataclass, field
from threading import RLock

from door.primitives import Acquirable, SLock as SyncSLock


@dataclass
class SLock(SyncSLock):
    """The class for shared locks.

    This class is designed to be used for multithreading.

    The implementations in this library is read-preferring and follow
    the pseudocode in Concurrent Programming: Algorithms, Principles,
    and Foundations by Michel Raynal.
    """

    _r: Acquirable = field(default_factory=RLock, init=False)
    _g: Acquirable = field(default_factory=RLock, init=False)
