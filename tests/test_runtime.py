from keebo.display.base import Display
from keebo.engine import events as E
from keebo.engine.runtime import Companion


class Recorder(Display):
    def __init__(self):
        self.shown = []

    def show(self, clip):
        self.shown.append(clip.name)


def test_companion_routes_events_to_display():
    rec = Recorder()
    comp = Companion([rec], probe=None, save=False)
    assert comp.step() == "idle"
    comp.emit(E.Event(E.TESTS_START, project="k"))
    assert comp.step() == "testing"
    comp.emit(E.Event(E.TESTS_PASS, project="k"))
    assert comp.step() == "celebrating"
    assert rec.shown == ["idle", "testing", "celebrating"]
    assert comp.progress.xp > 0
    assert comp.now_gif()[:6] == b"GIF89a"
