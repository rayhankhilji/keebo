"""Reusable scene pieces: rooms, furniture, gadgets and particle effects."""
from __future__ import annotations

import math
import random
from typing import Optional, Sequence

from .canvas import Canvas
from .palette import (
    CLEAR,
    COCOA,
    CORAL,
    DEEP,
    EMBER,
    FOG,
    GRAPE,
    INK,
    MINT,
    NIGHT,
    RAINBOW,
    RUBY,
    SKY,
    SLATE,
    SNOW,
    SUN,
    TEAL,
    VOID,
)

FLOOR = 51


def _hash(s: str) -> int:
    h = 2166136261
    for ch in s:
        h = ((h ^ ord(ch)) * 16777619) & 0xFFFFFFFF
    return h


# ---------------------------------------------------------------- rooms

def room(t: float = 0.0, stars: bool = True, window: bool = True, night: bool = False) -> Canvas:
    """The default backdrop: a cosy dark room with a floor and a window."""
    c = Canvas(fill=VOID)
    if window:
        c.rect(4, 6, 14, 12, INK)
        c.rect(5, 7, 12, 10, NIGHT if not night else VOID)
        c.vline(10, 7, 16, INK)
        c.hline(5, 16, 11, INK)
        if stars:
            rnd = random.Random(7)
            for i in range(5):
                x, y = rnd.randint(5, 16), rnd.randint(7, 16)
                if x in (10,) or y == 11:
                    continue
                if (int(t * 6) + i) % 5:
                    c.px(x, y, FOG if i % 2 else SNOW)
        if night:
            c.sprite(12, 8, [".##", "#..", "#..", ".##"], {"#": SUN})
    c.rect(0, FLOOR, 64, 64 - FLOOR, NIGHT)
    c.hline(0, 63, FLOOR, SLATE)
    for x in range(3, 64, 9):
        c.px(x, FLOOR + 5, INK)
        c.px(x + 4, FLOOR + 9, INK)
    return c


def shelf(c: Canvas, projects: Sequence[dict], x: int = 40, y: int = 12) -> None:
    """A wall shelf showing one trophy per finished project (visual history)."""
    c.rect(x, y, 21, 2, COCOA)
    c.hline(x, x + 20, y + 2, INK)
    for i, proj in enumerate(list(projects)[-5:]):
        colour = RAINBOW[_hash(proj.get("name", "?")) % len(RAINBOW)]
        tx = x + 1 + i * 4
        kind = proj.get("trophy", "cup")
        if kind == "flag":
            c.vline(tx, y - 6, y - 1, FOG)
            c.rect(tx + 1, y - 6, 2, 2, colour)
        elif kind == "star":
            c.sprite(tx, y - 4, [".#.", "###", "#.#"], {"#": colour})
            c.vline(tx + 1, y - 1, y - 1, FOG)
        else:
            c.sprite(tx, y - 5, ["###", "###", ".#.", "###"], {"#": colour})
            c.px(tx, y - 5, SNOW)


def xp_bar(c: Canvas, frac: float, level: int) -> None:
    """A 1px XP strip along the bottom edge plus a tiny level badge."""
    frac = max(0.0, min(1.0, frac))
    c.hline(0, 63, 63, INK)
    n = int(round(64 * frac))
    if n:
        c.hline(0, n - 1, 63, SUN)
    label = "LV%d" % level
    c.text(2, 57, label, FOG)


# ---------------------------------------------------------------- furniture

def desk(c: Canvas, y: int = 44) -> None:
    c.rect(4, y, 56, 3, COCOA)
    c.hline(4, 59, y, SUN if False else COCOA)
    c.hline(4, 59, y + 3, INK)
    c.rect(7, y + 3, 2, FLOOR - y - 3, COCOA)
    c.rect(55, y + 3, 2, FLOOR - y - 3, COCOA)


def laptop(c: Canvas, x: int, y: int, t: float, glow: bool = True, logo: int = MINT) -> None:
    """Mini MacBook from behind: lid facing us, base on the desk at row ``y``."""
    c.rect(x, y - 13, 22, 13, FOG)            # lid
    c.box(x - 1, y - 14, 24, 15, INK)
    c.hline(x, x + 21, y - 13, SNOW)
    c.rect(x - 3, y, 28, 2, FOG)              # base
    c.hline(x - 3, x + 24, y + 2, INK)
    c.px(x - 4, y, INK)
    c.px(x + 25, y, INK)
    # little keycap logo, breathing
    on = glow and (int(t * 4) % 4 != 0)
    c.sprite(x + 9, y - 9, [".##.", "####", "####", ".##."], {"#": logo if on else SNOW})
    if glow:
        # screen spill on the edges
        c.px(x - 1, y - 12, SKY)
        c.px(x + 22, y - 12, SKY)


