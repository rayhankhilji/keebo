"""The companion daemon: wires context probing, events, mood, XP and displays."""
from __future__ import annotations

import logging
import threading
import time
from typing import Dict, List, Optional

from ..animations.base import Clip, Look, build
from ..context.rules import Context, classify, load_rules
from ..display.base import Display
from ..display.gif import gif_bytes
from . import events as E
from . import progression
from .brain import Brain

log = logging.getLogger("keebo")


class Companion:
    def __init__(self, displays: List[Display], probe=None, poll: float = 2.0, sleep_after: float = 600,
                 show_hud: bool = False, save: bool = True) -> None:
        self.displays = displays
        self.bus = E.EventBus()
        self.progress = progression.load() if save else progression.Progress()
        self.save_enabled = save
        self.show_hud = show_hud
        self._clips: Dict[str, Clip] = {}
        self.brain = Brain(sleep_after=sleep_after, clip_seconds=self._clip_seconds)
        self.probe = probe
        self.poll = poll
        self.rules = load_rules()
        self.mood = ""
        self.context = Context()
        self.last_gain: Optional[progression.Gain] = None
        self._stop = threading.Event()
        self._now_gif = b""
        self._look_from: Optional[int] = None

    # ------------------------------------------------------------ clips

    def look(self) -> Look:
        lk = self.progress.look(self.show_hud)
        lk.from_form = self._look_from
        return lk

    def clip(self, name: str) -> Clip:
        lk = self.look()
        key = name + "|" + lk.key() + "|%s|%d" % (lk.show_hud, lk.level)
        c = self._clips.get(key)
        if c is None:
            c = self._clips[key] = build(name, lk)
        return c

    def _clip_seconds(self, name: str) -> float:
        try:
            return self.clip(name).duration_ms / 1000
        except KeyError:
            return 2.0

    # ------------------------------------------------------------ events

    def emit(self, ev: E.Event) -> None:
        self.bus.emit(ev)

    def _apply(self, ev: E.Event) -> None:
        before_form = self.progress.form
        gain = self.progress.record(ev)
        if gain.xp or gain.unlocked:
            self.last_gain = gain
            log.info("+%d XP (%s) %s", gain.xp, ev.kind, " ".join("unlocked:" + u for u in gain.unlocked))
            if self.save_enabled:
                progression.save(self.progress)
        self.brain.handle(ev)
        if gain.evolved:
            self._look_from = before_form
            self.brain.evolve()

    def _probe_loop(self) -> None:
        last_scene = object()
        idle_sent = False
        while not self._stop.is_set():
            try:
                ctx = self.probe()
                self.context = ctx
                scene = classify(ctx, self.rules)
                if scene != last_scene:
                    last_scene = scene
                    self.emit(E.Event(E.CONTEXT, data={"scene": scene, "app": ctx.app, "url": ctx.url}))
                if ctx.idle_seconds >= self.brain.sleep_after and not idle_sent:
                    idle_sent = True
                    self.emit(E.Event(E.IDLE))
                elif ctx.idle_seconds < self.poll * 2 and idle_sent:
                    idle_sent = False
                    self.emit(E.Event(E.ACTIVITY))
            except Exception as e:  # noqa: BLE001
                log.debug("probe failed: %s", e)
            self._stop.wait(self.poll)

    # ------------------------------------------------------------ main loop

    def state(self) -> dict:
        p = self.progress
        return {"mood": self.mood, "level": p.level, "xp": p.xp, "form": p.form, "look": self.look().key(),
                "equipped": p.equipped, "unlocked": p.unlocked, "projects": p.history(),
                "scene": self.brain.scene, "app": self.context.app}

    def now_gif(self) -> bytes:
        if not self._now_gif:
            self._now_gif = gif_bytes(self.clip(self.mood or "idle"), 4)
        return self._now_gif

    def step(self) -> str:
        for ev in self.bus.drain(timeout=0.1):
            self._apply(ev)
        mood = self.brain.current()
        look_key = self.look().key()
        if mood != self.mood or look_key != getattr(self, "_look_key", None):
            self.mood, self._look_key = mood, look_key
            if mood != "evolving":
                self._look_from = None
            clip = self.clip(mood)
            self._now_gif = b""
            log.info("mood -> %s", mood)
            for d in self.displays:
                d.show(clip)
        for d in self.displays:
            d.tick()
        return mood

    def run(self) -> None:
        if self.probe is not None:
            threading.Thread(target=self._probe_loop, daemon=True).start()
        try:
            while not self._stop.is_set():
                self.step()
                time.sleep(0.1)
        finally:
            for d in self.displays:
                d.close()

    def stop(self) -> None:
        self._stop.set()
