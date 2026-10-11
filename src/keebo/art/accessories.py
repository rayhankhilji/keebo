"""Wearables. Each slot (hat, face, neck, back) draws relative to the
:class:`~keebo.art.character.Geometry` of the current frame, so every
accessory follows Keebo through squash, lean and bounce automatically.

To add one: write a function below and register it in the matching dict.
"""
from __future__ import annotations

import math
from typing import Callable, Dict

from .canvas import Canvas
from .palette import (
    COCOA,
    CORAL,
    DEEP,
    EMBER,
    FOG,
    GRAPE,
    INK,
    MINT,
    RAINBOW,
    RUBY,
    SKY,
    SLATE,
    SNOW,
    SUN,
    TEAL,
)


def _outlined(draw_fn: Callable[[Canvas], None]) -> Canvas:
    layer = Canvas()
    draw_fn(layer)
    layer.outline(INK)
    return layer


# ---------------------------------------------------------------- hats

def hardhat(c: Canvas, p, g) -> None:
    hx, hy = g.head
    def d(l: Canvas) -> None:
        l.rrect(hx - 6, hy - 4, 13, 5, SUN, r=2)
        l.rect(hx - 8, hy, 17, 2, SUN)
        l.vline(hx, hy - 4, hy, EMBER)
        l.px(hx - 3, hy - 3, SNOW)
    c.blit(_outlined(d))


def partyhat(c: Canvas, p, g) -> None:
    hx, hy = g.head
    def d(l: Canvas) -> None:
        l.poly([(hx - 5, hy + 1), (hx + 5, hy + 1), (hx, hy - 10)], GRAPE)
        for i, y in enumerate(range(hy - 7, hy + 1, 3)):
            l.hline(hx - 1 - i, hx + 1 + i, y, SUN)
        l.disc(hx, hy - 11, 1, CORAL)
    c.blit(_outlined(d))


def nightcap(c: Canvas, p, g) -> None:
    hx, hy = g.head
    droop = int(round(math.sin(p.t * 2 * math.pi) * 1))
    def d(l: Canvas) -> None:
        l.rect(hx - 7, hy - 1, 15, 3, SNOW)
        l.poly([(hx - 6, hy - 1), (hx + 6, hy - 1), (hx + 9, hy - 6 + droop), (hx + 1, hy - 7)], SKY)
        l.hline(hx - 2, hx + 3, hy - 4, SNOW)
        l.disc(hx + 10, hy - 5 + droop, 1.5, SNOW)
    c.blit(_outlined(d))


def beanie(c: Canvas, p, g) -> None:
    hx, hy = g.head
    def d(l: Canvas) -> None:
        l.rrect(hx - 7, hy - 5, 15, 6, RUBY, r=3)
        l.rect(hx - 8, hy, 17, 2, CORAL)
        for x in range(hx - 6, hx + 7, 2):
            l.px(x, hy, RUBY)
        l.disc(hx, hy - 6, 1.5, SNOW)
    c.blit(_outlined(d))


def crown(c: Canvas, p, g) -> None:
    hx, hy = g.head
    def d(l: Canvas) -> None:
        l.rect(hx - 5, hy - 3, 11, 4, SUN)
        for x in (hx - 5, hx, hx + 5):
            l.rect(x, hy - 5, 1, 2, SUN)
            l.px(x, hy - 6, SUN)
        l.px(hx - 3, hy - 1, RUBY)
        l.px(hx, hy - 1, SKY)
        l.px(hx + 3, hy - 1, MINT)
    c.blit(_outlined(d))
    # orbiting sparkle
    a = p.t * 2 * math.pi
    sx = g.cx + int(math.cos(a) * (g.right - g.left) * 0.7)
    sy = g.top + 6 + int(math.sin(a) * 4)
    c.sprite(sx - 1, sy - 1, [".#.", "#s#", ".#."], {"#": SUN, "s": SNOW})


def headphones(c: Canvas, p, g) -> None:
    def d(l: Canvas) -> None:
        mid = (g.left + g.right) // 2
        r = (g.right - g.left) // 2 + 1
        for i in range(0, 181, 6):
            a = math.radians(180 + i)
            l.px(mid + math.cos(a) * r, g.top + 4 + math.sin(a) * 7, SLATE)
        l.rrect(g.left - 2, g.top + 3, 3, 6, CORAL, r=1)
        l.rrect(g.right, g.top + 3, 3, 6, CORAL, r=1)
    c.blit(_outlined(d))


def tophat(c: Canvas, p, g) -> None:
    hx, hy = g.head
    def d(l: Canvas) -> None:
        l.rect(hx - 4, hy - 8, 9, 8, SLATE)
        l.rect(hx - 4, hy - 3, 9, 2, RUBY)
        l.rect(hx - 7, hy, 15, 2, SLATE)
    c.blit(_outlined(d))


def wizard(c: Canvas, p, g) -> None:
    hx, hy = g.head
    def d(l: Canvas) -> None:
        l.poly([(hx - 7, hy + 1), (hx + 7, hy + 1), (hx + 3, hy - 12)], GRAPE)
        l.px(hx - 1, hy - 4, SUN)
        l.px(hx + 2, hy - 7, SUN)
        l.px(hx + 1, hy - 2, SNOW)
    c.blit(_outlined(d))


