#!/usr/bin/env python3

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

    def distance_from(self, other):
        """Returns the distance from self to other, squared."""
        return (
            (self._r - other._r) ** 2
            + (self._g - other._g) ** 2
            + (self._b - other._b) ** 2
        )

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

    def draw(self, fade=False):
        if fade:
            return [b"".join(c.fade().bytes() for c in line) for line in self.colors]
        return [b"".join(c.bytes() for c in line) for line in self.colors]


blank_tile = Tile(black)


color_values = [
    ("000000", "X...X/.X.X./..X../.X.X./X...X"),  # Black
    ("3c3c3c", "...../XXXXX/.XXX./..X../....."),  # Dark Gray
    ("787878", "...../XXXXX/...../XXXXX/....."),  # Gray
    ("d2d2d2", "...../..X../.X.X./X...X/....."),  # Light Gray
    ("ffffff", "...../...../..X../...../....."),  # White
    ("600018", "..X../...../XXXXX/...../..X.."),  # Deep Red
    ("ed1c24", ".XXX./X...X/X...X/X...X/.XXX."),  # Red
    ("ff7f27", "..X../..X../XX.XX/..X../..X.."),  # Orange
    ("f6aa09", "...../.XXX./.X.X./.XXX./....."),  # Gold
    ("f9dd3b", "..X../..X../X.X.X/.XXX./..X.."),  # Yellow
    ("fffabc", "..X../.X.X./X...X/.X.X./..X.."),  # Light Yellow
    ("0eb968", "..X../.XXX./X.X.X/..X../..X.."),  # Dark Green
    ("13e67b", ".X.../.XX../.XXX./.XX../.X..."),  # Green
    ("87ff5e", "...../X...X/.X.X./..X../....."),  # Light Green
    ("0c816e", "....X/...X./..X../.X.../X...."),  # Dark Teal
    ("10aea6", "..X../..X../XXXXX/..X../..X.."),  # Teal
    ("13e1be", "X...X/...X./..X../.X.../X...X"),  # Light Teal
    ("28509e", "..X../...X./XXXXX/...X./..X.."),  # Dark Blue
    ("4093e4", "...../..X../.XXX./XXXXX/....."),  # Blue
    ("60f7f2", "...X./..X../.X.../..X../...X."),  # Cyan
    ("6b50f6", "X..../.X.../..X../...X./....X"),  # Indigo
    ("99b1fb", "..X../..X../..X../..X../..X.."),  # Light Indigo
    ("780c99", "..X../..X../..X../...../..X.."),  # Dark Purple
    ("aa38b9", "...X./..XX./.XXX./..XX./...X."),  # Purple
    ("e09ff9", "...../.XXX./X...X/.XXX./....."),  # Light Purple
    ("cb007a", "...../...../XXXXX/...../....."),  # Dark Pink
    ("ec1f80", ".X.X./.X.X./.X.X./.X.X./.X.X."),  # Pink
    ("f38da9", "...../..X../.XXX./..X../....."),  # Light Pink
    ("684634", "XX.../XX.../...../...XX/...XX"),  # Dark Brown
    ("95682a", ".XXX./X...X/X.X.X/X...X/.XXX."),  # Brown
    ("f8b277", "..XXX/..X.X/XXXXX/X.X../XXX.."),  # Beige
    # PAY COLORS
    ("948c6b", "..X../.X.../XXXXX/.X.../..X.."),  # Stone
    ("cdc59e", ".X.../..X../...X./..X../.X..."),  # Light Stone
    ("6d643f", "XXXXX/.X.X./..X../.X.X./XXXXX"),  # Dark Stone
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
    return Tile(bg=Color(128,128,128), fg=white, pattern=['X.X.X','.....','X...X','.....','X.X.X'],
                highlight=white, shadow=black)


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

    def plot(self, row, col, tile):
        self.tiles[row][col] = tile

    def draw(self, hexts=[], vexts=[]):
        assert all(0 < x < self.width for x in hexts)
        assert all(0 < y < self.height for y in vexts)
        ans = []
        for line in self.tiles:
            nextlines = [[] for _ in range(9)]
            for tile in line:
                for nextline, drawn in zip(nextlines, tile.draw()):
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
    f,
    png_in,
    x_start,
    x_len,
    y_start,
    y_len,
    x_woff,
    y_woff,
    xstride=8,
    ystride=8,
    xstride_off=0,
    ystride_off=0,
):
    p_width, p_height, p_pixels, p_metadata = png.Reader(filename=png_in).asRGBA8()
    assert x_start + x_len <= p_width
    assert y_start + y_len <= p_height
    color_pixels = [alpha_line_to_colors(x) for x in p_pixels][
        y_start : y_start + y_len
    ]
    color_pixels = [row[x_start : x_start + x_len] for row in color_pixels]

    # add room for the coordinate values
    screen = Screen(x_len + 8, y_len + 8)
    for col in range(x_len):
        for row in range(y_len):
            screen.plot(row + 4, col + 4, color_tile_map[color_pixels[row][col]])

    # Draw every multiple of 5 coordinate
    for i in range(y_len):
        wplace_y = y_woff + y_start + i
        if wplace_y % 5 == 0 or i == 0 or i == y_len - 1:
            h_draw(screen, i + 4, 0, str(wplace_y).rjust(3))
            h_draw(screen, i + 4, x_len + 4, str(wplace_y).ljust(3))
    for i in range(x_len):
        wplace_x = x_woff + x_start + i
        if wplace_x % 5 == 0 or i == 0 or i == x_len - 1:
            v_draw(screen, 0, i + 4, str(wplace_x).rjust(3))
            v_draw(screen, y_len + 4, i + 4, str(wplace_x).ljust(3))

    # just brute force where the tile separation goes.  It's 1:40 and I want
    # to go to sleep
    hexts = [4, 4 + x_len]
    vexts = [4, 4 + y_len]
    for x in range(1, x_len - 1):
        if (x + x_start + xstride_off) % xstride == 0:
            hexts.append(x + 4)
    for y in range(1, y_len - 1):
        if (y + y_start + ystride_off) % ystride == 0:
            vexts.append(y + 4)

    screen.write_png(f, hexts=hexts, vexts=vexts)


# temporary ad-hoc for mapping snes to our wplace drawing
snes = {
    Color(0x40, 0x88, 0x20): Color(0x0C, 0x81, 0x6E),
    Color(0x40, 0xD0, 0x20): Color(0x13, 0xE6, 0x7B),
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


# In [22]: for name, dx, dy in quads:
#     ...:     fn = '/mnt/c/Zelda/smwplace_%s.png' % (name,)
#     ...:     x_start = dx * 160
#     ...:     y_start = dy * 156
#     ...:     with open(fn, 'wb') as f: colors.MakeSubset(f, '/mnt/c/Zelda/SMWplace.1.0.png', x_start, 200, y_start, 200, 3480, 2878)
#     ...:
