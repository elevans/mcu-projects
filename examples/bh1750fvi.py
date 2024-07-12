from mcuexlib.devices import BH1750FVI
from machine import I2C, Pin
from micropython import const

# config I2C speed
I2C_FREQ = const(400000)

# config pins

# initialize the BH1750FVI sensor
BH1750FVI(I2C(id=0, scl=, sda=, freq=), BH1750FVI.ADDR_L)
