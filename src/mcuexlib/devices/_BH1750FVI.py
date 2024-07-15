from micropython import const
from utime import sleep_ms

ADDR_H = const(0x5C)
ADDR_L = const(0x23)
CTRL_POWER_ON = const(0x01)
CTRL_POWER_OFF = const(0x00)
CTRL_RESET = const(0x07)
CONFIG_CONT_H_RES_1 = const(0x10)
CONFIG_CONT_H_RES_2 = const(0x11)
CONFIG_CONT_L_RES = const(0x13)
CONFIG_ONCE_H_RES_1 = const(0x20)
CONFIG_ONCE_H_RES_2 = const(0x21)
CONFIG_ONCE_L_RES = const(0x23)

class BH1750FVI:
    """
    """
    def __init__(self, i2c, addr):
        self.i2c = i2c
        self.addr = ADDR_L if addr is None else addr
        self._init_device()

    def _init_device(self):
        """Initialize the BH1750FVI device.
        """
        # power cycle the device -- leave in powered down state
        self.power_on()
        self.power_off()

    def read_cont(self):
        """Read cont.
        """

        return self.i2c.readfrom(self.addr, 2)

    def read_once(self, mode: str = None):
        """Read once.
        """
        if mode == "high1" or None:
            self.i2c.writeto(self.addr, bytes([CONFIG_ONCE_H_RES_1]))
            sleep_ms(120)
            # read 2 bytes (high/low)
            return self.i2c.readfrom(self.addr, 2)

        if mode == "high2":
            self.i2c.writeto(self.addr, bytes([CONFIG_ONCE_H_RES_2]))
            sleep_ms(120)
            # read 2 bytes (high/low)
            return self.i2c.readfrom(self.addr, 2)

        if mode == "low":
            self.i2c.writeto(self.addr, bytes([CONFIG_ONCE_L_RES]))
            sleep_ms(16)
            # read 2 bytes (high/low)
            return self.i2c.readfrom(self.addr, 2)

    def reset(self):
        """Reset the BH1750FVI.
        """
        self.i2c.writeto(self.addr, bytes([CTRL_RESET]))

    def power_off(self):
        """Power off the BH1750FVI.
        """
        self.i2c.writeto(self.addr, bytes([CTRL_POWER_OFF]))

    def power_on(self):
        """Power on the BH1750FVI.
        """
        self.i2c.writeto(self.addr, bytes([CTRL_POWER_ON]))

    def start_cont_reads(self, mode: str = None):
        """Start continous read mode.
        """
        if mode == "high1" or None:
            self.i2c.writeto(self.addr, bytes([CONFIG_CONT_H_RES_1]))
        if mode == "high2":
            self.i2c.writeto(self.addr, bytes([CONFIG_CONT_H_RES_2]))
        if mode == "low":
            self.i2c.writeto(self.addr, bytes([CONFIG_CONT_L_RES]))
