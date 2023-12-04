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
are compatible with acquirable doors.

Supports:

- Lock;
- RLock;
- Condition;
- Semaphore;
- BoundedSemaphore;
- et cetera.

Implementations:

- :class:`door.threading2.AcquirableDoor`
- :class:`door.multiprocessing2.AcquirableDoor`
- :class:`door.asyncio2.AcquirableDoor`

As long as the primitive implements :class:`door.primitives.Waitable`, they
are compatible with waitable doors.

Supports:

- Condition;
- et cetera.

Implementations:

- :class:`door.threading2.WaitableDoor`
- :class:`door.multiprocessing2.WaitableDoor`
- :class:`door.asyncio2.WaitableDoor`

As long as the primitive implements :class:`door.primitives.SAcquirable`, they
are compatible with shared acquirable doors.

- RSLock (Read-preferring shared lock);
- WSLock (Write-preferring shared lock);
- RSCondition (Read-preferring shared condition variables);
- WSCondition (Write-preferring shared condition variables);
- et cetera.

Implementations:

- :class:`door.threading2.SAcquirableDoor`
- :class:`door.multiprocessing2.SAcquirableDoor`
- :class:`door.asyncio2.SAcquirableDoor`

As long as the primitive implements :class:`door.primitives.SWaitable`, they
are compatible with shared waitable doors.

- RSCondition (Read-preferring shared condition variables);
- WSCondition (Write-preferring shared condition variables);
- et cetera.

Implementations:

- :class:`door.threading2.SWaitableDoor`
- :class:`door.multiprocessing2.SWaitableDoor`
- :class:`door.asyncio2.SWaitableDoor`

Below shows sample usages of doors.

First, initialize a resource.

.. code-block:: pycon

   >>> from dataclasses import dataclass
   >>> @dataclass
   ... class Resource:
   ...     key: str = 'value'
   ...
   >>> resource = Resource()
   >>> resource
   Resource(key='value')
   >>> resource.key
   'value'

Now, let's use acquirable door.

.. code-block:: pycon

   >>> from door.threading2 import AcquirableDoor
   >>> door = AcquirableDoor(resource)
   >>> with door() as proxy:
   ...     proxy.key
   ...     proxy.key = 'VALUE'
   ...     proxy.key
   ...
   'value'
   'VALUE'

Outside, the proxy is closed.

.. code-block:: pycon

   >>> proxy.key
   Traceback (most recent call last):
       ...
   ValueError: no read permission
   >>> proxy.key = 'value'
   Traceback (most recent call last):
       ...
   ValueError: no write permission

Check the value of resource.

.. code-block:: pycon

   >>> resource
   Resource(key='VALUE')
   >>> resource.key
   'VALUE'

Reset the resource.

.. code-block:: pycon

   >>> resource = Resource()
   >>> resource
   Resource(key='value')
   >>> resource.key
   'value'

We can also use shared acquirable doors. Acquirable doors allow client to
specify the type of operation they want.

.. code-block:: pycon

   >>> from door.threading2 import SAcquirableDoor
   >>> door = SAcquirableDoor(resource)
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
