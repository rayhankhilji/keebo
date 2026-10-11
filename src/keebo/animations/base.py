"""Animation registry and timing helpers.

An animation is a function ``fn(look) -> Clip``. Register one with
``@animation("name")`` and it becomes available to the engine, the CLI
(`keebo render name`) and the asset exporter.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from ..art.canvas import Canvas
from ..art.character import Pose

Frame = Tuple[Canvas, int]  # (canvas, duration in ms)


@dataclass
class Look:
    """How Keebo currently looks: evolution form, worn items and history."""

    form: int = 1
    hat: Optional[str] = None
    face: Optional[str] = None
    neck: Optional[str] = None
    back: Optional[str] = None
    projects: List[dict] = field(default_factory=list)
    level: int = 1
    xp_frac: float = 0.0
    show_hud: bool = False
    from_form: Optional[int] = None  # for "evolving"
    skin: str = "inky"

    def pose(self, **kw) -> Pose:
        base = dict(form=self.form, hat=self.hat, face_acc=self.face, neck=self.neck, back=self.back, skin=self.skin)
        base.update(kw)
        return Pose(**base)

    def key(self) -> str:
        return "%s-f%d-%s-%s-%s-%s-%d" % (self.skin, self.form, self.hat, self.face, self.neck, self.back,
                                          len(self.projects))


@dataclass
class Clip:
    name: str
    frames: List[Frame]
    loop: bool = True

    @property
    def duration_ms(self) -> int:
        return sum(d for _, d in self.frames)

    def __len__(self) -> int:
        return len(self.frames)


@dataclass
class AnimationSpec:
    name: str
    fn: Callable[[Look], Clip]
    kind: str            # "state", "scene" or "transition"
    loop: bool
    description: str


REGISTRY: Dict[str, AnimationSpec] = {}


def animation(name: str, kind: str = "state", loop: bool = True, description: str = ""):
    def deco(fn: Callable[[Look], List[Frame]]):
        def build(look: Look) -> Clip:
            return Clip(name, fn(look), loop)

        REGISTRY[name] = AnimationSpec(name, build, kind, loop, description or (fn.__doc__ or "").strip())
        return build

    return deco


def get(name: str) -> AnimationSpec:
    from . import load_all

    load_all()
    return REGISTRY[name]


def build(name: str, look: Optional[Look] = None) -> Clip:
    return get(name).fn(look or Look())


def names(kind: Optional[str] = None) -> List[str]:
    from . import load_all

    load_all()
    return [n for n, s in REGISTRY.items() if kind is None or s.kind == kind]


# ---------------------------------------------------------------- easing

def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def ease_out(t: float) -> float:
    return 1 - (1 - t) ** 3


def ease_in_out(t: float) -> float:
    return 3 * t * t - 2 * t * t * t


def wave(t: float, period: float = 1.0, phase: float = 0.0) -> float:
    """Sine in [-1, 1] with the given period (in loop fractions)."""
    return math.sin(2 * math.pi * (t / period + phase))


def bounce(t: float) -> float:
    """0 -> 1 -> 0 parabola, for jumps."""
    return 4 * t * (1 - t)


def steps(n: int) -> Sequence[float]:
    """n evenly spaced loop positions in [0, 1)."""
    return [i / n for i in range(n)]
