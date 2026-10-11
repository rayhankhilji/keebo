"""Keebo's core moods. Each loop starts and ends on the neutral standing
pose (squash 1, feet down) so any clip can cut into any other smoothly."""
from __future__ import annotations

import math
from typing import List

from ..art import props
from ..art.canvas import Canvas
from ..art.character import ARMS_DOWN, ARMS_OUT, ARMS_UP, draw
from ..art.palette import (
    EMBER,
    GRAPE,
    INK,
    MINT,
    RAINBOW,
    RUBY,
    SKY,
    SLATE,
    SNOW,
    SUN,
    VOID,
)
from .base import Frame, Look, animation, bounce, lerp, steps, wave


def stage(look: Look, t: float, night: bool = False) -> Canvas:
    c = props.room(t, night=night)
    props.shelf(c, look.projects)
    return c


def hud(c: Canvas, look: Look) -> Canvas:
    if look.show_hud:
        props.xp_bar(c, look.xp_frac, look.level)
    return c


@animation("idle", description="Breathing, blinking, glancing around.")
def idle(look: Look) -> List[Frame]:
    frames = []
    n = 20
    for i, t in enumerate(steps(n)):
        c = stage(look, t)
        breath = wave(t)
        eyes = "closed" if i in (7, 8) else "open"
        lookdir = (-1, 0) if 11 <= i <= 13 else ((1, 0) if 14 <= i <= 16 else (0, 0))
        p = look.pose(squash=1.0 + 0.05 * breath, t=t, eyes=eyes, look=lookdir,
                      arms=(55 - 6 * breath, 55 - 6 * breath))
        draw(c, p)
        frames.append((hud(c, look), 90))
    return frames


@animation("sleeping", description="Nightcap, slow breaths, drifting Zzz.")
def sleeping(look: Look) -> List[Frame]:
    frames = []
    n = 16
    for t in steps(n):
        c = stage(look, t, night=True)
        breath = wave(t)
        p = look.pose(squash=0.86 + 0.05 * breath, eyes="closed", mouth="o" if breath > 0.3 else "flat",
                      hat="nightcap", t=t, arms=(75, 75))
        g = draw(c, p)
        props.zzz(c, g.right - 2, g.top - 4, t)
        frames.append((hud(c, look), 140))
    return frames


@animation("wake", kind="transition", loop=False, description="Project start: blink, stretch, hop.")
def wake(look: Look) -> List[Frame]:
    frames = []
    seq = [
        dict(squash=0.86, eyes="closed", mouth="flat", hat="nightcap", ms=200),
        dict(squash=0.88, eyes="sleepy", mouth="flat", hat="nightcap", ms=220),
        dict(squash=0.88, eyes="closed", mouth="flat", hat="nightcap", ms=120),
        dict(squash=0.9, eyes="open", mouth="o", hat="nightcap", ms=200),
        dict(squash=1.12, eyes="closed", mouth="yell", arms=ARMS_UP, ms=160),
        dict(squash=1.16, eyes="closed", mouth="yell", arms=(-80, -80), ms=260),
        dict(squash=0.85, eyes="happy", mouth="smile", ms=90),
        dict(squash=1.08, eyes="happy", mouth="grin", arms=ARMS_UP, lift=6, ms=90),
        dict(squash=1.0, eyes="happy", mouth="grin", arms=ARMS_UP, lift=8, ms=90),
        dict(squash=0.88, eyes="happy", mouth="smile", ms=90),
        dict(squash=1.0, eyes="open", mouth="smile", blush=True, ms=300),
    ]
    for i, s in enumerate(seq):
        t = i / len(seq)
        c = stage(look, t, night=i < 4)
        ms = s.pop("ms")
        lift = s.pop("lift", 0)
        if "arms" not in s:
            s["arms"] = (75, 75) if i < 4 else ARMS_DOWN
        p = look.pose(t=t, y=50 - lift, **s)
        if i >= 4:
            p = p.but(hat=look.hat)
        g = draw(c, p)
        if i == 3:
            props.exclaim(c, g.right + 2, g.top - 8, SUN)
        frames.append((hud(c, look), ms))
    return frames


