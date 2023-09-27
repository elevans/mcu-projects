import lib.display as display
import lib.multiplexer as multiplexer
from machine import I2C, Pin


def init_analog_multiplexer(s0: Pin, s1: Pin, s2: Pin, s3: Pin):
    """Initialize an analog multiplexer.

    Initialize an analog multiplexer (e.g. a CD74HC4067).
    """
    return multiplexer.AnalogMultiplexer(s0, s1, s3, s3)


def init_i2c_multiplexer(mux: I2C):
    """Initialize an I2C multiplexer.

    Initialize an I2C multiplexer (e.g. a TCA9548).

    :param mux: A machine.I2C instance for the multiplexer.
    """
    return multiplexer.I2CMultiplexer(mux)


def init_ssd1306_display(w: int, h: int, protocol: str, i2c: I2C):
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
