Handle
======

Another main feature of ``door`` is sharing objects across multiple processes.

Note that you don't need this for threading or asyncio.

Normally, in Python, processes have separate memory spaces.

.. code-block:: pycon

   >>> from multiprocessing import Process
   >>> from door.utilities import Handle
   >>> obj = []
   >>> def before(obj):
   ...     obj.append('Hello, world!')
   ...     obj.append(-1)
   ... 
   >>> process = Process(target=before, args=(obj,))
   >>> process.start()
   >>> process.join()
   >>> obj
   []

With handle, sharing objects are made easier.

.. code-block:: pycon

   >>> handle = Handle([])
   >>> def after(handle):
   ...     obj = handle.get()
   ...     obj.append('Hello, world!')
   ...     obj.append(-1)
   ...     handle.set(obj)
   ... 
   >>> process = Process(target=after, args=(handle,))
   >>> process.start()
   >>> process.join()
   >>> handle.get()
   ['Hello, world!', -1]
   >>> handle.unlink()

When using multiprocessing, handle's functionalities are integrated with door.

.. code-block:: pycon

   >>> from door.multiprocessing2 import AcquirableDoor
   >>> from dataclasses import dataclass
   >>> @dataclass
   ... class Resource:
   ...     key: str = 'value'
   ... 
   >>> resource = Resource()
   >>> handle = Handle(resource)
   >>> door = AcquirableDoor(handle)
   >>> def change(door):
   ...     with door() as proxy:
   ...         proxy.key = 'VALUE'
   ... 
   >>> process = Process(target=change, args=(door,))
   >>> process.start()
   >>> process.join()
   >>> handle.get()
   Resource(key='VALUE')
   >>> handle.unlink()

Note that after usage, handle must be unlinked. Only one process needs to call
:meth:`door.utilities.Handle.unlink`.
