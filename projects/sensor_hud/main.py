import controled
import time
import machine
from micropython import const
from fonts import bookerly_15, ubuntu_condensed_12

# i2c config
FREQ = const(400000)

# state vars
snr_chs = bytes([1, 2]) # set sensor channels on the multiplexer
last_snr = snr_chs[0]
cur_ch = 0
dsp_state = 1

# interrupt vars
dsp_pwr = 1
mode = 0
snr = snr_chs[0]

def timed_function(f, *args, **kwargs):
    myname = str(f).split(' ')[1]
    def new_func(*args, **kwargs):
        t = time.ticks_us()
        result = f(*args, **kwargs)
        delta = time.ticks_diff(time.ticks_us(), t)
        print('Function {} Time = {:6.3f}ms'.format(myname, delta/1000))
        return result
    return new_func

def mode_interrupt(pin):
    """
    Mode selection interrupt (2 modes).
    """
    # get global states
    global mode

    # wait for stable butin signal (20ms)
    cur_val = pin.value()
    t = 0
    while t < 0:
        if pin.value() != cur_val:
            t += 1
        else:
            t = 0
        time.sleep(0.01)

    # toggle mode
    if mode == 0:
        mode = 1
    else:
        mode = 0

def snr_interrupt(pin):
    """
    Sensor selection interrupt.
    """
    # get global states
    global snr
    global last_snr
    last_snr = snr

    # wait for stable button signal (20ms)
    cur_val = pin.value()
    t = 0
    while t < 0:
        if pin.value() != cur_val:
            t += 1
        else:
            t = 0
        time.sleep(0.01)

    # cycle through sensors
    i = snr_chs.index((snr).to_bytes(1, 'little'))
    l = len(snr_chs)
    if i < l:
        i += 1
        if i >= l:
            i = 0
        snr = snr_chs[i]
    
def dsp_interrupt(pin):
    """
    Display power on/off interrupt.
    """
    # get global states
    global dsp_pwr
    
    # wait for stable button signal (20ms)
    cur_val = pin.value()
    t = 0
    while t < 0:
        if pin.value() != cur_val:
            t += 1
        else:
            t = 0
        time.sleep(0.01)

    # toggle display power state
    if dsp_pwr == 1:
        dsp_pwr = 0
    else:
        dsp_pwr = 1

# set sensor selection and mode pins
sel_btn = machine.Pin(16, machine.Pin.IN)
sel_btn.irq(snr_interrupt, machine.Pin.IRQ_FALLING)
mode_btn = machine.Pin(17, machine.Pin.IN)
mode_btn.irq(mode_interrupt, machine.Pin.IRQ_FALLING)
dsp_pwr_btn = machine.Pin(21, machine.Pin.IN)
dsp_pwr_btn.irq(dsp_interrupt, machine.Pin.IRQ_FALLING)

# init multiplexer
mux = controled.Multiplexer(machine.I2C(id=1, scl=machine.Pin(19), sda=machine.Pin(18), freq=FREQ))

# display logo
with open("lib/logo.bin", "rb") as f:
    logo = bytearray(f.read())
mux.select_channel(0)
mux.device.fill(0)
mux.device.draw_bytes(logo)
mux.device.show()
time.sleep(0.75)

while True:
    # toggle display on/off
    if dsp_pwr == 1 and dsp_state == 0:
        mux.select_channel(0)
        mux.device.poweron()
        dsp_state = 1
    elif dsp_pwr == 0 and dsp_state == 1:
        mux.select_channel(0)
        mux.device.poweroff()
        dsp_state = 0
    else:
        pass

    # read selected sensors (only when screen is on)
    if dsp_pwr == 1 and dsp_state == 1:
        # sensor selection
        if snr != last_snr:
            mux.select_channel(snr)
            last_snr = snr
        # delay sensor reads
        time.sleep(0.1)
        # read sensor via ID check
        if mux.device_id[snr] == 'sensor (hdc1080)':
            mux.select_channel(snr)
            if mode == 0:
                t = round(mux.device.get_temp('c'), 1)
            if mode == 1:
                t = round(mux.device.get_temp('f'), 1)
            h = round(mux.device.get_hum(), 1)
            # draw data on screen
            mux.select_channel(0)
            mux.device.fill(0)
            if snr == 1:
                mux.device.rect(85, 10, 32, 18, 1, False)
                mux.device.fw_text("inside", ubuntu_condensed_12, 89, 12)
                mux.device.text("T", 5, 8)
                mux.device.text(":", 21, 8)
            if snr == 2:
                mux.device.rect(85, 10, 38, 18, 1, False)
                mux.device.fw_text("outside", ubuntu_condensed_12, 89, 12)
                mux.device.text("T", 5, 8)
                mux.device.text(":", 21, 8)
            if mode == 0:
                mux.device.text(f"{t}C", 30, 8)
            if mode == 1:
                mux.device.text(f"{t}F", 30, 8)
            mux.device.text("RH:", 5, 25)
            mux.device.text(f"{h}%", 30, 25)
            mux.device.show()
    else:
        pass
