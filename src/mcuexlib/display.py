import framebuf
import array as arr
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
        self._fdata = [] # list of actual font data type bytes
        self._finfo = {} # dict for font info
        self._fmagickey = bytes([0x21, 0x46, 0x44, 0x01]) # magic key for fonts
        self.init_display()
        self.graph = Graph(self) # attah graphing methods

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
        # fetch methods
        write_cmd = self.write_cmd
        width = self.width

        x0 = 0
        x1 = width - 1
        if width != 128:
            # narrow displays use centred columns
            col_offset = (128 - width) // 2
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

        :param buffer: Image data in a bytearray.
        """
        fb = framebuf.FrameBuffer(buffer, self.width, self.height, framebuf.MONO_HLSB)
        self.fill(0)
        self.blit(fb, 0, 0)

    def draw_select_frame(self, l=5):
        """Draw a frame around the display.

        Draw a frame around the display. This is intended to indicate a selected
        display.

        :param l: Length of the frame lines (defualt=5)
        """
        # fetch methods and vars
        line = self.line
        h = self.height - 1
        w = self.width - 1

        # top left corner
        line(0,0,l,0,1)
        line(0,0,0,l,1)
        # top right corner
        line(w, 0, w - l, 0, 1)
        line(w, 0, w, l, 1)
        # bottom right corner
        line(w, h, w - l, h, 1)
        line(w, h, w, h - l, 1)
        # bottom left corner
        line(0, h, l, h, 1)
        line(0, h, 0, h - l, 1)

    def h_bar_graph_frame(self, x=0, y=0):
        """Draw a horizontal bar graph frame.
        """
        # fetch methods and vars
        line = self.line
        w = self.width - 1

        # draw frame and labels
        line(x + 10, y + 24, w - 10, y + 24, 1)
        line(x + 10, y + 18, x + 10, y + 30, 1)
        line(w - 10, y + 18, w - 10, y + 30, 1)

        # draw major and minor divisions on x axis
        div_major_pos = x + 10
        while div_major_pos <= (w - 10):
            line(div_major_pos, y + 20, div_major_pos, y + 28, 1)
            div_major_pos += round((w - 10)/10)

        div_minor_pos = x + 10
        while div_minor_pos <= (w - 10):
            line(div_minor_pos, y + 22, div_minor_pos, y + 26, 1)
            div_minor_pos += round((w - 10)/20)

    def fw_char(self, c, font, x=0, y=0):
        pixel = self.pixel
        colors = (0xffff, 0xffff, 0, 0)

        # for c in string:
        if not c in font.keys():
            return 0

        row = y
        _w, * _font = font[c]
        r = range(x, x + _w)
        for byte in _font:
            unsalted = byte
            for col in r:
                color = colors[unsalted & 0x03]
                pixel(col, row, color)
                unsalted >>= 2
            row += 1
        x += _w

    def fw_text(self, s, font, x=0, y=0):
        p = self.pixel
        colors = (0xffff, 0xffff, 0, 0)

        for c in s:
            if not ord(c) in font.keys():
                c = "?"

            row = y
            _w, * _font = font[ord(c)]
            r = range(x, x + _w)
            for byte in _font:
                unsalted = byte
                for col in r:
                    color = colors[unsalted & 0x03]
                    p(col, row, color)
                    unsalted >>= 2
                row += 1
            x += _w


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


class Graph():
    def __init__(self, fb):
        self._fb = fb
        self._bar_buff = arr.array('H', [0] * 5) # store up to 5 uint16 numbers

    def bar(
            self,
            v: int,
            x: int,
            y: int,
            l: int,
            h: int,
            id: int = 0
            ):
        """
        Render a bar in the frambuffer.

        :param v: uint16 integer value.
        :param x: Starting X position (lower left).
        :param y: Starting Y position (lower left).
        :param l: Length of the total bar in pixels.
        :param h: Height of the bar in pixels.
        :param id: Bar ID number (default=0).
        """

        # compute bar width
        bv = int(((v * l) / 65535) + 0.5)

        # clear and draw bar
        self._fb.rect(x, y, l, h, 0, True)
        self._fb.rect(x, y, bv, h, 1, True)

        # logic for max bar

    def scale(
            self,
            x: int,
            y: int,
            l: int,
            w: int,
            p: str,
            o: str,
            ):
        """
        Render a scale frame in the frambuffer.

        :param x: Scale frame X origin.
        :param y: Scale frame y origin.
        :param l: Length of the frame in pixels.
        :param w: Width or height of the scale base.
        :param p: Position of the scale relative to the base.
            Valid options are: "t", "c", "b".
        :param o: Orientation of the scale. Valid options are:
            "h", "v".
        """
        if o == "h":
            self._h_scale(x, y, l, w, p)
        #elif o == "v":
        #    self._v_scale(x, y, l, w, p)
        else:
            self._fb.text(f"Invalid orientation: {o}", 0, 0)

    def _h_scale(
            self,
            x: int,
            y: int,
            l: int,
            w: int,
            p: str,
    ):
        # base line
        self._fb.vline(x, y, w, 1)

        # scale line
        if p == "t": # top
            self._fb.hline(x, y, l, 1)
            self._h_major_ticks(x, y, l, p)
            self._h_minor_ticks(x, y, l, p)
        elif p == "b": # bottom
            self._fb.hline(x, y + w, l, 1)
            self._h_major_ticks(x, y + w, l, p)
            self._h_minor_ticks(x, y + w, l, p)
        elif p == "c": # center
            c = int((w / 2) + 0.5)
            self._fb.hline(x, y + c, l, 1)
            self._h_major_ticks(x, y + c, l, p)
            self._h_minor_ticks(x, y + c, l, p)
        else:
            self._fb.text(f"Invalid position: {p}", 0, 0)

    def _h_major_ticks(self, x, y, l, p):
        # tick mark details
        div = l // 10
        ndivs = l // div
        th = 6 # tick height in pixels
        tn = 0 # tick number
        tp = x + div # tick position

        # draw tick marks
        if p == "t":
            while tn < ndivs:
                self._fb.vline(tp, y, th, 1)
                tp += div
                tn += 1
        if p == "b":
            while tn < ndivs:
                self._fb.vline(tp, y - th, th + 1, 1)
                tp += div
                tn += 1
        if p == "c":
            while tn < ndivs:
                self._fb.vline(tp, y - th, 2 * th, 1)
                tp += div
                tn += 1

    def _h_minor_ticks(self, x, y, l, p):
        # tick mark details
        div = (l // 10) // 2
        ndivs = l // div
        th = 3 # tick height in pixels
        tn = 0 # tick number
        tp = x + div # tick position

        # draw tick marks
        if p == "t":
            while tn < ndivs - 1:
                self._fb.vline(tp, y, th, 1)
                tp += div
                tn += 1
        if p == "b":
            while tn < ndivs - 1:
                self._fb.vline(tp, y - th, th + 1, 1)
                tp += div
                tn += 1
        if p == "c":
            while tn < ndivs - 1:
                self._fb.vline(tp, y - th, 2 * th, 1)
                tp += div
                tn += 1