import framebuf
from micropython import const

# constants
SSD1306_ADDRESS = const(0x3C)
SET_CONTRAST = const(0x81)
SET_ENTIRE_ON = const(0xA4)
SET_NORM_INV = const(0xA6)
SET_DISP = const(0xAE)
SET_MEM_ADDR = const(0x20)
SET_COL_ADDR = const(0x21)
SET_PAGE_ADDR = const(0x22)
SET_DISP_START_LINE = const(0x40)
SET_SEG_REMAP = const(0xA0)
SET_MUX_RATIO = const(0xA8)
SET_IREF_SELECT = const(0xAD)
SET_COM_OUT_DIR = const(0xC0)
SET_DISP_OFFSET = const(0xD3)
SET_COM_PIN_CFG = const(0xDA)
SET_DISP_CLK_DIV = const(0xD5)
SET_PRECHARGE = const(0xD9)
SET_VCOM_DESEL = const(0xDB)
SET_CHARGE_PUMP = const(0x8D)


class SSD1306(framebuf.FrameBuffer):
    def __init__(self, width, height, external_vcc):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.temp_bar_max = [0, 0] # for dual bar graph max values
        self.init_display()

    def init_display(self):
        for cmd in (
            SET_DISP,  # display off
            # address setting
            SET_MEM_ADDR,
            0x00,  # horizontal
            # resolution and layout
            SET_DISP_START_LINE,  # start at line 0
            SET_SEG_REMAP | 0x01,  # column addr 127 mapped to SEG0
            SET_MUX_RATIO,
            self.height - 1,
            SET_COM_OUT_DIR | 0x08,  # scan from COM[N] to COM0
            SET_DISP_OFFSET,
            0x00,
            SET_COM_PIN_CFG,
            0x02 if self.width > 2 * self.height else 0x12,
            # timing and driving scheme
            SET_DISP_CLK_DIV,
            0x80,
            SET_PRECHARGE,
            0x22 if self.external_vcc else 0xF1,
            SET_VCOM_DESEL,
            0x30,  # 0.83*Vcc
            # display
            SET_CONTRAST,
            0xFF,  # maximum
            SET_ENTIRE_ON,  # output follows RAM contents
            SET_NORM_INV,  # not inverted
            SET_IREF_SELECT,
            0x30,  # enable internal IREF during display on
            # charge pump
            SET_CHARGE_PUMP,
            0x10 if self.external_vcc else 0x14,
            SET_DISP | 0x01,  # display on
        ):  # on
            self.write_cmd(cmd)
        self.fill(0)
        self.show()

    def poweroff(self):
        self.write_cmd(SET_DISP)

    def poweron(self):
        self.write_cmd(SET_DISP | 0x01)

    def contrast(self, contrast):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)

    def invert(self, invert):
        self.write_cmd(SET_NORM_INV | (invert & 1))

    def rotate(self, rotate):
        self.write_cmd(SET_COM_OUT_DIR | ((rotate & 1) << 3))
        self.write_cmd(SET_SEG_REMAP | (rotate & 1))

    def show(self):
        write_cmd = self.write_cmd
        x0 = 0
        x1 = self.width - 1
        if self.width != 128:
            # narrow displays use centred columns
            col_offset = (128 - self.width) // 2
            x0 += col_offset
            x1 += col_offset
        write_cmd(SET_COL_ADDR)
        write_cmd(x0)
        write_cmd(x1)
        write_cmd(SET_PAGE_ADDR)
        write_cmd(0)
        write_cmd(self.pages - 1)
        self.write_data(self.buffer)

    def draw_bytes(self, buffer: bytearray):
        """Draw an image from a bytearray/buffer.

        Draw a bytearray on the display using a FrameBuffer and blit.
        """
        fb = framebuf.FrameBuffer(buffer, self.width, self.height, framebuf.MONO_HLSB)
        self.fill(0)
        self.blit(fb, 0, 0)

    def circle(self, x0, y0, radius, *args, **kwargs):
        # Circle drawing function.  Will draw a single pixel wide circle with
        # center at x0, y0 and the specified radius.
        pixel = self.pixel
        f = 1 - radius
        ddF_x = 1
        ddF_y = -2 * radius
        x = 0
        y = radius
        pixel(x0, y0 + radius, *args, **kwargs)
        pixel(x0, y0 - radius, *args, **kwargs)
        pixel(x0 + radius, y0, *args, **kwargs)
        pixel(x0 - radius, y0, *args, **kwargs)
        while x < y:
            if f >= 0:
                y -= 1
                ddF_y += 2
                f += ddF_y
            x += 1
            ddF_x += 2
            f += ddF_x
            pixel(x0 + x, y0 + y, *args, **kwargs)
            pixel(x0 - x, y0 + y, *args, **kwargs)
            pixel(x0 + x, y0 - y, *args, **kwargs)
            pixel(x0 - x, y0 - y, *args, **kwargs)
            pixel(x0 + y, y0 + x, *args, **kwargs)
            pixel(x0 - y, y0 + x, *args, **kwargs)
            pixel(x0 + y, y0 - x, *args, **kwargs)
            pixel(x0 - y, y0 - x, *args, **kwargs)

    def h_dual_bar_graph_frame(self, x, y, s1, s2):
        # draw frame and labels
        line = self.line
        line(x + 10, y + 0, x + 10, y + 32, 1)
        line(x + 10, y + 16, self.width, y + 16, 1)
        self.text(s1, 0, 4)
        self.text(s2, 0, 24)

        # draw major and minor divisions on x axis
        div_major_pos = x + 10
        while div_major_pos <= (self.width - 10):
            line(div_major_pos, y + 12, div_major_pos, y + 20, 1)
            div_major_pos += 12 # 128 / 10 = ~12 divisions

        div_minor_pos = x + 10
        while div_minor_pos <= (self.width -10):
            line(div_minor_pos, y + 14, div_minor_pos, y + 18, 1)
            div_minor_pos += 6 # 128 / 20 = ~6 divisions

    def h_dual_bar_graph_data(self, v1, v2, rect, vline, x=0, y=0):
        # TODO: test if self.rect and self.vline vs rect and vline is same speed
        # clear bars
        rect(11, 4, self.width, 5, 0, True)
        rect(11, 24, self.width, 5, 0, True)
        # draw bars
        rect(11, 4, v1, 5, 1, True)
        rect(11, 24, v2, 5, 1, True)

        # draw/update max memory line
        if v1 > self.temp_bar_max[0]:
            self.temp_bar_max[0] = v1
        if v2 > self.temp_bar_max[1]:
            self.temp_bar_max[1] = v2
        vline(x + self.temp_bar_max[0] + 10, y + 4, 5, 1)
        vline(x + self.temp_bar_max[1] + 10, y + 24, 5, 1)

    def fill_circle(self, x0, y0, radius, *args, **kwargs):
        # Filled circle drawing function.  Will draw a filled circule with
        # center at x0, y0 and the specified radius.
        vline = self.vline
        vline(x0, y0 - radius, 2 * radius + 1, *args, **kwargs)
        f = 1 - radius
        ddF_x = 1
        ddF_y = -2 * radius
        x = 0
        y = radius
        while x < y:
            if f >= 0:
                y -= 1
                ddF_y += 2
                f += ddF_y
            x += 1
            ddF_x += 2
            f += ddF_x
            vline(x0 + x, y0 - y, 2 * y + 1, *args, **kwargs)
            vline(x0 + y, y0 - x, 2 * x + 1, *args, **kwargs)
            vline(x0 - x, y0 - y, 2 * y + 1, *args, **kwargs)
            vline(x0 - y, y0 - x, 2 * x + 1, *args, **kwargs)

    def triangle(self, x0, y0, x1, y1, x2, y2, c):
        # Triangle drawing function.  Will draw a single pixel wide triangle
        # around the points (x0, y0), (x1, y1), and (x2, y2).
        line = self.line
        line(x0, y0, x1, y1, c)
        line(x1, y1, x2, y2, c)
        line(x2, y2, x0, y0, c)

    def fill_triangle(self, x0, y0, x1, y1, x2, y2, *args, **kwargs):
        # Filled triangle drawing function.  Will draw a filled triangle around
        # the points (x0, y0), (x1, y1), and (x2, y2).
        hline = self.hline
        if y0 > y1:
            y0, y1 = y1, y0
            x0, x1 = x1, x0
        if y1 > y2:
            y2, y1 = y1, y2
            x2, x1 = x1, x2
        if y0 > y1:
            y0, y1 = y1, y0
            x0, x1 = x1, x0
        a = 0
        b = 0
        y = 0
        last = 0
        if y0 == y2:
            a = x0
            b = x0
            if x1 < a:
                a = x1
            elif x1 > b:
                b = x1
            if x2 < a:
                a = x2
            elif x2 > b:
                b = x2
            hline(a, y0, b - a + 1, *args, **kwargs)
            return
        dx01 = x1 - x0
        dy01 = y1 - y0
        dx02 = x2 - x0
        dy02 = y2 - y0
        dx12 = x2 - x1
        dy12 = y2 - y1
        if dy01 == 0:
            dy01 = 1
        if dy02 == 0:
            dy02 = 1
        if dy12 == 0:
            dy12 = 1
        sa = 0
        sb = 0
        if y1 == y2:
            last = y1
        else:
            last = y1 - 1
        for y in range(y0, last + 1):
            a = x0 + sa // dy01
            b = x0 + sb // dy02
            sa += dx01
            sb += dx02
            if a > b:
                a, b = b, a
            hline(a, y, b - a + 1, *args, **kwargs)
        sa = dx12 * (y - y1)
        sb = dx02 * (y - y0)
        while y <= y2:
            a = x1 + sa // dy12
            b = x0 + sb // dy02
            sa += dx12
            sb += dx02
            if a > b:
                a, b = b, a
            hline(a, y, b - a + 1, *args, **kwargs)
            y += 1


