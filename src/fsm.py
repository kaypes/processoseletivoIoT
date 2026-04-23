from micropython import const


class State:
    IDLE = 0
    LISTENING = 1
    PRESSING = 2
    DECODING = 3
    FEEDBACK = 4


class FSM:
    def __init__(self, event_queue, feedback, display=None):
        self._queue = event_queue
        self._fb = feedback
        self._display = display

        self._state = State.IDLE
        self._sequence: list = []
        self._message: list = []
        self._press_ts = 0
        self._watchdog = None

    async def run(self) -> None:
        self._enter_idle()
        while True:
            evt_type, ts = await self._queue.get()
            await self._dispatch(evt_type, ts)
