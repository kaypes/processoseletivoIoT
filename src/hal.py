from uasyncio import sleep_ms
from neopixel import NeoPixel
from machine import PWM, Pin
from micropython import const
from config import (
    PIN_BUZZER,
    PIN_NEOPIXEL,
    NUM_PIXELS,
    COLOR_OFF,
    COLOR_DOT,
    COLOR_DASH,
    COLOR_DONE,
)

_BUZZER_FREQ_HZ = const(440)
_BUZZER_DUTY_ON = const(512)
_BUZZER_DUTY_OFF = const(0)
_BLINK_DELAY_MS = const(200)


class FeedbackController:
    def __init__(self):
        self._pixel_index = 0
        self._buzzer = self._init_buzzer()
        self._np = self._init_neopixel()

    def _init_buzzer(self):
        try:
            buzzer = PWM(Pin(PIN_BUZZER))
            buzzer.freq(_BUZZER_FREQ_HZ)
            buzzer.duty(_BUZZER_DUTY_OFF)

            return buzzer
        except Exception as e:
            print(f"[HW] Buzzer init failed: {e}")

            return None

    def _init_neopixel(self):
        try:
            np = NeoPixel(Pin(PIN_NEOPIXEL), NUM_PIXELS)
            self._clear_strip(np)

            return np
        except Exception as e:
            print(f"[HW] NeoPixel init failed: {e}")

            return None

    def set_tone(self, active):
        if self._buzzer:
            self._buzzer.duty(_BUZZER_DUTY_ON if active else _BUZZER_DUTY_OFF)

    def add_visual_pulse(self, is_dash):
        if self._np and self._pixel_index < NUM_PIXELS:
            self._np[self._pixel_index] = COLOR_DASH if is_dash else COLOR_DOT
            self._np.write()

            self._pixel_index += 1

    def clear_visuals(self):
        self._pixel_index = 0

        if self._np:
            self._clear_strip(self._np)

    async def blink_success(self):
        self._pixel_index = 0

        if not self._np:
            return
        for i in range(NUM_PIXELS):
            self._np[i] = COLOR_DONE

        self._np.write()
        await sleep_ms(_BLINK_DELAY_MS)
        self.clear_visuals()

    @staticmethod
    def _clear_strip(np):
        for i in range(NUM_PIXELS):
            np[i] = COLOR_OFF

        np.write()
