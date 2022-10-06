import display
import sensors
from machine import Pin, I2C
from micropython import const

# addresses
MULTIPLEXER_ADDRESS = const(0x70)
HDC1080_ADDRESS = const(0x40)
SSD1306_ADDRESS = const(0x3C)

# i2c config
FREQUENCY_STANDARD = const(100000)
FREQUENCY_FAST = const(400000)

# device library
DEVICE_LIBRARY = {
    HDC1080_ADDRESS: "sensor_hdc1080",
    SSD1306_ADDRESS: "display_ssd1306"
}

# device settings
DISPLAY_WIDTH = const(128)
DISPLAY_HEIGHT = const(32)

class Multiplexer:
    def __init__(self, i2c_id: int, scl_pin: Pin, sda_pin: Pin, freq: int=FREQUENCY_FAST):
        """Multiplexer helper methods.

        Adds helpful multiplexer control methods (e.g. next_device()) and
        auto detection of connected I2C devices.

        :param i2c_id: ID of the I2C port
        :param scl_pin: SCL Pin.
        :param sda_pin: SDA Pin.
        :param freq: I2C device frequency (100 kHz or 400 kHz).
        """
        self.i2c_id = i2c_id
        self.scl_pin = scl_pin
        self.sda_pin = sda_pin
        self.freq = freq
        self.device = None # access the channel's device instance
        self.active_channels = [] # list of active channels - for valid channel options
        self.inactive_channels = [] # list of inactive channels - for skpping
        self.current_channel = 0 # current channel selected on multiplexer
        self.connected_device = {} # dict that stores device instances, keys are channel
        self.multiplexer = None # access to the multiplexer itself
        self.connected_device_id = {} # dict that stores device id, keys are channel
        self._initialized = False # multiplexer init complete?
        self._init_multiplexer()

    def select_channel(self, channel: int):
        """
        Select a channel (0 through 7).
        """
        if channel >= 0 and channel < 8:
            value = 1 << channel
            self.multiplexer.writeto(MULTIPLEXER_ADDRESS, bytearray([value]))
        
        self.current_channel = channel

        if self._initialized:
            self.device = self.connected_device[self.current_channel]

    def next_device(self):
        """
        Select the next channel.
        """
        ch_index = self.active_channels.index(self.current_channel)
        if ch_index >= 0 and ch_index < len(self.active_channels):
            ch_index += 1
            self.select_channel(self.active_channels[ch_index])
        else:
            ch_index = 0
            self.select_channel(self.active_channels[ch_index])

    def previous_device(self):
        """
        Select the previous channel.
        """
        ch_index = self.active_channels.index(self.current_channel)
        if ch_index >= 0 and ch_index < len(self.active_channels):
            ch_index -= 1
            self.select_channel(self.active_channels[ch_index])
        else:
            ch_index = len(self.active_channels) - 1
            self.select_channel(self.active_channels[ch_index])

    def _init_multiplexer(self):
        """
        Initialize the I2C multiplexer.
        """
        self.multiplexer = I2C(self.i2c_id, scl=self.scl_pin, sda=self.sda_pin, freq=self.freq)
        self._init_connected_devices()
        self._initialized = True
        self.select_channel(self.active_channels[0])

    def _init_connected_devices(self):
        """
        Initialize the devices connected to the multiplexer. Note,
        only devices that are in the device library will be connected.
        Added the deivce address to the device library to connect the
        desired device. This method expects one device per channel.
        """
        r = range(8)
        for i in r:
            self.select_channel(i)
            scan_result = self.multiplexer.scan() # [60, 112]
            for address in DEVICE_LIBRARY:
                if address in scan_result:
                    self._init_device(address)
                    self.active_channels.append(self.current_channel)
                    self.connected_device_id[self.current_channel] = DEVICE_LIBRARY[address]
            if len(scan_result) == 1 and MULTIPLEXER_ADDRESS in scan_result:
                self.inactive_channels.append(self.current_channel)

    def _init_device(self, address):
        """
        Setup routines for individual devices.
        """
        # initialize display (ssd1306)
        if address == SSD1306_ADDRESS:
            device = display.SSD1306_I2C(DISPLAY_WIDTH, DISPLAY_HEIGHT, self.multiplexer)
            device.fill(0)
            self.connected_device[self.current_channel] = device
        
        # initialize sensors (hdc1080)
        if address == HDC1080_ADDRESS:
            device = sensors.HDC1080(self.multiplexer)
            self.connected_device[self.current_channel] = device
