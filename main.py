#!/usr/bin/env python3
"""One-day newspaper: the world news of Thursday 26 November 2026.

Draws a single broadsheet front page (1024x1024 PNG) with eight stories:
the tankers hit by mines in the Strait of Hormuz, the USTR tariff
proposal, the Ukrainian strikes on Russian refineries and jets, the
Gaza strike, the Cartagena hostages, the Shenzhou-24 launch, the
Thanksgiving storm and the fuel-truck fire in Egypt.

Standard library only. No PIL, no network, no fonts on disk: the text
is set with a small bitmap face defined below, and the PNG file is
encoded by hand (zlib for the image data). Running the program twice
writes byte-identical output.
"""

import hashlib
import os
import struct
import zlib

W, H = 1024, 1024

# --- palette -------------------------------------------------------------
PAPER = (246, 241, 229)     # newsprint cream
PANEL = (238, 230, 207)     # slightly deeper cream for picture boxes
INK = (26, 23, 18)          # near-black ink
RED = (163, 29, 29)         # headline red
BLUE = (31, 58, 95)         # deep blue
NAVY = (22, 42, 66)         # night blue
SEA = (22, 50, 74)          # dark sea
SKY = (214, 226, 232)       # pale sky
SAND = (233, 222, 196)      # pale sand
GRAY = (120, 112, 96)       # warm gray
LGRAY = (185, 172, 147)     # light rule gray
ORANGE = (224, 110, 30)     # flame orange
GOLD = (240, 192, 64)       # flame gold
WHITE = (250, 248, 242)     # paper white
SMOKE = (96, 96, 92)        # smoke gray
DARK = (44, 40, 34)         # dark silhouette

