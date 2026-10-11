"""Keebo's mood state machine.

Three layers decide what plays, highest first:

1. **Reactions**: one-shot or timed clips triggered by events (celebrate,
   collapse, victory...). Transitions such as ``failure`` chain into a
   follow-up (``recovery``) before handing back.
2. **Work**: sticky states that last while something is running (building
   for an agent task, frantic testing while tests run).
3. **Base**: the context scene for the frontmost app, or idle; sleeping
   after a stretch of inactivity.

The brain is pure (no I/O, injectable clock) so it is easy to test.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from . import events as E


@dataclass(frozen=True)
class Reaction:
    clips: Tuple[str, ...]     # played in order; the last one holds for ``hold`` seconds
    hold: float = 4.0
    priority: int = 50


# event kind -> reaction. Extend or override via ``Brain(reactions=...)``.
REACTIONS: Dict[str, Reaction] = {
    E.PROJECT_START: Reaction(("wake",), hold=0, priority=40),
    E.TESTS_PASS: Reaction(("celebrating",), hold=6, priority=60),
    E.TESTS_FAIL: Reaction(("confused", "frustrated"), hold=5, priority=60),
    E.BUILD_PASS: Reaction(("celebrating",), hold=4, priority=55),
    E.BUILD_FAIL: Reaction(("failure", "recovery"), hold=0, priority=70),
    E.TASK_COMPLETE: Reaction(("victory",), hold=8, priority=80),
    E.AGENT_DONE: Reaction(("victory",), hold=5, priority=65),
    E.COMMIT: Reaction(("celebrating",), hold=3, priority=45),
    E.THINKING: Reaction(("thinking",), hold=8, priority=30),
    E.CONFUSED: Reaction(("confused",), hold=5, priority=30),
}

# event kind -> (work state to enter, event kinds that end it)
WORK_STARTS: Dict[str, Tuple[str, Tuple[str, ...]]] = {
    E.AGENT_START: ("building", (E.AGENT_DONE, E.TASK_COMPLETE)),
    E.BUILD_START: ("building", (E.BUILD_PASS, E.BUILD_FAIL)),
    E.TESTS_START: ("testing", (E.TESTS_PASS, E.TESTS_FAIL, E.BUILD_FAIL)),
}


@dataclass
class _Active:
    queue: List[str]
    hold: float
    priority: int
    started: float
    hold_until: Optional[float] = None


@dataclass
class Brain:
    clock: Callable[[], float] = time.monotonic
    sleep_after: float = 10 * 60          # seconds without activity before sleeping
    work_timeout: float = 30 * 60         # forget a work state if its end event never arrives
    reactions: Dict[str, Reaction] = field(default_factory=lambda: dict(REACTIONS))
    clip_seconds: Callable[[str], float] = lambda name: 2.0

    scene: Optional[str] = None
    work: Dict[str, Tuple[str, float, Tuple[str, ...]]] = field(default_factory=dict)
    reaction: Optional[_Active] = None
    last_activity: float = 0.0
    asleep: bool = False
    pending_evolve: bool = False

    def __post_init__(self) -> None:
        self.last_activity = self.clock()

    # ------------------------------------------------------------ input

    def handle(self, ev: E.Event) -> None:
        now = self.clock()
        kind = ev.kind
        if kind == E.CONTEXT:
            self.scene = ev.data.get("scene")
            self._touch(now)
            return
        if kind == E.IDLE:
            self.asleep = True
            return
        was_asleep = self.asleep
        self._touch(now)
        if kind == E.ACTIVITY:
            if was_asleep:
                self._react(Reaction(("wake",), hold=0, priority=40), now)
            return
        # finish any work states this event ends
        for key in [k for k, (_, _, ends) in self.work.items() if kind in ends]:
            del self.work[key]
        if kind in WORK_STARTS:
            state, ends = WORK_STARTS[kind]
            self.work[kind] = (state, now, ends)
            if was_asleep:
                self._react(Reaction(("wake",), hold=0, priority=40), now)
            return
        r = self.reactions.get(kind)
        if r is not None:
            if was_asleep and r.clips[0] != "wake":
                r = Reaction(("wake",) + r.clips, r.hold, r.priority)
            self._react(r, now)

    def evolve(self) -> None:
        """Queue the evolution sequence (called by progression on level-up)."""
        self.pending_evolve = True

    # ------------------------------------------------------------ output

    def current(self) -> str:
        """Name of the clip that should be showing right now."""
        now = self.clock()
        if self.pending_evolve:
            self.pending_evolve = False
            self._react(Reaction(("evolving",), hold=0, priority=90), now)
        if not self.asleep and now - self.last_activity >= self.sleep_after and not self.work:
            self.asleep = True
        for key in [k for k, (_, t0, _) in self.work.items() if now - t0 > self.work_timeout]:
            del self.work[key]

        a = self.reaction
        if a is not None:
            while a.queue:
                name = a.queue[0]
                if len(a.queue) > 1:
                    if now - a.started < self.clip_seconds(name):
                        return name
                    a.queue.pop(0)
                    a.started = now
                    continue
                end = a.started + max(a.hold, self.clip_seconds(name))
                if now < end:
                    return name
                a.queue.pop(0)
            self.reaction = None

        if self.work:
            # most recently started work wins
            return max(self.work.values(), key=lambda w: w[1])[0]
        if self.asleep:
            return "sleeping"
        return self.scene or "idle"

    # ------------------------------------------------------------ helpers

    def _touch(self, now: float) -> None:
        self.last_activity = now
        self.asleep = False

    def _react(self, r: Reaction, now: float) -> None:
        cur = self.reaction
        if cur is not None and cur.queue and cur.priority > r.priority:
            return
        self.reaction = _Active(list(r.clips), r.hold, r.priority, now)
