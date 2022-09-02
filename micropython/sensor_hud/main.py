import framebuf
from machine import Pin, I2C
from display import SSD1306_I2C

# set constants
DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 32
MULTIPLEXER_ADDR = 0x70
MULTIPLEXER_SCL = 15
MULTIPLEXER_SDA = 14
FREQ = 400000

# setup i2c devices
i2c_multiplexer = I2C(1, scl=MULTIPLEXER_SCL, sda=MULTIPLEXER_SDA, freq=FREQ)
#display.text("Tooled Technologies", 0, 0)
#display.show()


def get_display(channel):
    _select_channel(channel)
    display = SSD1306_I2C(DISPLAY_WIDTH, DISPLAY_HEIGHT, i2c_multiplexer)
    display.fill(0)
    return display

def _select_channel(channel):
    if channel >= 0 and channel < 8:
        value = 1 << channel
        # 0x70 is the default address of the tca - you can connect up to 8 - 0x70 to 0x77
        i2c_multiplexer.writeto(MULTIPLEXER_ADDR, value.to_bytes(1,'little') )