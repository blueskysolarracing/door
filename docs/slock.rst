Shared Lock
===========

While not the primary focus of the library, Door also offer implementations of
read-preferring and write-preferring shared locks (readers-writer locks).

The read-preferring implementations in this library follow the pseudocode in
Concurrent Programming: Algorithms, Principles, and Foundations by Michel
Raynal.

The usual acquire/release interface as modelled by
:class:`door.primitives.Acquirable` is not sufficient to describe the
functionalities of shared locks. Therefore, for
:class:`door.primitives.SAcquirable`, we expand the interface as follows:

- ``acquire-read``
- ``release-read``
- ``acquire-write``
- ``release-write``

We offer implementations for both synchronous and asynchronous programming.
These classes of shared locks are available, for different use cases:

- :class:`door.threading2.RSLock` for multithreading.
- :class:`door.multiprocessing2.RSLock` for multiprocessing.
- :class:`door.asyncio2.RSLock` for asynchronous programming.
- :class:`door.threading2.WSLock` for multithreading.
- :class:`door.multiprocessing2.WSLock` for multiprocessing.
- :class:`door.asyncio2.WSLock` for asynchronous programming.
