Proxy
=====

:class:`door.utilities.Proxy` is a protection proxy around any desired object to
facilitate enforcement of sound access. This class is used by doors.

A sample usage of :class:`door.utilities.Proxy` is shown below:

First, create a resource.

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

Next, wrap it in a proxy. Let us do read-only first.

.. code-block:: pycon

   >>> from door.utilities import Proxy
   >>> proxy = Proxy(resource, Proxy.Mode.READ)
   >>> proxy.key
   'value'
   >>> proxy.key = 'VALUE'
   Traceback (most recent call last):
       ...
   ValueError: no write permission
   >>> proxy.close()

When closed, all operations are forbidden.

.. code-block:: pycon

   >>> proxy.key
   Traceback (most recent call last):
       ...
   ValueError: no read permission
   >>> proxy.key = 'VALUE'
   Traceback (most recent call last):
       ...
   ValueError: no write permission

Again, wrap it in a proxy, this time, write-only.

.. code-block:: pycon

   >>> proxy = Proxy(resource, Proxy.Mode.WRITE)
   >>> proxy.key = 'VALUE'
   >>> proxy.key
   Traceback (most recent call last):
       ...
   ValueError: no read permission
   >>> proxy.close()

Finally, wrap it read-write proxy.

.. code-block:: pycon

   >>> proxy = Proxy(resource, Proxy.Mode.READ | Proxy.Mode.WRITE)
   >>> proxy.key
   'VALUE'
   >>> proxy.key = 'value'
   >>> proxy.key
   'value'
   >>> proxy.close()

Check the final value.

.. code-block:: pycon

   >>> resource
   Resource(key='value')
   >>> resource.key
   'value'
