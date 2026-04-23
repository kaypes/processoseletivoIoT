from machine import SoftI2C, Pin
from micropython import const
import ssd1306

from config import PIN_OLED_SDA, PIN_OLED_SCL, STATE_LABELS

_OLED_W = const(128)
_OLED_H = const(64)
_OLED_ADDR = const(0x3C)

_Y_STATE = const(0)


class DisplayDriver:
    def __init__(self):
        self._oled = self._init_oled()

    def _init_oled(self):
        try:
            i2c = SoftI2C(
                scl=Pin(PIN_OLED_SCL),
                sda=Pin(PIN_OLED_SDA),
                freq=400_000,
            )
            oled = ssd1306.SSD1306_I2C(_OLED_W, _OLED_H, i2c, addr=_OLED_ADDR)
            oled.fill(0)
            oled.text("Iniciando...", 0, _Y_STATE)
            oled.show()
            return oled
        except Exception as e:
            print(f"[HW] OLED init failed: {e}")
            return None

    def render(self, state, sequence, message):
        pass
