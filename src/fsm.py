import time

from config import DOT_MAX_MS
from morse_dict import decode_sequence
from input_handler import Evt
from micropython import const

_MSG_MAX_CHARS = const(32)


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

    async def _dispatch(self, evt_type, ts):
        if self._state == State.IDLE and evt_type == Evt.CTRL:
            self._reset_session()
            self._fb.clear_visuals()
            
            await self._enter_listening()

        elif self._state == State.LISTENING and evt_type == Evt.PRESS:
            self._cancel_watchdog()
            self._enter_pressing(ts)

        elif self._state == State.LISTENING and evt_type == Evt.CHAR_TIMEOUT:
            if len(self._sequence) > 0:
                await self._enter_decoding()

        elif self._state == State.LISTENING and evt_type == Evt.CTRL:
            self._cancel_watchdog()
            self._reset_session()
            self._fb.clear_visuals()
            self._enter_idle()

        elif self._state == State.PRESSING and evt_type == Evt.RELEASE:
            await self._process_release(ts)

    def _enter_idle(self):
        self._state = State.IDLE
        self._fb.set_tone(False)
        self._notify_display()

    async def _enter_listening(self):
        self._state = State.LISTENING
        self._start_watchdog()
        self._notify_display()

    def _enter_pressing(self, ts: int):
        self._state = State.PRESSING
        self._press_ts = ts
        self._fb.set_tone(True)

    async def _process_release(self, ts: int):
        duration = time.ticks_diff(ts, self._press_ts)
        is_dash = duration >= DOT_MAX_MS

        self._fb.set_tone(False)
        self._sequence.append("-" if is_dash else ".")
        self._fb.add_visual_pulse(is_dash)

        await self._enter_listening()

    async def _enter_decoding(self):
        self._state = State.DECODING
        
        seq_str = "".join(self._sequence)
        self._sequence.clear()

        if len(seq_str) >= 6 and seq_str.count(".") == len(seq_str):
            if self._message:
                self._message.pop()
            
            self._notify_display()
            await self._enter_feedback(success=True)
            
            return

        char = decode_sequence(seq_str) if seq_str else None

        if char and len(self._message) < _MSG_MAX_CHARS:
            if char != "?":
                self._message.append(char)

        self._notify_display()
        await self._enter_feedback(success=(char and char != "?"))

    async def _enter_feedback(self, success):
        self._state = State.FEEDBACK
        if success:
            await self._fb.blink_success()
        else:
            self._fb.clear_visuals()

        await self._enter_listening()

    def _reset_session(self) -> None:
        self._sequence.clear()
        self._message.clear()

    def _notify_display(self):
        if not self._display:
            return
        self._display.render(
            state=self._state,
            sequence=list(self._sequence),
            message="".join(self._message),
        )
