"""Direct upload to the AULA F75 Max screen over USB HID (macOS, Linux, Windows).

No vendor software, no firmware changes: this speaks the same GIF-slot
protocol AULA's app uses. See docs/HARDWARE.md for the byte-level details
and credits.
"""
from __future__ import annotations

import logging
import struct
import threading
import time
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

from PIL import Image

from ..animations.base import Clip
from .base import Display, clip_images

log = logging.getLogger("keebo.aula")

VID, PID = 0x0C45, 0x800A
USAGE_CMD, USAGE_PIXELS = 0xFF13, 0xFF68
SCREEN = 128
HEADER = 256
FRAME_BYTES = SCREEN * SCREEN * 2
CHUNK = 4096
REPORT = 64
MAX_FRAMES = 255
MIN_DELAY_MS, MAX_DELAY_MS = 30, 510

CMD_BEGIN = 0x18
CMD_META = 0x72
CMD_COMMIT = 0x02


# ---------------------------------------------------------------- encoding (pure)

def rgb565(img: Image.Image) -> bytes:
    """128x128 RGB image -> little-endian RGB565 bytes."""
    if img.size != (SCREEN, SCREEN):
        img = img.resize((SCREEN, SCREEN), Image.NEAREST)
    raw = img.convert("RGB").tobytes()
    out = bytearray(FRAME_BYTES)
    for i in range(SCREEN * SCREEN):
        r, g, b = raw[3 * i], raw[3 * i + 1], raw[3 * i + 2]
        v = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        out[2 * i] = v & 0xFF
        out[2 * i + 1] = v >> 8
    return bytes(out)


def fit_frames(frames: Sequence[Tuple[Image.Image, int]], max_frames: int = 48) -> List[Tuple[Image.Image, int]]:
    """Merge identical neighbours, split over-long holds and decimate to ``max_frames``.

    Uploads cost roughly 20 ms per 4 KB chunk, so fewer frames means Keebo
    reacts faster; holds are expressed with per-frame delays, not copies."""
    merged: List[Tuple[Image.Image, int]] = []
    for im, ms in frames:
        if merged and merged[-1][0].tobytes() == im.tobytes():
            merged[-1] = (merged[-1][0], merged[-1][1] + ms)
        else:
            merged.append((im, ms))
    max_frames = max(1, min(max_frames, MAX_FRAMES))
    if len(merged) > max_frames:
        step = len(merged) / max_frames
        out = []
        for k in range(max_frames):
            a, b = int(round(k * step)), int(round((k + 1) * step))
            out.append((merged[a][0], sum(ms for _, ms in merged[a:max(b, a + 1)])))
        merged = out
    final: List[Tuple[Image.Image, int]] = []
    for im, ms in merged:
        while ms > MAX_DELAY_MS and len(final) < MAX_FRAMES - 1:
            final.append((im, MAX_DELAY_MS))
            ms -= MAX_DELAY_MS
        final.append((im, max(MIN_DELAY_MS, ms)))
    return final[:MAX_FRAMES]


def encode(frames: Sequence[Tuple[Image.Image, int]]) -> bytes:
    """Build the upload payload: 256-byte header + RGB565 frames, padded to 4 KB."""
    if not frames:
        raise ValueError("no frames")
    if len(frames) > MAX_FRAMES:
        raise ValueError("the keyboard holds at most %d frames" % MAX_FRAMES)
    header = bytearray(HEADER)
    header[0] = len(frames)
    for i, (_, ms) in enumerate(frames):
        header[1 + i] = max(1, min(255, int(round(ms / 2))))
    body = b"".join(rgb565(im) for im, _ in frames)
    payload = bytes(header) + body
    pad = (-len(payload)) % CHUNK
    return payload + b"\x00" * pad


def chunks(payload: bytes) -> List[bytes]:
    return [payload[i:i + CHUNK] for i in range(0, len(payload), CHUNK)]


def command(op: int, slot: int = 0, count: int = 0) -> bytes:
    pkt = bytearray(REPORT)
    pkt[0], pkt[1] = 0x04, op
    if op == CMD_META:
        pkt[2] = slot
        struct.pack_into("<H", pkt, 8, count)
    return bytes(pkt)


# ---------------------------------------------------------------- device

class AulaError(RuntimeError):
    pass


@dataclass
class DeviceInfo:
    path: bytes
    usage_page: int
    interface: int
    product: str


def find() -> List[DeviceInfo]:
    try:
        import hid  # type: ignore
    except ImportError as e:  # pragma: no cover - depends on optional extra
        raise AulaError('hidapi is not installed: pip install "keebo[hid]"') from e
    return [DeviceInfo(d["path"], d.get("usage_page", 0), d.get("interface_number", -1),
                       d.get("product_string") or "")
            for d in hid.enumerate(VID, PID)]


