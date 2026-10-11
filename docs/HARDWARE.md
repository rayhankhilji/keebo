# Talking to the AULA F75 Max screen

Keebo pushes its animations straight to the keyboard's 128×128 TFT over USB.
It doesn't need AULA's Windows software or modified firmware, and it never
writes to the keyboard's flash beyond the GIF slot the official app already
uses. This is how we "jailbreak" the screen: it opens up the screen and does
nothing to the board itself.

## Requirements

- The keyboard plugged in with a **USB-C data cable**. The screen only works
  over a wired connection. The 2.4 GHz dongle and Bluetooth carry key
  presses and settings, but not pixels.
- `pip install "keebo[hid]"`, which installs the `hidapi` Python binding.
  macOS ships the HID framework, so you don't need anything else.
- Quit AULA's own software first. Only one program can hold the command
  interface at a time.

```sh
keebo device list            # should show 0c45:800a with pages ff13 and ff68
keebo device push assets/gifs/celebrating.gif
keebo run --display aula     # the live companion
```

## Protocol (as implemented in `keebo/display/aula.py`)

| Item | Value |
|---|---|
| USB id (wired) | `0c45:800a` (SONiX) |
| Command channel | usage page `0xff13`, 64-byte **feature** reports, report id 0 |
| Pixel channel | usage page `0xff68`, 4096-byte **output** reports, 128-byte ACK input reports |

Upload sequence:

1. `04 18`: begin.
2. `04 72`: slot at byte 2 (`1`), chunk count as a little-endian u16 at bytes 8–9.
3. Each 4096-byte chunk goes out as an output report, followed by a wait of up to 350 ms for the ACK.
4. `04 02`: commit. The screen only changes once this arrives.

For every command, Keebo waits about 35 ms, sends `SET_FEATURE`, waits about
35 ms, then reads `GET_FEATURE`. If byte 3 of the reply is `0x01`, the
keyboard accepted the command.

Payload: a 256-byte header (frame count in byte 0, then one delay byte per
frame in 2 ms units, usable range about 30–510 ms), followed by
`frames × 128 × 128` pixels of little-endian RGB565, zero-padded to a
multiple of 4096 bytes. The keyboard holds up to 255 frames.

## Behaviour to know about

- **Uploads aren't instant.** A 24-frame clip is about 192 chunks, which
  takes a few seconds. Keebo's device profile therefore keeps clips short,
  holds poses with per-frame delays instead of duplicate frames, caches
  encoded clips, and rate-limits uploads (`min_upload_interval`, 20 s by
  default). Short-lived reactions are merged into the next upload.
- Each upload rewrites the GIF slot, the same thing the official app does.
  Keebo uploads only when the mood actually changes, so normal use adds up
  to a few dozen writes a day.
- The keyboard sleeps after 5 minutes without a physical key press and drops
  off USB. Keebo notices, waits, and re-sends the current clip when it
  comes back.

## Credits

The protocol was reverse-engineered by the community. Keebo's encoder is
its own implementation, built from these MIT-licensed projects:

- [VitalyArt/Aula-F75-Max-Driver](https://github.com/VitalyArt/Aula-F75-Max-Driver)
- [schiz0x00/keyboard-screen](https://github.com/schiz0x00/keyboard-screen) (`docs/protocol.md`)
- [c0deJedi/aula-f75](https://github.com/c0deJedi/aula-f75)
- [RoseWaveStudio/Aula-F75-Max-OSX](https://github.com/RoseWaveStudio/Aula-F75-Max-OSX)
