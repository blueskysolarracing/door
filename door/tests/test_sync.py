from dataclasses import dataclass
from typing import Any
from unittest import main, TestCase
import multiprocessing
import threading

from door import multiprocessing2, threading2
from door.primitives import Acquirable, SAcquirable
from door.doors import AcquirableDoor, SAcquirableDoor


class SyncTestCase(TestCase):
    def test_acquirable(self) -> None:
        @dataclass
        class Resource:
            key: Any = 'value'

        for primitive in (
                threading.Lock(),
                threading.RLock(),
                threading.Condition(),
                threading.Semaphore(),
                threading.BoundedSemaphore(),
                multiprocessing.Lock(),
                multiprocessing.RLock(),
                multiprocessing.Condition(),
                multiprocessing.Semaphore(),
                multiprocessing.BoundedSemaphore(),
        ):
            assert isinstance(primitive, Acquirable)

            resource = Resource()
            door = AcquirableDoor(resource, primitive)

            with door.acquire() as proxy:
                self.assertEqual(proxy.key, 'value')
                proxy.key = 'VALUE'
                self.assertEqual(proxy.key, 'VALUE')

            self.assertRaises(ValueError, getattr, proxy, 'key')
            self.assertRaises(ValueError, setattr, proxy, 'key', 'value')
            self.assertEqual(resource, Resource('VALUE'))

    def test_shared_acquirable(self) -> None:
        @dataclass
        class Resource:
            key: Any = 'value'

        for primitive in (
                threading2.RSLock(),
                threading2.WSLock(),
                multiprocessing2.RSLock(),
                multiprocessing2.WSLock(),
        ):
            assert isinstance(primitive, SAcquirable)

            resource = Resource()
            door = SAcquirableDoor(resource, primitive)

            with door.acquire_read() as proxy:
                self.assertEqual(proxy.key, 'value')
                self.assertRaises(ValueError, setattr, proxy, 'key', 'VALUE')

            with door.acquire_write() as proxy:
                self.assertEqual(proxy.key, 'value')
                proxy.key = 'VALUE'
                self.assertEqual(proxy.key, 'VALUE')

            self.assertRaises(ValueError, getattr, proxy, 'key')
            self.assertRaises(ValueError, setattr, proxy, 'key', 'value')
            self.assertEqual(resource, Resource('VALUE'))


if __name__ == '__main__':
    main()  # pragma: no cover
