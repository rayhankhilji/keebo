"""GIF and sprite-sheet export, plus a display that keeps ``now.gif`` fresh."""
from __future__ import annotations

import io
import math
from pathlib import Path
from typing import Dict, List, Optional

from PIL import Image

from ..animations.base import Clip, Look, build, names
from ..art.canvas import SCALE
from .base import Display, clip_images


def gif_bytes(clip: Clip, scale: int = SCALE) -> bytes:
    imgs = clip_images(clip, scale)
    frames = [im.quantize(colors=32, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
              for im, _ in imgs]
    buf = io.BytesIO()
    frames[0].save(buf, format="GIF", save_all=True, append_images=frames[1:],
                   duration=[ms for _, ms in imgs], loop=0, disposal=1, optimize=False)
    return buf.getvalue()


def save_gif(clip: Clip, path: Path, scale: int = SCALE) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gif_bytes(clip, scale))
    return path


def sprite_sheet(clip: Clip, scale: int = SCALE, cols: int = 8, gap: int = 0) -> Image.Image:
    imgs = clip_images(clip, scale)
    size = imgs[0][0].width
    cols = min(cols, len(imgs))
    rows = math.ceil(len(imgs) / cols)
    sheet = Image.new("RGB", (cols * size + (cols - 1) * gap, rows * size + (rows - 1) * gap), (8, 7, 18))
    for i, (im, _) in enumerate(imgs):
        sheet.paste(im, ((i % cols) * (size + gap), (i // cols) * (size + gap)))
    return sheet


def export_all(out: Path, look: Optional[Look] = None, only: Optional[List[str]] = None,
               scale: int = SCALE, folder: str = "") -> Dict[str, Dict[str, str]]:
    """Write ``gifs/[folder/]<name>.gif`` and ``sheets/[folder/]<name>.png`` for every animation."""
    out = Path(out)
    result: Dict[str, Dict[str, str]] = {}
    for name in only or names():
        clip = build(name, look)
        gif = save_gif(clip, out / "gifs" / folder / ("%s.gif" % name), scale)
        sheet = out / "sheets" / folder / ("%s.png" % name)
        sheet.parent.mkdir(parents=True, exist_ok=True)
        sprite_sheet(clip, scale).save(sheet)
        result[name] = {"gif": str(gif), "sheet": str(sheet), "frames": str(len(clip))}
    return result


class FileDisplay(Display):
    """Writes the current clip to a GIF file (default ``~/.keebo/now.gif``)."""

    name = "file"

    def __init__(self, path: Path, scale: int = 4) -> None:
        self.path = Path(path)
        self.scale = scale
        self.latest: bytes = b""

    def show(self, clip: Clip) -> None:
        self.latest = gif_bytes(clip, self.scale)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_bytes(self.latest)
        tmp.replace(self.path)
