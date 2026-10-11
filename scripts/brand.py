"""Render the README artwork into assets/brand/.

    python scripts/brand.py
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Sequence

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from keebo.animations import build  # noqa: E402
from keebo.animations.base import Clip, Look  # noqa: E402
from keebo.art.canvas import Canvas, text_width  # noqa: E402
from keebo.art.character import ARMS_UP, FORM_NAMES, Pose, draw  # noqa: E402
from keebo.art.font import LOGO  # noqa: E402
from keebo.art.palette import (  # noqa: E402
    CORAL,
    GRAPE,
    INK,
    LILAC,
    LILAC_D,
    NIGHT,
    PALETTE,
    PINK,
    PINK_D,
    SLATE,
    SNOW,
    SUN,
)

ACCENT = {"inky": LILAC, "axo": PINK}

OUT = ROOT / "assets" / "brand"
SHELF = [{"name": "keebo", "trophy": "star"}, {"name": "builddit", "trophy": "cup"},
         {"name": "duocorn", "trophy": "flag"}]
BG = PALETTE[0]


def frame_at(clip: Clip, ms: int):
    t = ms % clip.duration_ms if clip.loop else min(ms, clip.duration_ms - 1)
    for canvas, d in clip.frames:
        if t < d:
            return canvas
        t -= d
    return clip.frames[-1][0]


def save_anim(frames: List[Image.Image], path: Path, ms: int) -> None:
    pal = [f.convert("RGB").quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
           for f in frames]
    pal[0].save(path, save_all=True, append_images=pal[1:], duration=ms, loop=0, disposal=1)
    print("wrote", path.relative_to(ROOT), "%d KB" % (path.stat().st_size // 1024))


def label(text: str, width: int, colour: int = SNOW) -> Canvas:
    c = Canvas(width, 9, NIGHT)
    c.text((width - text_width(text)) // 2, 2, text, colour)
    return c


def grid(names: Sequence[str], path: Path, cols: int = 4, tick: int = 80, seconds: float = 4.8,
         skin: str = "inky") -> None:
    look = Look(projects=SHELF, skin=skin)
    clips = [build(n, look) for n in names]
    rows = (len(clips) + cols - 1) // cols
    gap = 3
    tile_h = 64 + 9
    W, H = cols * 64 + (cols + 1) * gap, rows * tile_h + (rows + 1) * gap
    labels = [label(n.upper(), 64, ACCENT[skin]) for n in names]
    frames = []
    for ms in range(0, int(seconds * 1000), tick):
        c = Canvas(W, H, INK)
        for i, clip in enumerate(clips):
            x = gap + (i % cols) * (64 + gap)
            y = gap + (i // cols) * (tile_h + gap)
            c.blit(frame_at(clip, ms), x, y)
            c.blit(labels[i], x, y + 64)
        frames.append(c.to_image(3, 2))
    save_anim(frames, path, tick)


def big_logo(c: Canvas, x: int, y: int, k: int = 2, colour: int = LILAC, shade: int = LILAC_D) -> int:
    for i, ch in enumerate("KEEBO"):
        rows = LOGO[ch]
        for dy, row in enumerate(rows):
            for dx, v in enumerate(row):
                if v == "#":
                    c.rect(x + dx * k + 1, y + dy * k + 1, k, k, shade if i % 2 == 0 else PINK_D)
        for dy, row in enumerate(rows):
            for dx, v in enumerate(row):
                if v == "#":
                    c.rect(x + dx * k, y + dy * k, k, k, (colour if i % 2 == 0 else PINK) if dy > 0 else SNOW)
        x += (len(rows[0]) + 1) * k
    return x


def banner() -> None:
    W, H = 258, 72
    idle = build("idle", Look(skin="inky"))
    party = build("celebrating", Look(skin="axo"))
    frames = []
    for ms in range(0, 1800, 90):
        c = Canvas(W, H, NIGHT)
        for i in range(40):                        # starfield
            sx, sy = (i * 53) % W, (i * 29) % (H - 12)
            if (i + ms // 180) % 7:
                c.px(sx, sy, SLATE if i % 3 else GRAPE)
        c.rect(0, H - 6, W, 6, INK)
        stage = Canvas()
        stage.blit(frame_at(idle, ms))
        c.blit(stage, 4, 4)
        x = big_logo(c, 78, 14, 3)
        c.text(78, 42, "A PIXEL PET FOR YOUR KEYBOARD", SNOW, shadow=INK)
        c.text(78, 50, "INKY + AXO  .  AULA F75 MAX", SLATE)
        mini = frame_at(party, ms)
        c.blit(mini, x + 6, 4)
        frames.append(c.to_image(4, 1))
    save_anim(frames, OUT / "banner.gif", 90)


def keyboard() -> None:
    """A stylised F75 Max with Keebo living on its screen."""
    u = 44                     # key unit in px
    cols, rows = 16, 6
    pad = 26
    W = pad * 2 + cols * u + 12 + 150
    H = pad * 2 + rows * u + 20
    look = Look(projects=SHELF)
    clips = [build(n, look) for n in ("coding", "testing", "celebrating", "victory")]
    per = 1600
    frames = []
    rgb = [tuple(p) for p in PALETTE]
    for ms in range(0, per * len(clips), 100):
        img = Image.new("RGB", (W, H), (14, 12, 28))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((8, 8, W - 8, H - 8), 34, fill=(40, 36, 64), outline=(10, 9, 20), width=4)
        d.rounded_rectangle((pad - 6, pad - 6, pad + cols * u + 4, H - pad + 2), 18, fill=(24, 21, 40))
        layout = [[1] * 13 + [1, 1, 1], [1] * 13 + [2, 1], [1.5] + [1] * 12 + [1.5, 1],
                  [1.75] + [1] * 11 + [2.25, 1], [2.25] + [1] * 10 + [1.75, 1, 1], [1.25] * 3 + [6.25] + [1] * 6]
        wave = (ms // 100) % (cols + 6)
        for r, row in enumerate(layout):
            x = pad
            for k, w in enumerate(row):
                kx0, ky0 = int(x) + 2, pad + r * u + 2
                kx1, ky1 = int(x + w * u) - 3, pad + (r + 1) * u - 4
                lit = abs(int(x / u) - wave) <= 1 and r % 2 == 0
                cap = rgb[LILAC] if (r == 0 and k == 0) or lit else (rgb[CORAL] if (r, k) in ((3, 12), (5, 3)) else
                                                                    (225, 222, 238))
                d.rounded_rectangle((kx0, ky0 + 4, kx1, ky1 + 4), 7, fill=(120, 116, 150))
                d.rounded_rectangle((kx0, ky0, kx1, ky1), 7, fill=cap)
                d.rounded_rectangle((kx0 + 5, ky0 + 3, kx1 - 5, ky1 - 8), 5, fill=tuple(min(255, c + 12)
                                                                                          for c in cap))
                x += w * u
        # screen module
        sx, sy = pad + cols * u + 22, pad + 4
        d.rounded_rectangle((sx - 10, sy - 10, sx + 128 + 10, sy + 128 + 10), 16, fill=(10, 9, 20))
        clip = clips[(ms // per) % len(clips)]
        img.paste(frame_at(clip, ms % per).to_image(2).convert("RGB"), (sx, sy))
        # knob
        kx, ky = sx + 64, sy + 128 + 62
        d.ellipse((kx - 34, ky - 34, kx + 34, ky + 34), fill=(70, 66, 98), outline=(10, 9, 20), width=4)
        d.ellipse((kx - 22, ky - 22, kx + 22, ky + 22), fill=(92, 88, 124))
        frames.append(img)
    save_anim(frames, OUT / "keyboard.gif", 100)


def forms() -> None:
    n = len(FORM_NAMES)
    c = Canvas(n * 48 + 8, 2 * 56 + 10, NIGHT)
    for r, skin in enumerate(("inky", "axo")):
        for i, name in FORM_NAMES.items():
            stage = Canvas()
            draw(stage, Pose(skin=skin, form=i, eyes="happy" if i else "open", mouth="grin" if i > 2 else "smile",
                             arms=ARMS_UP if i == 4 else (55, 55), back="cape" if i == 4 else None,
                             hat="crown" if i == 4 else None, t=0.25))
            c.blit(stage, 4 + i * 48 - 8, r * 56 - 6)
            if r == 1:
                c.text(4 + i * 48 + 24 - text_width(name.upper()) // 2, 113, name.upper(), SUN if i == 4 else SNOW)
            if i < n - 1:
                c.text(4 + i * 48 + 45, r * 56 + 26, ">", SLATE)
    c.to_image(4, 1).save(OUT / "forms.png")
    print("wrote assets/brand/forms.png")


def wardrobe() -> None:
    outfits = [dict(hat="hardhat"), dict(hat="partyhat"), dict(hat="headphones"), dict(face_acc="glasses"),
               dict(face_acc="shades"), dict(neck="scarf"), dict(hat="tophat", face_acc="monocle", neck="bowtie"),
               dict(hat="wizard", back="cape"), dict(hat="beanie", face_acc="goggles"),
               dict(back="wings", hat="crown"), dict(face_acc="bandage", hat="nightcap")]
    cols = len(outfits)
    c = Canvas(cols * 36 + 4, 48, NIGHT)
    for i, o in enumerate(outfits):
        stage = Canvas()
        draw(stage, Pose(skin=("inky", "axo")[i % 2], eyes="happy", mouth="smile", t=0.1 * i, **o))
        crop = Canvas(36, 48)
        crop.blit(stage, -14, -10)
        c.blit(crop, 2 + i * 36, 0)
    c.to_image(3, 1).save(OUT / "wardrobe.png")
    print("wrote assets/brand/wardrobe.png")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    banner()
    keyboard()
    grid(["idle", "sleeping", "wake", "coding", "thinking", "building", "testing", "celebrating", "confused",
          "frustrated", "failure", "recovery", "victory", "evolving", "writing", "watching"],
         OUT / "states.gif", cols=4)
    grid(["idle", "sleeping", "wake", "coding", "thinking", "building", "testing", "celebrating", "confused",
          "frustrated", "failure", "recovery", "victory", "evolving", "writing", "watching"],
         OUT / "states_axo.gif", cols=4, skin="axo")
    grid(["coding", "terminal", "writing", "watching", "music", "chatting", "meeting", "browsing", "designing",
          "reading", "gaming", "building"], OUT / "scenes.gif", cols=4, skin="axo")
    forms()
    wardrobe()


if __name__ == "__main__":
    main()
