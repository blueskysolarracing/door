from dataclasses import dataclass
from unittest import main, TestCase
import multiprocessing
import threading

from door import multiprocessing2, threading2
from door.primitives import Primitive, FineGrainedPrimitive
from door.utilities import Door


class DoorTestCase(TestCase):
    def test_read_and_write(self) -> None:
        @dataclass
        class X:
            a: str = 'a'
            b: str = 'b'

        for primitive in (
                threading.Lock(),
                threading.RLock(),
                threading.Condition(),
                threading.Semaphore(),
                threading.BoundedSemaphore(),
                threading2.SLock(),
                multiprocessing.Lock(),
                multiprocessing.RLock(),
                multiprocessing.Condition(),
                multiprocessing.Semaphore(),
                multiprocessing.BoundedSemaphore(),
                multiprocessing2.SLock(),
        ):
            assert isinstance(primitive, Primitive | FineGrainedPrimitive)

            x = X()
            door = Door(x, primitive)

            with door.read() as resource:
                self.assertEqual(resource.a, 'a')

            self.assertRaises(ValueError, getattr, resource, 'a')
            self.assertRaises(ValueError, setattr, resource, 'a', 'A')

            with door.read() as resource:
                self.assertRaises(ValueError, setattr, resource, 'a', 'A')

            with door.write() as resource:
                resource.b = 'B'
                self.assertEqual(resource.b, 'B')
                self.assertEqual(resource.a, 'a')
                resource.a = 'A'
                self.assertEqual(resource.a, 'A')

            self.assertEqual(x, X('A', 'B'))


if __name__ == '__main__':
    main()  # pragma: no cover
