import displayed
import sensors
from machine import Pin, I2C
from micropython import const

# addresses
MULTIPLEXER_ADDRESS = const(0x70)
#BH1750VI_ADDRESS = const(0x00)
HDC1080_ADDRESS = const(0x40)
SSD1306_ADDRESS = const(0x3C)

# i2c config
FREQUENCY_STANDARD = const(100000)
FREQUENCY_FAST = const(400000)

# device library
DEVICE_LIBRARY = {
    HDC1080_ADDRESS: "sensor (hdc1080)",
    SSD1306_ADDRESS: "display (ssd1306)"
}

# device settings
DISPLAY_WIDTH = const(128)
DISPLAY_HEIGHT = const(32)

class Multiplexer:
    def __init__(self, i2c):
        """Multiplexer helper methods.

        Adds helpful multiplexer control methods (e.g. next_device()) and
        auto detection of connected I2C devices.

        :param i2c_id: ID of the I2C port
        :param scl_pin: SCL Pin.
        :param sda_pin: SDA Pin.
        :param freq: I2C device frequency (100 kHz or 400 kHz).
        """
        self.device = None # access the channel's device instance
        self.active_channels = bytearray() # array of active channels - for valid channel options
        self.inactive_channels = bytearray() # array of inactive channels - for skpping
        self.channel = 0 # current channel selected on multiplexer
        self.device_map = {} # dict that stores device instances, keys are channel
        self.multiplexer = i2c # access to the multiplexer itself
        self.device_id = {} # dict that stores device id, keys are channel
        self._chs = bytearray(8)
        self._buf = bytearray(1) # pre-allocate a 1 byte temp buffer
        self._init_multiplexer()

    def select_channel(self, ch: int):
        """
        Select a channel (0 through 7).
        """
        if ch >= 0 and ch < 8:
            self.multiplexer.writeto(MULTIPLEXER_ADDRESS, self._chs[ch])
        
        self.channel = ch
        self.device = self.device_map[self.channel]

    def next_device(self):
        """
        Select the next channel.
        """
        ch_index = self.active_channels.index(self.channel)
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
        ch_index = self.active_channels.index(self.channel)
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
        # pre-compute channels into bytearray
        chs = self._chs
        r = range(8)
        for i in r:
            chs[i] = 1 << i

        self._init_connected_devices()
        self.select_channel(self.active_channels[0])

    def _init_connected_devices(self):
        """
        Initialize the devices connected to the multiplexer. Note,
        only devices that are in the device library will be connected.
        Added the deivce address to the device library to connect the
        desired device. This method expects one device per channel.
        """
        # fetch methods and vars
        buf = self._buf
        chs = self._chs
        write = self.multiplexer.writeto
        scan = self.multiplexer.scan
        init_device = self._init_device
        a_chs = self.active_channels
        i_chs = self.inactive_channels
        device_id = self.device_id

        # find connected devices
        r = range(8)
        for i in r:
            buf[0] = chs[i]
            write(MULTIPLEXER_ADDRESS, buf)
            scan_out = scan()
            scan_out.remove(MULTIPLEXER_ADDRESS)
            for j in range(len(scan_out)):
                if scan_out[j] in DEVICE_LIBRARY:
                    init_device(scan_out[j], i)
                    a_chs.append(i)
                    device_id[i] = DEVICE_LIBRARY[scan_out[j]]
                elif len(scan_out) == 0:
                    i_chs.append(i)
                else:
                    device_id[i] = f"unknown device (addr: {scan_out[j]})"

    def _init_device(self, addr, ch):
        """
        Setup routines for individual devices.
        """
        # initialize display (ssd1306)
        if addr == SSD1306_ADDRESS:
            device = displayed.SSD1306_I2C(DISPLAY_WIDTH, DISPLAY_HEIGHT, self.multiplexer)
            device.fill(0)
            self.device_map[ch] = device
        
        # initialize sensors (hdc1080)
        if addr == HDC1080_ADDRESS:
            device = sensors.HDC1080(self.multiplexer)
            self.device_map[ch] = device
