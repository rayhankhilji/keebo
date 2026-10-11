"""Display backends: where Keebo's frames end up."""
from __future__ import annotations

from typing import List, Tuple

from PIL import Image

from ..animations.base import Clip
from ..art.canvas import SCALE


def clip_images(clip: Clip, scale: int = SCALE) -> List[Tuple[Image.Image, int]]:
    """RGB images (128x128 at the default scale) with per-frame durations in ms."""
    return [(canvas.to_image(scale).convert("RGB"), ms) for canvas, ms in clip.frames]


class Display:
    """Base class. ``show`` is called whenever the active clip changes."""

    name = "base"

    def show(self, clip: Clip) -> None:  # pragma: no cover - interface
        raise NotImplementedError

    def tick(self) -> None:
        """Called periodically from the main loop (for deferred work)."""

    def close(self) -> None:
        pass