class SSD1306_I2C(SSD1306):
    def __init__(self, width, height, i2c, addr=SSD1306_ADDRESS, external_vcc=False):
        self.i2c = i2c
        self.addr = addr
        self.temp = bytearray(2)
        self.write_list = [b"\x40", None]  # Co=0, D/C#=1
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        self.temp[0] = 0x80  # Co=1, D/C#=0
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)

    def write_data(self, buf):
        self.write_list[1] = buf
        self.i2c.writevto(self.addr, self.write_list)


class SSD1306_SPI(SSD1306):
    def __init__(self, width, height, spi, dc, res, cs, external_vcc=False):
        self.rate = 10 * 1024 * 1024
        dc.init(dc.OUT, value=0)
        res.init(res.OUT, value=0)
        cs.init(cs.OUT, value=1)
        self.spi = spi
        self.dc = dc
        self.res = res
        self.cs = cs
        import time

        self.res(1)
        time.sleep_ms(1)
        self.res(0)
        time.sleep_ms(10)
        self.res(1)
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(buf)
        self.cs(1)

# TODO: Initialize font writer w/ display on startup?
class FontWriter:
    """
    Creates an "Writer" object with the desired font. Different fonts can be used with different
    instances of the FontWriter
    """
    def __init__(self, buffer, font):
        self.buffer = buffer
        self.font = font._FONT

    def text(self, string, x=0, y=0, color=0xffff, bgcolor=0, colors=None):
        buffer = self.buffer
        font = self.font

        if colors is None:
            colors = (color, color, bgcolor, bgcolor)

        for c in string:

            if not ord(c) in font.keys():
                c = "?"

            row = y
            _w, * _font = font[ord(c)]
            for byte in _font:
                unsalted = byte
                for col in range(x, x + _w):
                    color = colors[unsalted & 0x03]
                    if color is not None:
                        buffer.pixel(col, row, color)
                    unsalted >>= 2
                row += 1
            x += _w

    def char(self, c, x=0, y=0, color=0xffff, bgcolor=0, colors=None):
        buffer = self.buffer
        font = self.font

        if colors is None:
            colors = (color, color, bgcolor, bgcolor)

        # for c in string:
        if not c in font.keys():
            return 0

        row = y
        _w, * _font = font[c]
        for byte in _font:
            unsalted = byte
            for col in range(x, x + _w):
                color = colors[unsalted & 0x03]
                if color is not None:
                    buffer.pixel(col, row, color)
                unsalted >>= 2
            row += 1
        x += _w
