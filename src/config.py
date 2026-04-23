from micropython import const

PIN_OLED_SDA = const(21)
PIN_OLED_SCL = const(22)
PIN_BTN_MORSE = const(14)
PIN_BTN_CTRL = const(15)
PIN_NEOPIXEL = const(27)
PIN_BUZZER = const(26)

DOT_MAX_MS = const(300)
CHAR_TIMEOUT_MS = const(800)
DEBOUNCE_MS = const(40)

NUM_PIXELS = const(8)

COLOR_OFF = (0, 0, 0)
COLOR_DOT = (0, 0, 255)
COLOR_DASH = (255, 165, 0)
COLOR_DONE = (0, 255, 0)

STATE_LABELS = {
    0: "IDLE",
    1: "LISTEN",
    2: "PRESS",
    3: "DECODE",
    4: "OK",
}
