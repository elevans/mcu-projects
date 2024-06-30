from machine import Pin
from utime import sleep_ms

# config pins
btn = Pin(14, Pin.IN)

# global push button vars
btn_cv = 1 # current value
btn_lv = 1 # last value
btn_state = 1 # global button state for ISR
btn_t = 0 # button time counter

def btn_push_interrupt(pin):
    """Detect a button press.

    Detect a button press with a default of
    10 ms delay.
    """
    global btn_state
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
    btn_state = btn_state ^ 1


# initialize button w/ intterupt
btn_1.irq(btn_push_interrupt, Pin.IRQ_FALLING)

# do something different based on the button state
while True:
    if btn_state == 1:
        print("1")
    else:
        print("0")
