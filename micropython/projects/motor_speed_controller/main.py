import displayed
import time
from machine import Pin, I2C, ADC, PWM
from micropython import const

# i2c config
FREQ = const(400000)
DISPLAY_HEIGHT = const(32)
DISPLAY_WIDTH = const(128)

# init resources
pot = ADC(26)
#pwm = PWM(Pin(10))
#pwm.freq(10000) # should be 10-20 khz for MOSFET

# init display
dsp = displayed.SSD1306_I2C(DISPLAY_WIDTH, DISPLAY_HEIGHT, I2C(id=1, scl=Pin(15), sda=Pin(14), freq=FREQ))
dsp.fill(0)

# draw bar graph frame
dsp.text("speed", 10, 0, 1)
dsp.h_bar_graph_frame()

while True:
    r = pot.read_u16()
    dsp.rect(60, 0, 67, 7, 0, True) # clear upper right corner
    dsp.text(f"{r}", 75, 0, 1)
    dsp.h_bar_graph_data(r, dsp.rect)
    dsp.show()
    #pwm.duty_u16(r)