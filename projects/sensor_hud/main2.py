import machine
import lib.devices as dev
from micropython import const

# const values
FREQ = const(400000)
DISPLAY_WIDTH = const(128)
DISPLAY_HEIGHT = const(32)

# setup pins
mux_scl = machine.Pin(19)
mux_sda = machine.Pin(18)

# init multiplexer
mux = dev.init_i2c_multiplexer(machine.I2C(id=0, scl=mux_scl, sda=mux_sda, freq=FREQ))

# init dual displays and register with the multiplexer
mux.register_device(
    mux.get_device_address(0)[0],
    0,
    "display 1",
    dev.init_ssd1306_display(DISPLAY_WIDTH, DISPLAY_HEIGHT, "i2c", mux.multiplexer),
)
mux.register_device(
    mux.get_device_address(1)[0],
    1,
    "display 2",
    dev.init_ssd1306_display(DISPLAY_WIDTH, DISPLAY_HEIGHT, "i2c", mux.multiplexer)
)

# register the sensors with the multiplexer