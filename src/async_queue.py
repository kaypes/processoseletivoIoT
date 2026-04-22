import uasyncio


class Queue:
    def __init__(self, maxsize=0):
        self._queue = []
        self._ev = uasyncio.Event()

    async def get(self):
        while not self._queue:
            self._ev.clear()
            await self._ev.wait()
        return self._queue.pop(0)

    def put_nowait(self, item):
        self._queue.append(item)
        self._ev.set()
