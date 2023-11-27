""":mod:`door.threading` defines utilities for multithreading."""

from dataclasses import dataclass, field
from threading import RLock

from door.primitives import Primitive, SLock as SyncSLock


@dataclass
class SLock(SyncSLock):
    """The class for shared locks.

    This class is designed to be used for multithreading.

    The implementations in this library is read-preferring and follow
    the pseudocode in Concurrent Programming: Algorithms, Principles,
    and Foundations by Michel Raynal.
    """

    _r: Primitive = field(default_factory=RLock, init=False)
    _g: Primitive = field(default_factory=RLock, init=False)
