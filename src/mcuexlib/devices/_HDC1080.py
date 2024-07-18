import time
from micropython import const

ADDR = const(0x40)
CTRL_HUM_REG = const(0x01)
CTRL_TEMP_REG = const(0x00)
HDC1080_CONFIG_REG = const(0x02)
HDC1080_CONFIG = const(0x00)

class HDC1080:
    def __init__(self, i2c):
        """MicroPython driver for the HDC1080 temperature/humidity sensor.

        This class is a MicroPython driver for the HDC1080 14-bit
        temperature and humidity sensor. Initialize this class with
        the machine.I2C object configured with the appropriate Pin
        and frequency settings.

        :param i2c:

            machine.I2C instance for the conencted device.
        """
        self.i2c = i2c
        self._addr = ADDR
        self._t
        self._t_reg_buf = bytes([HDC1080_TEMP_REG])
        self._h_reg_buf = bytes([HDC1080_HUM_REG])
        self._init_device()

    def _init_device(self):
        """
        Initialize an HDC1080 device. Default configuration:
            | Acquisition mode: 0  (temp or hum)
            | Temp resolution: 0 (14 bit)
            | Hum resolution: 0 (14 bit)
        """
        self.i2c.writeto_mem(
            self._addr,
            HDC1080_CONFIG_REG,
            bytes([HDC1080_CONFIG])
            )

    def read_temp(self, unit="c"):
        """Read the temperature.

        Read the temperature and return in Celcius, Fahrenheit or the raw
        value.

        :param unit:

            Set the unit of the temperature read.
        
        :return:

            Temperature in specified unit.
        """
        # point to temperature register
        self.i2c.writeto(self._addr, self._t_reg_buf)
        time.sleep(0.015)
        v = int.from_bytes(self.i2c.readfrom(self._addr, 2), "big")
        if unit == "c":
            return (v / 2 ** 16) * 165 - 40
        elif unit == "f":
            return (v * 1.8 / (2 ** 16)) * 165 - 40
        else:
            return v

    def read_hum(self):
        """Read the relative humidity.

        Read the relatively humidity as a percentage.

        :return: Relative humidity percent
        """
        # point to humidity register
        self.i2c.writeto(self._addr, self._h_reg_buf)
        time.sleep(0.015)
        value = int.from_bytes(self.i2c.readfrom(self._addr, 2), "big")
        
        return (value / 2 ** 16) * 100

