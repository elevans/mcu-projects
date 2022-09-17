import display
import controled
import sensors
import framebuf
import time
import bookerly_15, ubuntu_condensed_12
from machine import Pin
from micropython import const

# set pins
d1_sensor_select = Pin(16, Pin.IN, Pin.PULL_DOWN)
d1_mode_select = Pin(17, Pin.IN, Pin.PULL_DOWN)
d2_sensor_select = Pin(18, Pin.IN, Pin.PULL_DOWN)
d2_mode_select = Pin(19, Pin.IN, Pin.PULL_DOWN)
display_power_select = Pin(20, Pin.IN, Pin.PULL_DOWN)

# button states #TODO make sensor state reads local in a function
display_power_state = 0
d1_sensor_state = 0
d1_mode_state = 0
d2_sensor_state = 0
d2_mode_state = 0
last_display_power_state = 0
last_d1_sensor_state = 0
last_d1_mode_state = 0
last_d2_sensor_state = 0
last_d2_mode_state = 0

# global variables
dsp_chs = [0, 1] # use a bytearray or some other array of chs instead of List
dsp_pwr = 0
snr_loc = {
    6: "inside",
    7: "outside"
}
d1_linked_channel = None
d1_linked_device_id = None
d1_linked_mode = None
d2_linked_channel = None
d2_linked_device_id = None
d2_linked_mode = None

def create_writer(mux, ch, font):
    return display.FontWriter(mux.connected_device[ch], font)

def clear_displays(mux, ch_list):
    r = range(len(ch_list))
    for i in r:
        mux.connected_device[ch_list[i]].fill(0)

def draw_sensor_data(mux, dsp_ch, snr_ch, mode, id):
    if id == "sensor_hdc1080":
        mux.select_channel(snr_ch)
        if mode == 0:
            temp = round(mux.device.get_temp(), 1)
        else:
            temp = round(mux.device.get_temp(unit="f"), 1)
        hum = round(mux.device.get_hum(), 1)
    # draw display
    mux.connected_device[dsp_ch]
    return

def draw_logo(mux, ch_list):
    f = open("lib/logo.bin", "rb")
    img_bytes = bytearray(f.read())
    r = range(len(ch_list))
    for i in r:
        mux.connected_device[i].graphics.draw_bytes(img_bytes)

def update_displays(mux, ch_list):
    sel_ch = mux.select_channel
    show = mux.device.show
    r = range(len(ch_list))
    for i in r:
        sel_ch(ch_list[i])
        show()

# initialize I2C multiplexer
mux = controled.Multiplexer(i2c_id=1, scl_pin=Pin(15), sda_pin=Pin(14))

# draw logo on displays
#f = open("lib/logo.bin", "rb")
#img_bytes = bytearray(f.read())
#d1_graphics = display.Graphics(width=115, height=32, display=mux.connected_device[0])
#d2_graphics = display.Graphics(width=115, height=32, display=mux.connected_device[1])
#d1_graphics.draw_bytes(img_bytes)
#d2_graphics.draw_bytes(img_bytes)
draw_logo(mux, dsp_chs)
update_displays(mux, dsp_chs)
time.sleep(3.0)
clear_displays(mux, dsp_chs)
update_displays(mux, dsp_chs)

# create font writers
d1_writer12 = create_writer(mux, 0, ubuntu_condensed_12)
d1_writer15 = create_writer(mux, 0, bookerly_15)
d2_writer12 = create_writer(mux, 1, ubuntu_condensed_12)
d2_writer15 = create_writer(mux, 1, bookerly_15)

# skip the first two display channels
sensor_channels = mux.active_channels[2:]

# assign first two sensors to each dispaly
d1_linked_channel = sensor_channels[0]
d1_linked_device_id = mux.connected_device_id[sensor_channels[0]]
d1_linked_mode = 0
d2_linked_channel = sensor_channels[1]
d2_linked_device_id = mux.connected_device_id[sensor_channels[1]]
d2_linked_mode = 0

while True:
    # read button states
    d1_sensor_state = d1_sensor_select.value()
    d1_mode_state = d1_mode_select.value()
    d2_sensor_state = d2_sensor_select.value()
    d2_mode_state = d2_mode_select.value()
    display_power_state = display_power_select.value()

    # check if display power button pushed
    if display_power_state == 1 and last_display_power_state == 0:
        if dsp_pwr == 0:
            dsp_pwr = 1
        else:
            dsp_pwr = 0
            
    # assign a sensor to a display if button pushed
    if d1_sensor_state == 1 and last_d1_sensor_state == 0:
        i = sensor_channels.index(d1_linked_channel)
        if i < len(sensor_channels):
            i += 1
        if i >= len(sensor_channels):
            i = 0
        d1_linked_channel = sensor_channels[i]
        d1_linked_device_id = mux.connected_device_id[sensor_channels[i]]

    if d2_sensor_state == 1 and last_d2_sensor_state == 0:
        i = sensor_channels.index(d2_linked_channel)
        if i < len(sensor_channels):
            i += 1
        if i >= len(sensor_channels):
            i = 0
        d2_linked_channel = sensor_channels[i]
        d2_linked_device_id = mux.connected_device_id[sensor_channels[i]]
    
    # assign a mode if button pushed
    if d1_mode_state == 1 and last_d1_mode_state == 0:
        if d1_linked_mode == 0:
            d1_linked_mode = 1
        else:
            d1_linked_mode = 0
    if d2_mode_state == 1 and last_d2_mode_state == 0:
        if d2_linked_mode == 0:
            d2_linked_mode = 1
        else:
            d2_linked_mode = 0

    # draw sensor data
    draw_sensor_data(mux, dsp_chs[0], d1_linked_channel, d1_linked_mode, d1_linked_device_id)
    draw_sensor_data(mux, dsp_chs[1], d2_linked_channel, d2_linked_mode, d2_linked_device_id)

    # update displays
    update_displays(mux)

    # assign last sensors states
    last_d1_sensor_state = d1_sensor_state
    last_d1_mode_state = d1_mode_state
    last_d2_sensor_state = d2_sensor_state
    last_d2_mode_state = d2_mode_state