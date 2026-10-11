"""A tiny indexed-colour canvas for drawing pixel art in code.

Keebo is drawn on a 64x64 logical grid and shown at 2x on the keyboard's
128x128 screen, so every "pixel" here is a crisp 2x2 block on the device.
"""
from __future__ import annotations

import math
from typing import Dict, Iterable, Optional, Sequence, Tuple

import numpy as np

from .palette import CLEAR, flat_palette

SIZE = 64
SCALE = 2
DEVICE = SIZE * SCALE


class Canvas:
    """A grid of palette indices. ``CLEAR`` marks transparent pixels."""

    __slots__ = ("w", "h", "data")

    def __init__(self, w: int = SIZE, h: int = SIZE, fill: int = CLEAR) -> None:
        self.w, self.h = w, h
        self.data = np.full((h, w), fill, dtype=np.uint8)

    # -- basics ---------------------------------------------------------
    def copy(self) -> "Canvas":
        c = Canvas(self.w, self.h)
        c.data = self.data.copy()
        return c

    def clear(self, fill: int = CLEAR) -> "Canvas":
        self.data[:] = fill
        return self

    def get(self, x: int, y: int) -> int:
        if 0 <= x < self.w and 0 <= y < self.h:
            return int(self.data[y, x])
        return CLEAR

    def px(self, x: float, y: float, c: int) -> None:
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.w and 0 <= y < self.h and c != CLEAR:
            self.data[y, x] = c

    def pixels(self, pts: Iterable[Tuple[float, float]], c: int) -> None:
        for x, y in pts:
            self.px(x, y, c)

    # -- shapes ---------------------------------------------------------
    def rect(self, x: int, y: int, w: int, h: int, c: int) -> None:
        x0, y0 = max(0, int(x)), max(0, int(y))
        x1, y1 = min(self.w, int(x + w)), min(self.h, int(y + h))
        if x1 > x0 and y1 > y0:
            self.data[y0:y1, x0:x1] = c

    def box(self, x: int, y: int, w: int, h: int, c: int) -> None:
        self.hline(x, x + w - 1, y, c)
        self.hline(x, x + w - 1, y + h - 1, c)
        self.vline(x, y, y + h - 1, c)
        self.vline(x + w - 1, y, y + h - 1, c)

    def rrect(self, x: int, y: int, w: int, h: int, c: int, r: int = 1) -> None:
        """Filled rectangle with clipped (pixel-rounded) corners."""
        for row in range(h):
            inset = 0
            if row < r:
                inset = r - row
            elif row >= h - r:
                inset = row - (h - r) + 1
            self.rect(x + inset, y + row, w - 2 * inset, 1, c)

    def hline(self, x0: int, x1: int, y: int, c: int) -> None:
        if x1 < x0:
            x0, x1 = x1, x0
        self.rect(x0, y, x1 - x0 + 1, 1, c)

    def vline(self, x: int, y0: int, y1: int, c: int) -> None:
        if y1 < y0:
            y0, y1 = y1, y0
        self.rect(x, y0, 1, y1 - y0 + 1, c)

    def line(self, x0: float, y0: float, x1: float, y1: float, c: int) -> None:
        x0, y0, x1, y1 = (int(round(v)) for v in (x0, y0, x1, y1))
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            self.px(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx: float, cy: float, r: float, c: int) -> None:
        ri = int(math.ceil(r))
        for y in range(-ri, ri + 1):
            for x in range(-ri, ri + 1):
                if x * x + y * y <= r * r + r * 0.8:
                    self.px(cx + x, cy + y, c)

    def ring(self, cx: float, cy: float, r: float, c: int) -> None:
        steps = max(8, int(r * 8))
        for i in range(steps):
            a = 2 * math.pi * i / steps
            self.px(cx + math.cos(a) * r, cy + math.sin(a) * r, c)

    def ellipse(self, cx: float, cy: float, rx: float, ry: float, c: int) -> None:
        for y in range(-int(ry) - 1, int(ry) + 2):
            for x in range(-int(rx) - 1, int(rx) + 2):
                if rx > 0 and ry > 0 and (x / rx) ** 2 + (y / ry) ** 2 <= 1.0:
                    self.px(cx + x, cy + y, c)

    def poly(self, pts: Sequence[Tuple[float, float]], c: int) -> None:
        """Scanline-fill a polygon."""
        ys = [p[1] for p in pts]
        for y in range(int(min(ys)), int(max(ys)) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for a, b in zip(xs[::2], xs[1::2]):
                self.hline(int(round(a)), int(round(b)), y, c)

    def sprite(self, x: int, y: int, rows: Sequence[str], key: Dict[str, int],
               flip: bool = False) -> None:
        """Stamp an ASCII sprite. Characters missing from ``key`` are transparent."""
        for j, row in enumerate(rows):
            if flip:
                row = row[::-1]
            for i, ch in enumerate(row):
                if ch in key:
                    self.px(x + i, y + j, key[ch])

    # -- layers ---------------------------------------------------------
    def blit(self, other: "Canvas", x: int = 0, y: int = 0) -> None:
        x, y = int(round(x)), int(round(y))
        sx0, sy0 = max(0, -x), max(0, -y)
        dx0, dy0 = max(0, x), max(0, y)
        w = min(other.w - sx0, self.w - dx0)
        h = min(other.h - sy0, self.h - dy0)
        if w <= 0 or h <= 0:
            return
        src = other.data[sy0:sy0 + h, sx0:sx0 + w]
        dst = self.data[dy0:dy0 + h, dx0:dx0 + w]
        mask = src != CLEAR
        dst[mask] = src[mask]

    def outline(self, c: int, diagonal: bool = False) -> "Canvas":
        """Grow a 1px border of colour ``c`` around every opaque pixel."""
        solid = self.data != CLEAR
        padded = np.pad(solid, 1)
        grown = np.zeros_like(solid)
        offsets = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        if diagonal:
            offsets += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dy, dx in offsets:
            grown |= padded[1 + dy:1 + dy + self.h, 1 + dx:1 + dx + self.w]
        self.data[grown & ~solid] = c
        return self

    def recolor(self, mapping: Dict[int, int]) -> "Canvas":
        out = self.data.copy()
        for src, dst in mapping.items():
            out[self.data == src] = dst
        self.data = out
        return self

    def silhouette(self, c: int) -> "Canvas":
        self.data[self.data != CLEAR] = c
        return self

    def flipped(self) -> "Canvas":
        c = self.copy()
        c.data = c.data[:, ::-1].copy()
        return c

    # -- text -----------------------------------------------------------
    def text(self, x: int, y: int, s: str, c: int, shadow: Optional[int] = None) -> int:
        """Draw text in the 3x5 font. Returns the x after the last glyph."""
        from .font import TINY

        cx = x
        for ch in s.upper():
            glyph = TINY.get(ch, TINY["?"])
            if shadow is not None:
                self.sprite(cx + 1, y + 1, glyph, {"#": shadow})
            self.sprite(cx, y, glyph, {"#": c})
            cx += len(glyph[0]) + 1
        return cx

    # -- export ---------------------------------------------------------
    def to_image(self, scale: int = SCALE, background: int = 0):
        from PIL import Image

        data = np.where(self.data == CLEAR, background, self.data).astype(np.uint8)
        img = Image.fromarray(data, mode="P")
        img.putpalette(flat_palette())
        if scale != 1:
            img = img.resize((self.w * scale, self.h * scale), Image.NEAREST)
        return img


def text_width(s: str) -> int:
    from .font import TINY

    return sum(len(TINY.get(ch, TINY["?"])[0]) + 1 for ch in s.upper()) - 1
