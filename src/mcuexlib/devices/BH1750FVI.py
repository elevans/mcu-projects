from micropython import const
from utime import sleep_ms

ADDR_H = const(0x5C)
ADDR_L = const(0x23)
CMD_POWER_ON = const(0x01)
CMD_POWER_OFF = const(0x00)
CMD_RESET = const(0x07)
SET_CONT_H_RES_1 = const(0x10)
SET_CONT_H_RES_2 = const(0x11)
SET_CONT_L_RES = const(0x13)
SET_ONCE_H_RES_1 = const(0x20)
SET_ONCE_H_RES_2 = const(0x21)
SET_ONCE_L_RES = const(0x23)

class BH1750FVI:
    def __init__(self, i2c, addr_config: str = None):
        """MicroPython driver for the BH1750FVI ambient light sensor.

        This class is a MicroPython driver for the BH1750FVI 16-bit
        ambient light sensor, using the I2C bus interface. Initialize
        this class with the machine.I2C object configured with the
        apppropriate machine.Pin and frequency settings as well as
        the device address configuration.

        :param i2c:
                
            machine.I2C instance for the connected device.
        
        :param addr_config:

            Indicate either "l" or "h" for low (ADDR pin
            connected to GND) or high (ADDR pin connected
            to VCC) address configuration. If left None,
            the low address will be selected.
        """
        self.i2c = i2c
        self.config = addr_config
        self._addr = None
        self._buf = bytearray(2) # read buffer
        self._byte_power_on = bytes([CMD_POWER_ON])
        self._byte_power_off = bytes([CMD_POWER_OFF])
        self._byte_reset = bytes([CMD_RESET])
        self._byte_cont_hres1 = bytes([SET_CONT_H_RES_1])
        self._byte_cont_hres2 = bytes([SET_CONT_H_RES_2])
        self._byte_cont_lres = bytes([SET_CONT_L_RES])
        self._byte_once_hres1 = bytes([SET_ONCE_H_RES_1])
        self._byte_once_hres2 = bytes([SET_ONCE_H_RES_2])
        self._byte_once_lres = bytes([SET_ONCE_L_RES])
        self._init_device()
        
    def _init_device(self):
        """Initialize the BH1750FVI device.

        Initialize the BH1750FVI device with the desired address.
        The initialization routine power cycles the device.
        """
        # set device address, set default address to "l"
        if not self.config or self.config.lower() == "l":
            self._addr = ADDR_L
        elif self.config.lower() == "h":
            self._addr = ADDR_H
        else:
            # fail softly
            self._addr = None

        # power cycle the device, leave in powered down state
        self.power_on()
        self.power_off()

    def read_cont(self):
        """Read data from a continous read state.
        
        Read data from the device buffer. This method is intended
        to be used with the continous read mode.

        :return:

            Light measurement in "lx" units.
        """ 
        self.i2c.readfrom_into(self._addr, self._buf)

        return self._buf_to_lx()

    def read_once(self, mode: str = None):
        """Read data once from the device.

        Read data one time at the specified mode (i.e. the measurement
        resolution).

        :param mode:

            Indicate what measurement resolution to perform once. Options
            are "high1", "high2" and "low".

        :return:

            Light measurement in "lx" units.
        """
        if mode == "high1" or None:
            self.power_on()
            self.i2c.writeto(self._addr, self._byte_once_hres1)
            sleep_ms(120)
            self.i2c.readfrom_into(self._buf)
        if mode == "high2":
            self.power_on()
            self.i2c.writeto(self._addr, self._byte_once_hres2)
            sleep_ms(120)
            self.i2c.readfrom_into(self._buf)
        if mode == "low":
            self.power_on()
            self.i2c.writeto(self._addr, self._byte_once_lres)
            sleep_ms(16)
            self.i2c.readfrom_into(self._buf)

        return self._buf_to_lx()

    def reset(self):
        """Reset the BH1750FVI.

        Reset the device.
        """
        self.i2c.writeto(self._addr, self._byte_reset)

    def power_off(self):
        """Power off the BH1750FVI.

        Power off the device.
        """
        self.i2c.writeto(self._addr, self._byte_power_off)

    def power_on(self):
        """Power on the BH1750FVI.

        Power on the device.
        """
        self.i2c.writeto(self._addr, self._byte_power_on)

    def start_cont_read(self, mode: str = None):
        """Start continous reading state.

        Start a continous read state with the given resolution
        mode.

        :param mode:
        
            Indicate what measurement resolution to perform continously.
            Options are "high1", "high2" and "low".
        """
        if mode == "high1" or None:
            self.power_on()
            self.i2c.writeto(self._addr, self._byte_cont_hres1)
        if mode == "high2":
            self.power_on()
            self.i2c.writeto(self._addr, self._byte_cont_hres2)
        if mode == "low":
            self.power_on()
            self.i2c.writeto(self._addr, self._byte_cont_lres)

    def _buf_to_lx(self) -> float:
        """Convert the buffer into lx units.

        Convert the buffer from a bytearray into a
        light measurement in "lx" units.

        :return:

            Light measurement in "lx" units.
        """
        return int.from_bytes(self._buf, "big") / 1.2
