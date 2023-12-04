from dataclasses import dataclass
from multiprocessing import (
    BoundedSemaphore,
    Condition,
    Lock,
    RLock,
    Semaphore,
    Process,
)
from unittest import main, TestCase

from door.primitives import Acquirable, SAcquirable, SWaitable, Waitable
from door.multiprocessing2 import (
    AcquirableDoor,
    Handle,
    RSCondition,
    RSLock,
    SAcquirableDoor,
    SWaitableDoor,
    WaitableDoor,
    WSCondition,
    WSLock,
)


class MultiprocessingTestCase(TestCase):
    @dataclass
    class Resource:
        key: str = 'value'

    @dataclass
    class Flags:
        ready: bool = False
        processed: bool = False

    @dataclass
    class Counter:
        value: int = 0

    def test_handled(self) -> None:
        self.assertRaises(ValueError, AcquirableDoor, None, Lock())

    def test_acquirable(self) -> None:
        for primitive in (
                Lock(),
                RLock(),
                Condition(),
                Semaphore(),
                BoundedSemaphore(),
        ):
            assert isinstance(primitive, Acquirable)

            handle = Handle(self.Resource())
            door = AcquirableDoor[MultiprocessingTestCase.Resource](
                handle,
                primitive,
            )

            with door() as proxy:
                self.assertEqual(proxy.key, 'value')
                proxy.key = 'VALUE'
                self.assertEqual(proxy.key, 'VALUE')

            self.assertRaises(ValueError, getattr, proxy, 'key')
            self.assertRaises(ValueError, setattr, proxy, 'key', 'value')
            self.assertEqual(handle.get(), self.Resource('VALUE'))
            handle.unlink()

    def test_waitable(self) -> None:
        def worker() -> None:  # pragma: no cover
            with door() as proxy:
                while not proxy.ready:
                    door.wait()

                proxy.processed = True

                door.notify()

        for primitive in (
                Condition(),
        ):
            assert isinstance(primitive, Waitable)

            handle = Handle(self.Flags())
            door = WaitableDoor[MultiprocessingTestCase.Flags](
                handle,
                primitive,
            )
            process = Process(target=worker)

            process.start()

            with door() as proxy:
                proxy.ready = True

                door.notify()

            with door() as proxy:
                while not proxy.processed:
                    door.wait()

                self.assertTrue(proxy.processed)

            process.join()
            handle.unlink()

    def test_shared_acquirable_0(self) -> None:
        for primitive in (
                RSLock(),
                WSLock(),
                RSCondition(),
                WSCondition(),
        ):
            assert isinstance(primitive, SAcquirable)

            handle = Handle(self.Resource())
            door = SAcquirableDoor[MultiprocessingTestCase.Resource](
                handle,
                primitive,
            )

            with door.read() as proxy:
                self.assertEqual(proxy.key, 'value')
                self.assertRaises(ValueError, setattr, proxy, 'key', 'VALUE')

            with door.write() as proxy:
                self.assertEqual(proxy.key, 'value')
                proxy.key = 'VALUE'
                self.assertEqual(proxy.key, 'VALUE')

            self.assertRaises(ValueError, getattr, proxy, 'key')
            self.assertRaises(ValueError, setattr, proxy, 'key', 'value')
            self.assertEqual(handle.get(), self.Resource('VALUE'))
            handle.unlink()

    def test_shared_acquirable_1(self) -> None:
        ITER_COUNT = 1000
        PARALLELISM_COUNT = 10

        def read() -> int:  # pragma: no cover
            with door.read() as proxy:
                return proxy.value

        def write() -> None:  # pragma: no cover
            with door.write() as proxy:
                proxy.value += 1

        def target() -> None:  # pragma: no cover
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

            handle = Handle(self.Counter())
            door = SAcquirableDoor[MultiprocessingTestCase.Counter](
                handle,
                primitive,
            )
            processs = []

            for _ in range(PARALLELISM_COUNT):
                process = Process(target=target)

                process.start()
                processs.append(process)

            for process in processs:
                process.join()

            self.assertEqual(
                handle.get().value,
                ITER_COUNT * PARALLELISM_COUNT,
            )

            handle.unlink()

    def test_shared_waitable(self) -> None:
        def worker() -> None:  # pragma: no cover
            with door.write() as proxy:
                while not proxy.ready:
                    door.wait_write()

                proxy.processed = True

                door.notify_write()

        for primitive in (
                RSCondition(),
                WSCondition(),
        ):
            assert isinstance(primitive, SWaitable)

            handle = Handle(self.Flags())
            door = SWaitableDoor[MultiprocessingTestCase.Flags](
                handle,
                primitive,
            )
            process = Process(target=worker)

            process.start()

            with door.write() as proxy:
                proxy.ready = True

                door.notify_write()

            with door.read() as proxy:
                while not proxy.processed:
                    door.wait_read()

                self.assertTrue(proxy.processed)

            process.join()
            handle.unlink()


if __name__ == '__main__':
    main()  # pragma: no cover
