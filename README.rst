====
Door
====

Door is a comprehensive python library for synchronization proxies. Door's
reliability has been established through static type checking, extensive
doctests, and unit tests, achieving 93% code coverage.


Features
--------

- Share objects across processes without queues or pipes.
- Synchronization proxies to enforce sound synchronous data access.

  - Supported scenarios:
  
    - Threading;
    - Multiprocessing;
    - Asynchronous programming.

- Shared lock (Readers-writer lock) implementations.
- Shared condition variable (Readers-writer condition variables)
  implementations.

Installation
------------

.. code-block:: bash

   pip install door

Usage
-----

Below shows a sample usage of Door.

.. code-block:: pycon

   >>> from dataclasses import dataclass
   >>> from multiprocessing import Process
   >>> from door.multiprocessing2 import Handle, SAcquirableDoor
   >>> @dataclass
   ... class Resource:
   ...     key: str = 'value'
   ... 
   >>> handle = Handle(Resource())
   >>> handle.get()
   Resource(key='value')
   >>> door = SAcquirableDoor(handle)
   >>> def func(door):
   ...     with door.write() as proxy:
   ...         proxy.key = 'VALUE'
   ... 
   >>> process = Process(target=func, args=(door,))
   >>> process.start()
   >>> process.join()
   >>> handle.get()
   Resource(key='VALUE')
   >>> handle.unlink()

Testing and Validation
----------------------

Door has extensive test coverage, passes mypy static type checking with
strict parameter, and has been validated through extensive use in real-life
scenarios.

Contributing
------------

Contributions are welcome! Please read our Contributing Guide for more
information.

License
-------

Door is distributed under the MIT license.
