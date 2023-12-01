from asyncio import (
    BoundedSemaphore,
    Condition,
    create_task,
    gather,
    Lock,
    Semaphore,
)
from dataclasses import dataclass
from typing import Any
from unittest import IsolatedAsyncioTestCase, main

from door.asyncio2 import RSCondition, RSLock, WSCondition, WSLock
from door.primitives import Acquirable, SAcquirable, SWaitable, Waitable
from door.doors import (
    AsyncAcquirableDoor,
    AsyncSAcquirableDoor,
    AsyncSWaitableDoor,
    AsyncWaitableDoor,
)


class AsyncTestCase(IsolatedAsyncioTestCase):
    async def test_acquirable(self) -> None:
        @dataclass
        class Resource:
            key: Any = 'value'

        for primitive in (
                Lock(),
                Condition(),
                Semaphore(),
                BoundedSemaphore(),
        ):
            assert isinstance(primitive, Acquirable)

            resource = Resource()
            door = AsyncAcquirableDoor(resource, primitive)

            async with door() as proxy:
                self.assertEqual(proxy.key, 'value')
                proxy.key = 'VALUE'
                self.assertEqual(proxy.key, 'VALUE')

            self.assertRaises(ValueError, getattr, proxy, 'key')
            self.assertRaises(ValueError, setattr, proxy, 'key', 'value')
            self.assertEqual(resource, Resource('VALUE'))

    async def test_waitable(self) -> None:
        @dataclass
        class Flags:
            ready: bool = False
            processed: bool = False

        async def worker() -> None:
            async with door() as proxy:
                await door.wait_for(lambda: proxy.ready)

                proxy.processed = True

                await door.notify()

        for primitive in (
                Condition(),
        ):
            assert isinstance(primitive, Waitable)

            task = create_task(worker())
            door = AsyncWaitableDoor(Flags(), primitive)

            async with door() as proxy:
                proxy.ready = True

                await door.notify()

            async with door() as proxy:
                await door.wait_for(lambda: proxy.processed)

                self.assertTrue(proxy.processed)

            await task

    async def test_shared_acquirable_0(self) -> None:
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
            door = AsyncSAcquirableDoor(resource, primitive)

            async with door.read() as proxy:
                self.assertEqual(proxy.key, 'value')
                self.assertRaises(ValueError, setattr, proxy, 'key', 'VALUE')

            async with door.write() as proxy:
                self.assertEqual(proxy.key, 'value')
                proxy.key = 'VALUE'
                self.assertEqual(proxy.key, 'VALUE')

            self.assertRaises(ValueError, getattr, proxy, 'key')
            self.assertRaises(ValueError, setattr, proxy, 'key', 'value')
            self.assertEqual(resource, Resource('VALUE'))

    async def test_shared_acquirable_1(self) -> None:
        ITER_COUNT = 1000
        PARALLELISM_COUNT = 10

        @dataclass
        class Counter:
            value: int = 0

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

            counter = Counter()
            door = AsyncSAcquirableDoor(counter, primitive)
            tasks = []

            for _ in range(PARALLELISM_COUNT):
                task = create_task(target())

                tasks.append(task)

            await gather(*tasks)

            async with door.read() as proxy:
                self.assertEqual(proxy.value, ITER_COUNT * PARALLELISM_COUNT)

    async def test_shared_waitable(self) -> None:
        @dataclass
        class Flags:
            ready: bool = False
            processed: bool = False

        async def worker() -> None:
            async with door.write() as proxy:
                await door.wait_for_write(lambda: proxy.ready)

                proxy.processed = True

                await door.notify_write()

        for primitive in (
                RSCondition(),
                WSCondition(),
        ):
            assert isinstance(primitive, SWaitable)

            task = create_task(worker())
            door = AsyncSWaitableDoor(Flags(), primitive)

            async with door.write() as proxy:
                proxy.ready = True

                await door.notify_write()

            async with door.read() as proxy:
                await door.wait_for_read(lambda: proxy.processed)

                self.assertTrue(proxy.processed)

            await task


if __name__ == '__main__':
    main()  # pragma: no cover
