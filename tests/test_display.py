import io

from PIL import Image

from keebo.animations import build
from keebo.display import aula
from keebo.display.base import clip_images
from keebo.display.gif import gif_bytes, sprite_sheet


def test_gif_roundtrip_is_128px_and_animated():
    clip = build("idle")
    im = Image.open(io.BytesIO(gif_bytes(clip)))
    assert im.size == (128, 128)
    assert im.n_frames >= 2


def test_sprite_sheet_layout():
    clip = build("celebrating")
    sheet = sprite_sheet(clip, cols=8)
    assert sheet.width == 8 * 128 and sheet.height == 2 * 128


def test_rgb565_little_endian():
    img = Image.new("RGB", (128, 128), (255, 0, 0))
    data = aula.rgb565(img)
    assert len(data) == aula.FRAME_BYTES
    assert data[:2] == bytes([0x00, 0xF8])
    white = aula.rgb565(Image.new("RGB", (128, 128), (255, 255, 255)))
    assert white[:2] == b"\xff\xff"


def test_payload_header_and_padding():
    frames = aula.fit_frames(clip_images(build("thinking")), max_frames=12)
    payload = aula.encode(frames)
    assert payload[0] == len(frames) <= 12
    assert all(15 <= b <= 255 for b in payload[1:1 + len(frames)])
    assert len(payload) % aula.CHUNK == 0
    assert len(payload) >= aula.HEADER + len(frames) * aula.FRAME_BYTES


def test_fit_frames_merges_holds_and_splits_long_ones():
    a = Image.new("RGB", (128, 128), (0, 0, 0))
    b = Image.new("RGB", (128, 128), (9, 9, 9))
    out = aula.fit_frames([(a, 100), (a, 100), (b, 1200)])
    assert [ms for _, ms in out] == [200, 510, 510, 180]


def test_metadata_command_layout():
    pkt = aula.command(aula.CMD_META, slot=1, count=300)
    assert len(pkt) == 64
    assert pkt[:3] == b"\x04\x72\x01" and pkt[8:10] == (300).to_bytes(2, "little")
