"""Built-in context scenes: what Keebo does while you use different apps.

Add a scene with ``@scene("name")``; map apps to it in
``keebo/context/rules.py`` (or a user ``contexts.toml``)."""
from __future__ import annotations

import math
from typing import List

from ..animations.base import Frame, Look, animation, bounce, steps, wave
from ..animations.states import hud, stage
from ..art import props
from ..art.canvas import Canvas
from ..art.character import ARMS_DOWN, ARMS_OUT, draw
from ..art.palette import (
    COCOA,
    CORAL,
    DEEP,
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


def scene(name: str, description: str = ""):
    return animation(name, kind="scene", loop=True, description=description)


def _paper(c: Canvas, x: int, y: int, lines: int) -> None:
    c.rect(x, y, 14, 4, SNOW)
    c.box(x - 1, y - 1, 16, 6, INK)
    for k in range(lines):
        row = y + 1 + (k // 3) * 2
        col = x + 1 + (k % 3) * 4
        if row < y + 4:
            c.hline(col, col + 2, row, SLATE)


@scene("coding", "IDE or terminal open: typing away on a mini MacBook.")
def coding(look: Look) -> List[Frame]:
    frames = []
    n = 16
    for i, t in enumerate(steps(n)):
        c = stage(look, t)
        props.desk(c, 44)
        props.laptop_side(c, 36, 44, t)
        tap = i % 2
        blink = i == 9
        p = look.pose(t=t, y=44, x=21, eyes="closed" if blink else "focus", look=(1, 0),
                      mouth="cat" if i % 8 < 4 else "flat",
                      arms=(130 + 15 * tap, 30 + 12 * (1 - tap)), arms_front=True,
                      squash=1.0 + 0.02 * wave(t * 2), face_acc=look.face or "glasses")
        draw(c, p)
        frames.append((hud(c, look), 90))
    return frames


@scene("terminal", "Terminal focus: hacker hoodie mode with scrolling green text.")
def terminal(look: Look) -> List[Frame]:
    frames = []
    n = 16
    for i, t in enumerate(steps(n)):
        c = stage(look, t, night=True)
        props.monitor(c, 6, 6, 52, 22, VOID)
        for row in range(6):
            ln = (row + i) % 9
            w = 4 + (ln * 7) % 30
            c.hline(9, 9 + w, 9 + row * 3, MINT if ln % 3 else SKY)
        if i % 4 < 2:
            c.rect(9 + (i * 3) % 30, 24, 2, 2, SNOW)
        p = look.pose(t=t, y=56, eyes="focus", mouth="smirk", face_acc="shades",
                      arms=(130 + 15 * (i % 2), 130 + 15 * ((i + 1) % 2)), arms_front=True)
        draw(c, p)
        frames.append((hud(c, look), 90))
    return frames


@scene("writing", "Mail or Docs: scribbling a letter with a quill.")
def writing(look: Look) -> List[Frame]:
    frames = []
    n = 16
    for i, t in enumerate(steps(n)):
        c = stage(look, t)
        props.desk(c, 46)
        _paper(c, 33, 41, i + 1)
        # ink pot
        c.rect(52, 41, 4, 4, INK)
        c.hline(52, 55, 41, SKY)
        p = look.pose(t=t, x=24, y=46, eyes="happy" if i in (6, 7) else "open", look=(1, 1),
                      mouth="tongue" if i % 6 < 3 else "smile",
                      arms=(80, 35 + 10 * wave(t * 4)), arms_front=True)
        g = draw(c, p)
        # quill in right hand, nib wiggling across the page
        hx, hy = g.hand_r
        nib = (hx + 3 + int(2 * wave(t * 4)), hy + 3)
        c.line(hx, hy - 6, *nib, SNOW)
        c.line(hx - 1, hy - 6, hx, hy - 3, CORAL)
        c.px(*nib, INK)
        if i == 12:
            props.note(c, hx + 6, hy - 10, CORAL, 1)
        frames.append((hud(c, look), 110))
    return frames


@scene("watching", "YouTube or Netflix: munching popcorn in front of the TV.")
def watching(look: Look) -> List[Frame]:
    frames = []
    n = 16
    for i, t in enumerate(steps(n)):
        c = props.room(t, night=True, window=False)
        props.tv(c, 19, 3, t)
        # tv glow on the floor
        for x in range(14, 50, 2):
            c.px(x + (i % 2), 50, SKY)
        chew = i % 4
        to_mouth = chew in (0, 1)
        p = look.pose(t=t, y=56, eyes="squint" if i in (10, 11) else "open", look=(0, -1),
                      mouth="chew" if chew in (1, 2) else "smile",
                      arms=(-30 if to_mouth else 70, 95), arms_front=True)
        g = draw(c, p)
        # popcorn bucket hugged on the right
        bx, by = g.hand_r[0] - 6, g.hand_r[1] - 4
        c.rect(bx, by, 8, 7, SNOW)
        for k in range(0, 8, 2):
            c.vline(bx + k, by, by + 6, RUBY)
        c.box(bx - 1, by - 1, 10, 9, INK)
        for k in range(4):
            c.disc(bx + 1 + k * 2, by - 1, 1, SUN if (k + i) % 3 else SNOW)
        if to_mouth:
            hx, hy = g.hand_l
            c.rect(hx, hy - 1, 2, 2, SUN)
        if chew == 2:
            props.sparkle(c, g.cx + 6, g.mouth_y - 2, 0, SNOW)
        frames.append((hud(c, look), 120))
    return frames


@scene("music", "Spotify or Music: headphones on, bopping to the beat.")
def music(look: Look) -> List[Frame]:
    frames = []
    n = 16
    for i, t in enumerate(steps(n)):
        c = stage(look, t)
        beat = (t * 4) % 1
        h = bounce(beat)
        p = look.pose(t=t, y=50 - 2 * h, squash=0.94 + 0.1 * h, lean=2 * wave(t * 2),
                      eyes="closed", mouth="smile" if i % 4 else "o", hat="headphones",
                      arms=(40 - 30 * h, 40 - 30 * (1 - h)), blush=True)
        g = draw(c, p)
        for k in range(3):
            ph = (t + k / 3) % 1
            props.note(c, g.right + 2 + int(4 * ph), g.top - int(14 * ph), RAINBOW[k * 2 % len(RAINBOW)], k % 2)
        frames.append((hud(c, look), 90))
    return frames


@scene("chatting", "Slack, Discord or Messages: speech bubbles flying.")
def chatting(look: Look) -> List[Frame]:
    frames = []
    n = 16
    for i, t in enumerate(steps(n)):
        c = stage(look, t)
        p = look.pose(t=t, x=22, eyes="happy" if i % 8 >= 6 else "open", look=(1, -1),
                      mouth="grin" if i % 8 >= 6 else ("o" if i % 2 else "smile"),
                      arms=(55, 110 + 10 * (i % 2)), arms_front=True)
        g = draw(c, p)
        # phone in hand
        hx, hy = g.hand_r
        c.rect(hx - 1, hy - 5, 4, 6, INK)
        c.rect(hx, hy - 4, 2, 3, SKY)
        # bubbles rising
        for k in range(3):
            ph = (t + k / 3) % 1
            y = 40 - int(ph * 34)
            if y < 4:
                continue
            w = 8 + k * 2
            x = 38 + (k % 2) * 6
            c.rrect(x, y, w, 5, MINT if k % 2 else SNOW, 1)
            c.hline(x + 2, x + w - 3, y + 2, DEEP if k % 2 else SLATE)
        frames.append((hud(c, look), 110))
    return frames


@scene("meeting", "Zoom, Meet or Teams: on camera, nodding along.")
def meeting(look: Look) -> List[Frame]:
    frames = []
    n = 16
    for i, t in enumerate(steps(n)):
        c = props.room(t, window=False)
        # grid of tiny call tiles
        for k in range(3):
            x = 4 + k * 20
            c.rect(x, 4, 16, 12, NIGHT)
            c.box(x - 1, 3, 18, 14, SLATE if not (k == (i // 4) % 3) else MINT)
            c.disc(x + 8, 9, 3, [CORAL, SUN, GRAPE][k])
            c.rect(x + 4, 12, 9, 4, [CORAL, SUN, GRAPE][k])
        nod = int(1.5 * max(0, wave(t * 2)))
        p = look.pose(t=t, y=56 + nod, eyes="open" if i % 8 else "closed", mouth="smile" if i % 6 else "o",
                      neck="bowtie", arms=ARMS_DOWN)
        draw(c, p)
        c.px(58, 22, RUBY if i % 4 < 2 else NIGHT)      # recording dot
        frames.append((hud(c, look), 120))
    return frames


@scene("browsing", "Browser: surfing the web on a tiny surfboard.")
def browsing(look: Look) -> List[Frame]:
    frames = []
    n = 16
    for i, t in enumerate(steps(n)):
        c = props.room(t, window=False)
        c.rect(0, 36, 64, 28, DEEP)
        for x in range(64):                               # waves
            y = 38 + int(2 * math.sin((x + t * 64) / 5))
            c.vline(x, y, 40, TEAL)
            c.px(x, y - 1, SNOW if (x + i * 4) % 11 == 0 else SKY)
        bob = int(2 * wave(t))
        c.rrect(17, 46 + bob, 30, 3, CORAL, 1)
        c.hline(18, 45, 47 + bob, SUN)
        p = look.pose(t=t, y=46 + bob, lean=2 * wave(t), eyes="happy", mouth="grin", arms=ARMS_OUT,
                      face_acc=look.face or "shades")
        draw(c, p)
        # "www" cloud of tabs
        for k in range(3):
            x = 6 + k * 18 + int(t * 18) % 18
            c.rrect(x % 70 - 6, 6 + (k % 2) * 4, 9, 5, [SKY, MINT, SUN][k], 1)
        frames.append((hud(c, look), 100))
    return frames


@scene("designing", "Figma or Photoshop: painting at an easel.")
def designing(look: Look) -> List[Frame]:
    frames = []
    n = 16
    for i, t in enumerate(steps(n)):
        c = stage(look, t)
        # easel
        c.line(40, 52, 46, 18, COCOA)
        c.line(58, 52, 52, 18, COCOA)
        c.rect(38, 18, 22, 18, SNOW)
        c.box(37, 17, 24, 20, INK)
        strokes = min(len(RAINBOW), 1 + i // 2)
        for k in range(strokes):
            c.line(40, 33 - k * 2, 46 + k, 22 + (k * 3) % 8, RAINBOW[k])
        p = look.pose(t=t, x=22, eyes="focus" if i % 8 else "happy", look=(1, 0), mouth="tongue",
                      arms=(80, -20 + 25 * wave(t * 2)), hat="beanie" if look.hat is None else look.hat)
        g = draw(c, p)
        hx, hy = g.hand_r
        c.line(hx, hy, hx + 4, hy - 3, COCOA)
        c.px(hx + 5, hy - 4, RAINBOW[i % len(RAINBOW)])
        frames.append((hud(c, look), 100))
    return frames


@scene("reading", "PDFs, docs or Kindle: reading a big book.")
def reading(look: Look) -> List[Frame]:
    frames = []
    n = 16
    for i, t in enumerate(steps(n)):
        c = stage(look, t)
        p = look.pose(t=t, eyes="sleepy" if i in (12, 13) else "open", look=(0, 1), mouth="o" if i == 14 else "smile",
                      arms=(115, 115), arms_front=True, face_acc=look.face or "monocle")
        g = draw(c, p)
        bx, by = g.cx - 10, g.mouth_y + 4
        c.rect(bx, by, 20, 9, SNOW)
        c.box(bx - 1, by - 1, 22, 11, INK)
        c.rect(bx - 1, by + 9, 22, 1, RUBY)
        c.vline(g.cx, by, by + 8, SLATE)
        for r in range(3):
            c.hline(bx + 2, bx + 7, by + 2 + r * 2, SLATE)
            c.hline(bx + 12, bx + 17, by + 2 + r * 2, SLATE)
        if i in (7, 8):     # page flip
            c.rect(g.cx + (1 if i == 7 else -6), by - 2, 6, 10, FOG)
        frames.append((hud(c, look), 120))
    return frames


@scene("gaming", "Steam or a game: gamepad mashing, tongue out.")
def gaming(look: Look) -> List[Frame]:
    frames = []
    n = 16
    for i, t in enumerate(steps(n)):
        c = props.room(t, night=True, window=False)
        props.monitor(c, 14, 4, 36, 20, NIGHT)
        # tiny platformer
        px = 18 + (i * 2) % 26
        c.rect(15, 20, 34, 3, MINT)
        c.rect(px, 16 - int(4 * bounce((t * 2) % 1)), 3, 3, CORAL)
        c.rect(30, 17, 3, 3, RUBY)
        p = look.pose(t=t, y=56, eyes="focus", mouth="tongue", look=(0, -1),
                      arms=(120 + 10 * (i % 2), 120 + 10 * ((i + 1) % 2)), arms_front=True,
                      lean=(i % 4 == 0) - (i % 4 == 2), hat="headphones")
        g = draw(c, p)
        c.rrect(g.cx - 6, g.hand_l[1] - 1, 13, 5, SLATE, 1)
        c.px(g.cx + 3, g.hand_l[1] + 1, RUBY)
        c.px(g.cx - 3, g.hand_l[1] + 1, SNOW)
        frames.append((hud(c, look), 80))
    return frames


