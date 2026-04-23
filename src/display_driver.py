from machine import SoftI2C, Pin
from micropython import const
import ssd1306

from config import PIN_OLED_SDA, PIN_OLED_SCL, STATE_LABELS

_OLED_W = const(128)
_OLED_H = const(64)
_OLED_ADDR = const(0x3C)
_LINE_H = const(8)

_Y_STATE = const(0)
_Y_SEQ = const(16)
_Y_MSG_LABEL = const(32)
_Y_MSG_TEXT = const(46)

_MSG_VISIBLE = const(16)


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
        if not self._oled:
            return

        oled = self._oled
        oled.fill(0)

        state_label = STATE_LABELS.get(state, "?")
        oled.text(f"Status: {state_label}", 0, _Y_STATE)
        oled.hline(0, _Y_STATE + _LINE_H + 2, _OLED_W, 1)

        seq_str = "".join(sequence) if sequence else ""
        oled.text(seq_str, 0, _Y_SEQ)

        oled.text("Mensagem:", 0, _Y_MSG_LABEL)
        visible_msg = message[-_MSG_VISIBLE:] if message else ""
        oled.text(visible_msg, 0, _Y_MSG_TEXT)

        oled.show()
