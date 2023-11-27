from asyncio import BoundedSemaphore, Condition, Lock, Semaphore
from dataclasses import dataclass
from unittest import IsolatedAsyncioTestCase, main

from door.asyncio2 import SLock
from door.primitives import AsyncPrimitive, FineGrainedAsyncPrimitive
from door.utilities import AsyncDoor


class AsyncDoorTestCase(IsolatedAsyncioTestCase):
    async def test_read_and_write(self) -> None:
        @dataclass
        class X:
            a: str = 'a'
            b: str = 'b'

        for primitive in (
                Lock(),
                Condition(),
                Semaphore(),
                BoundedSemaphore(),
                SLock(),
        ):
            assert isinstance(
                primitive,
                AsyncPrimitive | FineGrainedAsyncPrimitive,
            )

            x = X()
            door = AsyncDoor(x, primitive)

            async with door.read() as resource:
                self.assertEqual(resource.a, 'a')

            self.assertRaises(ValueError, getattr, resource, 'a')
            self.assertRaises(ValueError, setattr, resource, 'a', 'A')

            async with door.read() as resource:
                self.assertRaises(ValueError, setattr, resource, 'a', 'A')

            async with door.write() as resource:
                resource.b = 'B'
                self.assertEqual(resource.b, 'B')
                self.assertEqual(resource.a, 'a')
                resource.a = 'A'
                self.assertEqual(resource.a, 'A')

            self.assertEqual(x, X('A', 'B'))


if __name__ == '__main__':
    main()  # pragma: no cover
