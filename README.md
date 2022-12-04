# mcu-projects

This repository contains various microcontrolluer unit (MCU) projects and libraries##. The arduino and micropython folders contain their respecive projects. Typically I use an Arduino Nano and Raspberry Pi Pico (RP2040).

## Arduino Projects
Things :).

## MicroPython projects
| Project | File | Description |
| :---: | :---: | :---: |
| DC Motor controller | `projects/motor_speed_controller` | Uses RP2040 to generate PWM to drive a MOSFET |
| Snensor hud | `projects/sensor_hud` | Uses I2C Multiplexer to read and display connected sensors

## MicroPython libraries

| Library | File | Description | 
| :---: | :---: | :---: |
| `controled` | `lib/controled.py` | I2C Multiplexer controls |
| `displayed` | `lib/displayed.py` | Modified version of the `micropython-ssd1306` driver |
| `sensors` | `lib/sensors.py` | Drivers for various sensors |
| `fonts` | `lib/fonts.py` | Fonts converted into Python binary |