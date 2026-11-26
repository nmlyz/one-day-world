#!/usr/bin/env python3
"""one-day-world: draw a newspaper front page summing up the world news
of Thursday 26 November 2026 as one 1024x1024 PNG.

Eight stories: two more tankers hit mines in the Strait of Hormuz lead the
page, then U.S. tariff proposals on 14 economies, Ukrainian strikes on two
Russian refineries, a Gaza strike killing a Hamas security chief, the
Cartagena hostage rescue, Pakistan's first astronaut aboard Shenzhou-24, a
storm hitting Thanksgiving travel, and a deadly fuel-truck blaze in Egypt.
Everything is drawn with code: a hand-made 5x7 bitmap font, flat ink shapes
and eight spot illustrations, one per story. No network, no files are read,
no randomness, no clock: every run writes the same bytes.

Run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
Writes entry.png into the output directory (default /output).
"""

import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (246, 241, 227)
INK = (26, 26, 26)
RED = (179, 38, 30)
SEA = (22, 50, 74)
SEA2 = (38, 84, 112)
GOLD = (200, 155, 60)
GREEN = (46, 125, 50)
GREY = (120, 116, 108)
LIGHT = (226, 219, 200)
ORANGE = (232, 110, 30)
YELLOW = (245, 190, 60)
WHITE = (255, 255, 255)
SKY = (168, 196, 214)
DARK = (30, 34, 40)


def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, pixels):
    """pixels: bytes of W*H*3 RGB rows, top to bottom."""
    raw = b"".join(b"\x00" + pixels[y * W * 3:(y + 1) * W * 3] for y in range(H))
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
           + _chunk(b"IDAT", zlib.compress(raw, 9)) + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    try:
        os.chmod(path, 0o644)
    except OSError:
        pass