# --- bitmap face ---------------------------------------------------------
# A 5x7 face. Each glyph is seven rows of five cells, '#' set, '.' clear.
# Capitals sit on rows 0-6; lower case sits on rows 2-6 (baseline row 6).
FONT = {
    "A": ("#...#",
          "##.##",
          "#.#.#",
          "#####",
          "#...#",
          "#...#",
          "#...#"),
    "B": ("####.",
          "#...#",
          "#...#",
          "####.",
          "#...#",
          "#...#",
          "####."),
    "C": (".####",
          "#....",
          "#....",
          "#....",
          "#....",
          "#....",
          ".####"),
    "D": ("####.",
          "#...#",
          "#...#",
          "#...#",
          "#...#",
          "#...#",
          "####."),
    "E": ("#####",
          "#....",
          "#....",
          "####.",
          "#....",
          "#....",
          "#####"),
    "F": ("#####",
          "#....",
          "#....",
          "####.",
          "#....",
          "#....",
          "#...."),
    "G": (".####",
          "#....",
          "#....",
          "#.###",
          "#...#",
          "#...#",
          ".###."),
    "H": ("#...#",
          "#...#",
          "#...#",
          "#####",
          "#...#",
          "#...#",
          "#...#"),
    "I": ("#####",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          "#####"),
    "J": ("..###",
          "...#.",
          "...#.",
          "...#.",
          "...#.",
          "#..#.",
          ".##.."),
    "K": ("#...#",
          "#..#.",
          "#.#..",
          "##...",
          "#.#..",
          "#..#.",
          "#...#"),
    "L": ("#....",
          "#....",
          "#....",
          "#....",
          "#....",
          "#....",
          "#####"),
    "M": ("#...#",
          "##.##",
          "#.#.#",
          "#.#.#",
          "#...#",
          "#...#",
          "#...#"),
    "N": ("#...#",
          "##..#",
          "##..#",
          "#.#.#",
          "#..##",
          "#..##",
          "#...#"),
    "O": (".###.",
          "#...#",
          "#...#",
          "#...#",
          "#...#",
          "#...#",
          ".###."),
    "P": ("####.",
          "#...#",
          "#...#",
          "####.",
          "#....",
          "#....",
          "#...."),
    "Q": (".###.",
          "#...#",
          "#...#",
          "#...#",
          "#.#.#",
          "#..#.",
          ".##.#"),
    "R": ("####.",
          "#...#",
          "#...#",
          "####.",
          "#.#..",
          "#..#.",
          "#...#"),
    "S": (".####",
          "#....",
          "#....",
          ".###.",
          "....#",
          "....#",
          "####."),
    "T": ("#####",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          "..#.."),
    "U": ("#...#",
          "#...#",
          "#...#",
          "#...#",
          "#...#",
          "#...#",
          ".###."),
    "V": ("#...#",
          "#...#",
          "#...#",
          "#...#",
          "#...#",
          ".#.#.",
          "..#.."),
    "W": ("#...#",
          "#...#",
          "#...#",
          "#.#.#",
          "#.#.#",
          "##.##",
          "#...#"),
    "X": ("#...#",
          "#...#",
          ".#.#.",
          "..#..",
          ".#.#.",
          "#...#",
          "#...#"),
    "Y": ("#...#",
          "#...#",
          ".#.#.",
          "..#..",
          "..#..",
          "..#..",
          "..#.."),
    "Z": ("#####",
          "....#",
          "...#.",
          "..#..",
          ".#...",
          "#....",
          "#####"),
    "0": (".###.",
          "#..##",
          "#.#.#",
          "##..#",
          "#...#",
          "#...#",
          ".###."),
    "1": ("..#..",
          ".##..",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          ".###."),
    "2": (".###.",
          "#...#",
          "....#",
          "...#.",
          "..#..",
          ".#...",
          "#####"),
    "3": ("####.",
          "....#",
          "....#",
          ".###.",
          "....#",
          "....#",
          "####."),
    "4": ("...#.",
          "..##.",
          ".#.#.",
          "#..#.",
          "#####",
          "...#.",
          "...#."),
    "5": ("#####",
          "#....",
          "####.",
          "....#",
          "....#",
          "#...#",
          ".###."),
    "6": (".###.",
          "#....",
          "#....",
          "####.",
          "#...#",
          "#...#",
          ".###."),
    "7": ("#####",
          "....#",
          "...#.",
          "...#.",
          "..#..",
          "..#..",
          "..#.."),
    "8": (".###.",
          "#...#",
          "#...#",
          ".###.",
          "#...#",
          "#...#",
          ".###."),
    "9": (".###.",
          "#...#",
          "#...#",
          ".####",
          "....#",
          "....#",
          ".###."),
    "a": (".....",
          ".....",
          ".###.",
          "....#",
          ".####",
          "#...#",
          ".####"),
    "b": ("#....",
          "#....",
          "####.",
          "#...#",
          "#...#",
          "#...#",
          "####."),
    "c": (".....",
          ".....",
          ".####",
          "#....",
          "#....",
          "#....",
          ".####"),
    "d": ("....#",
          "....#",
          ".####",
          "#...#",
          "#...#",
          "#...#",
          ".####"),
    "e": (".....",
          ".....",
          ".###.",
          "#...#",
          "#####",
          "#....",
          ".###."),
    "f": ("..##.",
          ".#..#",
          ".#...",
          "####.",
          ".#...",
          ".#...",
          ".#..."),
    "g": (".....",
          ".....",
          ".####",
          "#...#",
          "#...#",
          ".####",
          "....#"),
    "h": ("#....",
          "#....",
          "####.",
          "#...#",
          "#...#",
          "#...#",
          "#...#"),
    "i": ("..#..",
          ".....",
          ".##..",
          "..#..",
          "..#..",
          "..#..",
          ".###."),
    "j": ("...#.",
          ".....",
          "..##.",
          "...#.",
          "...#.",
          "...#.",
          ".##.."),
    "k": ("#....",
          "#....",
          "#..#.",
          "#.#..",
          "##...",
          "#.#..",
          "#..#."),
    "l": (".##..",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          ".###."),
    "m": (".....",
          ".....",
          "##.#.",
          "#.#.#",
          "#.#.#",
          "#.#.#",
          "#.#.#"),
    "n": (".....",
          ".....",
          "####.",
          "#...#",
          "#...#",
          "#...#",
          "#...#"),
    "o": (".....",
          ".....",
          ".###.",
          "#...#",
          "#...#",
          "#...#",
          ".###."),
    "p": (".....",
          ".....",
          "####.",
          "#...#",
          "#...#",
          "####.",
          "#...."),
    "q": (".....",
          ".....",
          ".####",
          "#...#",
          "#...#",
          ".####",
          "....#"),
    "r": (".....",
          ".....",
          "#.##.",
          "##..#",
          "#....",
          "#....",
          "#...."),
    "s": (".....",
          ".....",
          ".####",
          "#....",
          ".###.",
          "....#",
          "####."),
    "t": (".#...",
          ".#...",
          "####.",
          ".#...",
          ".#...",
          ".#...",
          "..##."),
    "u": (".....",
          ".....",
          "#...#",
          "#...#",
          "#...#",
          "#..##",
          ".##.#"),
    "v": (".....",
          ".....",
          "#...#",
          "#...#",
          "#...#",
          ".#.#.",
          "..#.."),
    "w": (".....",
          ".....",
          "#...#",
          "#.#.#",
          "#.#.#",
          "#.#.#",
          ".#.#."),
    "x": (".....",
          ".....",
          "#...#",
          ".#.#.",
          "..#..",
          ".#.#.",
          "#...#"),
    "y": (".....",
          ".....",
          "#...#",
          "#...#",
          ".#.##",
          "..#..",
          ".##.."),
    "z": (".....",
          ".....",
          "#####",
          "...#.",
          "..#..",
          ".#...",
          "#####"),
    " ": (".....",
          ".....",
          ".....",
          ".....",
          ".....",
          ".....",
          "....."),
    ".": (".....",
          ".....",
          ".....",
          ".....",
          ".....",
          ".##..",
          ".##.."),
    ",": (".....",
          ".....",
          ".....",
          ".....",
          ".##..",
          ".##..",
          ".#..."),
    ":": (".....",
          ".##..",
          ".##..",
          ".....",
          ".##..",
          ".##..",
          "....."),
    ";": (".....",
          ".##..",
          ".##..",
          ".....",
          ".##..",
          ".##..",
          ".#..."),
    "!": ("..#..",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          ".....",
          "..#.."),
    "?": (".###.",
          "#...#",
          "....#",
          "...#.",
          "..#..",
          ".....",
          "..#.."),
    "-": (".....",
          ".....",
          ".....",
          ".###.",
          ".....",
          ".....",
          "....."),
    "'": ("..#..",
          "..#..",
          ".#...",
          ".....",
          ".....",
          ".....",
          "....."),
    '"': (".#.#.",
          ".#.#.",
          ".#.#.",
          ".....",
          ".....",
          ".....",
          "....."),
    "(": ("...##",
          "..#..",
          ".#...",
          ".#...",
          ".#...",
          "..#..",
          "...##"),
    ")": ("##...",
          "..#..",
          "...#.",
          "...#.",
          "...#.",
          "..#..",
          "##..."),
    "/": ("....#",
          "....#",
          "...#.",
          "..#..",
          ".#...",
          "#....",
          "#...."),
    "%": ("##..#",
          "##.#.",
          "...#.",
          "..#..",
          ".#...",
          "#.##.",
          "#..##"),
    "$": ("..#..",
          ".####",
          "#.#..",
          ".###.",
          "..#.#",
          "####.",
          "..#.."),
    "·": (".....",
          ".....",
          ".##..",
          ".##..",
          ".....",
          ".....",
          "....."),
    "&": (".##..",
          "#..#.",
          "#.#..",
          ".#...",
          "#.#.#",
          "#..#.",
          ".##.#"),
    "+": (".....",
          "..#..",
          "..#..",
          "#####",
          "..#..",
          "..#..",
          "....."),
    "=": (".....",
          ".....",
          "#####",
          ".....",
          "#####",
          ".....",
          "....."),
    "[": (".###.",
          ".#...",
          ".#...",
          ".#...",
          ".#...",
          ".#...",
          ".###."),
    "]": (".###.",
          "...#.",
          "...#.",
          "...#.",
          "...#.",
          "...#.",
          ".###."),
    "_": (".....",
          ".....",
          ".....",
          ".....",
          ".....",
          ".....",
          "#####"),
    "É": ("..##.",
          ".##..",
          "#####",
          "#....",
          "####.",
          "#....",
          "#####"),
    "é": ("..##.",
          ".##..",
          ".###.",
          "#...#",
          "#####",
          "#....",
          ".###."),
}

