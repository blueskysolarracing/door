from dataclasses import dataclass
from threading import (
    BoundedSemaphore,
    Condition,
    Lock,
    RLock,
    Semaphore,
    Thread,
)
from typing import Any
from unittest import main, TestCase

from door.doors import (
    AcquirableDoor,
    SAcquirableDoor,
    SWaitableDoor,
    WaitableDoor,
)
from door.primitives import Acquirable, SAcquirable, SWaitable, Waitable
from door.threading2 import (
    RSCondition,
    RSLock,
    WSCondition,
    WSLock,
)


class SyncTestCase(TestCase):
    def test_acquirable(self) -> None:
        @dataclass
        class Resource:
            key: Any = 'value'

        for primitive in (
                Lock(),
                RLock(),
                Condition(),
                Semaphore(),
                BoundedSemaphore(),
        ):
            assert isinstance(primitive, Acquirable)

            resource = Resource()
            door = AcquirableDoor(resource, primitive)

            with door() as proxy:
                self.assertEqual(proxy.key, 'value')
                proxy.key = 'VALUE'
                self.assertEqual(proxy.key, 'VALUE')

            self.assertRaises(ValueError, getattr, proxy, 'key')
            self.assertRaises(ValueError, setattr, proxy, 'key', 'value')
            self.assertEqual(resource, Resource('VALUE'))

    def test_waitable(self) -> None:
        @dataclass
        class Flags:
            ready: bool = False
            processed: bool = False

        def worker() -> None:
            with door() as proxy:
                door.wait_for(lambda: proxy.ready)

                proxy.processed = True

                door.notify()

        for primitive in (
                Condition(),
        ):
            assert isinstance(primitive, Waitable)

            thread = Thread(target=worker)
            door = WaitableDoor(Flags(), primitive)

            thread.start()

            with door() as proxy:
                proxy.ready = True

                door.notify()

            with door() as proxy:
                door.wait_for(lambda: proxy.processed)

                self.assertTrue(proxy.processed)

            thread.join()

    def test_shared_acquirable_0(self) -> None:
        @dataclass
        class Resource:
            key: Any = 'value'

        for primitive in (
                RSLock(),
                WSLock(),
                RSCondition(),
                WSCondition(),
        ):
            assert isinstance(primitive, SAcquirable)

            resource = Resource()
            door = SAcquirableDoor(resource, primitive)

            with door.read() as proxy:
                self.assertEqual(proxy.key, 'value')
                self.assertRaises(ValueError, setattr, proxy, 'key', 'VALUE')

            with door.write() as proxy:
                self.assertEqual(proxy.key, 'value')
                proxy.key = 'VALUE'
                self.assertEqual(proxy.key, 'VALUE')

            self.assertRaises(ValueError, getattr, proxy, 'key')
            self.assertRaises(ValueError, setattr, proxy, 'key', 'value')
            self.assertEqual(resource, Resource('VALUE'))

    def test_shared_acquirable_1(self) -> None:
        ITER_COUNT = 1000
        PARALLELISM_COUNT = 10

        @dataclass
        class Counter:
            value: int = 0

        def read() -> int:
            with door.read() as proxy:
                return proxy.value

        def write() -> None:
            with door.write() as proxy:
                proxy.value += 1

        def target() -> None:
            for _ in range(ITER_COUNT):
                write()
                read()

        for primitive in (
                RSLock(),
                WSLock(),
                RSCondition(),
                WSCondition(),
        ):
            assert isinstance(primitive, SAcquirable)

            counter = Counter()
            door = SAcquirableDoor(counter, primitive)
            threads = []

            for _ in range(PARALLELISM_COUNT):
                thread = Thread(target=target)

                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

            with door.read() as proxy:
                self.assertEqual(proxy.value, ITER_COUNT * PARALLELISM_COUNT)

    def test_shared_waitable(self) -> None:
        @dataclass
        class Flags:
            ready: bool = False
            processed: bool = False

        def worker() -> None:
            with door.write() as proxy:
                door.wait_for_write(lambda: proxy.ready)

                proxy.processed = True

                door.notify_write()

        for primitive in (
                RSCondition(),
                WSCondition(),
        ):
            assert isinstance(primitive, SWaitable)

            thread = Thread(target=worker)
            door = SWaitableDoor(Flags(), primitive)

            thread.start()

            with door.write() as proxy:
                proxy.ready = True

                door.notify_write()

            with door.read() as proxy:
                door.wait_for_read(lambda: proxy.processed)

                self.assertTrue(proxy.processed)

            thread.join()


if __name__ == '__main__':
    main()  # pragma: no cover
