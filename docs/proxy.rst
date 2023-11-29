Proxy
=====

:class:`door.utilities.Proxy` is a protection proxy around any desired object to
facilitate enforcement of sound access. This class is used by doors.

A sample usage of :class:`door.utilities.Proxy` is shown below:

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
   >>> proxy = Proxy(resource, Proxy.Mode.READ)
   >>> proxy.key
   'value'
   >>> proxy.key = 'VALUE'
   Traceback (most recent call last):
       ...
   ValueError: no write permission
   >>> proxy.close()
   >>> proxy = Proxy(resource, Proxy.Mode.WRITE)
   >>> proxy.key = 'VALUE'
   >>> proxy.key
   Traceback (most recent call last):
       ...
   ValueError: no read permission
   >>> proxy.close()
   >>> proxy = Proxy(resource, Proxy.Mode.READ | Proxy.Mode.WRITE)
   >>> proxy.key
   'VALUE'
   >>> proxy.key = 'value'
   >>> proxy.key
   'value'
   >>> proxy.close()
   >>> proxy.key
   Traceback (most recent call last):
       ...
   ValueError: no read permission
   >>> proxy.key = 'VALUE'
   Traceback (most recent call last):
       ...
   ValueError: no write permission
   >>> resource
   Resource(key='value')
   >>> resource.key
   'value'
