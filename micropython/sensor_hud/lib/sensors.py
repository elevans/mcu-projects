import time
from micropython import const

# set constants
HDC1080_ADDRESS = const(0x40)
HDC1080_TEMP_REG = const(0x00)
HDC1080_HUM_REG = const(0x01)
HDC1080_CONFIG_REG = const(0x02)
HDC1080_MANUFACTURER_ID = const(0xFE)
HDC1080_DEVICE_ID = const(0xFF)
HDC1080_SERIAL_ID_FIRST = const(0xFB)
HDC1080_SERIAL_ID_MID = const(0xFC)
HDC1080_SERIAL_ID_LAST = const(0xFD)

class HDC1080():
    def __init__(self, i2c):
        self.i2c = i2c
        self.init_device()
        return

    def init_device(self):
        """
        Initialize an HDC1080 device with 14-bit resolution.
        """
        self.i2c.writeto_mem(HDC1080_ADDRESS, HDC1080_CONFIG_REG, bytearray([1 << 4]))

    def get_temp(self, unit="c"):
        """
        Get temperature measurement in Celcius or Fahrenheiht.
        """
        # point to temperature register
        self.i2c.writeto(HDC1080_ADDRESS, bytearray([HDC1080_TEMP_REG]))
        time.sleep(0.0635)
        value = int.from_bytes(self.i2c.readfrom(HDC1080_ADDRESS, 2), "big")
        if unit.lower() == "f":
            return (value * 1.8 / (2 ** 16)) * 165 - 40
        else:
            return (value / 2 ** 16) * 156 - 40

    def get_hum(self):
        """
        Get relative humidity measurement.
        """
        # point to humidity register
        self.i2c.writeto(HDC1080_ADDRESS, bytearray([HDC1080_HUM_REG]))
        time.sleep(0.065)
        value = int.from_bytes(self.i2c.readfrom(HDC1080_ADDRESS, 2), "big")
        return (value / 2 ** 16) * 100