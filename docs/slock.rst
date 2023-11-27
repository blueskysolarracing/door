Shared Lock
===========

While not the primary focus of the library, Door also offer implementations of
read-preferring shared locks (readers-writer locks).

The implementations in this library follow the pseudocode in Concurrent
Programming: Algorithms, Principles, and Foundations by Michel Raynal.

The usual acquire/release interface as modelled by
:class:`door.primitives.Primitive` is not sufficient to describe the
functionalities of shared locks. Therefore, we expand the interface as follows:

- acquire-read
- release-read
- acquire-write
- release-write

We offer two implementations, one for synchronous and another for asynchronous
programming. Three classes of shared locks are available, for different use
cases:

- :class:`door.threading2.SLock` for multithreading
- :class:`door.multiprocessing2.SLock` for multiprocessing
- :class:`door.asyncio2.SLock` for asynchronous programming
