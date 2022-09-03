import framebuf
import sensors
import time
from machine import Pin, I2C
from display import SSD1306_I2C
from micropython import const

# set constants
DISPLAY_WIDTH = const(128)
DISPLAY_HEIGHT = const(32)
MULTIPLEXER_ADDRESS = const(0x70)
FREQ = const(100000)
SENSOR_COUNT = const(2)
MODE_COUNT = const(2)

# set pins
mux_scl = Pin(15)
mux_sda = Pin(14)
button_sensor_select = Pin(16, Pin.IN, Pin.PULL_DOWN)
button_mode_select = Pin(17, Pin.IN, Pin.PULL_DOWN)

# global vars
sensor_selected = 1
mode_selected = 1
button_sensor_select_state = 0
button_mode_select_state = 0
last_button_sensor_select_state = 0
last_button_mode_select_state = 0

def get_display(channel):
    select_mux_channel(channel)
    display = SSD1306_I2C(DISPLAY_WIDTH, DISPLAY_HEIGHT, i2c_multiplexer)
    display.fill(0)
    return display

def select_mux_channel(channel):
    if channel >= 0 and channel < 8:
        value = 1 << channel
        # 0x70 is the default address of the tca - you can connect up to 8 - 0x70 to 0x77
        i2c_multiplexer.writeto(MULTIPLEXER_ADDRESS, value.to_bytes(1,'little'))

def next_sensor():
    global sensor_selected
    sensor_selected += 1
    if sensor_selected > SENSOR_COUNT:
        sensor_selected = 1

def next_mode():
    global mode_selected
    mode_selected += 1
    if mode_selected > MODE_COUNT:
        mode_selected = 1

# initialize I2C multiplexer
i2c_multiplexer = I2C(1, scl=mux_scl, sda=mux_sda, freq=FREQ)

# initialize multiplexer connected devices
select_mux_channel(0)
display_1 = SSD1306_I2C(DISPLAY_WIDTH, DISPLAY_HEIGHT, i2c_multiplexer)
select_mux_channel(1)
sensor_temp_hum_1 = sensors.HDC1080(i2c_multiplexer)
select_mux_channel(2)
sensor_temp_hum_2 = sensors.HDC1080(i2c_multiplexer)

while True:
    # read button states
    button_sensor_select_state = button_sensor_select.value()
    button_mode_select_state = button_mode_select.value()

    # check if buttons are pushed
    if (button_sensor_select_state == 1) and (last_button_sensor_select_state == 0):
        next_sensor()
    if (button_mode_select_state == 1) and (last_button_mode_select_state == 0):
        next_mode()

    # read the appropriate sensors
    if sensor_selected == 1:
        select_mux_channel(1)
        if mode_selected == 1:
            temp = round(sensor_temp_hum_1.get_temp(), 1)
        if mode_selected == 2:
            temp = round(sensor_temp_hum_1.get_temp(unit="f"), 1)
        hum = round(sensor_temp_hum_1.get_hum(), 1)
    if sensor_selected == 2:
        select_mux_channel(2)
        if mode_selected == 1:
            temp = round(sensor_temp_hum_2.get_temp(), 1)
        if mode_selected == 2:
            temp = round(sensor_temp_hum_2.get_temp(unit="f"), 1)
        hum = round(sensor_temp_hum_2.get_hum(), 1)

    # display sensor data
    select_mux_channel(0)
    display_1.fill(0)
    if sensor_selected == 1:
        if mode_selected == 1:
            display_1.text(f"Ti: {temp}C", 0, 0)
            display_1.text(f"Hum: {hum}%", 0, 12)
        if mode_selected == 2:
            display_1.text(f"Ti: {temp}F", 0, 0)
            display_1.text(f"Hum: {hum}%", 0, 12)
    if sensor_selected == 2:
        if mode_selected == 1:
            display_1.text(f"To: {temp}C", 0, 0)
            display_1.text(f"Hum: {hum}%", 0, 12)
        if mode_selected == 2:
            display_1.text(f"To: {temp}F", 0, 0)
            display_1.text(f"Hum: {hum}%", 0, 12)
    display_1.show()

    # read button states
    last_button_sensor_select_state = button_sensor_select_state
    last_button_mode_select_state = button_mode_select_state