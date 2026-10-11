<div align="center">

<img src="assets/brand/banner.gif" alt="Keebo: Inky and Axo, pixel pets for your keyboard" width="100%">

**Tiny pixel-art companions for the 128×128 screen on your AULA F75 Max**<br>
They code when you code, panic when your tests run, throw a party when they pass<br>
and faceplant (then dust themselves off) when the build breaks.

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-c9a7ff?style=flat-square&labelColor=1d193a)](#install)
[![macOS](https://img.shields.io/badge/macOS-Intel%20%26%20Apple%20silicon-c9a7ff?style=flat-square&labelColor=1d193a)](#install)
[![AULA F75 Max](https://img.shields.io/badge/AULA-F75%20Max-ffb3c7?style=flat-square&labelColor=1d193a)](docs/HARDWARE.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-ffd85e?style=flat-square&labelColor=1d193a)](LICENSE)

<img src="assets/brand/keyboard.gif" alt="Inky animating on the screen of an AULA F75 Max" width="760">

</div>

---

## Meet Inky and Axo

Keebo comes as two creatures, and you can swap between them whenever you like.

<table>
<tr>
<td align="center" width="50%"><img src="assets/gifs/inky/idle.gif" width="192" alt="Inky idling"><br><b>Inky</b><br><sub>A small lilac octopus. All tentacles, all heart.<br>Types with four arms at once.</sub></td>
<td align="center" width="50%"><img src="assets/gifs/axo/idle.gif" width="192" alt="Axo idling"><br><b>Axo</b><br><sub>A pink axolotl whose frilly gills wiggle when it is happy,<br>which is most of the time.</sub></td>
</tr>
</table>

```sh
keebo skin axo     # switch to Axo
keebo skin inky    # back to Inky (the default)
```

Your level, XP, unlocks and project history belong to you, not to the
creature, so switching never resets anything.

Both are drawn on a 64×64 grid and shown at exactly 2× on the keyboard's
128×128 screen, so every pixel stays crisp. Neither is a pile of hand-pasted
frames. Each one is a **parametric rig**: squash and stretch, eyes, mouth,
arms, tentacles, gills, evolution form and accessories are all pose
parameters. That is why every animation moves smoothly, and why every
animation works for both creatures in every outfit they unlock.

## Every mood, both creatures

Each pair below is the real 128×128 GIF that gets sent to the keyboard,
with Inky on the left and Axo on the right.

<table>
<tr>
<td align="center" width="25%"><img src="assets/gifs/inky/idle.gif" width="96" alt="Inky idle"> <img src="assets/gifs/axo/idle.gif" width="96" alt="Axo idle"><br><b><code>idle</code></b><br><sub>breathing, blinking, glancing around</sub></td>
<td align="center" width="25%"><img src="assets/gifs/inky/sleeping.gif" width="96" alt="Inky sleeping"> <img src="assets/gifs/axo/sleeping.gif" width="96" alt="Axo sleeping"><br><b><code>sleeping</code></b><br><sub>nightcap on, slow breaths, drifting Zzz</sub></td>
<td align="center" width="25%"><img src="assets/gifs/inky/wake.gif" width="96" alt="Inky wake"> <img src="assets/gifs/axo/wake.gif" width="96" alt="Axo wake"><br><b><code>wake</code></b><br><sub>blinks awake, stretches, hops</sub></td>
<td align="center" width="25%"><img src="assets/gifs/inky/thinking.gif" width="96" alt="Inky thinking"> <img src="assets/gifs/axo/thinking.gif" width="96" alt="Axo thinking"><br><b><code>thinking</code></b><br><sub>chin scratch, thought bubble, light bulb</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="assets/gifs/inky/building.gif" width="96" alt="Inky building"> <img src="assets/gifs/axo/building.gif" width="96" alt="Axo building"><br><b><code>building</code></b><br><sub>hard hat on, stacking bricks for your agent</sub></td>
<td align="center" width="25%"><img src="assets/gifs/inky/testing.gif" width="96" alt="Inky testing"> <img src="assets/gifs/axo/testing.gif" width="96" alt="Axo testing"><br><b><code>testing</code></b><br><sub>frantic typing, sweat and speed lines</sub></td>
<td align="center" width="25%"><img src="assets/gifs/inky/celebrating.gif" width="96" alt="Inky celebrating"> <img src="assets/gifs/axo/celebrating.gif" width="96" alt="Axo celebrating"><br><b><code>celebrating</code></b><br><sub>party hat, jumps and confetti</sub></td>
<td align="center" width="25%"><img src="assets/gifs/inky/confused.gif" width="96" alt="Inky confused"> <img src="assets/gifs/axo/confused.gif" width="96" alt="Axo confused"><br><b><code>confused</code></b><br><sub>head tilts, question marks pop</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="assets/gifs/inky/frustrated.gif" width="96" alt="Inky frustrated"> <img src="assets/gifs/axo/frustrated.gif" width="96" alt="Axo frustrated"><br><b><code>frustrated</code></b><br><sub>stomping under a tiny storm cloud</sub></td>
<td align="center" width="25%"><img src="assets/gifs/inky/failure.gif" width="96" alt="Inky failure"> <img src="assets/gifs/axo/failure.gif" width="96" alt="Axo failure"><br><b><code>failure</code></b><br><sub>collapses into a pancake while the build burns</sub></td>
<td align="center" width="25%"><img src="assets/gifs/inky/recovery.gif" width="96" alt="Inky recovery"> <img src="assets/gifs/axo/recovery.gif" width="96" alt="Axo recovery"><br><b><code>recovery</code></b><br><sub>peels off the floor, bandage, thumbs up</sub></td>
<td align="center" width="25%"><img src="assets/gifs/inky/victory.gif" width="96" alt="Inky victory"> <img src="assets/gifs/axo/victory.gif" width="96" alt="Axo victory"><br><b><code>victory</code></b><br><sub>trophy held high in the spotlight</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="assets/gifs/inky/evolving.gif" width="96" alt="Inky evolving"> <img src="assets/gifs/axo/evolving.gif" width="96" alt="Axo evolving"><br><b><code>evolving</code></b><br><sub>glows, flashes and grows into a new form</sub></td>
</tr>
</table>

## They react to your work

| When... | Keebo... | Clip |
|---|---|---|
| you open a project | blinks awake, stretches, hops | `wake` |
| a coding agent starts a task | puts on a hard hat and stacks bricks | `building` |
| tests are running | types frantically, sweating, with speed lines | `testing` |
| tests pass | party hat, jumps and confetti | `celebrating` |
| tests fail | tilts its head, then stomps under a storm cloud | `confused` → `frustrated` |
| the build fails | collapses into a pancake while the build catches fire | `failure` |
| you fix it | peels itself off the floor, slaps on a bandage, thumbs up | `recovery` |
| a task completes | raises a trophy in the spotlight | `victory` |
| you level up | glows, flashes and evolves into its next form | `evolving` |
| you go quiet for a while | puts on a nightcap and drifts off | `sleeping` |
| nothing in particular | breathes, blinks and glances around | `idle` |

## They know what you are doing

Keebo checks the frontmost app and the active browser tab, locally, using
nothing but macOS's built-in AppleScript, and acts out a matching mini-scene.

<table>
<tr>
<td align="center" width="25%"><img src="assets/gifs/inky/coding.gif" width="96" alt="Inky coding"> <img src="assets/gifs/axo/coding.gif" width="96" alt="Axo coding"><br><b><code>coding</code></b><br><sub>typing on a mini MacBook<br><i>VS Code, Cursor, Xcode, JetBrains, Zed, GitHub, Claude, Devin</i></sub></td>
<td align="center" width="25%"><img src="assets/gifs/inky/terminal.gif" width="96" alt="Inky terminal"> <img src="assets/gifs/axo/terminal.gif" width="96" alt="Axo terminal"><br><b><code>terminal</code></b><br><sub>shades on, green text scrolling<br><i>Terminal, iTerm2, Warp, Ghostty</i></sub></td>
<td align="center" width="25%"><img src="assets/gifs/inky/writing.gif" width="96" alt="Inky writing"> <img src="assets/gifs/axo/writing.gif" width="96" alt="Axo writing"><br><b><code>writing</code></b><br><sub>writing a letter with a quill<br><i>Outlook, Mail, Google Docs, Word, Notion</i></sub></td>
<td align="center" width="25%"><img src="assets/gifs/inky/watching.gif" width="96" alt="Inky watching"> <img src="assets/gifs/axo/watching.gif" width="96" alt="Axo watching"><br><b><code>watching</code></b><br><sub>munching popcorn in front of the TV<br><i>YouTube, Netflix, Twitch</i></sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="assets/gifs/inky/music.gif" width="96" alt="Inky music"> <img src="assets/gifs/axo/music.gif" width="96" alt="Axo music"><br><b><code>music</code></b><br><sub>headphones on, bopping<br><i>Spotify, Apple Music</i></sub></td>
<td align="center" width="25%"><img src="assets/gifs/inky/chatting.gif" width="96" alt="Inky chatting"> <img src="assets/gifs/axo/chatting.gif" width="96" alt="Axo chatting"><br><b><code>chatting</code></b><br><sub>speech bubbles flying<br><i>Slack, Discord, Messages</i></sub></td>
<td align="center" width="25%"><img src="assets/gifs/inky/meeting.gif" width="96" alt="Inky meeting"> <img src="assets/gifs/axo/meeting.gif" width="96" alt="Axo meeting"><br><b><code>meeting</code></b><br><sub>on camera in a bow tie<br><i>Zoom, Meet, Teams</i></sub></td>
<td align="center" width="25%"><img src="assets/gifs/inky/designing.gif" width="96" alt="Inky designing"> <img src="assets/gifs/axo/designing.gif" width="96" alt="Axo designing"><br><b><code>designing</code></b><br><sub>painting at an easel<br><i>Figma, Photoshop, Aseprite</i></sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="assets/gifs/inky/reading.gif" width="96" alt="Inky reading"> <img src="assets/gifs/axo/reading.gif" width="96" alt="Axo reading"><br><b><code>reading</code></b><br><sub>nose in a big book<br><i>Preview, Books, arXiv, PDFs</i></sub></td>
<td align="center" width="25%"><img src="assets/gifs/inky/gaming.gif" width="96" alt="Inky gaming"> <img src="assets/gifs/axo/gaming.gif" width="96" alt="Axo gaming"><br><b><code>gaming</code></b><br><sub>mashing a gamepad<br><i>Steam, chess.com</i></sub></td>
<td align="center" width="25%"><img src="assets/gifs/inky/browsing.gif" width="96" alt="Inky browsing"> <img src="assets/gifs/axo/browsing.gif" width="96" alt="Axo browsing"><br><b><code>browsing</code></b><br><sub>surfing the web, literally<br><i>any other browser tab</i></sub></td>
</tr>
</table>

Want more? One line of JSON or a tiny plugin file adds a new app or scene
([see Extending](#extending)).

## They grow with you

<div align="center">
<img src="assets/brand/forms.png" alt="Baby, Buddy, Clicky, Mecha and Legend forms for both creatures" width="760">
</div>

- **XP from finished work.** Commits, green test runs, finished builds and completed agent tasks all count.
- **Five forms.** Baby, then Buddy (level 3), Clicky (level 8, spots and RGB underglow), Mecha (level 15, visor and antenna) and finally Legend (level 25, crown and cape).
- **Seventeen accessories** to unlock through levels and small achievements. Both creatures can wear all of them.

<div align="center">
<img src="assets/brand/wardrobe.png" alt="The accessory wardrobe on Inky and Axo" width="760">
</div>

- **Your projects become their history.** Every project you work on puts a
  trophy on the shelf behind them: a cup, a star once you have shipped ten
  tasks, or a battle flag for the hard-fought ones.
- **They are kind.** XP never goes down. A failure followed by a fix earns a
  *comeback* bonus (and the bandage). A long break makes Keebo *well
  rested*, worth 1.5× XP for an hour. Breaks are never punished.

## See it live

`keebo run` serves a pixel-perfect live preview at **http://127.0.0.1:7428**,
so you can meet Keebo before the keyboard is even plugged in.

<div align="center">
<img src="assets/brand/preview.png" alt="The live preview page showing Axo celebrating at level 5" width="560">
</div>

`keebo status` shows how your companion is doing:

```text
$ keebo status
Keebo (axo)  ·  Buddy  ·  level 5  ·  485 XP  (75% to next)
mood: idle
equipped: face=glasses
unlocked: partyhat, hardhat, headphones, glasses, shades
projects:
  keebo                  15 XP    0 tasks  cup
  builddit              275 XP    6 tasks  cup
  widefive              195 XP    4 tasks  cup
```

---

## Install

You need macOS (Intel or Apple silicon), Python 3.9 or newer, and an AULA
F75 Max **plugged in with a USB-C cable**. The screen only works over a
wired connection: Bluetooth and the 2.4 GHz dongle can't carry pixels.

```sh
git clone https://github.com/rayhankhilji/keebo && cd keebo
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[hid]"
```

Quit AULA's own app if it's running. Then:

```sh
keebo skin axo                 # or inky (the default)
keebo device list              # finds the keyboard (0c45:800a)
keebo device push celebrating  # one-off: put a clip on the screen
keebo run --display aula       # the live companion
```

With no display flag, `keebo run` only writes `~/.keebo/now.gif` and serves
the live preview page.

> **Permissions.** The first time Keebo checks which app is in front, macOS
> asks whether your terminal may control *System Events* (and your browser,
> to read the tab URL). Say yes, or manage it later in System Settings →
> Privacy & Security → Automation. Keebo never reads keystrokes, and
> nothing leaves your machine.

**Start at login:** copy [`examples/launchd.plist`](examples/launchd.plist)
into `~/Library/LaunchAgents/` and fix the path to `keebo`.

## Hook it up to your work

Keebo listens on `127.0.0.1:7428`. Anything that can run a shell command or
make an HTTP request can poke it.

```sh
# wrap any command: Keebo guesses tests / build / agent from the command
keebo wrap -- pytest -q
keebo wrap -- npm run build
keebo wrap --kind agent -- claude -p "fix the flaky test"

# or send events directly
keebo emit project_start
keebo emit task_complete --project keebo
curl -s localhost:7428/event -d '{"kind":"tests_pass","project":"keebo"}'
```

| Integration | Setup |
|---|---|
| **git**: a little cheer on every commit | `keebo hooks git` (inside a repo) |
| **zsh**: wake on `cd` into a project, plus `kt`/`kb`/`ka` aliases | `keebo hooks zsh >> ~/.zshrc` |
| **Claude Code**: build while the agent works, victory when it stops | `keebo hooks claude`, then merge the output into `~/.claude/settings.json` |
| **Anything else** | `POST /event {"kind": ..., "project": ...}` |

Event kinds: `project_start`, `agent_start`, `agent_done`, `tests_start`,
`tests_pass`, `tests_fail`, `build_start`, `build_pass`, `build_fail`,
`task_complete`, `commit`, `thinking`, `confused`.

## Command line

```text
keebo run       [--display aula|terminal|file]... [--hud] [--sleep-after MIN]
keebo skin      [inky|axo]                 show or switch creature
keebo list                                 every animation and scene
keebo preview   coding victory [--skin axo]  play in your terminal (truecolor)
keebo render    building -o out            GIF + sprite sheet for one or more clips
keebo export    -o assets                  GIFs + sprite sheets for everything, both skins
keebo status                               level, XP, unlocks, project history
keebo equip     tophat                     wear something you've unlocked
keebo context                              what Keebo thinks you're doing right now
keebo device    list | push <clip|file.gif> [--dry-run]
keebo emit      <kind> [--project NAME]
keebo wrap      [--kind test|build|agent|task] -- <command>
keebo hooks     git | zsh | claude
```

## Sprite sheets and GIFs

Every clip for both skins is pre-rendered in [`assets/gifs/inky`](assets/gifs/inky)
and [`assets/gifs/axo`](assets/gifs/axo) (128×128, also ready for AULA's own
software), with matching sprite sheets in [`assets/sheets/`](assets/sheets)
(8 frames per row). Regenerate them with `keebo export`. The README
art comes from `python scripts/brand.py`.

## Extending

Keebo is built to grow. All of these take a few lines each, and
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) walks through every one:

- **A new animation or scene**: decorate a function with `@animation("name")`
  and drop the file into `~/.keebo/plugins/`. No fork needed. See
  [`examples/plugin_rubber_duck.py`](examples/plugin_rubber_duck.py).
- **A new context**: add `{"scene": "duck", "titles": ["*debug*"]}` to
  `~/.keebo/contexts.json`.
- **A new reaction**: map an event kind to clips in `brain.REACTIONS`.
- **A new accessory**: a draw function plus an unlock rule.
- **A new creature**: add a colour set to `SKINS` and a silhouette branch in `art/character.py`.
- **A new display**: subclass `Display`.

## How the keyboard part works

Keebo talks to the F75 Max's screen directly over USB HID, using the same
GIF-slot upload protocol as AULA's own app. It needs no vendor software,
modifies no firmware and never touches the keyboard's settings. Clips are
encoded as RGB565, uploaded in 4 KB chunks, rate-limited and cached, so
the screen only changes when Keebo's mood does. Byte-level details and
credits to the community reverse-engineering work are in
[docs/HARDWARE.md](docs/HARDWARE.md).

**FAQ**

- *Bluetooth?* No. The screen is USB-only. You can still type over
  Bluetooth while the cable is plugged in.
- *Will it wear out the keyboard?* Each upload rewrites the GIF slot,
  which is exactly what the official app does. Keebo only uploads when its
  mood actually changes, rate-limited (`--min-upload-interval`).
- *The keyboard went dark?* The board sleeps 5 minutes after your last key
  press and drops off USB. Keebo re-sends the current clip when it wakes.

## Development

```sh
pip install -e ".[dev,hid]"
pytest           # art, animations, mood engine, XP, contexts, encoder, HTTP
ruff check .
```

## License

[MIT](LICENSE) © Rayhan Khilji. Protocol knowledge comes from the open-source AULA community; see [docs/HARDWARE.md](docs/HARDWARE.md).