class AulaScreen:
    """A connected F75 Max. Use as a context manager."""

    def __init__(self, slot: int = 1, verbose: bool = False) -> None:
        self.slot = slot
        self.verbose = verbose
        self.cmd = None
        self.pix = None

    def __enter__(self) -> "AulaScreen":
        self.open()
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def open(self) -> None:
        import hid  # type: ignore

        devs = find()
        cmd = next((d for d in devs if d.usage_page == USAGE_CMD), None)
        pix = next((d for d in devs if d.usage_page == USAGE_PIXELS), None)
        if cmd is None or pix is None:
            raise AulaError("AULA F75 Max not found over USB. Plug in the USB-C cable (the screen is wired-only) "
                            "and quit AULA's own software.")
        self.cmd, self.pix = hid.device(), hid.device()
        try:
            self.cmd.open_path(cmd.path)
            self.pix.open_path(pix.path)
        except OSError as e:
            self.close()
            raise AulaError("could not open the keyboard (is another app using it?): %s" % e) from e

    def close(self) -> None:
        for d in (self.cmd, self.pix):
            if d is not None:
                try:
                    d.close()
                except Exception:  # noqa: BLE001
                    pass
        self.cmd = self.pix = None

    def _exchange(self, pkt: bytes) -> bool:
        time.sleep(0.035)
        self.cmd.send_feature_report(b"\x00" + pkt)
        time.sleep(0.035)
        reply = bytes(self.cmd.get_feature_report(0, REPORT + 1))
        if len(reply) == REPORT + 1:
            reply = reply[1:]
        ok = len(reply) > 3 and reply[3] == 0x01
        if self.verbose:
            log.info("cmd %02x -> %s", pkt[1], reply[:8].hex())
        return ok

    def _ack(self, timeout_ms: int) -> bool:
        return bool(self.pix.read(128, timeout_ms))

    def upload(self, payload: bytes, progress=None) -> None:
        parts = chunks(payload)
        if not self._exchange(command(CMD_BEGIN)):
            log.debug("begin not acknowledged; continuing")
        self._exchange(command(CMD_META, self.slot, len(parts)))
        self._ack(150)
        for i, part in enumerate(parts):
            self.pix.write(b"\x00" + part)
            if not self._ack(350):
                log.debug("no ack for chunk %d", i)
            if progress:
                progress(i + 1, len(parts))
        if not self._exchange(command(CMD_COMMIT)):
            raise AulaError("the keyboard did not confirm the upload")

    def show_clip(self, clip: Clip, max_frames: int = 48, progress=None) -> int:
        payload = encode(fit_frames(clip_images(clip), max_frames))
        self.upload(payload, progress)
        return len(payload) // CHUNK


class AulaDisplay(Display):
    """Live backend: uploads in a background thread, rate-limited and cached.

    Each upload rewrites the GIF slot, so only real mood changes are sent and
    rapid-fire changes collapse into one upload of the latest clip."""

    name = "aula"

    def __init__(self, min_interval: float = 20.0, max_frames: int = 48, slot: int = 1) -> None:
        self.min_interval = min_interval
        self.max_frames = max_frames
        self.slot = slot
        self._pending: Optional[Clip] = None
        self._last_sent_key: Optional[str] = None
        self._last_upload = 0.0
        self._cache: dict = {}
        self._lock = threading.Lock()
        self._busy = False

    def _key(self, clip: Clip) -> str:
        return "%s:%d:%d" % (clip.name, len(clip), clip.duration_ms)

    def show(self, clip: Clip) -> None:
        with self._lock:
            self._pending = clip
        self.tick()

    def tick(self) -> None:
        with self._lock:
            clip = self._pending
            if clip is None or self._busy:
                return
            if self._key(clip) == self._last_sent_key:
                self._pending = None
                return
            if time.monotonic() - self._last_upload < self.min_interval:
                return
            self._pending = None
            self._busy = True
        threading.Thread(target=self._send, args=(clip,), daemon=True).start()

    def _send(self, clip: Clip) -> None:
        key = self._key(clip)
        try:
            payload = self._cache.get(key)
            if payload is None:
                payload = self._cache[key] = encode(fit_frames(clip_images(clip), self.max_frames))
            with AulaScreen(self.slot) as screen:
                screen.upload(payload)
            self._last_sent_key = key
            log.info("uploaded %s (%d KB)", clip.name, len(payload) // 1024)
        except Exception as e:  # noqa: BLE001 - keyboard asleep/unplugged: retry on next tick
            log.warning("upload failed: %s", e)
            with self._lock:
                if self._pending is None:
                    self._pending = clip
        finally:
            self._last_upload = time.monotonic()
            with self._lock:
                self._busy = False
