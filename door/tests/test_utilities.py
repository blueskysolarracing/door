from dataclasses import dataclass
from typing import Any
from unittest import main, TestCase

from door.utilities import Proxy


class ResourceTestCase(TestCase):
    def test_getattr_0(self) -> None:
        @dataclass
        class Resource:
            key: Any = 'value'

            def get(self) -> Any:
                return self.key

            def set(self, value: Any) -> None:
                self.key = value

        resource = Resource()

        proxy = Proxy(resource, Proxy.Mode.READ)
        proxy.get()
        self.assertRaises(ValueError, proxy.set, 'value')
        proxy.close()

        proxy = Proxy(resource, Proxy.Mode.READ | Proxy.Mode.WRITE)
        proxy.get()
        proxy.set('value')
        proxy.close()

        proxy = Proxy(resource, Proxy.Mode.READ | Proxy.Mode.WRITE)
        get = proxy.get
        set_ = proxy.set
        proxy.close()

        self.assertRaises(ValueError, get)
        self.assertRaises(ValueError, set_, 'value')

    def test_getattr_1(self) -> None:
        proxy = Proxy(list[Any](), Proxy.Mode.READ)
        self.assertRaises(ValueError, getattr, proxy, 'append')
        proxy.close()


if __name__ == '__main__':
    main()  # pragma: no cover
