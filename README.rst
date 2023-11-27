====
Door
====

Door is a comprehensive python library for advanced synchronization mechanisms.
Door's reliability has been established through static type checking, extensive
doctests, and unit tests, achieving 100% code coverage.


Features
--------

- Data access system to enforce sound synchronous data access.
- SLock (Readers-writer lock) implementations.
- Supported scenarios:

  - Multithreading;
  - Multiprocessing;
  - Asynchronous programming.

- Supported primitives:

  - Lock;
  - RLock;
  - Condition;
  - Semaphore;
  - BoundedSemaphore;
  - SLock (Readers-writer lock);
  - et cetera.

Installation
------------

.. code-block:: bash

   pip install door

Usage
-----

Below shows a sample usage of Door.

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
