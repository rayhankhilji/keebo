"""Play clips in a truecolor terminal using half-block characters."""
from __future__ import annotations

import sys
import threading
import time
from typing import List, Optional, TextIO

from ..animations.base import Clip
from ..art.palette import PALETTE
from .base import Display


def frame_ansi(canvas, background: int = 0) -> List[str]:
    data = canvas.data
    h, w = data.shape
    lines = []
    for y in range(0, h, 2):
        row = []
        for x in range(w):
            top = int(data[y, x])
            bot = int(data[y + 1, x]) if y + 1 < h else background
            tr, tg, tb = PALETTE[top if top < len(PALETTE) else background]
            br, bg, bb = PALETTE[bot if bot < len(PALETTE) else background]
            row.append("\x1b[38;2;%d;%d;%dm\x1b[48;2;%d;%d;%dm\u2580" % (tr, tg, tb, br, bg, bb))
        lines.append("".join(row) + "\x1b[0m")
    return lines


def play(clip: Clip, loops: int = 1, out: TextIO = sys.stdout, stop: Optional[threading.Event] = None) -> None:
    rendered = [(frame_ansi(c), ms) for c, ms in clip.frames]
    out.write("\x1b[?25l")
    try:
        n = 0
        while loops <= 0 or n < loops:
            for lines, ms in rendered:
                if stop is not None and stop.is_set():
                    return
                out.write("\x1b[H" + "\n".join(lines) + "\n")
                out.flush()
                time.sleep(ms / 1000)
            n += 1
    finally:
        out.write("\x1b[?25h")
        out.flush()


class TerminalDisplay(Display):
    """Animates the active clip in this terminal (great for trying Keebo out)."""

    name = "terminal"

    def __init__(self, out: TextIO = sys.stdout) -> None:
        self.out = out
        self._stop: Optional[threading.Event] = None
        self._thread: Optional[threading.Thread] = None
        out.write("\x1b[2J")

    def show(self, clip: Clip) -> None:
        self.close()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=play, args=(clip, 0, self.out, self._stop), daemon=True)
        self._thread.start()

    def close(self) -> None:
        if self._stop is not None:
            self._stop.set()
            if self._thread is not None:
                self._thread.join(timeout=1)
