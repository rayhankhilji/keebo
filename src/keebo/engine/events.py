"""Events Keebo reacts to, and a tiny thread-safe bus to deliver them."""
from __future__ import annotations

import queue
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

# Canonical event kinds. Hooks may send anything; unknown kinds are ignored.
PROJECT_START = "project_start"
AGENT_START = "agent_start"
AGENT_DONE = "agent_done"
TESTS_START = "tests_start"
TESTS_PASS = "tests_pass"
TESTS_FAIL = "tests_fail"
BUILD_START = "build_start"
BUILD_PASS = "build_pass"
BUILD_FAIL = "build_fail"
TASK_COMPLETE = "task_complete"
COMMIT = "commit"
THINKING = "thinking"
CONFUSED = "confused"
ACTIVITY = "activity"   # keyboard/mouse activity seen (wakes Keebo)
IDLE = "idle"           # no input for a while (sleep)
CONTEXT = "context"     # frontmost app/tab changed: data = {"scene": ..., "app": ...}

KINDS = (
    PROJECT_START, AGENT_START, AGENT_DONE, TESTS_START, TESTS_PASS, TESTS_FAIL,
    BUILD_START, BUILD_PASS, BUILD_FAIL, TASK_COMPLETE, COMMIT, THINKING, CONFUSED,
    ACTIVITY, IDLE, CONTEXT,
)

ALIASES = {
    "start": PROJECT_START, "open": PROJECT_START,
    "agent": AGENT_START, "agent_end": AGENT_DONE, "agent_stop": AGENT_DONE,
    "test": TESTS_START, "tests": TESTS_START, "pass": TESTS_PASS, "green": TESTS_PASS,
    "fail": TESTS_FAIL, "red": TESTS_FAIL,
    "build": BUILD_START, "built": BUILD_PASS, "broken": BUILD_FAIL,
    "done": TASK_COMPLETE, "complete": TASK_COMPLETE, "ship": TASK_COMPLETE,
    "think": THINKING, "huh": CONFUSED,
}


def normalize(kind: str) -> str:
    k = kind.strip().lower().replace("-", "_").replace(" ", "_")
    return ALIASES.get(k, k)


@dataclass
class Event:
    kind: str
    project: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    ts: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        self.kind = normalize(self.kind)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Event":
        return cls(kind=str(d.get("kind") or d.get("event") or ""), project=d.get("project"),
                   data=dict(d.get("data") or {}), ts=float(d.get("ts") or time.time()))

    def to_dict(self) -> Dict[str, Any]:
        return {"kind": self.kind, "project": self.project, "data": self.data, "ts": self.ts}


class EventBus:
    def __init__(self) -> None:
        self._q: "queue.Queue[Event]" = queue.Queue()

    def emit(self, event: Event) -> None:
        self._q.put(event)

    def drain(self, timeout: float = 0.0):
        """Yield all pending events, waiting up to ``timeout`` for the first."""
        try:
            yield self._q.get(timeout=timeout) if timeout else self._q.get_nowait()
        except queue.Empty:
            return
        while True:
            try:
                yield self._q.get_nowait()
            except queue.Empty:
                return