def laptop_side(c: Canvas, x: int, y: int, t: float, code: bool = True) -> None:
    """Mini MacBook in profile: base on the desk at row ``y``, lid opening to the right.

    The screen faces left (towards Keebo); its glow spills on the desk and the
    lid edge, and tiny code tokens float up while ``code`` is set."""
    c.rect(x, y - 2, 17, 2, FOG)                 # base
    c.hline(x, x + 16, y - 3, SNOW)
    c.hline(x - 1, x + 17, y, INK)
    for k in range(4):                           # keys catching screen light
        c.px(x + 2 + k * 3, y - 3, SLATE if int(t * 8 + k) % 3 else SKY)
    for i in range(15):                          # lid, leaning back
        lx = x + 16 + i // 5
        c.px(lx, y - 3 - i, FOG)
        c.px(lx + 1, y - 3 - i, INK)
        c.px(lx - 1, y - 3 - i, SKY if i % 4 else MINT)
    if code:
        tokens = ["</>", "{}", "=>", "()", "#"]
        k = int(t * 5) % len(tokens)
        rise = int((t * 5 % 1) * 6)
        c.text(x + 4, y - 14 - rise, tokens[k], MINT if k % 2 else SKY)


def monitor(c: Canvas, x: int, y: int, w: int, h: int, screen: int = VOID) -> None:
    c.rect(x, y, w, h, INK)
    c.rect(x + 1, y + 1, w - 2, h - 2, screen)
    c.rect(x + w // 2 - 1, y + h, 3, 2, SLATE)
    c.rect(x + w // 2 - 4, y + h + 2, 9, 1, SLATE)


def tv(c: Canvas, x: int, y: int, t: float) -> None:
    c.rect(x, y, 26, 18, INK)
    c.rect(x + 1, y + 1, 24, 16, SKY)
    # animated "video": hills + bouncing sun
    sx = x + 4 + int((t * 18) % 18)
    c.disc(sx, y + 6, 2, SUN)
    for i in range(24):
        hy = y + 12 + int(math.sin((i + t * 20) / 3) * 1.5)
        c.vline(x + 1 + i, hy, y + 16, MINT)
    c.px(x + 23, y + 2, RUBY)
    c.rect(x + 11, y + 18, 4, 2, SLATE)


# ---------------------------------------------------------------- effects

def bubble(c: Canvas, x: int, y: int, w: int, h: int, tail_x: int, thought: bool = False) -> None:
    c.rrect(x, y, w, h, SNOW, r=2)
    c.hline(x + 2, x + w - 3, y - 1, INK)
    c.hline(x + 2, x + w - 3, y + h, INK)
    c.vline(x - 1, y + 2, y + h - 3, INK)
    c.vline(x + w, y + 2, y + h - 3, INK)
    for (px_, py_) in ((x, y + 1), (x + 1, y), (x + w - 1, y + 1), (x + w - 2, y),
                       (x, y + h - 2), (x + 1, y + h - 1), (x + w - 1, y + h - 2), (x + w - 2, y + h - 1)):
        c.px(px_, py_, INK)
    if thought:
        c.disc(tail_x, y + h + 3, 1, SNOW)
        c.px(tail_x - 1, y + h + 6, SNOW)
    else:
        c.sprite(tail_x, y + h, ["ss#", "s#.", "#.."], {"s": SNOW, "#": INK})


def zzz(c: Canvas, x: int, y: int, t: float) -> None:
    for i in range(3):
        phase = (t + i / 3.0) % 1.0
        zx = x + int(phase * 8) + i
        zy = y - int(phase * 12)
        if phase < 0.9:
            size = 1 + int(phase * 2.5)
            col = SNOW if phase < 0.6 else FOG
            if size == 1:
                c.sprite(zx, zy, ["##", ".#", "##"][:1] + ["#."], {"#": col})
            else:
                c.text(zx, zy, "Z", col)


def sparkle(c: Canvas, x: int, y: int, phase: int, colour: int = SUN) -> None:
    shapes = [
        ["#"],
        [".#.", "#s#", ".#."],
        ["..#..", "..#..", "##s##", "..#..", "..#.."],
        [".#.", "#.#", ".#."],
    ]
    rows = shapes[phase % len(shapes)]
    o = len(rows) // 2
    c.sprite(x - o, y - o, rows, {"#": colour, "s": SNOW})


def confetti(c: Canvas, t: float, seed: int = 3, n: int = 26, top: int = 0) -> None:
    rnd = random.Random(seed)
    for i in range(n):
        x0 = rnd.randint(0, 63)
        speed = rnd.uniform(18, 34)
        y = (top + rnd.randint(-60, 0) + t * speed * 2.2) % 70 - 4
        x = x0 + math.sin(t * 6 + i) * 2
        col = RAINBOW[i % len(RAINBOW)]
        if i % 3 == 0:
            c.rect(int(x), int(y), 2, 1, col)
        else:
            c.px(x, y, col)


def fire(c: Canvas, x: int, y: int, t: float, size: int = 1) -> None:
    """A flickering pixel flame with its base at (x, y)."""
    f = int(t * 10) % 3
    shapes = [
        ["..#..", ".###.", ".#o#.", "#ooo#", "#oyo#", ".###."],
        [".#...", "..#..", ".###.", "#ooo#", "#oyo#", ".###."],
        ["...#.", "..#..", ".#o#.", "#ooo#", "#oyy#", ".###."],
    ]
    rows = shapes[f]
    if size > 1:
        big = []
        for r in rows:
            row = "".join(ch * 2 for ch in r)
            big += [row, row]
        rows = big
    c.sprite(x - len(rows[0]) // 2, y - len(rows) + 1, rows, {"#": RUBY, "o": EMBER, "y": SUN})


def smoke(c: Canvas, x: int, y: int, t: float) -> None:
    for i in range(3):
        ph = (t * 1.5 + i / 3) % 1
        c.disc(x + math.sin(ph * 6 + i) * 2, y - ph * 14, 1 + ph * 1.5, SLATE if ph < 0.6 else INK)


def steam(c: Canvas, x: int, y: int, t: float) -> None:
    for i in range(2):
        ph = (t * 2 + i / 2) % 1
        c.disc(x + (i * 2 - 1) * (2 + ph * 3), y - ph * 6, 1 + ph, SNOW if ph < 0.5 else FOG)


def note(c: Canvas, x: int, y: int, colour: int, kind: int = 0) -> None:
    if kind % 2 == 0:
        c.sprite(x, y, ["..##", "..#.", "..#.", "###.", "##.."], {"#": colour})
    else:
        c.sprite(x, y, [".####", ".#..#", ".#..#", "##.##", "#..#."][:5], {"#": colour})


def speed_lines(c: Canvas, t: float, y0: int = 20, y1: int = 48) -> None:
    rnd = random.Random(int(t * 20))
    for _ in range(6):
        y = rnd.randint(y0, y1)
        x = rnd.choice([rnd.randint(1, 10), rnd.randint(52, 60)])
        c.hline(x, x + rnd.randint(2, 4), y, FOG)


def question(c: Canvas, x: int, y: int, colour: int = SUN, big: bool = True) -> None:
    rows = [".###.", "#...#", "...#.", "..#..", ".....", "..#.."] if big else ["##.", "..#", ".#.", "...", ".#."]
    lay = Canvas()
    lay.sprite(x, y, rows, {"#": colour})
    lay.outline(INK)
    c.blit(lay)


def exclaim(c: Canvas, x: int, y: int, colour: int = RUBY) -> None:
    lay = Canvas()
    lay.sprite(x, y, ["##", "##", "##", "##", "..", "##"], {"#": colour})
    lay.outline(INK)
    c.blit(lay)


def burst(c: Canvas, cx: int, cy: int, r: float, colour: int = SUN, rays: int = 8) -> None:
    for i in range(rays):
        a = 2 * math.pi * i / rays
        x0, y0 = cx + math.cos(a) * r, cy + math.sin(a) * r
        x1, y1 = cx + math.cos(a) * (r + 3), cy + math.sin(a) * (r + 3)
        c.line(x0, y0, x1, y1, colour)


def trophy(c: Canvas, x: int, y: int, shine: bool = False) -> None:
    lay = Canvas()
    lay.sprite(x, y, [
        "#.#####.#",
        "#.#####.#",
        ".#######.",
        "..#####..",
        "...###...",
        "....#....",
        "...###...",
        "..#####..",
    ], {"#": SUN})
    lay.outline(INK)
    c.blit(lay)
    if shine:
        c.px(x + 3, y + 1, SNOW)
        c.px(x + 3, y + 2, SNOW)


def storm_cloud(c: Canvas, x: int, y: int, t: float) -> None:
    lay = Canvas()
    lay.disc(x + 3, y + 3, 3, SLATE)
    lay.disc(x + 8, y + 2, 4, SLATE)
    lay.disc(x + 13, y + 3, 3, SLATE)
    lay.rect(x + 2, y + 3, 13, 4, SLATE)
    lay.outline(INK)
    c.blit(lay)
    if int(t * 8) % 4 == 0:
        c.sprite(x + 7, y + 7, [".#", "#.", "##", ".#", "#."], {"#": SUN})
    for i in range(3):
        ry = y + 8 + int((t * 30 + i * 4) % 8)
        c.px(x + 4 + i * 4, ry, SKY)


def brick(c: Canvas, x: int, y: int, colour: int = EMBER) -> None:
    c.rect(x, y, 6, 3, colour)
    c.hline(x, x + 5, y, SUN if colour == EMBER else SNOW)
    c.box(x - 1, y - 1, 8, 5, INK)


def hammer(c: Canvas, x: int, y: int, angle: float) -> None:
    a = math.radians(angle)
    hx, hy = x + math.cos(a) * 6, y + math.sin(a) * 6
    c.line(x, y, hx, hy, COCOA)
    px, py = -math.sin(a), math.cos(a)
    c.line(hx - px * 2, hy - py * 2, hx + px * 2, hy + py * 2, FOG)
    ox, oy = math.cos(a), math.sin(a)
    c.line(hx - px * 2 + ox, hy - py * 2 + oy, hx + px * 2 + ox, hy + py * 2 + oy, SLATE)


_unused = (CLEAR, CORAL, DEEP, GRAPE, TEAL, Optional)
