Door
====

The main feature of the Door library is its synchronization proxy
implementation.

Typically, when locks are used, there is a risk that, due to programmer error,
a race condition is introduced by improperly accessing data.

Doors support the following scenarios:

- Multithreading;
- Multiprocessing;
- Asynchronous programming.

As long as the primitive implements :class:`door.primitives.Acquirable`, they
are compatible with :class:`door.doors.AcquirableDoor`.

- Lock;
- RLock;
- Condition;
- Semaphore;
- BoundedSemaphore;
- et cetera.

As long as the primitive implements :class:`door.primitives.Waitable`, they
are compatible with :class:`door.doors.WaitableDoor`.

- Condition;
- et cetera.

As long as the primitive implements :class:`door.primitives.SAcquirable`, they
are compatible with :class:`door.doors.SAcquirableDoor`.

- RSLock (Read-preferring shared lock);
- et cetera.

Below shows sample usages of doors.

.. code-block:: pycon

   >>> @dataclass
   ... class Resource:
   ...     key: Any = 'value'
   ...
   >>> resource = Resource()
   >>> resource
   Resource(key='value')
   >>> resource.key
   'value'
   >>> from threading import Lock
   >>> door = AcquirableDoor(resource, Lock())

   >>> with door() as proxy:
   ...     proxy.key
   ...     proxy.key = 'VALUE'
   ...     proxy.key
   ...
   'value'
   'VALUE'
   >>> proxy.key
   Traceback (most recent call last):
       ...
   ValueError: no read permission
   >>> proxy.key = 'value'
   Traceback (most recent call last):
       ...
   ValueError: no write permission
   >>> resource
   Resource(key='VALUE')
   >>> resource.key
   'VALUE'

   >>> resource = Resource()
   >>> resource
   Resource(key='value')
   >>> resource.key
   'value'
   >>> from door.threading2 import RSLock
   >>> door = SAcquirableDoor(resource, RSLock())
   >>> with door.read() as proxy:
   ...     proxy.key
   ...
   'value'
   >>> with door.read() as proxy:
   ...     proxy.key = 'VALUE'
   ...
   Traceback (most recent call last):
       ...
   ValueError: no write permission
   >>> with door.write() as proxy:
   ...     proxy.key
   ...     proxy.key = 'VALUE'
   ...     proxy.key
   ...
   'value'
   'VALUE'
   >>> proxy.key
   Traceback (most recent call last):
       ...
   ValueError: no read permission
   >>> proxy.key = 'value'
   Traceback (most recent call last):
       ...
   ValueError: no write permission
   >>> resource
   Resource(key='VALUE')
   >>> resource.key
   'VALUE'
