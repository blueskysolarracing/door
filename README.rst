====
Door
====

Door is a comprehensive python library for synchronization proxies. Door's
reliability has been established through static type checking, extensive
doctests, and unit tests, achieving 83% code coverage.


Features
--------

- Synchronization proxies to enforce sound synchronous data access.

  - Supported scenarios:
  
    - Multithreading;
    - Asynchronous programming.

  - Supported primitives:
  
    - Lock;
    - RLock;
    - Condition;
    - Semaphore;
    - BoundedSemaphore;
    - RSLock (Read-preferring shared lock);
    - WSLock (Write-preferring shared lock);
    - et cetera.

- Shared lock (Readers-writer lock) implementations.

  - Supported scenarios:
  
    - Multithreading;
    - Multiprocessing;
    - Asynchronous programming.

Installation
------------

.. code-block:: bash

   pip install door

Usage
-----

Below shows a sample usage of Door.

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
