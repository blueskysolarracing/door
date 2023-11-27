Resource
========

:class:`door.utilities.Resource` is a wrapper around any desired object to
facilitate enforcement of sound access. This class is used by doors.

A sample usage of :class:`door.utilities.Resource` is shown below:

.. code-block:: pycon

   >>> from dataclasses import dataclass
   >>> from door import Resource
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
   >>> resource = Resource(x, Resource.Mode.READ)
   >>> resource.a
   'a'
   >>> resource.a = 'A'
   Traceback (most recent call last):
       ...
   ValueError: no write permission
   >>> resource.close()
   >>> resource.a
   Traceback (most recent call last):
       ...
   ValueError: no read permission
   >>> resource.a = 'A'
   Traceback (most recent call last):
       ...
   ValueError: no write permission
   >>> resource = Resource(x, Resource.Mode.WRITE)
   >>> resource.b = 'B'
   >>> resource.b
   Traceback (most recent call last):
       ...
   ValueError: no read permission
   >>> resource.close()
   >>> resource = Resource(x, Resource.Mode.READ | Resource.Mode.WRITE)
   >>> resource.b
   'B'
   >>> resource.a
   'a'
   >>> resource.a = 'A'
   >>> resource.a
   'A'
   >>> resource.close()
   >>> x
   X(a='A', b='B')
   >>> x.a
   'A'
   >>> x.b
   'B'
