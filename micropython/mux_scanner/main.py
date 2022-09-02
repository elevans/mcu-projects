from machine import Pin, I2C
from micropython import const

# set constants
MULTIPLEXER_ADDR = const(0x70)

# initialize multiplexer
i2c_multiplexer = I2C(1 ,scl=Pin(15), sda=Pin(14), freq=400000)

def select_channel(ch):
    if ch >= 0 and ch < 8:
        value = 1 << ch
        # 0x70 is the default address of the tca - you can connect up to 8 - 0x70 to 0x77
        i2c_multiplexer.writeto(MULTIPLEXER_ADDR, value.to_bytes(1,'little') )
                
select_channel(0) # from 0..7