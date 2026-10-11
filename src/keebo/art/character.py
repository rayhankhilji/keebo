"""Keebo's creatures: a parametric pixel-art rig with swappable skins.

Two skins share one rig: **Inky**, a little octopus, and **Axo**, an
axolotl. Instead of hand-drawing every frame, Keebo is drawn from a :class:`Pose`
(squash, lean, eyes, mouth, arm angles, ...). Animations are just
functions that produce a sequence of poses, which keeps every state in the
same style and makes in-betweens free.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from typing import Dict, Optional, Tuple

from .canvas import Canvas
from .palette import (
    BLUSH,
    CLEAR,
    CORAL,
    FOG,
    INK,
    LILAC,
    LILAC_D,
    LILAC_L,
    PINK,
    PINK_D,
    PINK_L,
    RAINBOW,
    RUBY,
    SKY,
    SNOW,
    SUN,
)

# Body size per evolution form: (width, height)
FORM_SIZES = {0: (18, 14), 1: (24, 18), 2: (24, 18), 3: (26, 19), 4: (26, 19)}
FORM_NAMES = {0: "Baby", 1: "Buddy", 2: "Clicky", 3: "Mecha", 4: "Legend"}

#: Skin name -> (body, shade, highlight)
SKINS: Dict[str, Tuple[int, int, int]] = {
    "inky": (LILAC, LILAC_D, LILAC_L),
    "axo": (PINK, PINK_D, PINK_L),
}
DEFAULT_SKIN = "inky"

ARMS_DOWN = (55.0, 55.0)
ARMS_OUT = (10.0, 10.0)
ARMS_UP = (-65.0, -65.0)
ARMS_TYPE = (125.0, 125.0)


@dataclass(frozen=True)
class Pose:
    """Everything needed to draw one frame of Keebo."""

    x: float = 32            # feet centre
    y: float = 50            # feet baseline (row the feet sit on)
    squash: float = 1.0      # <1 squashes down, >1 stretches up
    lean: float = 0.0        # px the top of the body shifts sideways
    eyes: str = "open"       # see EYES
    look: Tuple[int, int] = (0, 0)
    mouth: str = "smile"     # see MOUTHS
    arms: Tuple[float, float] = ARMS_DOWN  # degrees, 0 = out, 90 = down, -90 = up
    arms_front: bool = False  # draw arms over the body (typing, holding)
    feet: Tuple[int, int] = (0, 0)          # lift of each foot in px
    blush: bool = False
    sweat: int = 0           # 0 none, 1-2 drop phase
    form: int = 1
    tint: Optional[int] = None      # flood body with one colour (evolve flash)
    hat: Optional[str] = None
    face_acc: Optional[str] = None
    neck: Optional[str] = None
    back: Optional[str] = None
    t: float = 0.0           # animation clock, drives antenna sway and RGB
    flip: bool = False
    lying: bool = False      # flattened into a pancake on the floor
    skin: str = DEFAULT_SKIN

    def but(self, **kw) -> "Pose":
        return replace(self, **kw)


@dataclass
class Geometry:
    """Anchor points of the frame just drawn, for props and effects."""

    cx: int
    top: int
    bottom: int
    left: int
    right: int
    eye_y: int
    mouth_y: int
    hand_l: Tuple[int, int]
    hand_r: Tuple[int, int]
    head: Tuple[int, int]  # top of the head, where hats sit
    eye_gap: int = 4
    extra: Dict[str, Tuple[int, int]] = field(default_factory=dict)


def _body_size(p: Pose) -> Tuple[int, int]:
    w, h = FORM_SIZES.get(p.form, FORM_SIZES[1])
    sy = 0.5 if p.lying else p.squash
    sx = 1.0 + (1.0 - sy) * 0.7
    return max(8, int(round(w * sx))), max(7, int(round(h * sy)))


def _colours(p: Pose) -> Tuple[int, int, int]:
    if p.tint is not None:
        return p.tint, p.tint, p.tint
    return SKINS.get(p.skin, SKINS[DEFAULT_SKIN])


def _round_inset(row: int, rows: int, radius: int) -> int:
    """Inset of a row inside a box with rounded corners of ``radius``."""
    d = min(row, rows - 1 - row)
    if d >= radius:
        return 0
    return radius - int(round(math.sqrt(radius * radius - (radius - d - 0.5) ** 2)))


def _body_layer(p: Pose) -> Tuple[Canvas, Geometry]:
    layer = Canvas()
    w, h = _body_size(p)
    body, shade, light = _colours(p)
    axo = p.skin == "axo"
    cx = int(round(p.x))
    if p.lying:
        legs = 1
    elif axo:
        legs = 2 if p.form == 0 else 3
    else:
        legs = 4 if p.form == 0 else 6
    bottom = int(round(p.y)) - legs
    top = bottom - h + 1
    left = cx - w // 2
    head_h = int(round(h * 0.72)) if axo else h
    torso_in = max(2, w // 5)

    def shear(row: int) -> int:
        return int(round(p.lean * (1.0 - row / max(1, h - 1))))

    def inset(row: int) -> int:
        if not axo:
            dome = int(h * 0.6)
            if row < dome:
                r = w / 2.0
                dy = (dome - row - 0.5) / dome
                return int(round(r - r * math.sqrt(max(0.0, 1 - dy * dy))))
            return 1 if row == h - 1 else 0
        if row < head_h:
            return _round_inset(row, head_h, 5 if p.form else 4)
        return torso_in + (1 if row == h - 1 else 0)

    if axo:
        # tail, behind the body
        wag = int(round(1.5 * math.sin(p.t * 4 * math.pi)))
        tx = left + w - torso_in - 1
        ty = bottom - 2 if not p.lying else bottom
        for i in range(8):
            th = max(1, 3 - i // 3)
            layer.rect(tx + i, ty - th // 2 + int(round(wag * i / 7)), 1, th, body if i < 6 else shade)
        # gills
        n = 3
        for side in (-1, 1):
            ex = left - 1 if side < 0 else left + w
            for k in range(n):
                wob = int(round(math.sin(p.t * 2 * math.pi + k * 1.7)))
                reach = 3 + (1 if k == 1 else 0) + (1 if p.form >= 3 else 0) - (1 if p.form == 0 else 0)
                sy = top + 2 + k * 3
                dy = (k - 1) * 2 + (2 if p.lying else 0) - 1
                gx, gy = ex + side * reach, sy + dy + wob
                layer.line(ex - side * 2, sy + 1, gx, gy, shade)
                layer.rect(gx - (side < 0), gy - 1, 2, 2, shade)

    for row in range(h):
        i = inset(row)
        colour = shade if (row == h - 1 and not p.lying) else body
        layer.rect(left + i + shear(row), top + row, w - 2 * i, 1, colour)

    if p.tint is None:
        gx = left + 4 + shear(2)
        layer.hline(gx, gx + 2, top + 2, light)
        layer.px(gx - 1, top + 3, light)
        layer.px(gx, top + 2, SNOW)
        if axo and not p.lying and h - head_h > 3:
            bw = w - 2 * torso_in - 6
            layer.rrect(cx - bw // 2 + shear(head_h + 1), top + head_h + 1, bw, h - head_h - 2, light, 1)
        if p.form >= 2:
            for sx, sy in ((-6, 3), (5, 2), (7, 5), (-3, 1)):
                layer.px(cx + sx + shear(sy), top + sy, shade)
        if p.form >= 4:
            layer.hline(left + 2 + shear(h - 2), left + w - 3 + shear(h - 2), top + h - 2, SUN)

    if axo and not p.lying:
        for i, fx in enumerate((cx - w // 4 - 1, cx + w // 4 - 1)):
            lift = p.feet[i]
            layer.rect(fx, bottom + 1 - lift, 3, legs, shade)
    elif not axo:
        n = 3 if p.form == 0 else 4
        span = w - 6
        for i in range(n):
            bx = left + 3 + int(round(i * span / (n - 1))) - 1
            out = -1 if i < n / 2 else 1
            if p.lying:
                layer.rect(bx + out * 2, bottom + 1, 3, 1, body)
                continue
            lift = p.feet[0 if i < n / 2 else 1]
            length = max(2, legs - lift)
            sway = 1.3 * math.sin(p.t * 2 * math.pi + i * 1.3)
            for j in range(length):
                ox = int(round(sway * j / length))
                last = j == length - 1
                layer.rect(bx + ox + (out if last else 0), bottom + 1 + j - lift, 3 if not last else 2, 1,
                           body if not last else shade)

    top_shift = shear(0)
    if axo:
        eye_y = top + max(2, head_h // 2 - 2)
    else:
        eye_y = top + max(2, int(round(h * 0.42)) - 1)
    hand_y = top + head_h + 1 if axo else top + int(round(h * 0.62))
    hand_x = torso_in if axo else 0
    geo = Geometry(
        cx=cx + top_shift // 2, top=top, bottom=bottom, left=left, right=left + w - 1,
        eye_y=eye_y, mouth_y=eye_y + (3 if p.form == 0 else 4),
        hand_l=(left + hand_x, hand_y), hand_r=(left + w - 1 - hand_x, hand_y),
        head=(cx + top_shift, top - 1),
        eye_gap=(4 if p.form == 0 else 5) if axo else (3 if p.form == 0 else 4),
    )
    return layer, geo


def _stem(c: Canvas, p: Pose, g: Geometry) -> None:
    if p.form == 3:
        # mecha antenna light
        on = int(p.t * 4) % 2 == 0
        hx, hy = g.head
        c.vline(hx + 3, hy - 3, hy + 1, FOG)
        c.px(hx + 3, hy - 4, RUBY if on else SUN)


EYES = (
    "open", "closed", "happy", "sleepy", "x", "spiral", "wide", "star",
    "angry", "focus", "heart", "sad", "squint", "uneven", "shades",
)
MOUTHS = (
    "smile", "grin", "o", "flat", "wavy", "frown", "teeth", "cat", "yell",
    "tongue", "smirk", "none", "chew",
)


def _eye(c: Canvas, x: int, y: int, style: str, look: Tuple[int, int], right: bool, t: float) -> None:
    lx, ly = look
    if style == "open":
        c.rect(x + lx, y + ly, 2, 3, INK)
        c.px(x + lx, y + ly, SNOW)
    elif style == "wide":
        c.rect(x - 1 + lx, y - 1 + ly, 3, 4, INK)
        c.px(x - 1 + lx, y - 1 + ly, SNOW)
        c.px(x + lx, y - 1 + ly, SNOW)
    elif style == "closed":
        c.hline(x - 1, x + 1, y + 2, INK)
    elif style == "sleepy":
        c.hline(x - 1, x + 1, y + 2, INK)
        c.px(x + (1 if right else -1), y + 1, INK)
    elif style == "happy":
        c.sprite(x - 1, y, [".#.", "#.#"], {"#": INK})
    elif style == "x":
        c.sprite(x - 1, y, ["#.#", ".#.", "#.#"], {"#": INK})
    elif style == "spiral":
        frames = [["###", "#.#", "#.."], ["###", "..#", "###"], ["..#", "#.#", "###"], ["###", "#..", "###"]]
        c.sprite(x - 1, y, frames[(int(t * 8) + (2 if right else 0)) % 4], {"#": INK})
    elif style == "star":
        c.sprite(x - 1, y - 1, [".#.", "###", ".#.", "#.#"], {"#": SUN})
        c.px(x, y, SNOW)
    elif style == "angry":
        c.rect(x + lx, y + 1 + ly, 2, 2, INK)
        if right:
            c.line(x - 1, y - 1, x + 2, y + 0, INK)
        else:
            c.line(x - 1, y + 0, x + 2, y - 1, INK)
    elif style == "focus":
        c.rect(x + lx, y + 1 + ly, 2, 2, INK)
        c.hline(x - 1, x + 2, y - 1, INK)
    elif style == "heart":
        c.sprite(x - 1, y, ["#.#", "###", ".#."], {"#": CORAL})
    elif style == "sad":
        c.rect(x + lx, y + 1 + ly, 2, 2, INK)
        if right:
            c.line(x - 1, y - 1, x + 2, y + 0, INK)
            c.line(x - 1, y - 1, x + 2, y - 1, CLEAR)
        else:
            c.line(x - 1, y, x + 2, y - 1, INK)
    elif style == "squint":
        c.sprite(x - 1, y + 1, (["##.", "..#"] if not right else [".##", "#.."]), {"#": INK})
    elif style == "uneven":
        if right:
            c.rect(x - 1, y - 1, 3, 4, INK)
            c.px(x - 1, y - 1, SNOW)
        else:
            c.rect(x, y + 1, 2, 2, INK)
    elif style == "shades":
        pass  # drawn as a face accessory
    else:
        c.rect(x, y, 2, 3, INK)


def _mouth(c: Canvas, x: int, y: int, style: str, t: float) -> None:
    if style == "smile":
        c.sprite(x - 1, y, ["#.#", ".#."], {"#": INK})
    elif style == "grin":
        c.sprite(x - 3, y, ["######", "#cccc#", ".####."], {"#": INK, "c": CORAL})
    elif style == "o":
        c.sprite(x - 1, y, [".#.", "#c#", ".#."], {"#": INK, "c": CORAL})
    elif style == "flat":
        c.hline(x - 2, x + 1, y + 1, INK)
    elif style == "wavy":
        c.sprite(x - 3, y, [".#...#", "#.#.#.", "...#.."][:2], {"#": INK})
    elif style == "frown":
        c.sprite(x - 2, y, [".##.", "#..#"], {"#": INK})
    elif style == "teeth":
        c.sprite(x - 3, y, ["######", "#s#s##", "######"], {"#": INK, "s": SNOW})
    elif style == "cat":
        c.sprite(x - 3, y, ["#.#.#.", ".#.#.."], {"#": INK})
    elif style == "yell":
        c.sprite(x - 2, y, [".##.", "#cc#", "#cc#", ".##."], {"#": INK, "c": CORAL})
    elif style == "tongue":
        c.sprite(x - 2, y, ["#..#", ".##.", ".c.."], {"#": INK, "c": CORAL})
    elif style == "smirk":
        c.sprite(x - 2, y, ["...#", "###."], {"#": INK})
    elif style == "chew":
        c.sprite(x - 2, y, (["####", ".##."] if int(t * 10) % 2 else [".##.", "####"]), {"#": INK})


def _arm_end(sx: int, sy: int, angle: float, length: float, left: bool) -> Tuple[int, int]:
    a = math.radians(angle)
    dx = math.cos(a) * length
    dy = math.sin(a) * length
    return int(round(sx - dx if left else sx + dx)), int(round(sy + dy))


def _arms_layer(p: Pose, g: Geometry) -> Canvas:
    layer = Canvas()
    body = _colours(p)[0]
    axo = p.skin == "axo"
    length = (3.0 if axo else 5.0) if p.form == 0 else (4.0 if axo else 7.0)
    sl = (g.left + 1, g.hand_l[1] - 1)
    sr = (g.right - 1, g.hand_r[1] - 1)
    ends = []
    for (sx, sy), ang, left in ((sl, p.arms[0], True), (sr, p.arms[1], False)):
        ex, ey = _arm_end(sx, sy, ang, length, left)
        layer.line(sx, sy, ex, ey, body)
        layer.line(sx, sy + 1, ex, ey + 1, body)
        if not axo:
            layer.line(sx, sy - 1, ex, ey - 1, body)
            layer.disc(ex, ey, 1.5, body)
        else:
            layer.rect(ex - 1, ey, 2, 2, body)
        ends.append((ex, ey))
    g.hand_l, g.hand_r = ends[0], ends[1]
    return layer


def _face(c: Canvas, p: Pose, g: Geometry) -> None:
    gap = g.eye_gap
    lx = g.cx - gap - 1
    rx = g.cx + gap - 1
    _eye(c, lx, g.eye_y, p.eyes, p.look, False, p.t)
    _eye(c, rx, g.eye_y, p.eyes, p.look, True, p.t)
    cheek = CORAL if p.blush else BLUSH
    c.hline(lx - 2, lx - 1, g.eye_y + 3, cheek)
    c.hline(rx + 2, rx + 3, g.eye_y + 3, cheek)
    _mouth(c, g.cx + p.look[0] // 2, g.mouth_y, p.mouth, p.t)
    g.extra["eye_l"] = (lx, g.eye_y)
    g.extra["eye_r"] = (rx, g.eye_y)


def _sweat(c: Canvas, p: Pose, g: Geometry) -> None:
    if not p.sweat:
        return
    x = g.right + 2
    y = g.top + 1 + (p.sweat - 1) * 2
    c.sprite(x, y, [".s.", "sss", ".s."], {"s": SKY})
    c.px(x + 1, y + 1, SNOW)


def _underglow(c: Canvas, p: Pose, g: Geometry) -> None:
    if p.form < 2 or p.lying or p.tint is not None:
        return
    y = int(round(p.y)) + 1
    w = g.right - g.left - 2
    for i in range(w):
        colour = RAINBOW[(i // 2 + int(p.t * 12)) % len(RAINBOW)]
        if (i + int(p.t * 12)) % 3 != 0:
            c.px(g.left + 1 + i, y, colour)


def draw(c: Canvas, p: Pose) -> Geometry:
    """Draw Keebo onto ``c`` and return its anchor geometry."""
    from . import accessories

    body, g = _body_layer(p)
    _stem(body, p, g)
    if p.back:
        accessories.draw_back(c, p, g)
    arms = _arms_layer(p, g)
    if not p.arms_front:
        arms.outline(INK)
        c.blit(arms)
    body.outline(INK)
    if p.form == 3 and p.tint is None:
        # mecha visor band
        body.hline(g.left + 3, g.right - 3, g.eye_y - 3, FOG)
    c.blit(body)
    if p.tint is None and p.eyes != "none":
        _face(c, p, g)
    _underglow(c, p, g)
    if p.neck:
        accessories.draw_neck(c, p, g)
    if p.face_acc:
        accessories.draw_face(c, p, g)
    if p.hat or p.form == 4:
        accessories.draw_hat(c, p, g)
    if p.arms_front:
        arms.outline(INK)
        c.blit(arms)
    _sweat(c, p, g)
    if p.flip:
        c.data = c.data[:, ::-1].copy()
    return g


def render(p: Pose, background: Optional[Canvas] = None) -> Canvas:
    c = background.copy() if background is not None else Canvas()
    draw(c, p)
    return c


__all__ = ["Pose", "Geometry", "draw", "render", "FORM_NAMES", "FORM_SIZES",
           "SKINS", "DEFAULT_SKIN", "ARMS_DOWN", "ARMS_OUT", "ARMS_UP", "ARMS_TYPE", "EYES", "MOUTHS",
           ]