HATS: Dict[str, Callable] = {
    "hardhat": hardhat, "partyhat": partyhat, "nightcap": nightcap,
    "beanie": beanie, "crown": crown, "headphones": headphones,
    "tophat": tophat, "wizard": wizard,
}


def draw_hat(c: Canvas, p, g) -> None:
    name = p.hat or ("crown" if p.form == 4 else None)
    if name in HATS:
        HATS[name](c, p, g)


# ---------------------------------------------------------------- face

def glasses(c: Canvas, p, g) -> None:
    (lx, ly), (rx, _) = g.extra["eye_l"], g.extra["eye_r"]
    for x in (lx, rx):
        c.box(x - 2, ly - 1, 6, 5, INK)
    c.hline(lx + 4, rx - 3, ly, INK)


def shades(c: Canvas, p, g) -> None:
    (lx, ly), (rx, _) = g.extra["eye_l"], g.extra["eye_r"]
    c.rect(lx - 2, ly, rx - lx + 6, 1, INK)
    c.rect(lx - 2, ly + 1, 5, 2, INK)
    c.rect(rx - 1, ly + 1, 5, 2, INK)
    c.px(lx - 1, ly + 1, SNOW)
    c.px(rx, ly + 1, SNOW)


def goggles(c: Canvas, p, g) -> None:
    (lx, ly), (rx, _) = g.extra["eye_l"], g.extra["eye_r"]
    c.hline(g.left, g.right, ly + 1, COCOA)
    for x in (lx, rx):
        c.rect(x - 2, ly - 1, 6, 5, INK)
        c.rect(x - 1, ly, 4, 3, SKY)
        c.px(x - 1, ly, SNOW)


def bandage(c: Canvas, p, g) -> None:
    x, y = g.right - 6, g.top + 2
    c.sprite(x, y, [".s..", "sxs.", ".sxs", "..s."], {"s": SNOW, "x": FOG})


def monocle(c: Canvas, p, g) -> None:
    rx, ry = g.extra["eye_r"]
    c.ring(rx + 1, ry + 1, 3, SUN)
    c.line(rx + 3, ry + 4, rx + 4, ry + 9, SUN)


FACE: Dict[str, Callable] = {
    "glasses": glasses, "shades": shades, "goggles": goggles,
    "bandage": bandage, "monocle": monocle,
}


def draw_face(c: Canvas, p, g) -> None:
    if p.face_acc in FACE and "eye_l" in g.extra:
        FACE[p.face_acc](c, p, g)


# ---------------------------------------------------------------- neck

def scarf(c: Canvas, p, g) -> None:
    y = g.bottom - 4
    flap = int(p.t * 8) % 2
    def d(l: Canvas) -> None:
        l.rect(g.left + 1, y, g.right - g.left - 1, 2, RUBY)
        l.rect(g.right - 3, y + 2, 3, 3 + flap, RUBY)
        l.px(g.right - 2, y + 4 + flap, CORAL)
    c.blit(_outlined(d))


def bowtie(c: Canvas, p, g) -> None:
    x, y = g.cx - 3, g.bottom - 4
    c.sprite(x, y, ["#..#.#", "##.###", "#..#.#"][:3], {"#": CORAL})
    c.sprite(x, y, ["##.###", "#####", "##.###"], {"#": CORAL})
    c.rect(x + 2, y + 1, 2, 1, RUBY)


NECK: Dict[str, Callable] = {"scarf": scarf, "bowtie": bowtie}


def draw_neck(c: Canvas, p, g) -> None:
    if p.neck in NECK:
        NECK[p.neck](c, p, g)


# ---------------------------------------------------------------- back

def cape(c: Canvas, p, g) -> None:
    wave = math.sin(p.t * 2 * math.pi * 2)
    def d(l: Canvas) -> None:
        top = g.top + 5
        l.poly([(g.left + 2, top), (g.right - 2, top),
                (g.right + 4 + wave * 2, g.bottom + 2), (g.left - 4 - wave * 2, g.bottom + 2)], RUBY)
    c.blit(_outlined(d))


def wings(c: Canvas, p, g) -> None:
    flap = int(p.t * 6) % 2
    def d(l: Canvas) -> None:
        y = g.top + 4 - flap * 2
        l.sprite(g.left - 7, y, ["...###", ".#####", "######", ".####."], {"#": SNOW})
        l.sprite(g.right + 2, y, ["###...", "#####.", "######", ".####."], {"#": SNOW})
    c.blit(_outlined(d))


BACK: Dict[str, Callable] = {"cape": cape, "wings": wings}


def draw_back(c: Canvas, p, g) -> None:
    if p.back in BACK:
        BACK[p.back](c, p, g)


SLOTS = {"hat": HATS, "face": FACE, "neck": NECK, "back": BACK}
_unused = (DEEP, EMBER, FOG, RAINBOW, TEAL)
