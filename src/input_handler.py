import uasyncio
from machine import Pin

from config import (
    PIN_BTN_MORSE,
    PIN_BTN_CTRL,
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
        pass

    async def _poll_ctrl(self):
        pass
