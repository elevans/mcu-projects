import time
from micropython import const

# set constants
HDC1080_ADDRESS = const(0x40)
HDC1080_TEMP_REG = const(0x00)
HDC1080_HUM_REG = const(0x01)
HDC1080_CONFIG_REG = const(0x02)
HDC1080_CONFIG = const(0x00)
HDC1080_MANUFACTURER_ID = const(0xFE)
HDC1080_DEVICE_ID = const(0xFF)
HDC1080_SERIAL_ID_FIRST = const(0xFB)
HDC1080_SERIAL_ID_MID = const(0xFC)
HDC1080_SERIAL_ID_LAST = const(0xFD)

class HDC1080:
    """
    HDC1080 Texas Instruments Temperature/Humidity sensor. HDC1080 measurement conversion time
    is 6.35 ms, however actual conversion time takes ~12 ms. A delay of 15 ms is used to ensure
    enough time has elapsed for a measurement conversion.
    """
    def __init__(self, i2c):
        self.i2c = i2c
        self._t_reg_buf = bytes([HDC1080_TEMP_REG])
        self._h_reg_buf = bytes([HDC1080_HUM_REG])
        self._init_device()
        return

    def _init_device(self):
        """
        Initialize an HDC1080 device. Default configuration:
            | Acquisition mode: 0  (temp or hum)
            | Temp resolution: 0 (14 bit)
            | Hum resolution: 0 (14 bit)
        """
        self.i2c.writeto_mem(
            HDC1080_ADDRESS,
            HDC1080_CONFIG_REG,
            bytes([HDC1080_CONFIG])
            )

    def get_temp(self, unit="c"):
        """
        Get temperature measurement in Celcius or Fahrenheiht.
        """
        # point to temperature register
        self.i2c.writeto(HDC1080_ADDRESS, self._t_reg_buf)
        time.sleep(0.015)
        value = int.from_bytes(self.i2c.readfrom(HDC1080_ADDRESS, 2), "big")
        if unit == "c":
            return (value / 2 ** 16) * 165 - 40
        elif unit == "f":
            return (value * 1.8 / (2 ** 16)) * 165 - 40
        else:
            return None

    def get_hum(self):
        """
        Get relative humidity measurement.
        """
        # point to humidity register
        self.i2c.writeto(HDC1080_ADDRESS, self._h_reg_buf)
        time.sleep(0.015)
        value = int.from_bytes(self.i2c.readfrom(HDC1080_ADDRESS, 2), "big")
        return (value / 2 ** 16) * 100

class LSM303DLHC:
    """
    """
    def __init__(self, i2c):
        self.i2c = i2c
        return