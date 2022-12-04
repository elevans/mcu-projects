# MicroPython Projects
Here are my miropython projects

## Support Libraries
These libraries provide basic controls for multiplexers, displays and sensors.

### controled
This library provides methods to automatically initialize an I2C multiplexer and the devices connected to it. `controled.py` depends on `sensors.py` which contains the drivers for various sensors.

### displayed
A modified version of the `micropython-ssd1306` display driver. Added features include:

- Font text/char writer
- Single/Dual horizontal bar graphs (scale frame)
- Draw images using the `FrameBuffer`.
- Draw a display selection frame (for multiple displays)
- Various minor speed improvments

`displayed.py` depends on `fonts.py` which contains 3 different fonts in binary format.

## Projects

### motor_speed_controller

### sensor_hud

### digital delay magic