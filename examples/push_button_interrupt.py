from machine import Pin, disable_irq, enable_irq
from utime import sleep_ms

def btn_push_interrupt(pin):
    """Detect a button press.

    Detect a button press with a default of
    10 ms delay.
    """
    global btn_st
    global btn_t

    cv = pin.value()
    btn_t = 0
    # wait for stable button signal
    while btn_t < 10:
        if pin.value() ==  cv:
            btn_t += 1
        else:
            btn_t = 0
        sleep_ms(1)
    
    # toggle between 0 and 1
    btn_st ^= 1

# config pins
btn = Pin(14, Pin.IN)

# global button vars
btn_cv = 1 # current value
btn_lv = 1 # last value
btn_st = 1 # button state for ISR
btn_t = 0 # button time counter

# initialize button w/ intterupt
btn.irq(btn_push_interrupt, Pin.IRQ_FALLING)

# do something different based on the button state
while True:
    if btn_st == 1:
        st = disable_irq()
        # do something
        enable_irq(st)
    else:
        st = disable_irq()
        # do something
        enable_irq(st)

