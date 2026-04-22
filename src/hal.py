from machine import PWM, Pin
from micropython import const
from config import PIN_BUZZER

_BUZZER_FREQ_HZ = const(440)
_BUZZER_DUTY_ON = const(512)
_BUZZER_DUTY_OFF = const(0)


class FeedbackController:
    def __init__(self):
        self._buzzer = self._init_buzzer()

    def _init_buzzer(self):
        try:
            buzzer = PWM(Pin(PIN_BUZZER))
            buzzer.freq(_BUZZER_FREQ_HZ)
            buzzer.duty(_BUZZER_DUTY_OFF)

            return buzzer
        except Exception as e:
            print(f"[HW] Buzzer init failed: {e}")

            return None

    def set_tone(self, active):
        if self._buzzer:
            self._buzzer.duty(_BUZZER_DUTY_ON if active else _BUZZER_DUTY_OFF)
