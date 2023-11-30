from asyncio import BoundedSemaphore, Condition, Lock, Semaphore
from dataclasses import dataclass
from typing import Any
from unittest import IsolatedAsyncioTestCase, main

from door.asyncio2 import RSLock, WSLock
from door.primitives import Acquirable, SAcquirable
from door.doors import AsyncAcquirableDoor, AsyncSAcquirableDoor


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

            async with door.acquire() as proxy:
                self.assertEqual(proxy.key, 'value')
                proxy.key = 'VALUE'
                self.assertEqual(proxy.key, 'VALUE')

            self.assertRaises(ValueError, getattr, proxy, 'key')
            self.assertRaises(ValueError, setattr, proxy, 'key', 'value')
            self.assertEqual(resource, Resource('VALUE'))

    async def test_shared_acquirable(self) -> None:
        @dataclass
        class Resource:
            key: Any = 'value'

        for primitive in (
                RSLock(),
                WSLock(),
        ):
            assert isinstance(primitive, SAcquirable)

            resource = Resource()
            door = AsyncSAcquirableDoor(resource, primitive)

            async with door.acquire_read() as proxy:
                self.assertEqual(proxy.key, 'value')
                self.assertRaises(ValueError, setattr, proxy, 'key', 'VALUE')

            async with door.acquire_write() as proxy:
                self.assertEqual(proxy.key, 'value')
                proxy.key = 'VALUE'
                self.assertEqual(proxy.key, 'VALUE')

            self.assertRaises(ValueError, getattr, proxy, 'key')
            self.assertRaises(ValueError, setattr, proxy, 'key', 'value')
            self.assertEqual(resource, Resource('VALUE'))


if __name__ == '__main__':
    main()  # pragma: no cover
