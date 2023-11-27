Door
====

The main feature of the Door library is its novel data access system. It
enforces synchronous data access.

Typically, when locks are used, there is a risk that, due to programmer error,
a race condition is introduced by improperly accessing data.

:class:`door.utilities.Door` ensures that read/write access to the data is always enforced, thus
making the code more robust.

:class:`door.utilities.Door` supports the following scenarios:

- Multithreading;
- Multiprocessing;
- Asynchronous programming.

As long as the primitive implements ``acquire`` and ``release`` methods, they
are compatible with doors.

:class:`door.utilities.Door` supports the following primitives:

- Lock;
- RLock;
- Condition;
- Semaphore;
- BoundedSemaphore;
- SLock (Readers-writer lock);
- et cetera.

Below shows sample usages of :class:`door.utilities.Door`.

.. code-block:: pycon

   >>> from dataclasses import dataclass
   >>> from door import Door
   >>> from threading import RLock
   >>> @dataclass
   ... class X:
   ...     a: str = 'a'
   ...     b: str = 'b'
   ...
   >>> x = X()
   >>> x
   X(a='a', b='b')
   >>> x.a
   'a'
   >>> x.b
   'b'
   >>> door = Door(x, RLock())
   >>> with door.read() as resource:
   ...     resource.a
   ...
   'a'
   >>> resource.a
   Traceback (most recent call last):
       ...
   ValueError: no read permission
   >>> resource.a = 'A'
   Traceback (most recent call last):
       ...
   ValueError: no write permission
   >>> with door.read() as resource:
   ...     resource.a = 'A'
   ...
   Traceback (most recent call last):
       ...
   ValueError: no write permission
   >>> with door.write() as resource:
   ...     resource.b = 'B'
   ...     resource.b
   ...     resource.a
   ...     resource.a = 'A'
   ...     resource.a
   ...
   'B'
   'a'
   'A'
   >>> x
   X(a='A', b='B')
   >>> x.a
   'A'
   >>> x.b
   'B'

Note that context only allows for allowed operations, with
:meth:`door.utilities.door.read` only allowing read operations and
:meth:`door.utilities.door.write` allowing both read and write operations. After
the context ends, the data becomes inaccessible.

With asynchronous programming, you can achieve identical behaviors as shown:

.. code-block:: python

   from asyncio import Lock, run
   from door import AsyncDoor
   

   async def main():
       door = AsyncDoor(..., Lock())
   
       ...
   
       async with door.read() as resource:
           ...
   
       ...
   
       async with door.write() as resource:
           ...

       ...
   
   
   if __name__ == '__main__':
       run(main())
