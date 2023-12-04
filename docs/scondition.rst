Shared Condition
================

While not the primary focus of the library, Door also offer implementations of
read-preferring and write-preferring shared conditions (readers-writer
conditions).

The usual acquire/release/wait/notify interface as modelled by
:class:`door.primitives.Waitable` is not sufficient to describe the
functionalities of shared conditions. Therefore, for
:class:`door.primitives.SWaitable`, we expand the interface as follows:

- ``acquire-read``
- ``release-read``
- ``wait-read``
- ``wait-for-read``
- ``notify-read``
- ``notify-all-read``
- ``acquire-write``
- ``release-write``
- ``wait-write``
- ``wait-for-write``
- ``notify-write``
- ``notify-all-write``

We offer implementations for both synchronous and asynchronous programming.
These classes of shared conditions are available, for different use cases:

Read-preferring:

- :class:`door.threading2.RSCondition` for multithreading.
- :class:`door.multiprocessing2.RSCondition` for multiprocessing.
- :class:`door.asyncio2.RSCondition` for asynchronous programming.

Write-preferring:

- :class:`door.threading2.WSCondition` for multithreading.
- :class:`door.multiprocessing2.WSCondition` for multiprocessing.
- :class:`door.asyncio2.WSCondition` for asynchronous programming.
