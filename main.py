#!/usr/bin/env python3
"""Five Stories, One Friday -- 27 November 2026.

A program that draws a one-page newspaper poster summing up five
world-news stories of Friday 27 November 2026 and writes it to
/output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).

Pure Python 3.13 standard library. No network, no files read, no clock,
no randomness: every run writes the same bytes. All pixels -- masthead,
storm scene, four drawn icons, headlines and captions -- are produced by
the drawing code below, including a 5x7 bitmap font defined by hand in
this file.

The five stories (checked against first publication; dates noted honestly):
  1. Thanksgiving nor'easter batters the US East Coast through
     Thanksgiving Day into Friday 27 Nov: gusts to 70 mph, more than
     730,000 without power, 400+ flights cancelled, coastal flooding
     (Reuters, WSJ, NY Post, 26 Nov 2026; storm departs overnight
     into Friday).
  2. Israel kills a third senior Hamas leader in three days; Hamas
     weighs a response as strikes kill 10 in Gaza, including the
     Hamas-appointed deputy education minister (Reuters, CNN, NY Post,
     26 Nov 2026; summary published 27 Nov 00:04 UTC).
  3. The diesel tanker Med Emre capsizes off Ibiza: one crew member
     dead, 7,000 tonnes of diesel aboard, Spain activates its
     level-2 pollution plan and races to stop a spill (Reuters,
     26 Nov 2026; hull inspection and spill watch, 27 Nov 2026).
  4. North Korea orders the Swiss envoy out: the 48-hour deadline to
     leave falls on Friday 27 Nov, and Pyongyang shuts the Swiss
     office in a row over sanctions on a children's camp
     (KCNA via BBC/Xinhua, ordered 25 Nov 2026; Asia Daily, 27 Nov).
  5. China shuts golf courses in a new crackdown on the "sport for
     millionaires": at least 18 courses announce closure in November,
     ten of them in Beijing (AFP, 26 Nov 2026).
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

# Palette: paper front page, navy masthead, gold rule, five accents.
PAPER = (248, 244, 233)
CARD = (255, 255, 255)
NAVY = (13, 27, 51)
NAVY2 = (24, 45, 76)
GOLD = (198, 154, 52)
INK = (16, 22, 36)
GREY = (96, 102, 116)
LIGHT = (226, 220, 203)
WHITE = (255, 255, 255)
ACCENTS = [(186, 52, 38), (28, 110, 168), (198, 104, 24), (84, 82, 150), (42, 122, 102)]
SKY = (158, 190, 220)
CLOUD = (52, 68, 96)
RAIN = (90, 130, 180)

# ------------------------------------------------------------------ font
# 5x7 glyphs, rows top to bottom, "#" = on, "." = off.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def wrap(text, max_chars):
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            for a in range(thick):
                for b in range(thick):
                    self.set(x + a, y + b, color)
            if x == x1 and y == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    def ring(self, cx, cy, r, color, thick=3):
        for a in range(360):
            rad = a * math.pi / 180.0
            for t in range(thick):
                self.set(int(cx + (r - t) * math.cos(rad)),
                         int(cy + (r - t) * math.sin(rad)), color)

    def poly(self, pts, color):
        # Scanline fill for a simple polygon.
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                for x in range(int(xs[k]), int(xs[k + 1]) + 1):
                    self.set(x, y, color)

    def text(self, x, y, s, scale, color):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        for a in range(scale):
                            for b in range(scale):
                                self.set(cx + col * scale + a,
                                         y + row * scale + b, color)
            cx += 6 * scale
        return cx

    def text_center(self, y, s, scale, color):
        self.text((self.w - text_width(s, scale)) // 2, y, s, scale, color)


# ------------------------------------------------------------------ PNG
def write_png(path, cv):
    raw = b"".join(b"\x00" + bytes(cv.px[y * cv.w * 3:(y + 1) * cv.w * 3])
                   for y in range(cv.h))

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


# ------------------------------------------------------------------ icons
def icon_storm(cv, x, y, w, h):
    """Nor'easter: dark cloud, lightning, rain, flooded rooftops."""
    cv.rect(x, y, w, h, SKY)
    cv.rect(x, y + h - 26, w, 26, (38, 78, 122))
    # Rooftops poking out of the flood water.
    cv.poly([(x + 12, y + h - 26), (x + 52, y + h - 62),
             (x + 92, y + h - 26)], (70, 60, 52))
    cv.poly([(x + 108, y + h - 26), (x + 148, y + h - 58),
             (x + 188, y + h - 26)], (70, 60, 52))
    # Cloud: overlapping discs on a slab.
    for cx, cy, r in [(x + 55, y + 52, 30), (x + 95, y + 38, 36),
                      (x + 140, y + 52, 30), (x + 95, y + 58, 34)]:
        cv.disc(cx, cy, r, CLOUD)
    cv.rect(x + 28, y + 52, 140, 26, CLOUD)
    # Lightning bolt.
    cv.poly([(x + 96, y + 74), (x + 78, y + 118), (x + 92, y + 118),
             (x + 82, y + 152), (x + 116, y + 100), (x + 100, y + 100),
             (x + 114, y + 74)], GOLD)
    # Rain, slanting.
    for rx in range(x + 14, x + w - 8, 22):
        cv.line(rx, y + 96, rx - 8, y + 122, RAIN, 2)
        cv.line(rx + 8, y + 128, rx, y + 152, RAIN, 2)


