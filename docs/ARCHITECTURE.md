# How Keebo works

```
 macOS probe ──context──┐                       ┌──> AulaDisplay  (USB HID, keyboard screen)
 (app, tab, idle)       │                       │
                        ▼                       │
 hooks / CLI ──HTTP──> EventBus ──> Brain ──mood──> Companion ──clip──> FileDisplay (~/.keebo/now.gif)
 (git, zsh, agents,     │           (pure state │      ▲                │
  keebo wrap)           │            machine)   │      │                └──> TerminalDisplay
                        └──> Progress (XP, unlocks, projects) ──look──┘
```

| Package | Job |
|---|---|
| `keebo.art` | 64×64 indexed-colour canvas, 16-colour palette, 3×5 font, the parametric Keebo rig (`Pose` → pixels), accessories, props and particle effects. |
| `keebo.animations` | Animation registry (`@animation`), timing helpers, and the core moods and transitions. |
| `keebo.scenes` | Context mini-scenes (coding, writing, watching, ...). |
| `keebo.engine` | `events` (kinds + bus), `brain` (mood state machine), `progression` (XP/forms/unlocks/history), `runtime` (the daemon). |
| `keebo.context` | `rules` (app/url/title → scene) and `macos` (AppleScript + `ioreg` probe). |
| `keebo.display` | Backends: GIF/sprite-sheet export, terminal player, AULA F75 Max uploader. |
| `keebo.integrations` | Local HTTP server, client, `keebo wrap`, git/zsh/Claude Code hooks. |

## Art pipeline

Everything is drawn on a **64×64 logical grid** and scaled 2× with
nearest-neighbour to the screen's 128×128. A 2-pixel "fat pixel" keeps
outlines crisp and readable on a tiny TFT viewed from a metre away, and it
halves the art budget.

Keebo isn't a stack of hand-drawn frames. It's a **parametric rig**:
`Pose(squash, lean, eyes, mouth, arms, feet, form, hat, ...)` → pixels. An
animation is just a function that varies a pose over time. This gives you:

- smooth motion for free (squash and stretch, anticipation, follow-through),
- every animation works with every evolution form and accessory,
- new moods cost a few lines, not a new sprite sheet.

All clips start and end on the neutral standing pose, so a cut between any
two moods reads as a natural transition.

## Mood priority

1. **Reactions** (timed, by priority): victory 80 > failure 70 > agent done 65 > tests pass/fail 60 > ...
2. **Work** (sticky until the end event): `testing` while tests run, `building` while an agent or build runs.
3. **Base**: the context scene for the frontmost app → `idle` → `sleeping` after inactivity.

## Extending

### A new animation

```python
from keebo.animations.base import Look, animation, steps, wave
from keebo.animations.states import stage
from keebo.art.character import draw

@animation("stretch", description="Big morning stretch.")
def stretch(look: Look):
    frames = []
    for t in steps(12):
        c = stage(look, t)
        draw(c, look.pose(t=t, squash=1 + 0.15 * wave(t), arms=(-60, -60)))
        frames.append((c, 100))
    return frames
```

Drop it into `~/.keebo/plugins/stretch.py` (no fork needed) or into
`src/keebo/animations/`. See `examples/plugin_rubber_duck.py`.

### A new context

Add a `Rule` to `DEFAULT_RULES` in `keebo/context/rules.py`, or add one
without touching code in `~/.keebo/contexts.json`:

```json
[{"scene": "duck", "titles": ["*debug*"]}, {"scene": "music", "apps": ["Tidal"]}]
```

### A new reaction

`keebo.engine.brain.REACTIONS` maps an event kind to the clips it plays,
how long it holds, and its priority. Hooks can send any kind, for example
`keebo emit deploy`. Register `REACTIONS["deploy"] = Reaction(("victory",), hold=6, priority=70)`.

### A new accessory

Write `def jetpack(c, p, g)` in `keebo/art/accessories.py` and register it
in `BACK`. Then give it an unlock condition in `progression.UNLOCKS`.

### A new display

Subclass `keebo.display.base.Display` and implement `show(clip)` (plus
`tick()` if you need deferred work).
