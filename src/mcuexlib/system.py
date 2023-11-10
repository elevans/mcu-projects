import machine
import utime

def temp(unit: str = 'c'):
    """
    Get internal temperature reading (C or F).
    """
    convresion = 3.3 / (65535)
    read = machine.ADC(4).read_u16() * convresion
    t = 27 - (read - 0.706)/0.001721
    if unit == 'c':
        return t
    else:
        return t * 9 / 5 + 32