class Canvas:
    def __init__(self):
        self.px = bytearray(PAPER) * (W * H)

    def set(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(W, x + w), min(H, y + h)
        for yy in range(y0, y1):
            i = (yy * W + x0) * 3
            self.px[i:i + (x1 - x0) * 3] = bytes(c) * (x1 - x0)

    def frame(self, x, y, w, h, c, t=1):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.rect(x0 - t // 2, y0 - t // 2, t, t, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d <= r * r:
                        self.set(xx, yy, c)
                elif abs(d - r * r) <= r:
                    self.set(xx, yy, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for yy in range(cy - ry, cy + ry + 1):
            for xx in range(cx - rx, cx + rx + 1):
                if ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1.0:
                    self.set(xx, yy, c)

    def poly(self, pts, c):
        """Scanline fill of a polygon given as [(x, y), ...]."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(H, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(int(xs[i]), y, max(1, int(xs[i + 1]) - int(xs[i])), 1, c)

    def text(self, s, x, y, scale=1, c=INK):
        s = s.upper()
        cx = x
        for ch in s:
            g = FONT.get(ch)
            if g is None:
                cx += 6 * scale
                continue
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits >> (4 - col) & 1:
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx - x

    def text_w(self, s, scale=1):
        return len(s) * 6 * scale - scale

    def center(self, s, cx, y, scale=1, c=INK):
        self.text(s, cx - self.text_w(s, scale) // 2, y, scale, c)


# 5x7 bitmap font. Each glyph is 7 rows of 5 bits, top to bottom.
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ",": (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    ":": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ";": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    "-": (0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00),
    "+": (0x00, 0x04, 0x04, 0x0E, 0x04, 0x04, 0x00),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "%": (0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "/": (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x06, 0x04, 0x00, 0x04),
    "=": (0x00, 0x00, 0x0E, 0x00, 0x0E, 0x00, 0x00),
    "|": (0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
}


# ---------------------------------------------------------------------------
# Spot illustrations. Each draws inside (x, y, w, h). Nothing may draw
# outside its own box: panel gaps are scanned for stray pixels.
# ---------------------------------------------------------------------------

def _tanker(c, x, y, w, flame=True):
    """A small oil tanker: dark hull, red waterline, deckhouse, flames."""
    h = w // 4
    c.rect(x, y + h // 2, w, h // 2, (40, 40, 44))
    c.rect(x, y + h * 3 // 4, w, h // 4, (150, 40, 30))
    c.rect(x + w * 3 // 5, y, w // 5, h // 2, (230, 225, 210))
    c.rect(x + w // 8, y + h // 2 - 4, 4, 4, GOLD)
    if flame:
        c.poly([(x + w // 4, y), (x + w // 4 + 12, y - 26),
                (x + w // 4 + 24, y)], ORANGE)
        c.poly([(x + w // 2, y - 6), (x + w // 2 + 10, y - 30),
                (x + w // 2 + 20, y - 6)], YELLOW)
        c.poly([(x + w * 3 // 4, y), (x + w * 3 // 4 + 9, y - 20),
                (x + w * 3 // 4 + 18, y)], ORANGE)


def _mine(c, cx, cy, r=7):
    c.circle(cx, cy, r, INK)
    for dx, dy in ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0),
                   (-1, 1), (0, 1), (1, 1)):
        c.line(cx + dx * r, cy + dy * r, cx + dx * (r + 5),
               cy + dy * (r + 5), INK, 2)


def draw_hormuz(c, x, y, w, h):
    """Lead picture: the Strait of Hormuz, two burning tankers, mines."""
    c.rect(x, y, w, h, SEA)
    # Land on both sides of the strait channel.
    c.poly([(x, y), (x + w * 3 // 5, y), (x + w // 2, y + h // 3),
            (x, y + h // 2)], (214, 196, 150))
    c.poly([(x + w - 1, y + h), (x + w * 2 // 5, y + h),
            (x + w // 2, y + h * 2 // 3), (x + w - 1, y + h // 2)],
           (198, 178, 132))
    # Dashed shipping lane through the channel.
    for i in range(0, w, 26):
        c.line(x + i, y + h * 2 // 3 - i // 3, x + i + 14,
               y + h * 2 // 3 - (i + 14) // 3, (150, 190, 210), 2)
    _mine(c, x + w // 4, y + h * 3 // 5)
    _mine(c, x + w * 3 // 5, y + h // 2)
    _tanker(c, x + w // 8, y + h // 2, w // 3)
    _tanker(c, x + w // 2, y + h // 2, w // 4)
    _tanker(c, x + w * 3 // 4 - 20, y + h // 3, w // 5, flame=False)
    # Smoke columns over the burning ships.
    c.circle(x + w // 4, y + h // 2 - 34, 12, (90, 90, 92))
    c.circle(x + w // 4 + 16, y + h // 2 - 48, 9, (110, 110, 112))
    c.circle(x + w * 5 // 8, y + h // 2 - 36, 10, (90, 90, 92))
    # Big callout: the count that matters, top right over the dark sea.
    c.text("2", x + w - 132, y + 8, 4, WHITE)
    c.text("TANKERS", x + w - 102, y + 22, 2, WHITE)


def med_tariffs(c, x, y, w, h):
    """USTR tariffs: a falling bar chart and the two headline rates."""
    c.rect(x, y, w, h, WHITE)
    c.frame(x, y, w, h, INK)
    base = y + h - 10
    heights = [52, 44, 34, 24, 14]
    for i, hh in enumerate(heights):
        bx = x + 16 + i * 24
        c.rect(bx, base - hh, 15, hh, RED)
    c.line(x + 14, base - 56, x + 128, base - 16, INK, 3)
    c.poly([(x + 128, base - 16), (x + 114, base - 20),
            (x + 120, base - 6)], INK)
    c.text("20%", x + w - 118, y + 6, 3, RED)
    c.text("35%", x + w - 118, y + 44, 3, INK)
    c.text("SINGAPORE", x + w - 116, y + 30, 1, INK)
    c.text("VIETNAM", x + w - 116, y + 68, 1, INK)


def med_refinery(c, x, y, w, h):
    """Ukraine's refinery strikes: towers burning, a drone, 800 KM."""
    c.rect(x, y, w, h, DARK)
    base = y + h
    for i, tx in enumerate((x + 14, x + 78, x + 142, x + 206)):
        tw = 34
        th = 22 + (i % 2) * 8
        c.rect(tx, base - th, tw, th, (90, 96, 104))
        c.rect(tx + 6, base - th - 8, 6, 8, (90, 96, 104))
        c.rect(tx + 22, base - th - 8, 6, 8, (90, 96, 104))
        if i in (0, 2):
            c.poly([(tx + 8, base - th - 8), (tx + 14, base - th - 24),
                    (tx + 20, base - th - 8)], ORANGE)
            c.poly([(tx + 20, base - th - 8), (tx + 25, base - th - 18),
                    (tx + 30, base - th - 8)], YELLOW)
    # Drone silhouette, top right.
    dx, dy = x + w - 44, y + 12
    c.poly([(dx, dy - 4), (dx + 10, dy), (dx, dy + 4), (dx - 10, dy)], WHITE)
    c.line(dx - 14, dy, dx + 14, dy, WHITE, 2)
    c.text("800 KM", x + 12, y + 8, 2, YELLOW)
    c.text("5 JETS", x + w - 78, y + h - 22, 2, YELLOW)


def med_gaza(c, x, y, w, h):
    """Gaza: a dark city skyline, rain, tents in front."""
    c.rect(x, y, w, h, (58, 66, 78))
    c.ellipse(x + 34, y + 6, 26, 8, (140, 146, 152))
    c.ellipse(x + w - 40, y + 8, 22, 7, (140, 146, 152))
    for i in range(10):
        c.line(x + 14 + i * 30, y + 16, x + 11 + i * 30, y + 24, SKY, 2)
    base = y + h
    for i, fr in enumerate([0.45, 0.70, 0.55, 0.85, 0.60, 0.42]):
        hh = int(fr * (h - 12))
        bw = w // 6
        c.rect(x + i * bw + 2, base - hh - 12, bw - 4, hh, (20, 22, 28))
    for i, tx in enumerate((x + 20, x + w // 2 - 12, x + w - 66)):
        c.poly([(tx, base - 2), (tx + 20, base - 16), (tx + 40, base - 2)],
               (228, 226, 216) if i != 1 else (150, 180, 210))


def strip_cartagena(c, x, y, w, h):
    """Cartagena: a supermarket front, troops moving in at dawn."""
    c.rect(x, y, w, h, (232, 224, 204))
    base = y + h
    # Supermarket: wide low block, sign band, glass front.
    c.rect(x + 8, y + 18, w - 16, h - 36, (240, 236, 224))
    c.rect(x + 8, y + 18, w - 16, 16, RED)
    c.text("SUPERMARKET", x + 14, y + 24, 1, WHITE)
    for i in range(5):
        gx = x + 16 + i * 40
        c.rect(gx, y + 44, 30, h - 62, (168, 196, 214))
    # Three troop silhouettes advancing, rifles raised.
    for i, tx in enumerate((x + 24, x + 96, x + 168)):
        ty = base - 12
        c.circle(tx, ty - 22, 5, INK)
        c.rect(tx - 4, ty - 17, 8, 17, INK)
        c.line(tx + 4, ty - 12, tx + 16, ty - 20, INK, 3)
        c.line(tx - 4, ty, tx - 10, ty - 8, INK, 3)
        c.line(tx + 4, ty, tx + 10, ty - 8, INK, 3)
    c.text("16 HOURS", x + w - 100, y + h - 18, 2, RED)


def strip_shenzhou(c, x, y, w, h):
    """Shenzhou-24: a rocket climbing past a space station, two flags."""
    c.rect(x, y, w, h, (24, 28, 44))
    # Stars.
    for sx, sy in ((18, 10), (60, 26), (110, 8), (170, 20), (210, 12),
                   (40, 48), (150, 44), (200, 52)):
        c.set(x + sx, y + sy, WHITE)
        c.set(x + sx + 1, y + sy, WHITE)
    # Rocket, nose up, left.
    rx = x + 30
    c.rect(rx, y + 30, 20, 38, (230, 230, 228))
    c.poly([(rx, y + 30), (rx + 10, y + 16), (rx + 20, y + 30)], RED)
    c.poly([(rx - 8, y + 68), (rx, y + 52), (rx, y + 68)], RED)
    c.poly([(rx + 20, y + 68), (rx + 20, y + 52), (rx + 28, y + 68)], RED)
    c.poly([(rx + 6, y + 68), (rx + 10, y + h - 4), (rx + 14, y + 68)],
           ORANGE)
    c.circle(rx + 10, y + 44, 4, SEA2)
    # Space station, right.
    sx, sy = x + w - 110, y + 24
    c.rect(sx, sy, 86, 10, (200, 200, 196))
    c.rect(sx + 30, sy - 8, 26, 26, (160, 164, 168))
    c.rect(sx + 8, sy + 4, 70, 3, GOLD)
    # Two flags at the bottom: Pakistan, then China.
    fx = x + w - 96
    c.rect(fx, y + h - 26, 40, 20, (20, 90, 60))
    c.rect(fx, y + h - 26, 10, 20, WHITE)
    c.circle(fx + 26, y + h - 16, 5, WHITE, fill=False)
    c.rect(fx + 48, y + h - 26, 40, 20, (200, 40, 30))
    c.circle(fx + 58, y + h - 19, 3, YELLOW)
    c.text("08:18", x + 10, y + 6, 2, YELLOW)


def strip_storm(c, x, y, w, h):
    """Thanksgiving storm: a rain cloud over a parade balloon."""
    c.rect(x, y, w, h, SKY)
    # Dark rain cloud.
    c.ellipse(x + w // 2, y + 14, 62, 14, (70, 80, 92))
    c.ellipse(x + w // 2 - 34, y + 20, 34, 10, (70, 80, 92))
    c.ellipse(x + w // 2 + 34, y + 20, 34, 10, (70, 80, 92))
    for i in range(7):
        rx = x + 20 + i * 28
        c.line(rx, y + 34, rx - 4, y + 46, SEA2, 2)
    # Parade balloon, low and tilted by the wind.
    bx, by = x + w // 2, y + h - 34
    c.ellipse(bx, by, 46, 20, (220, 90, 80))
    c.ellipse(bx - 12, by - 4, 12, 8, (240, 160, 120))
    c.line(bx + 40, by + 8, bx + 52, by + 22, INK, 2)
    c.line(bx - 40, by + 8, bx - 52, by + 22, INK, 2)
    c.text("81.5M", x + 10, y + h - 20, 2, INK)


def strip_egypt(c, x, y, w, h):
    """Egypt blaze: a fuel truck in flames on the ring road."""
    c.rect(x, y, w, h, (232, 224, 204))
    base = y + h
    # Road and tunnel mouth.
    c.rect(x, base - 18, w, 18, (90, 88, 84))
    c.rect(x + 8, base - 44, 60, 26, (60, 58, 54))
    c.rect(x + 14, base - 38, 48, 20, INK)
    # Fuel truck, centre.
    tx, ty = x + w // 2 - 30, base - 40
    c.ellipse(tx + 46, ty + 6, 44, 12, (200, 200, 196))
    c.rect(tx, ty, 26, 22, RED)
    c.rect(tx + 4, ty + 4, 12, 8, SKY)
    c.circle(tx + 12, ty + 24, 6, INK)
    c.circle(tx + 72, ty + 24, 6, INK)
    # Flames over the tank.
    c.poly([(tx + 30, ty + 2), (tx + 40, ty - 22), (tx + 50, ty + 2)],
           ORANGE)
    c.poly([(tx + 52, ty + 2), (tx + 60, ty - 16), (tx + 68, ty + 2)],
           YELLOW)
    c.circle(tx + 40, ty - 28, 9, (90, 90, 92))
    c.text("30", x + w - 44, y + 8, 3, RED)

# ---------------------------------------------------------------------------
# Page layout.
# ---------------------------------------------------------------------------

M = 24                      # outer margin
CW = W - 2 * M              # content width


def story(c, x, y, w, h, kicker, heads, body, draw, pic_h):
    """Medium story: kicker, illustration, headline, 3 facts, rule."""
    c.text(kicker, x, y, 1, RED)
    draw(c, x, y + 16, w, pic_h)
    hy = y + 16 + pic_h + 10
    for hd in heads:
        c.text(hd, x, hy, 2, INK)
        hy += 24
    by = hy + 4
    for line in body:
        c.text(line, x, by, 2, INK)
        by += 15
    c.hline(x, y + h - 1, w, INK, 1)


def small_story(c, x, y, w, h, kicker, heads, body, draw, pic_h):
    """Small story: kicker, strip illustration, headline, 3 facts, rule."""
    c.text(kicker, x, y, 1, RED)
    draw(c, x, y + 16, w, pic_h)
    hy = y + 16 + pic_h + 8
    for hd in heads:
        c.text(hd, x, hy, 2, INK)
        hy += 22
    by = hy + 4
    for line in body:
        c.text(line, x, by, 2, INK)
        by += 16
    c.hline(x, y + h - 1, w, INK, 1)


def build():
    c = Canvas()
    # Masthead.
    c.hline(M, 14, CW, INK, 3)
    c.center("THE WORLD IN ONE PICTURE", W // 2, 30, 4, INK)
    c.center("THURSDAY  -  26 NOVEMBER 2026", W // 2, 66, 2, RED)
    c.hline(M, 90, CW, INK, 1)
    c.text("THE DAY IN EIGHT STORIES", M, 98, 1, INK)
    c.text("WORLD NEWS  -  ONE IMAGE", W - M - c.text_w(
        "WORLD NEWS  -  ONE IMAGE", 1), 98, 1, INK)
    c.hline(M, 114, CW, INK, 3)

    # Lead story: Hormuz. Illustration left, text right.
    ly, lh = 126, 280
    lx, lw = M, 540
    tx = lx + lw + 16
    tw = M + CW - tx
    draw_hormuz(c, lx, ly + 20, lw, lh - 28)
    c.text("THE STRAIT OF HORMUZ  -  MIDDLE EAST", tx, ly + 4, 1, RED)
    hy = ly + 26
    for hd in ("TWO MORE TANKERS", "HIT MINES IN HORMUZ"):
        c.text(hd, tx, hy, 3, INK)
        hy += 30
    by = hy + 8
    for line in ("IRAN SAYS TWO TANKERS HIT MINES",
                 "AND CAUGHT FIRE AT DAWN.",
                 "TEHRAN TELLS SHIPS TO COORDINATE",
                 "PASSAGE OR RISK THE SAME FATE.",
                 "COMMERCIAL TRANSIT HAS NEARLY",
                 "STOPPED. BRENT CRUDE ABOVE $94."):
        c.text(line, tx, by, 2, INK)
        by += 19
    c.frame(tx, by + 6, tw, 40, RED, 2)
    c.center("BRENT CRUDE ABOVE $94 A BARREL", tx + tw // 2, by + 17, 2, RED)
    c.text("IRAN'S CLAIMS ARE UNCONFIRMED BY INDEPENDENT MONITORS.",
           tx, by + 56, 1, GREY)
    c.hline(M, ly + lh, CW, INK, 2)

    # Row two: three medium stories.
    ry, rh = 414, 258
    rw = (CW - 32) // 3
    story(c, M, ry, rw, rh, "TRADE  -  WASHINGTON",
          ("U.S. PROPOSES TARIFFS", "ON 14 ECONOMIES"),
          ("USTR PROPOSES NEW TARIFFS",
           "ON 14 ECONOMIES.",
           "SINGAPORE FACES UP TO 20%,",
           "VIETNAM UP TO 35%.",
           "THE RATES ARE PROPOSED,",
           "NOT YET IN FORCE."),
          med_tariffs, 84)
    story(c, M + rw + 16, ry, rw, rh, "UKRAINE  -  WAR",
          ("UKRAINE HITS TWO", "RUSSIAN REFINERIES"),
          ("UKRAINIAN DRONES SET TWO",
           "SAMARA REFINERIES ABLAZE.",
           "FIVE JETS DAMAGED AT",
           "SAVASLEYKA AIRFIELD.",
           "BOTH PLANTS STAND ABOUT",
           "800 KM FROM UKRAINE."),
          med_refinery, 84)
    story(c, M + 2 * (rw + 16), ry, rw, rh, "MIDDLE EAST  -  GAZA",
          ("GAZA STRIKE KILLS", "HAMAS SECURITY CHIEF"),
          ("ISRAELI STRIKE KILLS HAMAS",
           "SECURITY CHIEF AND FAMILY.",
           "SECOND HAMAS OFFICIAL",
           "KILLED IN 24 HOURS.",
           "AT LEAST 1,600 KILLED IN",
           "GAZA SINCE THE CEASEFIRE."),
          med_gaza, 84)
    c.hline(M, ry + rh, CW, INK, 2)

    # Row three: four small stories.
    ry, rh = 680, 292
    sw = (CW - 48) // 4
    small_story(c, M, ry, sw, rh, "LATIN AMERICA  -  COLOMBIA",
                ("ALL HOSTAGES FREED", "IN CARTAGENA"),
                ("30 HOSTAGES FREED",
                 "AFTER 16-HOUR SIEGE",
                 "TROOPS STORMED THE",
                 "SUPERMARKET AT DAWN",
                 "ONE GUNMAN KILLED,",
                 "PRESIDENT CONFIRMS."),
                strip_cartagena, 112)
    small_story(c, M + sw + 16, ry, sw, rh, "SPACE  -  CHINA",
                ("PAKISTAN'S FIRST", "ASTRONAUT IN ORBIT"),
                ("SHENZHOU-24 LIFTED",
                 "OFF AT 08:18.",
                 "THREE ASTRONAUTS",
                 "HEAD FOR TIANGONG.",
                 "PAKISTAN HAILS",
                 "A SPACE FIRST."),
                strip_shenzhou, 112)
    small_story(c, M + 2 * (sw + 16), ry, sw, rh, "UNITED STATES",
                ("STORM HITS", "THANKSGIVING TRAVEL"),
                ("RAIN AND GALES HIT",
                 "THE EAST COAST.",
                 "81.5 MILLION ON THE",
                 "MOVE THIS WEEK.",
                 "PARADE BALLOONS MAY",
                 "STAY GROUNDED."),
                strip_storm, 112)
    small_story(c, M + 3 * (sw + 16), ry, sw, rh, "MIDDLE EAST  -  EGYPT",
                ("30 KILLED IN", "EGYPT FUEL BLAZE"),
                ("FUEL TRUCK CRASH",
                 "SPARKS HUGE BLAZE.",
                 "AT LEAST 30 KILLED,",
                 "15 INJURED.",
                 "BLAZE ABOVE A TUNNEL",
                 "IN GIZA, NEAR CAIRO."),
                strip_egypt, 112)

    # Footer.
    c.hline(M, 986, CW, INK, 2)
    c.text("SOURCES: IRNA, REUTERS, USTR, KYIV INDEPENDENT, "
           "AL JAZEERA, AP, BBC, AAA, AFP",
           M, 992, 1, GREY)
    return c


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    c = build()
    write_png(os.path.join(out, "entry.png"), bytes(c.px))


if __name__ == "__main__":
    main()
