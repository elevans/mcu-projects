# Controled

This library contains the following convience classes for controlling devices.

| Class | Purpose |
| :---: | :---: |
| `Multiplexer` | Initializes a multiplexer and connected dvices. |

## Usage

Initialize the Multiplexer class with the I2C clock and data pins.

```python
import controled
from machine import Pin

mux = controled.Multiplexer(i2c_id=1, scl_pin=Pin(15), sda_pin=Pin(14))
```

The `Multiplexer` class will automatically scan all channels and populate the `connected_devices` dictionary.

```python
>>> mux.connected_devices
```

To add new devices to the `Multiplexer` setup, add the address to the `DEVICE_LIBRARY` dictionary and add the appropriate startup steps to the `_init_device` function.