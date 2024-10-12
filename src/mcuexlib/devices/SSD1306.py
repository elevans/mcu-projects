import framebuf
import array as arr
from micropython import const

ADDR = const(0x3C)
CONFIG_CONTRAST = const(0x81)
CONFIG_ENTIRE_ON = const(0xA4)
CONFIG_NORM_INV = const(0xA6)
CONFIG_DISP = const(0xAE)
CONFIG_MEM_ADDR = const(0x20)
CONFIG_COL_ADDR = const(0x21)
CONFIG_PAGE_ADDR = const(0x22)
CONFIG_DISP_START_LINE = const(0x40)
CONFIG_SEG_REMAP = const(0xA0)
CONFIG_MUX_RATIO = const(0xA8)
CONFIG_IREF_SELECT = const(0xAD)
CONFIG_COM_OUT_DIR = const(0xC0)
CONFIG_DISP_OFFSET = const(0xD3)
CONFIG_COM_PIN_CFG = const(0xDA)
CONFIG_DISP_CLK_DIV = const(0xD5)
CONFIG_PRECHARGE = const(0xD9)
CONFIG_VCOM_DESEL = const(0xDB)
CONFIG_CHARGE_PUMP = const(0x8D)

class SSD1306(framebuf.FrameBuffer):
    def __init__(self, width:int, height: int):
        self.width = width
        self.height = height
        self._pages = self.height // 8
        self._buf = bytearray(self._pages * self.width)
        super().__init__(self._buf, self.width, self.height, framebuf.MONO_VSLB)
        self._init_device()

    def _init_device(self):
        """
        """
        # initialization commands
        cmds = (
                CONFIG_DISP, # set display off
                CONFIG_MEM_ADDR,
                0x00,
                CONFIG_DISP_START_LINE, # set start line
                CONFIG_SEG_REMAP | 0x01,
                CONFIG_MUX_RATIO,
                self.height - 1,
                CONFIG_COM_OUT_DIR | 0x08,
                CONFIG_DISP_OFFSET,
                0x00,
                CONFIG_COM_PIN_CFG,
                0x02 if self.width > 2 * self.height else 0x12,
                CONFIG_DISP_CLK_DIV,
                0x80,
                CONFIG_PRECHARGE, # no external vcc
                0xF1,
                CONFIG_VCOM_DESEL,
                0x30, # 0.83 * vcc
                CONFIG_CONTRAST,
                0xFF, # set to max contrast
                CONFIG_ENTIRE_ON, # set output to follow RAM contents
                CONFIG_NORM_INV, # set
                )
        for c  in cmds:
            # TODO in python test in a for loop 0x80 <<< 8 | c
            cmd_byte = 0x80 << 8
            self.i2c.writeto(self.addr, cmd_byte | c)


class SSD1306_I2C(SSD1306):
    def __init__(self, height: int, width: int, i2c):
        # TODO finish this section

class SSD1306_SPI(SSD1306):
    def __init__(self, height: int, width: int, spi, dc, res, cs):
        # TODO finish this section
