# displayed

This library is a custom version of the `micropython-ssd1306` display driver. This version adds minor speed improvements, for example by pre-fetching frequently used methods, and additional drawing functions.

## Usage

```python
import displayed
from machine import Pin, I2C

# initialize the display
i2c = I2C(id=0, scl=Pin(13), sda=Pin(12), freq=400000)
dsp = displayed.SSD1306_12C(128, 32, i2c)
```