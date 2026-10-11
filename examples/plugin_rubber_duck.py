"""Example plugin: a rubber-duck debugging scene.

Copy to ~/.keebo/plugins/ and add a context rule so it plays while you
debug, e.g. in ~/.keebo/contexts.json:

    [{"scene": "duck", "titles": ["*debug*"]}]

Then `keebo render duck` or `keebo preview duck`.
"""
from keebo.animations.base import Look, animation, steps, wave
from keebo.animations.states import stage
from keebo.art import props
from keebo.art.character import draw
from keebo.art.palette import EMBER, INK, SUN


@animation("duck", kind="scene", description="Explaining the bug to a rubber duck.")
def duck(look: Look):
    frames = []
    for i, t in enumerate(steps(12)):
        c = stage(look, t)
        p = look.pose(t=t, x=22, look=(1, 0), mouth="o" if i % 2 else "smile", arms=(55, 20 + 20 * (i % 2)))
        draw(c, p)
        bob = int(wave(t * 2))
        c.ellipse(46, 46 + bob, 6, 4, SUN)        # body
        c.disc(49, 40 + bob, 3, SUN)              # head
        c.rect(52, 40 + bob, 3, 2, EMBER)         # beak
        c.px(49, 39 + bob, INK)                   # eye
        if i % 4 == 3:
            props.question(c, 52, 28, SUN, big=False)
        frames.append((c, 120))
    return frames
