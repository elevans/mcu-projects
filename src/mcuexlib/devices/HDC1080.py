from micropython import const
from utime import sleep_ms

ADDR = const(0x40)
CTRL_HUM = const(0x01)
CTRL_TEMP = const(0x00)
CONFIG_REG = const(0x02)

class HDC1080:
    def __init__(self, i2c, mode: int = 0, heat: bool = False, tres: int = 14, hres: int = 14):
        """MicroPython driver for the HDC1080 temperature/humidity sensor.

        This class is a MicroPython driver for the HDC1080 14-bit
        temperature and humidity sensor. Initialize this class with
        the machine.I2C object configured with the appropriate Pin
        and frequency settings as well as the device configuration.

        :param i2c:

            machine.I2C instance for the conencted device.

        :param mode:

            Mode of acquisition. If 0, temperature or humidity (only one) is acquired.
            If 1, temperature and humidity are both acquired in sequence (temperature
            first).

        :param heat:

            Enable or disable the heater (used to drive condensation off the sensor
            and to test the sensor). Once enabled the heater is turned on only during
            the measurement mode. Increase the measurement rate to increase the
            temperature.

        :param tres:

            Temperature measurement resolution. Supported resolutions include 14 and 11 bit.

        :param hres:
        
            Humidity measurement resolution. Supported resolutions include 14, 11, and 8 bit.
        """
        self.i2c = i2c
        self._addr = ADDR
        self._byte_config_reg = bytes([CONFIG_REG])
        self._byte_hum = bytes([CTRL_HUM])
        self._byte_temp = bytes([CTRL_TEMP])
        self._hres = hres
        self._tres = tres
        self._init_device(mode, heat, tres, hres)

    def _init_device(self, mode, heat, tres, hres):
        """Initialize the HDC1080 device.

        Initialize the HDC1080 device with the desired configuration.
        The initialization routine configures the device and leaves it
        in a low power mode.
        """
        # create register byte with bit masks
        reg = 0x0
        if mode == 1:
            reg |= 0x10
        if heat:
            reg |= 0x20
        if tres == 11:
            reg |= 0x4
        if hres == 11:
            reg |= 0x1
        elif hres == 8:
            reg |= 0x2
            
        self.i2c.writeto_mem(self._addr, self._byte_config_reg)
        self.i2c.writeto_mem(
            self._addr,
            CONFIG_REG,
            bytes([reg << 8])
            )
        # give the sensor 15 ms to start
        sleep_ms(15)

    def get_hum(self):
        """Measure the relative humidity.

        Measure the relative humidity (single measurement).

        :return:

            Relative humidity percent.
        """
        # trigger a humidity measurement
        self.i2c.writeto(self._addr, self._byte_hum)
        # wait for measurement
        if self._hres == 8:
            sleep_ms(3)
        elif self._hres == 11:
            sleep_ms(4)
        elif self._hres == 14:
            sleep_ms(7)
        
        return (int.from_bytes(self.i2c.readfrom(self._addr, 2)) / 2 ** 16) * 100

    def get_temp(self, unit: str = "c"):
        """Measure the temperature.

        Measure the temperature and return Celcius or Fahrenheit.

        :param unit:

            Specify the temperature unit.

        :return:

            Temperature measurement.
        """
        # trigger a temperature measurement
        self.i2c.writeto(self._addr, self._byte_temp)
        # wait for measurement
        if self._tres == 11:
            sleep_ms(4)
        elif self._tres == 14:
            sleep_ms(7)

        t = int.from_bytes(self.i2c.readfrom(self._addr, 2))
        if unit == "c":
            return (t / 2 ** 16) * 165 - 40
        else: 
            return (t * 1.8 / (2 ** 16)) * 165 - 40

    def get_temp_hum(self, unit: str = "c") -> tuple[float, float]:
        """Measure the temperature and humidity sequentially.

        Measure the temperature and humidity sequentially. Returns
        the temperature in specified unit and relatively humidity
        as a percentage.

        :param unit:

            Specify the temperature unit.

        :return:

            A Tuple containing the temperature and humidity values.
        """
        # trigger a temperature/humidity sequential measurement
        self.i2c.writeto(self._addr, self._byte_temp)
        return

