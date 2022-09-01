from machine import Pin, I2C

i2c = I2C(0,scl=Pin(17), sda=Pin(16), freq=400000)

def select_channel(ch):
    if ch >= 0 and ch < 8:
        value = 1 << ch
        # 0x70 is the default address of the tca - you can connect up to 8 - 0x70 to 0x77
        i2c.writeto( 0x70, value.to_bytes(1,'little') )
                
select_channel(7) # from 0..7