def icon_gaza(cv, x, y, w, h):
    """A broken olive branch over a cracked wall: ceasefire under strain."""
    accent = ACCENTS[1]
    cv.rect(x, y, w, h, (232, 238, 244))
    # Wall blocks.
    cv.rect(x + 14, y + 108, w - 28, 14, (120, 118, 110))
    cv.rect(x + 14, y + 86, 62, 14, (140, 138, 130))
    cv.rect(x + 88, y + 86, 62, 14, (140, 138, 130))
    # Crack down the middle.
    cv.line(x + 96, y + 86, x + 88, y + 108, INK, 2)
    cv.line(x + 88, y + 108, x + 98, y + 122, INK, 2)
    # Branch stem, snapped.
    cv.line(x + 30, y + 30, x + 88, y + 88, (52, 110, 66), 4)
    cv.line(x + 112, y + 58, x + 168, y + 22, (52, 110, 66), 4)
    # Leaves.
    for lx, ly in [(52, 44), (66, 62), (44, 66), (132, 40), (148, 52), (162, 34)]:
        cv.disc(lx + x - 14, ly + y - 8, 9, (66, 138, 80))
    # One fallen leaf.
    cv.disc(x + 150, y + 78, 8, GOLD)
    cv.text(x + 18, y + 126, "CEASEFIRE", 1, accent)


def icon_tanker(cv, x, y, w, h):
    """A capsized tanker, keel up, in a slick-ringed sea."""
    accent = ACCENTS[2]
    cv.rect(x, y, w, h, (214, 232, 240))
    # Sea.
    cv.rect(x, y + 104, w, h - 104, (36, 98, 150))
    for wx in range(x + 6, x + w - 10, 26):
        cv.line(wx, y + 116, wx + 14, y + 116, WHITE, 2)
        cv.line(wx + 4, y + 132, wx + 18, y + 132, WHITE, 2)
    # Overturned hull, keel up.
    cv.poly([(x + 34, y + 104), (x + 62, y + 62), (x + 146, y + 62),
             (x + 172, y + 104)], (150, 48, 36))
    cv.rect(x + 62, y + 52, 84, 12, (120, 36, 28))
    # Oil slick ring around the hull.
    cv.line(x + 22, y + 108, x + 186, y + 108, (20, 20, 20), 3)
    cv.line(x + 30, y + 118, x + 178, y + 118, (20, 20, 20), 2)
    # Smoke.
    cv.disc(x + 158, y + 44, 12, (110, 110, 110))
    cv.disc(x + 172, y + 32, 9, (140, 140, 140))
    cv.text(x + 18, y + 122, "7,000 T DIESEL", 1, WHITE)


def icon_envoy(cv, x, y, w, h):
    """A flag at half-mast and a closing gate: an envoy sent home."""
    accent = ACCENTS[3]
    cv.rect(x, y, w, h, (236, 232, 244))
    # Gate posts and bars.
    cv.rect(x + 20, y + 30, 8, 96, INK)
    cv.rect(x + 172, y + 30, 8, 96, INK)
    for gx in range(x + 34, x + 168, 16):
        cv.line(gx, y + 34, gx, y + 124, INK, 3)
    cv.rect(x + 16, y + 28, 168, 8, INK)
    # Flag at half-mast on the left post.
    cv.line(x + 24, y + 30, x + 24, y + 8, INK, 3)
    cv.poly([(x + 26, y + 10), (x + 74, y + 20), (x + 26, y + 32)],
            (200, 40, 40))
    cv.disc(x + 40, y + 21, 4, WHITE)
    # A small suitcase leaving through the gate.
    cv.rect(x + 118, y + 102, 34, 22, (120, 84, 40))
    cv.rect(x + 128, y + 94, 14, 8, (120, 84, 40))
    cv.text(x + 18, y + 128, "48 HOURS", 1, accent)


