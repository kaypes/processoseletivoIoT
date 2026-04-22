import time
import uasyncio
from machine import Pin

from config import (
    PIN_BTN_MORSE,
    PIN_BTN_CTRL,
    DEBOUNCE_MS,
)


class Evt:
    PRESS = 0
    RELEASE = 1
    CTRL = 2
    CHAR_TIMEOUT = 3
    BACKSPACE = 4


class ButtonMatrix:
    def __init__(self, event_queue):
        self._queue = event_queue

        self._pin_morse = Pin(PIN_BTN_MORSE, Pin.IN, Pin.PULL_UP)
        self._pin_ctrl = Pin(PIN_BTN_CTRL, Pin.IN, Pin.PULL_UP)

        uasyncio.create_task(self._poll_morse())
        uasyncio.create_task(self._poll_ctrl())

    async def _poll_morse(self):
        last_state = self._pin_morse.value()
        while True:
            current_state = self._pin_morse.value()
            if current_state != last_state:
                await uasyncio.sleep_ms(DEBOUNCE_MS)
                current_state = self._pin_morse.value()

                if current_state != last_state:
                    last_state = current_state
                    evt = Evt.PRESS if current_state == 0 else Evt.RELEASE
                    now = time.ticks_ms()
                    self._queue.put_nowait((evt, now))

            await uasyncio.sleep_ms(10)

    async def _poll_ctrl(self):
        last_state = self._pin_ctrl.value()
        while True:
            current_state = self._pin_ctrl.value()
            if current_state != last_state:
                await uasyncio.sleep_ms(DEBOUNCE_MS)
                current_state = self._pin_ctrl.value()

                if current_state != last_state:
                    last_state = current_state
                    if current_state == 0:
                        now = time.ticks_ms()
                        self._queue.put_nowait((Evt.CTRL, now))

            await uasyncio.sleep_ms(10)
