=========
Changelog
=========

All notable changes to this project will be documented in this file.

Version 0.0.3 (December 3, 2023)
--------------------------------

**Changes**

- Doors now compatible with multiprocessing.
- Each door class now in ``door.threading2``, ``door.asyncio2``, and
  ``door.multiprocessing2``.

**Additions**

- Add ``door.utilities.Handle`` for object sharing across processes.

Version 0.0.2 (November 30, 2023)
---------------------------------

**Changes**

- Split all ``SLock`` to ``RSLock`` and ``WSLock``.
- Rename ``door.acquire`` to ``door.__call__``, ``door.acquire_read`` to
  ``door.read``, ``door.acquire_write`` to ``door.write``.

**Additions**

- Add shared waitables.

Version 0.0.1 (November 29, 2023)
---------------------------------

**Changes**

- Rename ``door.utilities.Resource`` to ``door.utilities.Proxy``.
- Separate and move ``door.utilities.Door`` into ``door.doors.AcquirableDoor``
  and ``door.doors.SAcquirableDoor``.
- Separate and move ``door.utilities.AsyncDoor`` into
  ``door.doors.AsyncAcquirableDoor`` and ``door.doors.AsyncSAcquirableDoor``.
- Remove ``door.primitives.AsyncPrimitive`` and
  ``door.primitives.FineGrainedAsyncPrimitive``.
- Fix documentations.

**Additions**

- Add ``door.primitives.Waitable``, ``door.doors.WaitableDoor``,
  ``door.doors.AsyncWaitableDoor`` for conditional variables.
- Add ``door.utilities.await_if_available``.

Version 0.0.0 (November 27, 2023)
---------------------------------

**Initial Release**