# The middle dot and the accented capitals have their own slots above.

# Punctuation that the face draws with a plain hyphen or quote.
NORMALIZE = {
    "\u2013": "-", "\u2014": "-", "\u2019": "'", "\u2018": "'",
    "\u201c": '"', "\u201d": '"', "\u00d7": "x", "\u00b7": "·",
}


def glyph(ch):
    ch = NORMALIZE.get(ch, ch)
    return FONT.get(ch, FONT["?"])


# --- canvas --------------------------------------------------------------
class Canvas:
    """An RGB framebuffer with small drawing primitives."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bytes(bg)) * (w * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def block(self, x, y, s, c):
        for yy in range(y, y + s):
            if yy < 0 or yy >= self.h:
                continue
            x0 = max(x, 0)
            x1 = min(x + s, self.w)
            if x1 <= x0:
                continue
            i = (yy * self.w + x0) * 3
            self.px[i:i + (x1 - x0) * 3] = bytes(c) * (x1 - x0)

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            if yy < 0 or yy >= self.h:
                continue
            x0 = max(x, 0)
            x1 = min(x + w, self.w)
            if x1 <= x0:
                continue
            i = (yy * self.w + x0) * 3
            self.px[i:i + (x1 - x0) * 3] = bytes(c) * (x1 - x0)

    def outline(self, x, y, w, h, c):
        self.rect(x, y, w, 1, c)
        self.rect(x, y + h - 1, w, 1, c)
        self.rect(x, y, 1, h, c)
        self.rect(x + w - 1, y, 1, h, c)

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        half = t // 2
        while True:
            self.rect(x0 - half, y0 - half, t, t, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for dy in range(-ry, ry + 1):
            t = 1.0 - (dy * dy) / float(ry * ry)
            dx = int(rx * (t ** 0.5)) if t > 0 else 0
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def tri(self, p0, p1, p2, c):
        self.poly([p0, p1, p2], c)

    def poly(self, pts, c):
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if y0 == y1:
                    continue
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            if len(xs) >= 2:
                xs.sort()
                self.rect(int(xs[0]), y, int(xs[-1]) - int(xs[0]) + 1, 1, c)

    # -- text -------------------------------------------------------------
    def text_w(self, s, scale, tracking=None, bold=False):
        if tracking is None:
            tracking = max(1, scale // 2)
        extra = max(1, scale // 2) if bold else 0
        return len(s) * (5 * scale + tracking) - tracking + extra

    def text(self, x, y, s, scale, c, bold=False, tracking=None):
        if tracking is None:
            tracking = max(1, scale // 2)
        bold_dx = max(1, scale // 2) if bold else 0
        cx = x
        for ch in s:
            rows = glyph(ch)
            for r, row in enumerate(rows):
                for col, bit in enumerate(row):
                    if bit == "#":
                        self.block(cx + col * scale, y + r * scale,
                                   scale, c)
                        if bold:
                            self.block(cx + col * scale + bold_dx,
                                       y + r * scale, scale, c)
            cx += 5 * scale + tracking
        return cx


def wrap(text, scale, max_w, tracking=None, bold=False):
    """Greedy word wrap. Re-tries a little narrower when the last line
    would hold a single word, so no fact ends on a lone word."""
    if tracking is None:
        tracking = max(1, scale // 2)
    probe = Canvas(1, 1, PAPER)

    def do_wrap(width):
        lines, cur = [], ""
        for word in text.split(" "):
            trial = word if not cur else cur + " " + word
            if probe.text_w(trial, scale, tracking, bold) <= width or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    lines = do_wrap(max_w)
    if len(lines) > 1 and len(lines[-1].split(" ")) == 1:
        for shrink in range(4, 44, 4):
            alt = do_wrap(max_w - shrink)
            if len(alt[-1].split(" ")) >= 2:
                return alt
    return lines


def para(cv, x, y, lines, scale, c, lh, tracking=None, bold=False):
    for line in lines:
        cv.text(x, y, line, scale, c, bold=bold, tracking=tracking)
        y += lh
    return y


# --- PNG writer ----------------------------------------------------------
def save_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# --- stories --------------------------------------------------------------
# (kicker, headline, [fact line, fact line, fact line])
LEAD = (
    "STRAIT OF HORMUZ - LEAD STORY",
    "TWO MORE TANKERS HIT MINES IN HORMUZ",
    [
        "Iran's Revolutionary Guard navy says two oil tankers struck "
        "mines in the Strait of Hormuz early on Wednesday.",
        "Both ships caught fire in their engine rooms. Tehran says "
        "ships must coordinate with its navy.",
        "Three more ships were hit on Monday night. Traffic has nearly "
        "stopped; Brent crude rose above $94.",
    ],
)

MEDIUM = [
    (
        "TRADE - WASHINGTON",
        "U.S. TARIFFS FOR 14 ECONOMIES",
        [
            "USTR proposed tariffs on 14 economies under Section 301.",
            "Singapore faces up to 20% and Vietnam up to 35%.",
            "China, the EU, Japan and India are among the 14 named.",
        ],
    ),
    (
        "WAR IN UKRAINE",
        "UKRAINE HITS REFINERIES, JETS",
        [
            "Kyiv says drones struck two refineries in Samara region.",
            "Kuybyshev's AVT-4, AVT-5 and two tanks were damaged.",
            "Five jets hit at Savasleyka: three MiG-31s, two Su-34s.",
        ],
    ),
    (
        "GAZA",
        "GAZA STRIKE KILLS HAMAS CHIEF",
        [
            "Strike kills Hamas security chief Abu Elrouf, 47.",
            "His wife and two daughters died with him at their home.",
            "Over 1,600 have died since the October 2025 ceasefire.",
        ],
    ),
]

SMALL = [
    (
        "COLOMBIA",
        "HOSTAGES FREED IN CARTAGENA",
        [
            "Gunmen took about 30 hostages in a Cartagena store.",
            "Ten were freed on Tuesday; the other 20 were rescued at dawn.",
            "The president confirmed all freed; one gunman dead.",
        ],
    ),
    (
        "SPACE - CHINA",
        "PAKISTAN'S FIRST ASTRONAUT",
        [
            "Shenzhou-24 launched from Jiuquan at 08:18 Beijing time.",
            "Aboard: Tang Hongbo, Wu Yi and Pakistan's Muhammad Zeeshan Ali.",
            "Ali: Pakistan's first astronaut, first foreigner aboard.",
        ],
    ),
    (
        "UNITED STATES",
        "STORM HITS THANKSGIVING",
        [
            "A storm is hitting the East Coast on Thanksgiving Day.",
            "New York faces 1-2 inches of rain and gusts of 35-45 mph.",
            "81.5 million travel; parade balloons may stay down.",
        ],
    ),
    (
        "EGYPT",
        "FUEL FIRE KILLS 30 IN EGYPT",
        [
            "Fuel tanker overturns on Cairo's Ring Road and catches fire.",
            "Thirty were killed and 15 injured, the health ministry said.",
            "39 ambulances were sent; prosecutors opened an inquiry.",
        ],
    ),
]


# --- spot illustrations ----------------------------------------------------
def flame(cv, x, y, w, h):
    """A small flame: orange outer, gold inner, on a dark base."""
    cv.tri((x, y + h), (x + w // 2, y), (x + w, y + h), ORANGE)
    cv.tri((x + w // 4, y + h), (x + w // 2, y + h // 3),
           (x + 3 * w // 4, y + h), GOLD)
    cv.disc(x + w // 2, y + h - 2, max(1, w // 6), GOLD)


def tanker(cv, x, y, w, h, on_fire):
    """A tanker seen side-on: dark hull, pale deckhouse, funnel."""
    hull_h = max(8, h * 2 // 3)
    cv.rect(x, y + h - hull_h, w, hull_h, DARK)
    cv.rect(x, y + h - 3, w, 3, RED)
    deck = max(6, hull_h // 2)
    cv.rect(x + w - w // 5, y + h - hull_h - deck, w // 6, deck, WHITE)
    cv.rect(x + w - w // 5 - 4, y + h - hull_h - deck - 6, 5, 6, DARK)
    cv.rect(x + 6, y + h - hull_h - 4, 3, 4, GOLD)
    if on_fire:
        flame(cv, x + w // 3, y - h // 2, w // 4, h // 2 + 6)
        cv.disc(x + w // 3 + w // 8, y - h // 2 - 6, 5, SMOKE)
        cv.disc(x + w // 3 + w // 8 + 8, y - h // 2 - 12, 7, SMOKE)


def mine(cv, cx, cy, r):
    cv.disc(cx, cy, r, INK)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)):
        cv.line(cx + dx * r, cy + dy * r,
                cx + dx * (r + 4), cy + dy * (r + 4), INK, 2)


def pic_strait(cv, x, y, w, h):
    cv.rect(x, y, w, h, SEA)
    cv.rect(x, y, w, h // 3, SAND)
    cv.rect(x, y + h // 3 - 2, w, 2, INK)
    cv.poly([(x, y + h // 3), (x + w // 3, y + h // 3 - 18),
             (x + w // 2, y + h // 3), (x, y + h // 3)], (214, 200, 160))
    cv.text(x + 10, y + 8, "STRAIT OF HORMUZ", 1, INK, bold=True)
    tanker(cv, x + 24, y + h // 2 - 10, w // 2 - 40, 46, True)
    tanker(cv, x + w // 2 + 6, y + h // 2 + 34, w // 2 - 60, 40, True)
    mine(cv, x + w // 4, y + h - 26, 6)
    mine(cv, x + 3 * w // 4, y + h - 40, 5)
    mine(cv, x + w - 46, y + h - 22, 5)
    for wy in (y + h - 60, y + h - 44):
        for wx in range(x + 12, x + w - 12, 34):
            cv.hline(wx, wy, 16, (120, 160, 185))


def pic_tariffs(cv, x, y, w, h):
    cv.rect(x, y, w, h, PANEL)
    base = y + h - 16
    cv.hline(x + 8, base, w - 16, INK)
    sg_h, vn_h = 23, 40
    cv.rect(x + 26, base - sg_h, 44, sg_h, BLUE)
    cv.rect(x + 96, base - vn_h, 44, vn_h, RED)
    cv.text(x + 30, base - sg_h + 4, "20%", 2, WHITE, bold=True)
    cv.text(x + 100, base - vn_h + 4, "35%", 2, WHITE, bold=True)
    cv.text(x + 22, base + 4, "SINGAPORE", 1, INK, bold=True)
    cv.text(x + 100, base + 4, "VIETNAM", 1, INK, bold=True)
    cv.text(x + 196, y + 6, "14", 4, INK, bold=True)
    cv.text(x + 196, y + 40, "ECONOMIES", 1, INK, bold=True)
    cv.text(x + 196, y + 52, "NAMED", 1, GRAY, bold=True)


def jet(cv, x, y, s):
    cv.poly([(x, y), (x + s, y + s // 3), (x, y + 2 * s // 3)], WHITE)
    cv.poly([(x + s // 2, y + s // 6), (x + s, y + s // 3),
             (x + s // 2, y + s // 2)], GOLD)


def pic_ukraine(cv, x, y, w, h):
    cv.rect(x, y, w, h, PANEL)
    cv.rect(x, y, w, 18, GOLD)
    cv.rect(x, y + 18, w, 8, ORANGE)
    cv.rect(x, y + 26, w, h - 26, (52, 48, 44))
    for tx, th in ((18, 26), (52, 34), (92, 22)):
        cv.rect(x + tx, y + h - 8 - th, 16, th, INK)
        cv.rect(x + tx + 5, y + h - 8 - th - 6, 6, 6, INK)
    flame(cv, x + 92, y + h - 8 - 22 - 16, 14, 16)
    cv.line(x + 150, y + h - 8, x + w - 8, y + h - 30, (120, 112, 96), 2)
    for i in range(5):
        jet(cv, x + 160 + i * 26, y + h - 26 - (i % 2) * 4, 16)
    cv.rect(x + w - 92, y + 4, 86, 18, INK)
    cv.text(x + w - 88, y + 7, "800 KM", 2, WHITE, bold=True)
    cv.rect(x + 6, y + 4, 74, 18, INK)
    cv.text(x + 10, y + 7, "5 JETS", 2, WHITE, bold=True)


def pic_gaza(cv, x, y, w, h):
    cv.rect(x, y, w, h, SKY)
    for bx, bh in ((8, 22), (40, 34), (78, 26), (116, 40), (160, 30),
                   (200, 36), (244, 24), (282, 30)):
        cv.rect(x + bx, y + h - bh, 30, bh, DARK)
        for wy in range(y + h - bh + 5, y + h - 4, 9):
            cv.rect(x + bx + 5, wy, 4, 5, GOLD)
    cv.disc(x + 130, y + 16, 6, SMOKE)
    cv.disc(x + 142, y + 12, 7, SMOKE)
    cv.disc(x + 118, y + 14, 5, (140, 140, 136))
    cv.rect(x + w - 106, y + 4, 100, 18, INK)
    cv.text(x + w - 102, y + 7, "2ND IN 24 HOURS", 1, WHITE, bold=True)


def figure(cv, x, y, h, c):
    cv.disc(x + 4, y + 4, 4, c)
    cv.rect(x, y + 9, 9, h - 9, c)
    cv.rect(x - 3, y + 9, 3, h // 2, c)
    cv.rect(x + 9, y + 9, 3, h // 2, c)


def pic_cartagena(cv, x, y, w, h):
    cv.rect(x, y, w, h, PANEL)
    cv.text(x + 8, y + 2, "16 HOURS", 2, RED, bold=True)
    cv.rect(x + 8, y + 20, 130, h - 28, WHITE)
    cv.outline(x + 8, y + 20, 130, h - 28, INK)
    cv.rect(x + 8, y + 20, 130, 12, RED)
    cv.text(x + 16, y + 23, "ÉXITO", 1, WHITE, bold=True)
    cv.rect(x + 20, y + 40, 18, 12, BLUE)
    cv.rect(x + 52, y + 40, 18, 12, BLUE)
    cv.rect(x + 88, y + 40, 18, 12, BLUE)
    cv.rect(x + 60, y + h - 14, 26, 6, DARK)
    figure(cv, x + 158, y + 22, 34, DARK)
    figure(cv, x + 182, y + 26, 30, BLUE)
    figure(cv, x + 204, y + 22, 34, DARK)
    cv.line(x + 158, y + 26, x + 150, y + 14, DARK, 2)


def pic_shenzhou(cv, x, y, w, h):
    cv.rect(x, y, w, h, NAVY)
    for sx, sy in ((14, 8), (40, 20), (110, 6), (130, 14), (170, 8),
                   (200, 22), (222, 10), (30, 40), (220, 40), (150, 44)):
        cv.set(x + sx, y + sy, WHITE)
        cv.set(x + sx + 1, y + sy, WHITE)
    cv.text(x + 8, y + 4, "08:18", 2, WHITE, bold=True)
    cv.rect(x + 84, y + 12, 12, 30, WHITE)
    cv.tri((x + 84, y + 12), (x + 96, y + 12), (x + 90, y + 2), RED)
    cv.rect(x + 78, y + 22, 6, 8, RED)
    cv.rect(x + 96, y + 22, 6, 8, RED)
    flame(cv, x + 84, y + 42, 12, 14)
    cv.disc(x + 76, y + 57, 5, SMOKE)
    cv.disc(x + 98, y + 58, 5, SMOKE)
    cv.rect(x + 140, y + 20, 66, 8, WHITE)
    cv.rect(x + 146, y + 12, 14, 8, (200, 210, 220))
    cv.rect(x + 186, y + 12, 14, 8, (200, 210, 220))
    cv.rect(x + 140, y + 28, 20, 4, BLUE)
    cv.rect(x + 186, y + 28, 20, 4, BLUE)


def pic_storm(cv, x, y, w, h):
    cv.rect(x, y, w, h, (176, 190, 200))
    cv.ellipse(x + 40, y + 14, 34, 12, (110, 120, 128))
    cv.ellipse(x + 70, y + 10, 30, 12, (130, 140, 148))
    cv.ellipse(x + 100, y + 16, 28, 10, (110, 120, 128))
    for rx in range(20, 130, 16):
        cv.line(x + rx, y + 30, x + rx - 5, y + 44, (90, 105, 118), 2)
    cv.ellipse(x + 172, y + 26, 26, 18, ORANGE)
    cv.ellipse(x + 172, y + 26, 18, 12, GOLD)
    cv.rect(x + 168, y + 48, 8, 6, DARK)
    cv.line(x + 172, y + 44, x + 172, y + 48, INK, 1)
    cv.rect(x + 8, y + h - 20, 66, 16, INK)
    cv.text(x + 12, y + h - 17, "81.5M", 2, WHITE, bold=True)


def pic_egypt(cv, x, y, w, h):
    cv.rect(x, y, w, h, SAND)
    cv.disc(x + 150, y + 8, 5, SMOKE)
    cv.disc(x + 168, y + 6, 6, SMOKE)
    cv.disc(x + 158, y + 14, 4, (140, 140, 136))
    cv.rect(x, y + h - 20, w, 20, (70, 66, 60))
    for dx in range(6, w - 6, 22):
        cv.hline(x + dx, y + h - 10, 12, GOLD)
    cv.rect(x + 20, y + h - 30, 104, 16, ORANGE)
    cv.disc(x + 20, y + h - 22, 8, ORANGE)
    cv.rect(x + 124, y + h - 32, 26, 18, DARK)
    cv.rect(x + 128, y + h - 28, 10, 6, SKY)
    flame(cv, x + 130, y + 8, 24, 22)
    flame(cv, x + 160, y + 14, 16, 16)
    cv.rect(x + 6, y + 4, 116, 30, INK)
    cv.text(x + 10, y + 7, "30 KILLED", 2, WHITE, bold=True)
    cv.text(x + 10, y + 24, "15 INJURED", 1, WHITE, bold=True)


PICS = {
    "strait": pic_strait,
    "tariffs": pic_tariffs,
    "ukraine": pic_ukraine,
    "gaza": pic_gaza,
    "cartagena": pic_cartagena,
    "shenzhou": pic_shenzhou,
    "storm": pic_storm,
    "egypt": pic_egypt,
}

MEDIUM_PICS = ["tariffs", "ukraine", "gaza"]
SMALL_PICS = ["cartagena", "shenzhou", "storm", "egypt"]


# --- page ------------------------------------------------------------------
def masthead(cv):
    cv.rect(22, 10, 980, 3, INK)
    cv.rect(22, 15, 980, 1, INK)
    name = "THE WORLD IN ONE PICTURE"
    nw = cv.text_w(name, 6, bold=True)
    cv.text((W - nw) // 2, 22, name, 6, INK, bold=True)
    cv.rect(22, 72, 980, 1, INK)
    cv.text(22, 78, "EIGHT STORIES", 1, INK, bold=True)
    date = "THURSDAY - 26 NOVEMBER 2026"
    dw = cv.text_w(date, 2, bold=True)
    cv.text((W - dw) // 2, 76, date, 2, INK, bold=True)
    tail = "ONE DAY'S NEWS"
    tw = cv.text_w(tail, 1, bold=True)
    cv.text(W - 22 - tw, 78, tail, 1, INK, bold=True)
    cv.rect(22, 96, 980, 1, INK)


def lead(cv):
    kicker, head, facts = LEAD
    y = 108
    cv.text(22, y, kicker, 1, RED, bold=True)
    cv.text(22, y + 18, head, 4, INK, bold=True)
    cv.rect(22, y + 54, 980, 1, INK)
    px, py, pw, ph = 22, y + 64, 540, 272
    PICS["strait"](cv, px, py, pw, ph)
    cv.outline(px, py, pw, ph, INK)
    tx, tw = 586, 416
    cv.rect(tx, py, tw, 64, INK)
    cv.text(tx + 14, py + 10, "2 TANKERS", 4, WHITE, bold=True)
    cv.text(tx + 14, py + 44, "BRENT CRUDE ABOVE $94", 2, GOLD, bold=True)
    cv.text(tx, py + 74, "IRAN'S CLAIM - UNCONFIRMED", 1, RED, bold=True)
    fy = py + 96
    for i, fact in enumerate(facts):
        lines = wrap(fact, 2, tw, bold=False)
        fy = para(cv, tx, fy, lines, 2, INK, 17)
        fy += 8


def medium(cv, x, story, pic_name):
    kicker, head, facts = story
    y = 466
    cv.text(x, y, kicker, 1, RED, bold=True)
    lines = wrap(head, 3, 320, bold=True)
    para(cv, x, y + 16, lines, 3, INK, 25, bold=True)
    px, py, pw, ph = x, y + 78, 320, 62
    PICS[pic_name](cv, px, py, pw, ph)
    cv.outline(px, py, pw, ph, INK)
    fy = py + 70
    for fact in facts:
        fl = wrap(fact, 2, 320, bold=False)
        fy = para(cv, x, fy, fl, 2, INK, 16)
        fy += 3


def small(cv, x, story, pic_name):
    kicker, head, facts = story
    y = 732
    cv.text(x, y, kicker, 1, RED, bold=True)
    lines = wrap(head, 2, 238, bold=True)
    para(cv, x, y + 14, lines, 2, INK, 18, bold=True)
    px, py, pw, ph = x, y + 60, 238, 64
    PICS[pic_name](cv, px, py, pw, ph)
    cv.outline(px, py, pw, ph, INK)
    fy = py + 72
    for fact in facts:
        fl = wrap(fact, 2, 238, bold=False)
        fy = para(cv, x, fy, fl, 2, INK, 16)
        fy += 2


def build():
    cv = Canvas(W, H, PAPER)
    masthead(cv)
    lead(cv)
    cv.rect(22, 458, 980, 2, INK)
    for i, story in enumerate(MEDIUM):
        x = 22 + i * 330
        medium(cv, x, story, MEDIUM_PICS[i])
        if i:
            cv.vline(x - 10, 466, 258, LGRAY)
    cv.rect(22, 726, 980, 1, INK)
    for i, story in enumerate(SMALL):
        x = 22 + i * 246
        small(cv, x, story, SMALL_PICS[i])
        if i:
            cv.vline(x - 8, 732, 280, LGRAY)
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    cv = build()
    size = save_png(cv, path)
    digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
    print("wrote %s (%d bytes) sha256=%s" % (path, size, digest))


if __name__ == "__main__":
    main()