@animation("thinking", description="Chin scratch, thought bubble, light-bulb moment.")
def thinking(look: Look) -> List[Frame]:
    frames = []
    n = 20
    for i, t in enumerate(steps(n)):
        c = stage(look, t)
        p = look.pose(t=t, eyes="open", look=(1, -1), mouth="flat" if i < 15 else "o",
                      arms=(55, -95 + 8 * wave(t * 4)), lean=1 * wave(t))
        g = draw(c, p)
        props.bubble(c, 36, 4, 22, 13, g.right - 2, thought=True)
        if i < 15:
            dots = min(3, (i // 3) % 4)
            for d in range(dots):
                c.rect(41 + d * 5, 10, 2, 2, SLATE)
        else:
            c.sprite(44, 6, [".###.", "#sss#", "#sss#", ".#s#.", "..#..", ".###."],
                     {"#": SUN, "s": SNOW})
            props.burst(c, 46, 9, 5 + (i - 15), SUN)
        frames.append((hud(c, look), 110))
    return frames


@animation("building", description="Hard hat on, stacking bricks for the agent.")
def building(look: Look) -> List[Frame]:
    frames = []
    n = 16
    for i, t in enumerate(steps(n)):
        c = stage(look, t)
        hit = i % 4
        ang = [-120, -70, 10, -40][hit]
        p = look.pose(t=t, x=26, hat="hardhat", eyes="focus", mouth="tongue" if hit == 2 else "flat",
                      arms=(55, ang + 90 if hit != 2 else 40), squash=0.96 if hit == 2 else 1.0)
        g = draw(c, p)
        # brick wall grows across the loop
        bricks = 2 + i // 3
        for b in range(bricks):
            row, col = divmod(b, 2)
            props.brick(c, 44 + col * 7 + (3 if row % 2 else 0), 47 - row * 4,
                        EMBER if (row + col) % 2 else RUBY)
        hx, hy = g.hand_r
        props.hammer(c, hx, hy, [-110, -60, 20, -30][hit])
        if hit == 2:
            props.sparkle(c, hx + 7, hy + 4, 1)
            props.sparkle(c, hx + 9, hy + 1, 0, SNOW)
        frames.append((hud(c, look), 85))
    return frames


@animation("testing", description="Tests running: frantic typing, sweat, speed lines.")
def testing(look: Look) -> List[Frame]:
    frames = []
    n = 16
    for i, t in enumerate(steps(n)):
        c = stage(look, t)
        props.speed_lines(c, t)
        props.desk(c, 44)
        props.laptop_side(c, 36, 44, t, code=False)
        jitter = (i % 2) * 2 - 1
        p = look.pose(t=t, y=44, x=21 + jitter * 0.5, eyes="wide", mouth="teeth" if i % 4 < 2 else "o",
                      look=(1, 0), arms=(130 + 20 * (i % 2), 25 + 15 * ((i + 1) % 2)), arms_front=True,
                      sweat=1 + (i // 2) % 2)
        draw(c, p)
        # running test dots marching above
        for k in range(6):
            on = (k + i) % 6
            col = SUN if on == 0 else (MINT if on < 3 else SLATE)
            c.rect(14 + k * 6, 4, 4, 4, col)
            c.box(13 + k * 6, 3, 6, 6, INK)
        frames.append((hud(c, look), 60))
    return frames


@animation("celebrating", description="Tests passed! Party hat, jumps and confetti.")
def celebrating(look: Look) -> List[Frame]:
    frames = []
    n = 16
    for t in steps(n):
        c = stage(look, t)
        ph = (t * 2) % 1
        h = bounce(ph)
        sq = 0.85 if ph < 0.08 or ph > 0.92 else 1.0 + 0.12 * h
        p = look.pose(t=t, y=50 - 9 * h, squash=sq, hat="partyhat", eyes="happy", mouth="grin",
                      blush=True, arms=ARMS_UP if h > 0.2 else ARMS_OUT, feet=(1, 1) if h > 0.2 else (0, 0))
        draw(c, p)
        props.confetti(c, t, seed=5)
        frames.append((hud(c, look), 70))
    return frames


@animation("confused", description="Head tilts, question marks pop.")
def confused(look: Look) -> List[Frame]:
    frames = []
    n = 16
    for i, t in enumerate(steps(n)):
        c = stage(look, t)
        tilt = 3 * wave(t)
        p = look.pose(t=t, lean=tilt, eyes="uneven" if i % 8 < 5 else "spiral", mouth="wavy",
                      arms=(55, 150), arms_front=True, look=(1 if tilt > 0 else -1, 0))
        g = draw(c, p)
        if i % 8 >= 1:
            props.question(c, g.right + 1, g.top - 10 - (i % 8 < 3), SUN)
        if i % 8 >= 4:
            props.question(c, g.left - 6, g.top - 6, SKY, big=False)
        frames.append((hud(c, look), 100))
    return frames


@animation("frustrated", description="Stomping, steam and a tiny storm cloud.")
def frustrated(look: Look) -> List[Frame]:
    frames = []
    n = 16
    for i, t in enumerate(steps(n)):
        c = stage(look, t)
        stomp = i % 4
        p = look.pose(t=t, eyes="angry", mouth="teeth" if stomp < 2 else "frown",
                      feet=(3, 0) if stomp == 0 else ((0, 3) if stomp == 2 else (0, 0)),
                      squash=0.92 if stomp in (1, 3) else 1.0, arms=(20 + 30 * (i % 2), 20 + 30 * (i % 2)),
                      x=32 + (stomp == 1) - (stomp == 3))
        g = draw(c, p)
        props.storm_cloud(c, g.cx - 8, max(0, g.top - 20), t)
        props.steam(c, g.left - 2, g.top + 2, t)
        props.steam(c, g.right + 3, g.top + 2, t + 0.5)
        frames.append((hud(c, look), 80))
    return frames


@animation("failure", kind="transition", loop=False,
           description="Build failed: collapse into a pancake while the build catches fire.")
def failure(look: Look) -> List[Frame]:
    frames = []
    n = 20
    for i, t in enumerate(steps(n)):
        c = stage(look, t)
        k = min(1.0, i / 5)
        block_y = 47
        # the broken build: a crooked tower on fire
        for b in range(3):
            props.brick(c, 46 + (b % 2) * 2 - b, block_y - b * 4, SLATE if b else RUBY)
        if i >= 2:
            props.fire(c, 49, 38, t, 2 if i > 6 else 1)
            props.smoke(c, 49, 26, t)
        if i < 3:
            p = look.pose(t=t, x=26, eyes="wide", mouth="o", arms=ARMS_UP)
            g = draw(c, p)
            props.exclaim(c, g.right - 2, g.top - 10)
        elif i < 6:
            p = look.pose(t=t, x=26, squash=lerp(1.0, 0.55, k), eyes="x", mouth="yell", arms=ARMS_OUT)
            draw(c, p)
        else:
            p = look.pose(t=t, x=26, lying=True, eyes="x", mouth="wavy", arms=(5, 5))
            g = draw(c, p)
            # dizzy stars orbit
            for s in range(3):
                a = t * 6 * math.pi + s * 2.1
                props.sparkle(c, g.cx + int(math.cos(a) * 8), g.top - 4 + int(math.sin(a) * 2), 1, SUN)
        frames.append((hud(c, look), 110 if i < 6 else 130))
    return frames


@animation("recovery", kind="transition", loop=False,
           description="Failure recovery: peel off the floor, bandage, thumbs up.")
def recovery(look: Look) -> List[Frame]:
    frames = []
    seq = [
        dict(lying=True, eyes="x", mouth="wavy", ms=260),
        dict(lying=True, eyes="sleepy", mouth="flat", ms=200),
        dict(squash=0.7, eyes="open", mouth="flat", ms=150),
        dict(squash=0.85, eyes="open", mouth="o", ms=150),
        dict(squash=1.1, eyes="closed", mouth="flat", ms=120),
        dict(squash=1.0, eyes="open", mouth="flat", face_acc="bandage", arms=(55, 140), ms=160),
        dict(squash=1.0, eyes="closed", mouth="flat", face_acc="bandage", arms=(55, 120), ms=160),
        dict(squash=1.0, eyes="open", mouth="smirk", face_acc="bandage", arms=(55, -60), ms=200),
        dict(squash=1.05, eyes="happy", mouth="smile", face_acc="bandage", arms=(55, -70), ms=420),
    ]
    for i, s in enumerate(seq):
        t = i / len(seq)
        c = stage(look, t)
        if i < 3:
            props.smoke(c, 49, 40, t)
        ms = s.pop("ms")
        s.setdefault("arms", ARMS_OUT if i < 5 else ARMS_DOWN)
        p = look.pose(t=t, x=28, **s)
        g = draw(c, p)
        if i >= 7:
            hx, hy = g.hand_r
            c.sprite(hx - 1, hy - 4, [".#.", ".#.", "###", "###"], {"#": SNOW if i == 8 else MINT})
            props.sparkle(c, hx + 4, hy - 4, i, SUN)
        frames.append((hud(c, look), ms))
    return frames


@animation("victory", description="Task complete: trophy held high, cape flutters, spotlight.")
def victory(look: Look) -> List[Frame]:
    frames = []
    n = 16
    for i, t in enumerate(steps(n)):
        c = stage(look, t)
        # spotlight cone
        for y in range(0, 51):
            half = 4 + y // 3
            for x in range(32 - half, 33 + half):
                if c.get(x, y) == VOID and (x + y + i) % 2 == 0:
                    c.px(x, y, INK)
        props.burst(c, 32, 10, 6 + (i % 4), SUN, rays=10)
        p = look.pose(t=t, squash=1.06 + 0.03 * wave(t * 2), eyes="star" if i % 8 < 4 else "happy",
                      mouth="grin", back="cape", arms=(55, -75), blush=True)
        g = draw(c, p)
        hx, hy = g.hand_r
        props.trophy(c, hx - 4, hy - 9 + int(wave(t * 2)), shine=i % 4 == 0)
        props.sparkle(c, 10 + (i * 7) % 44, 20 + (i * 5) % 20, i, RAINBOW[i % len(RAINBOW)])
        frames.append((hud(c, look), 90))
    return frames


@animation("evolving", kind="transition", loop=False, description="Level up: glow, flash, new form.")
def evolving(look: Look) -> List[Frame]:
    frames = []
    old = look.from_form if look.from_form is not None else max(0, look.form - 1)
    new = look.form
    n = 24
    for i in range(n):
        t = i / n
        c = stage(look, t, night=True)
        r = 4 + i * 1.6
        c.ring(32, 38, r % 30, GRAPE)
        c.ring(32, 38, (r + 10) % 30, SKY)
        if i < 8:
            p = look.pose(form=old, t=t, eyes="wide" if i < 4 else "closed", mouth="o", arms=ARMS_OUT)
        elif i < 18:
            form = old if i % 2 == 0 else new
            tint = SNOW if i % 3 else SUN
            p = look.pose(form=form, t=t, tint=tint, squash=1.0 + 0.08 * wave(t * 4), arms=ARMS_OUT)
        else:
            p = look.pose(form=new, t=t, eyes="star" if i < 21 else "happy", mouth="grin", blush=True,
                          arms=ARMS_UP)
        draw(c, p)
        for s in range(6):
            a = t * 4 * math.pi + s * math.pi / 3
            props.sparkle(c, 32 + int(math.cos(a) * (22 - i * 0.4)), 36 + int(math.sin(a) * 12), i + s,
                          RAINBOW[s % len(RAINBOW)])
        if 16 <= i <= 17:
            c.clear(SNOW)
        frames.append((hud(c, look), 90 if i < 18 else 160))
    return frames


