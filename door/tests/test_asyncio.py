from asyncio import (
    BoundedSemaphore,
    Condition,
    create_task,
    gather,
    Lock,
    Semaphore,
)
from dataclasses import dataclass
from unittest import IsolatedAsyncioTestCase, main

from door.asyncio2 import (
    AcquirableDoor,
    RSCondition,
    RSLock,
    SAcquirableDoor,
    SWaitableDoor,
    WaitableDoor,
    WSCondition,
    WSLock,
)
from door.multiprocessing2 import Handle
from door.primitives import Acquirable, SAcquirable, SWaitable, Waitable


class AsyncioTestCase(IsolatedAsyncioTestCase):
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

    def test_unhandled(self) -> None:
        handle = Handle(None)

        self.assertRaises(ValueError, AcquirableDoor, handle, Lock())
        handle.unlink()

    async def test_acquirable(self) -> None:
        for primitive in (
                Lock(),
                Condition(),
                Semaphore(),
                BoundedSemaphore(),
        ):
            assert isinstance(primitive, Acquirable)

            resource = self.Resource()
            door = AcquirableDoor(resource, primitive)

            async with door() as proxy:
                self.assertEqual(proxy.key, 'value')
                proxy.key = 'VALUE'
                self.assertEqual(proxy.key, 'VALUE')

            self.assertRaises(ValueError, getattr, proxy, 'key')
            self.assertRaises(ValueError, setattr, proxy, 'key', 'value')
            self.assertEqual(resource, self.Resource('VALUE'))

    async def test_waitable(self) -> None:
        async def worker() -> None:
            async with door() as proxy:
                while not proxy.ready:
                    await door.wait()

                proxy.processed = True

                await door.notify()

        for primitive in (
                Condition(),
        ):
            assert isinstance(primitive, Waitable)

            resource = self.Flags()
            door = WaitableDoor(resource, primitive)
            task = create_task(worker())

            async with door() as proxy:
                proxy.ready = True

                await door.notify()

            async with door() as proxy:
                while not proxy.processed:
                    await door.wait()

                self.assertTrue(proxy.processed)

            await task

    async def test_shared_acquirable_0(self) -> None:
        for primitive in (
                RSLock(),
                WSLock(),
                RSCondition(),
                WSCondition(),
        ):
            assert isinstance(primitive, SAcquirable)

            resource = self.Resource()
            door = SAcquirableDoor(resource, primitive)

            async with door.read() as proxy:
                self.assertEqual(proxy.key, 'value')
                self.assertRaises(ValueError, setattr, proxy, 'key', 'VALUE')

            async with door.write() as proxy:
                self.assertEqual(proxy.key, 'value')
                proxy.key = 'VALUE'
                self.assertEqual(proxy.key, 'VALUE')

            self.assertRaises(ValueError, getattr, proxy, 'key')
            self.assertRaises(ValueError, setattr, proxy, 'key', 'value')
            self.assertEqual(resource, self.Resource('VALUE'))

    async def test_shared_acquirable_1(self) -> None:
        ITER_COUNT = 1000
        PARALLELISM_COUNT = 10

        async def read() -> int:
            async with door.read() as proxy:
                return proxy.value

        async def write() -> None:
            async with door.write() as proxy:
                proxy.value += 1

        async def target() -> None:
            for _ in range(ITER_COUNT):
                await write()
                await read()

        for primitive in (
                RSLock(),
                WSLock(),
                RSCondition(),
                WSCondition(),
        ):
            assert isinstance(primitive, SAcquirable)

            counter = self.Counter()
            door = SAcquirableDoor(counter, primitive)
            tasks = []

            for _ in range(PARALLELISM_COUNT):
                task = create_task(target())

                tasks.append(task)

            await gather(*tasks)

            self.assertEqual(counter.value, ITER_COUNT * PARALLELISM_COUNT)

    async def test_shared_waitable(self) -> None:
        async def worker() -> None:
            async with door.write() as proxy:
                while not proxy.ready:
                    await door.wait_write()

                proxy.processed = True

                await door.notify_write()

        for primitive in (
                RSCondition(),
                WSCondition(),
        ):
            assert isinstance(primitive, SWaitable)

            resource = self.Flags()
            door = SWaitableDoor(resource, primitive)
            task = create_task(worker())

            async with door.write() as proxy:
                proxy.ready = True

                await door.notify_write()

            async with door.read() as proxy:
                while not proxy.processed:
                    await door.wait_read()

                self.assertTrue(proxy.processed)

            await task


if __name__ == '__main__':
    main()  # pragma: no cover
