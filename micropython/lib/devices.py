import lib.display as display
from lib.multiplexer import I2CMultiplexer
from machine import I2C


def init_i2c_multiplexer(mux: I2C):
    """Initialize an I2C multiplexer.

    Initialize an I2C multiplexer (e.g. a TCA9548).

    :param mux: A machine.I2C instance for the multiplexer.
    """
    return I2CMultiplexer(mux)


def init_display(w: int, h: int, protocol: str, i2c: I2C):
    """Initialize an SSD1306 display.

    Initialize an SSD1306 display with the specified protocol
    and dimensions.

    :param w: Width of the display.
    :param h: Height of the display.
    :param protocol: Display protocl (I2C/SPI).
    :param i2c: A machine.I2C instance of the SSD1306 display.
    :return: An instance of display.SSD1306 class.
    """
    if protocol.lower() == "i2c":
        dsp = display.SSD1306_I2C(w, h, i2c)
        dsp.fill(0)
        return dsp
    if protocol.lower() == "spi":
        # note that SPI is untested
        dsp = display.SSD1306_SPI(w, h, i2c)
        dsp.fill(0)
        return dsp
    else:
        return None
