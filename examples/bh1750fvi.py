from mcuexlib.devices import BH1750FVI
from machine import I2C, Pin
from micropython import const

# config I2C speed
I2C_FREQ = const(400000)

# config pins
bh1750_sda = Pin()
bh1750_scl = Pin()

# initialize the BH1750FVI sensor
BH1750FVI(I2C(id=0,sda=bh1750_sda, scl=bh1750_scl, freq=I2C_FREQ), BH1750FVI.ADDR_L)
