"""XP, levels, evolution forms, unlockable accessories and project history.

Design rules (deliberately kind):

* Work earns XP; nothing ever takes XP away.
* Setbacks are funny, not costly: a failure followed by a fix earns a
  *comeback* bonus and, the first time, the bandage accessory.
* Breaks are rewarded: coming back after a long pause grants a
  "well rested" multiplier for the next hour.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from . import events as E

XP_REWARDS: Dict[str, int] = {
    E.PROJECT_START: 5,
    E.COMMIT: 5,
    E.BUILD_PASS: 10,
    E.TESTS_PASS: 15,
    E.AGENT_DONE: 20,
    E.TASK_COMPLETE: 30,
}
COMEBACK_BONUS = 10
RESTED_AFTER = 4 * 3600      # a break this long earns "well rested"
RESTED_FOR = 3600
RESTED_MULT = 1.5

# level at which each evolution form unlocks
FORM_LEVELS: List[Tuple[int, int]] = [(1, 0), (3, 1), (8, 2), (15, 3), (25, 4)]

# accessory -> (slot, how it unlocks). Level unlocks are "lvl:N", achievements are named.
UNLOCKS: Dict[str, Tuple[str, str]] = {
    "hardhat": ("hat", "lvl:2"),
    "headphones": ("hat", "lvl:4"),
    "glasses": ("face", "lvl:5"),
    "scarf": ("neck", "lvl:6"),
    "bowtie": ("neck", "lvl:7"),
    "beanie": ("hat", "lvl:9"),
    "goggles": ("face", "lvl:11"),
    "cape": ("back", "lvl:12"),
    "tophat": ("hat", "lvl:14"),
    "monocle": ("face", "lvl:17"),
    "wings": ("back", "lvl:20"),
    "wizard": ("hat", "lvl:22"),
    "crown": ("hat", "lvl:30"),
    "partyhat": ("hat", "first_green"),      # first passing test run
    "bandage": ("face", "comeback"),         # fix something after it broke
    "shades": ("face", "ten_victories"),
    "nightcap": ("hat", "night_owl"),        # finish a task between 00:00 and 05:00
}


def xp_for_level(level: int) -> int:
    """Total XP needed to *reach* ``level`` (level 1 = 0)."""
    return int(round(40 * (level - 1) ** 1.6))


def level_for_xp(xp: int) -> int:
    lvl = 1
    while xp_for_level(lvl + 1) <= xp:
        lvl += 1
    return lvl


def form_for_level(level: int) -> int:
    form = 0
    for need, f in FORM_LEVELS:
        if level >= need:
            form = f
    return form


@dataclass
class Project:
    name: str
    xp: int = 0
    tasks: int = 0
    passes: int = 0
    fails: int = 0
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)

    @property
    def trophy(self) -> str:
        if self.tasks >= 10:
            return "star"
        if self.fails > self.passes:
            return "flag"    # a battle flag: hard-fought
        return "cup"


@dataclass
class Gain:
    xp: int = 0
    levelled: bool = False
    evolved: bool = False
    unlocked: List[str] = field(default_factory=list)
    note: str = ""


@dataclass
class Progress:
    xp: int = 0
    victories: int = 0
    achievements: List[str] = field(default_factory=list)
    unlocked: List[str] = field(default_factory=list)
    equipped: Dict[str, Optional[str]] = field(default_factory=lambda: {"hat": None, "face": None,
                                                                        "neck": None, "back": None})
    auto_equip: bool = True
    skin: str = "inky"
    projects: Dict[str, Project] = field(default_factory=dict)
    last_event: float = 0.0
    rested_until: float = 0.0
    broken: Dict[str, bool] = field(default_factory=dict)   # project -> currently failing

    # ------------------------------------------------------------ derived

    @property
    def level(self) -> int:
        return level_for_xp(self.xp)

    @property
    def form(self) -> int:
        return form_for_level(self.level)

    @property
    def level_frac(self) -> float:
        lo, hi = xp_for_level(self.level), xp_for_level(self.level + 1)
        return (self.xp - lo) / max(1, hi - lo)

    def history(self, n: int = 5) -> List[dict]:
        """Most recent projects as shelf items (name + trophy kind)."""
        ps = sorted(self.projects.values(), key=lambda p: p.last_seen)[-n:]
        return [{"name": p.name, "trophy": p.trophy, "tasks": p.tasks} for p in ps]

    def look(self, show_hud: bool = False):
        from ..animations.base import Look

        eq = self.equipped
        return Look(form=self.form, hat=eq.get("hat"), face=eq.get("face"), neck=eq.get("neck"),
                    back=eq.get("back"), projects=self.history(), level=self.level,
                    xp_frac=self.level_frac, show_hud=show_hud, skin=self.skin)

    # ------------------------------------------------------------ updates

    def record(self, ev: E.Event) -> Gain:
        now = ev.ts
        gain = Gain()
        if self.last_event and now - self.last_event >= RESTED_AFTER:
            self.rested_until = now + RESTED_FOR
            gain.note = "well rested"
        if ev.kind not in (E.CONTEXT, E.ACTIVITY, E.IDLE):
            self.last_event = now

        proj = None
        if ev.project:
            proj = self.projects.get(ev.project)
            if proj is None:
                proj = self.projects[ev.project] = Project(ev.project, first_seen=now, last_seen=now)
            proj.last_seen = now

        key = ev.project or "_"
        base = XP_REWARDS.get(ev.kind, 0)
        if ev.kind in (E.TESTS_FAIL, E.BUILD_FAIL):
            self.broken[key] = True
            if proj:
                proj.fails += 1
        elif ev.kind in (E.TESTS_PASS, E.BUILD_PASS):
            if proj:
                proj.passes += 1
            if ev.kind == E.TESTS_PASS:
                self._achieve("first_green", gain)
            if self.broken.pop(key, False):
                base += COMEBACK_BONUS
                gain.note = gain.note or "comeback!"
                self._achieve("comeback", gain)
        if ev.kind in (E.TASK_COMPLETE, E.AGENT_DONE):
            self.victories += 1
            if proj:
                proj.tasks += 1
            if self.victories >= 10:
                self._achieve("ten_victories", gain)
            hour = time.localtime(now).tm_hour
            if hour < 5:
                self._achieve("night_owl", gain)

        if base:
            mult = RESTED_MULT if now < self.rested_until else 1.0
            gain.xp = int(round(base * mult))
            before_lvl, before_form = self.level, self.form
            self.xp += gain.xp
            if proj:
                proj.xp += gain.xp
            gain.levelled = self.level > before_lvl
            gain.evolved = self.form > before_form
            for lvl in range(before_lvl + 1, self.level + 1):
                self._achieve("lvl:%d" % lvl, gain)
        return gain

    def _achieve(self, name: str, gain: Gain) -> None:
        if name not in self.achievements:
            self.achievements.append(name)
        for item, (slot, cond) in UNLOCKS.items():
            if cond == name and item not in self.unlocked:
                self.unlocked.append(item)
                gain.unlocked.append(item)
                if self.auto_equip and slot in ("face", "neck", "back") and not self.equipped.get(slot):
                    if item not in ("bandage",):
                        self.equipped[slot] = item

    def equip(self, item: Optional[str], slot: Optional[str] = None) -> None:
        if item is None:
            if slot:
                self.equipped[slot] = None
            return
        if item not in self.unlocked:
            raise ValueError("%s is still locked (%s)" % (item, UNLOCKS.get(item, ("?", "?"))[1]))
        self.equipped[UNLOCKS[item][0]] = item

    # ------------------------------------------------------------ persistence

    def to_json(self) -> dict:
        d = asdict(self)
        d["projects"] = {k: asdict(v) for k, v in self.projects.items()}
        return d

    @classmethod
    def from_json(cls, d: dict) -> "Progress":
        d = dict(d)
        projects = {k: Project(**v) for k, v in (d.pop("projects", None) or {}).items()}
        known = {f for f in cls.__dataclass_fields__}
        p = cls(**{k: v for k, v in d.items() if k in known})
        p.projects = projects
        return p


def home() -> Path:
    return Path(os.environ.get("KEEBO_HOME", Path.home() / ".keebo"))


def load(path: Optional[Path] = None) -> Progress:
    path = path or home() / "progress.json"
    try:
        return Progress.from_json(json.loads(path.read_text()))
    except (OSError, ValueError, TypeError):
        return Progress()


def save(p: Progress, path: Optional[Path] = None) -> None:
    path = path or home() / "progress.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(p.to_json(), indent=1))
    tmp.replace(path)