def icon_golf(cv, x, y, w, h):
    """A green being dug up: flag, ball, and a bulldozer track."""
    accent = ACCENTS[4]
    cv.rect(x, y, w, h, (228, 240, 222))
    # Green.
    cv.disc(x + 100, y + 88, 46, (88, 168, 96))
    cv.rect(x, y + 88, w, 6, (88, 168, 96))
    # Flag and hole.
    cv.line(x + 100, y + 34, x + 100, y + 88, INK, 3)
    cv.poly([(x + 102, y + 36), (x + 146, y + 48), (x + 102, y + 60)],
            (200, 40, 40))
    cv.disc(x + 100, y + 88, 7, INK)
    # Ball rolling away.
    cv.disc(x + 52, y + 80, 9, WHITE)
    cv.ring(x + 52, y + 80, 9, INK, 2)
    # Dug-up turf: brown clods.
    for cx, cy, r in [(x + 138, y + 104, 12), (x + 162, y + 112, 10),
                      (x + 122, y + 118, 8)]:
        cv.disc(cx, cy, r, (120, 88, 52))
    cv.text(x + 18, y + 126, "18 COURSES", 1, accent)


ICONS = [icon_storm, icon_gaza, icon_tanker, icon_envoy, icon_golf]

STORIES = [
    ("UNITED STATES", "WEATHER",
     "THANKSGIVING STORM BATTERS EAST COAST",
     "GUSTS TO 70 MPH. MORE THAN 730,000 WITHOUT POWER. 400+ FLIGHTS "
     "CANCELLED. COASTAL TOWNS FLOOD."),
    ("GAZA", "WAR",
     "ISRAEL KILLS THIRD HAMAS LEADER IN THREE DAYS",
     "STRIKES KILL 10, INCLUDING A DEPUTY MINISTER. HAMAS SAYS IT WILL "
     "DISCUSS A RESPONSE."),
    ("SPAIN", "SEA",
     "TANKER CAPSIZES OFF IBIZA; SPAIN RACES TO STOP A SPILL",
     "ONE CREW MEMBER DEAD. 7,000 TONNES OF DIESEL ABOARD THE MED EMRE. "
     "NO POLLUTION SEEN SO FAR."),
    ("NORTH KOREA", "DIPLOMACY",
     "SWISS ENVOY ORDERED OUT AS DEADLINE FALLS TODAY",
     "PYONGYANG SHUTS THE SWISS OFFICE IN A ROW OVER SANCTIONS ON A "
     "CHILDREN'S CAMP."),
    ("CHINA", "CRACKDOWN",
     "GOLF COURSES SHUT IN DRIVE ON 'SPORT FOR MILLIONAIRES'",
     "AT LEAST 18 COURSES CLOSE IN NOVEMBER, TEN OF THEM IN BEIJING."),
]


def draw_story_band(cv, y, h, num, story):
    place, topic, headline, caption = story
    accent = ACCENTS[num - 1]
    x = 16
    cv.rect(x, y, W - 32, h, CARD)
    cv.rect(x, y, 6, h, accent)
    # Icon square.
    ix, iy, iw, ih = x + 18, y + 10, 196, h - 20
    cv.rect(ix - 2, iy - 2, iw + 4, ih + 4, accent)
    if num == 1:
        icon_storm(cv, ix, iy, iw, ih)
    else:
        ICONS[num - 1](cv, ix, iy, iw, ih)
    # Number badge.
    bx, by = x + 224, y + 12
    cv.disc(bx + 16, by + 16, 16, accent)
    cv.text(bx + 10, by + 7, str(num), 2, WHITE)
    # Kicker, headline, caption.
    tx = x + 268
    cv.text(tx, y + 14, place + "  -  " + topic, 2, accent)
    max_head = (W - 32 - 268 - 16) // 18
    lines = wrap(headline, max_head)
    hy = y + 44
    for ln in lines[:2]:
        cv.text(tx, hy, ln, 3, INK)
        hy += 3 * 8
    max_cap = (W - 32 - 268 - 16) // 12
    cy = hy + 6
    for ln in wrap(caption, max_cap)[:2]:
        cv.text(tx, cy, ln, 2, GREY)
        cy += 2 * 8


def main():
    cv = Canvas(W, H, PAPER)
    # Masthead.
    cv.rect(0, 0, W, 104, NAVY)
    cv.rect(0, 104, W, 6, GOLD)
    cv.text_center(16, "FRIDAY, 27 NOVEMBER 2026", 2, GOLD)
    cv.text_center(44, "THE DAY IN FIVE STORIES", 4, WHITE)
    # Hero story, taller band with the storm scene on the right.
    draw_story_band(cv, 122, 196, 1, STORIES[0])
    # Four more stories.
    y = 330
    for i, story in enumerate(STORIES[1:], start=2):
        draw_story_band(cv, y, 158, i, story)
        y += 166
    # Footer.
    cv.rect(0, 994, W, 30, NAVY2)
    cv.text_center(1002, "SOURCES: REUTERS, AP, AFP, CNN, BBC  -  27 NOVEMBER 2026",
                   2, (200, 205, 215))

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    write_png(os.path.join(out_dir, "entry.png"), cv)


if __name__ == "__main__":
    main()
