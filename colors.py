#!/usr/bin/env python3

import numpy


def _asscaler(c):
    return c.item()


numpy.asscalar = _asscaler

import colormath.color_conversions
import colormath.color_diff
import colormath.color_objects
import png


class Color:
    """Immutable color with alpha channel."""

    def __init__(self, r, g, b, a=255):
        self._r = r
        self._g = g
        self._b = b
        self._a = a

    def __eq__(self, other):
        return self.bytes() == other.bytes()

    def __hash__(self):
        return hash(self.bytes())

    def __repr__(self):
        return "<c%02x%02x%02x%02x>" % (self._r, self._g, self._b, self._a)

    def bytes(self):
        return bytes([self._r, self._g, self._b, self._a])

    def bright(self):
        if self._r == 255 and self._g == 255 and self._b == 255:
            return Color(192, 192, 192)
        return Color((self._r + 255) // 2, (self._g + 255) // 2, (self._b + 255) // 2)

    def dim(self):
        if self._r == 0 and self._g == 0 and self._b == 0:
            return Color(64, 64, 64)
        return Color(self._r // 2, self._g // 2, self._b // 2)

    def faded(self):
        return Color(64 + self._r // 2, 64 + self._g // 2, 64 + self._b // 2, self._a)

    def distance_from(self, other, _cache={}):
        if (self, other) in _cache:
            return _cache[(self, other)]
        if (other, self) in _cache:
            return _cache[(other, self)]
        key = (self, other)
        """Returns the perceptual distance from self to othe."""
        c1 = colormath.color_objects.sRGBColor(
            self._r, self._g, self._b, is_upscaled=True
        )
        c2 = colormath.color_objects.sRGBColor(
            other._r, other._g, other._b, is_upscaled=True
        )
        c1 = colormath.color_conversions.convert_color(
            c1, colormath.color_objects.LabColor
        )
        c2 = colormath.color_conversions.convert_color(
            c2, colormath.color_objects.LabColor
        )
        result = colormath.color_diff.delta_e_cie2000(c1, c2)
        _cache[key] = result
        return result

    def highlight(self):
        a = self.bright()
        b = self.dim()
        if self.distance_from(a) > self.distance_from(b):
            return a
        return b


black = Color(0, 0, 0)
white = Color(255, 255, 255)


class Tile:
    """A tile is an immutable 9x9 graphic.  Can be drawn extended or faded."""

    def __init__(self, bg, fg=None, pattern=(), highlight=None, shadow=None):
        colors = [[bg] * 9 for _ in range(9)]
        if highlight is not None:
            for i in range(1, 9):
                colors[0][i] = highlight
                colors[i][8] = highlight
        if shadow is not None:
            for i in range(0, 8):
                colors[i][0] = shadow
                colors[8][i] = shadow
        if pattern and fg:
            off = (9 - len(pattern)) // 2
            for i, row in enumerate(pattern):
                for j, col in enumerate(row):
                    if col == "X":
                        colors[off + i][off + j] = fg
        self.colors = tuple(tuple(row) for row in colors)

    def draw(self, fade=False, halo=None):
        colors = self.colors
        if fade:
            colors = [[c.fade() for c in line] for line in colors]
        if halo is not None:
            colors = [list(x) for x in colors]
            for i in range(9):
                colors[i][0] = halo
                colors[i][8] = halo
                colors[0][i] = halo
                colors[8][i] = halo
        return [b"".join(c.bytes() for c in line) for line in colors]

       
blank_tile = Tile(black)


color_values = [
    ("000000", "X...X/.X.X./..X../.X.X./X...X"),  # Black
    ("3c3c3c", "...../XXXXX/.XXX./..X../....."),  # Dark Gray
    ("787878", "...../XXXXX/...../XXXXX/....."),  # Gray
    ("aaaaaa", ".XX.X/X.XX./...../.XX.X/X.XX."),  # $ Medium Gray
    ("d2d2d2", "...../..X../.X.X./X...X/....."),  # Light Gray
    ("ffffff", "...../...../..X../...../....."),  # White
    ("600018", "..X../...../XXXXX/...../..X.."),  # Deep Red
    ("a50e1e", "XXX../X.X../XXXXX/..X.X/..XXX"),  # $ Dark Red
    ("ed1c24", ".XXX./X...X/X...X/X...X/.XXX."),  # Red
    ("fa8072", "...../...X./..XX./.XXX./....."),  # $ Light Red
    ("e45c1a", "..X../.XXX./XXXXX/.XXX./..X.."),  # $ Dark Orange
    ("ff7f27", "..X../..X../XX.XX/..X../..X.."),  # Orange
    ("f6aa09", "...../.XXX./.X.X./.XXX./....."),  # Gold
    ("f9dd3b", "..X../..X../X.X.X/.XXX./..X.."),  # Yellow
    ("fffabc", "..X../.X.X./X...X/.X.X./..X.."),  # Light Yellow
    ("9c8431", ".XXX./X...X/.XXX./X...X/.XXX."),  # $ Dark Goldenrod
    ("c5ad31", "..X../.X.X./.X.X./.X.X./..X.."),  # $ Goldenrod
    ("e8d45f", "...XX/...XX/...../XX.../XX..."),  # $ Light Goldenrod
    ("4a6b3a", "...../.XXX./.XX../.X.../....."),  # $ Dark Olive
    ("5a944a", "X...X/.X.X./..X../..X../..X.."),  # $ Olive
    ("84c573", "XXXXX/X...X/X...X/X...X/XXXXX"),  # $ Light Olive
    ("0eb968", "..X../.XXX./X.X.X/..X../..X.."),  # Dark Green
    ("13e67b", ".X.../.XX../.XXX./.XX../.X..."),  # Green
    ("87ff5e", "...../X...X/.X.X./..X../....."),  # Light Green
    ("0c816e", "....X/...X./..X../.X.../X...."),  # Dark Teal
    ("10aea6", "..X../..X../XXXXX/..X../..X.."),  # Teal
    ("13e1be", "X...X/...X./..X../.X.../X...X"),  # Light Teal
    ("0f799f", "...../.XXX./..XX./...X./....."),  # $ Dark Cyan
    ("60f7f2", "...X./..X../.X.../..X../...X."),  # Cyan
    ("bbfaf2", "X...X/XX.XX/XXXXX/XX.XX/X...X"),  # $ Light Cyan
    ("28509e", "..X../...X./XXXXX/...X./..X.."),  # Dark Blue
    ("4093e4", "...../..X../.XXX./XXXXX/....."),  # Blue
    ("7dc7ff", "X...X/...../...../...../X...X"),  # $ Light Blue
    ("4d31b8", "....X/...X./..X../.X.X./X...X"),  # $ Dark Indigo
    ("6b50f6", "X..../.X.../..X../...X./....X"),  # Indigo
    ("99b1fb", "..X../..X../..X../..X../..X.."),  # Light Indigo
    ("4a4284", "...../..X../...../..X../....."),  # $ Dark Slate Blue
    ("7a71c4", ".X.X./X.X.X/X...X/.X.X./..X.."),  # $ Slate Blue
    ("b5aef1", ".XXX./X..XX/X.X.X/XX..X/.XXX."),  # $ Light Slate Blue
    ("780c99", "..X../..X../..X../...../..X.."),  # Dark Purple
    ("aa38b9", "...X./..XX./.XXX./..XX./...X."),  # Purple
    ("e09ff9", "...../.XXX./X...X/.XXX./....."),  # Light Purple
    ("cb007a", "...../...../XXXXX/...../....."),  # Dark Pink
    ("ec1f80", ".X.X./.X.X./.X.X./.X.X./.X.X."),  # Pink
    ("f38da9", "...../..X../.XXX./..X../....."),  # Light Pink
    ("9b5249", ".XXX./XX..X/X.X.X/X..XX/.XXX."),  # $ Dark Peach
    ("d18078", ".X.X./XXXXX/XXXXX/.XXX./..X.."),  # $ Peach
    ("fab6a4", ".X.X./.X.X./.X.X./...../.X.X."),  # $ Light Peach
    ("684634", "XX.../XX.../...../...XX/...XX"),  # Dark Brown
    ("95682a", ".XXX./X...X/X.X.X/X...X/.XXX."),  # Brown
    ("dba463", "...../...../.X.X./...../....."),  # $ Light Brown
    ("7b6352", "...../.X.../.XX../.XXX./....."),  # $ Dark Tan
    ("9c846b", ".XXX./X...X/..XX./...../..X.."),  # $ Tan
    ("d6b594", "...../XXXXX/.X.X./.X.X./....."),  # $ Light Tan
    ("d18051", "...../..X../.X.X./..X../....."),  # $ Dark Beige
    ("f8b277", "..XXX/..X.X/XXXXX/X.X../XXX.."),  # Beige
    ("ffc5a5", "XXXXX/X...X/X.X.X/X...X/XXXXX"),  # $ Light Beige
    ("6d643f", "XXXXX/.X.X./..X../.X.X./XXXXX"),  # $ Dark Stone
    ("948c6b", "..X../.X.../XXXXX/.X.../..X.."),  # $ Stone
    ("cdc59e", ".X.../..X../...X./..X../.X..."),  # $ Light Stone
    ("333941", "XXXXX/.X.../..X../.X.../XXXXX"),  # $ Dark Slate
    ("6d758d", "XXXXX/.XXX./..X../.XXX./XXXXX"),  # $ Slate
    ("b3b9d1", "X...X/...../..X../...../X...X"),  # $ Light Slate
]

# from the IBM PC BIOS font...
font = {
    "0": [
        ".XXXXX.",
        "XX...XX",
        "XX..XXX",
        "XX.XXXX",
        "XXXX.XX",
        "XXX..XX",
        ".XXXXX.",
    ],
    "1": [
        "..XX...",
        ".XXX...",
        "..XX...",
        "..XX...",
        "..XX...",
        "..XX...",
        "XXXXXX.",
    ],
    "2": [
        ".XXXX..",
        "XX..XX.",
        "....XX.",
        "..XXX..",
        ".XX....",
        "XX..XX.",
        "XXXXXX.",
    ],
    "3": [
        ".XXXX..",
        "XX..XX.",
        "....XX.",
        "..XXX..",
        "....XX.",
        "XX..XX.",
        ".XXXX..",
    ],
    "4": [
        "...XXX.",
        "..XXXX.",
        ".XX.XX.",
        "XX..XX.",
        "XXXXXXX",
        "....XX.",
        "...XXXX",
    ],
    "5": [
        "XXXXXX.",
        "XX.....",
        "XXXXX..",
        "....XX.",
        "....XX.",
        "XX..XX.",
        ".XXXX..",
    ],
    "6": [
        "..XXX..",
        ".XX....",
        "XX.....",
        "XXXXX..",
        "XX..XX.",
        "XX..XX.",
        ".XXXX..",
    ],
    "7": [
        "XXXXXX.",
        "XX..XX.",
        "....XX.",
        "...XX..",
        "..XX...",
        "..XX...",
        "..XX...",
    ],
    "8": [
        ".XXXX..",
        "XX..XX.",
        "XX..XX.",
        ".XXXX..",
        "XX..XX.",
        "XX..XX.",
        ".XXXX..",
    ],
    "9": [
        ".XXXX..",
        "XX..XX.",
        "XX..XX.",
        ".XXXXX.",
        "....XX.",
        "...XX..",
        ".XXX...",
    ],
    " ": [
        ".......",
        ".......",
        ".......",
        ".......",
        ".......",
        ".......",
        ".......",
    ],
    "-": [
        ".......",
        ".......",
        ".......",
        "XXXXXX.",
        ".......",
        ".......",
        ".......",
    ],
}


def rotate_right(pattern):
    s = len(pattern)
    ans = []
    for i in range(s):
        line = []
        for j in range(s):
            line.append(pattern[s - j - 1][i])
        ans.append("".join(line))
    return ans


def _make_transparent():
    trans = Color(0, 0, 0, 0)
    black = Color(0, 0, 0)
    white = Color(255, 255, 255)
    lines = [[trans] * 9 for _ in range(9)]
    for i in range(1, 8):
        color = white if i % 2 == 0 else black
        lines[i][1] = color
        lines[i][7] = color
        lines[1][i] = color
        lines[7][i] = color
    return Tile(
        bg=Color(128, 128, 128),
        fg=white,
        pattern=["X.X.X", ".....", "X...X", ".....", "X.X.X"],
        highlight=black,
        shadow=white,
    )


class ColorMap:
    def __init__(self, values, transparent):
        self.color_map = {}
        self.colors = []
        for htmlcolor, pattern in values:
            color = Color(
                int(htmlcolor[0:2], 16),
                int(htmlcolor[2:4], 16),
                int(htmlcolor[4:6], 16),
            )
            tile = Tile(
                bg=color,
                fg=color.highlight(),
                pattern=pattern.split("/"),
                highlight=color.bright(),
                shadow=color.dim(),
            )
            self.colors.append(color)
            self.color_map[color] = tile
        self.transparent = transparent

    def __getitem__(self, color):
        if color._a == 0:
            return self.transparent
        return self.color_map[color]

    def get_closest_color(self, color):
        if color._a == 0:
            return Color(0, 0, 0, 0)
        if color in self.color_map:
            return color
        return min(self.color_map.keys(), key=lambda c: c.distance_from(color))


color_tile_map = ColorMap(color_values, _make_transparent())

h_font_map = {}
for ch, pattern in font.items():
    h_font_map[ch] = Tile(fg=white, bg=black, pattern=pattern)

v_font_map = {}
for ch, pattern in font.items():
    v_font_map[ch] = Tile(fg=white, bg=black, pattern=rotate_right(pattern))


class Screen:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = [[blank_tile for _ in range(width)] for _ in range(height)]
        self.dim = [[False for _ in range(width)] for _ in range(height)]
        self._halo = [[None for _ in range(width)] for _ in range(height)]

    def plot(self, row, col, tile):
        self.tiles[row][col] = tile
        
    def halo(self, row, col, color):
        self._halo[row][col] = color

    def draw(self, hexts=[], vexts=[]):
        assert all(0 < x < self.width for x in hexts)
        assert all(0 < y < self.height for y in vexts)
        ans = []
        for line, haloline in zip(self.tiles, self._halo):
            nextlines = [[] for _ in range(9)]
            for tile, halo in zip(line, haloline):
                for nextline, drawn in zip(nextlines, tile.draw(halo=halo)):
                    nextline.extend(drawn)
            ans.extend(bytes(x) for x in nextlines)
        hexts = sorted((x * 9 for x in hexts), reverse=True)
        vexts = sorted((y * 9 for y in vexts), reverse=True)
        # horizontal first
        for i in range(len(ans)):
            line = ans[i]
            for hext in hexts:
                left, right = line[: hext * 4], line[hext * 4 :]
                line = left + left[-4:] + right[:4] + right
            ans[i] = line
        # then vertical
        for vext in vexts:
            top, bottom = ans[:vext], ans[vext:]
            ans = top + top[-1:] + bottom[:1] + bottom
        return ans

    def write_png(self, f, hexts=[], vexts=[]):
        png.Writer(
            width=self.width * 9 + 2 * len(hexts),
            height=self.height * 9 + 2 * len(vexts),
            greyscale=False,
            bitdepth=8,
            alpha=True,
        ).write(f, self.draw(hexts=hexts, vexts=vexts))


def alpha_line_to_colors(line, fix=True):
    ll = len(line)
    ans = []
    for i in range(0, ll, 4):
        c = Color(line[i], line[i + 1], line[i + 2], line[i + 3])
        if fix:
            c = color_tile_map.get_closest_color(c)
        ans.append(c)
    return ans


def h_draw(screen, row, col, s):
    for i, c in enumerate(s):
        screen.plot(row, col + i, h_font_map.get(c, blank_tile))


def v_draw(screen, row, col, s):
    for i, c in enumerate(s):
        screen.plot(row + i, col, v_font_map.get(c, blank_tile))


def MakeSubset(
    png_in=None,
    png_out=None,
    diffbase_in=None,
    x_start=0,
    x_len=None,
    y_start=0,
    y_len=None,
    x_woff=0,
    y_woff=0,
    xstride=8,
    ystride=8,
    xstride_off=0,
    ystride_off=0,
):
    """The main drawing method.  (Despite the "subset" name, it can draw a full grid.)
    
    Required arguments:
      png_in: The path to the PNG to convert.
        The input PNG should be in wplace colors if possible; a nearest match will be
        used otherwise.
      png_out: The path that the generated grid will be written to.
      
    Optional arguments:
      x_start, x_len
      y_start, y_len
        By default, the whole image will be output to a grid.  But you can emit
        a subset of the image instead, by giving the coordinate of the upper-
        left corner, and the length to use in each direction.  (These take coordinates
        of the input image; 0,0 is the upper-left corner.)
        
      x_woff, y_woff:
        wplace coordinate offsets.  Set these to the coordinate of the pixel in wplace
        where you want the upper left of your drawing to live.  This currently doesn't
        support region-spans (wrapping around at 4000).
        
      x_stride, y_stride:
        How many pixels wide and tall the larger grid divisions should be.  8x8 is good
        for video game images, 5x5 for more freeform art.  4x6 is good for PICO-8 text.
        
      x_strideoff, y_strideoff:
        Set these if the grid division shouldn't be flush with the grid.  (For instance,
        an x_strideoff of 2 means you want the first column of larger divisions to be
        only two pixels wide.)
        
      diffbase_in:
        If provided, this must be a PNG of the same dimensions as png_in.  Colors that
        have changed between png_in and diffbase_in are drawn highlighted in the
        generated output.
    """
    
    with open(png_out, "wb") as f:
        p_width, p_height, p_pixels, _ = png.Reader(filename=png_in).asRGBA8()
        if x_len is None:
            x_len = p_width - x_start
        if y_len is None:
            y_len = p_height - y_start
        assert x_start + x_len <= p_width
        assert y_start + y_len <= p_height
        color_pixels = [alpha_line_to_colors(x) for x in p_pixels][
            y_start : y_start + y_len
        ]
        color_pixels = [row[x_start : x_start + x_len] for row in color_pixels]

        diff = [[False for _ in range(x_len)] for _ in range(y_len)]
        if diffbase_in is not None:
            d_width, d_height, d_pixels, _ = png.Reader(filename=diffbase_in).asRGBA8()
            assert d_width == p_width
            assert d_height == p_height
            diff_pixels = [alpha_line_to_colors(x) for x in d_pixels][
                y_start : y_start + y_len
            ]
            diff_pixels = [row[x_start : x_start + x_len] for row in diff_pixels]
            for x in range(x_len):
                for y in range(y_len):
                    if color_pixels[y][x] != diff_pixels[y][x]:
                        diff[y][x] = True

        # add room for the coordinate values
        screen = Screen(x_len + 8, y_len + 8)
        
        red = Color(255, 0, 0)
        for col in range(x_len):
            for row in range(y_len):
                screen.plot(row + 4, col + 4, color_tile_map[color_pixels[row][col]])
                if diff[row][col]:
                    screen.halo(row + 4, col + 4, red)

        # Draw every multiple of 5 coordinate
        for i in range(y_len):
            wplace_y = y_woff + y_start + i
            if wplace_y % 5 == 0 or i == 0 or i == y_len - 1:
                h_draw(screen, i + 4, 0, str(wplace_y).rjust(4))
                h_draw(screen, i + 4, x_len + 4, str(wplace_y).ljust(4))
        for i in range(x_len):
            wplace_x = x_woff + x_start + i
            if wplace_x % 5 == 0 or i == 0 or i == x_len - 1:
                v_draw(screen, 0, i + 4, str(wplace_x).rjust(4))
                v_draw(screen, y_len + 4, i + 4, str(wplace_x).ljust(4))

        # just brute force where the tile separation goes.  It's 1:40 and I want
        # to go to sleep
        hexts = [4, 4 + x_len]
        vexts = [4, 4 + y_len]
        for x in range(1, x_len - 1):
            if (x + x_start - xstride_off) % xstride == 0:
                hexts.append(x + 4)
        for y in range(1, y_len - 1):
            if (y + y_start - ystride_off) % ystride == 0:
                vexts.append(y + 4)

        screen.write_png(f, hexts=hexts, vexts=vexts)


# temporary ad-hoc for mapping snes to our wplace drawing
snes = {
    Color(0x40, 0x88, 0x20): Color(0x0C, 0x81, 0x6E),
    Color(0x40, 0xD0, 0x20): Color(0x13, 0xE6, 0x7B),
    Color(0x90, 0x80, 0x60): Color(0x6D, 0x64, 0x3F),
}


def Map(c):
    if c in snes:
        return snes[c]
    return color_tile_map.get_closest_color(c)


def Nearest(f_in, f_out):
    width, height, pixels, metadata = png.Reader(filename=f_in).asRGBA8()
    color_pixels = [alpha_line_to_colors(x, fix=False) for x in pixels]
    color_pixels = [[Map(c) for c in row] for row in color_pixels]
    data = [b"".join(c.bytes() for c in row) for row in color_pixels]
    with open(f_out, "wb") as f:
        png.Writer(
            width=width, height=height, greyscale=False, bitdepth=8, alpha=True
        ).write(f, data)


sections = [
    ('nw', 0, 0), ('n', 1, 0), ('ne', 2, 0),
    ('w', 0, 1), ('c', 1, 1), ('e', 2, 1),
    ('sw', 0, 2), ('s', 1, 2), ('se', 2, 2),
]

# In [22]: for name, dx, dy in colors.sections:
#     ...:     fn = '/mnt/c/Zelda/smwplace_1.1_%s.png' % (name,)
#     ...:     x_start = dx * 160
#     ...:     y_start = dy * 156
#     ...:     with open(fn, 'wb') as f: colors.MakeSubset(f, '/mnt/c/Zelda/SMWplace.1.1.png', x_start, 200, y_start, 200, 3480, 2878)
#     ...:
