# mcu-projects

This repository contains various microcontrolluer unit (MCU) projects and libraries. The arduino and micropython folders contain their respecive projects. Typically I use an Arduino Nano and Raspberry Pi Pico (RP2040).

## Arduino Projects
| Project             | File                                     | Description                             |
| -------             | ----                                     | -----------                             |
| I2C address scanner | `arduino/sketch/i2c_address_scanner.ino` | Scans all address on an I2C multiplexer |
| LED dimmer (PWM)    | `arduino/sketch/led_dimmer.ino`          | Dims LED's via PWM and a MOSFET         |

## MicroPython projects
| Project             | File                                          | Description                                                |
| -------             | ----                                          | -----------                                                |
| DC Motor controller | `micropython/projects/motor_speed_controller` | Uses RP2040 to generate PWM to drive a MOSFET              |
| Snensor hud         | `micropython/projects/sensor_hud`             | Uses I2C Multiplexer to read and display connected sensors |

## MicroPython libraries

| Library     | File                           | Description                                          |
| -------     | ----                           | -----------                                          |
| `controled` | `micropython/lib/controled.py` | I2C Multiplexer controls                             |
| `displayed` | `micropython/lib/displayed.py` | Modified version of the `micropython-ssd1306` driver |
| `sensors`   | `micropython/lib/sensors.py`   | Drivers for various sensors                          |
| `fonts`     | `micropython/lib/fonts.py`     | Fonts converted into Python binary                   |