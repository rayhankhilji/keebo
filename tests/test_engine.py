from keebo.engine import events as E
from keebo.engine.brain import Brain
from keebo.engine.progression import Progress, form_for_level, level_for_xp, xp_for_level


class Clock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


def brain(**kw):
    clock = Clock()
    return Brain(clock=clock, clip_seconds=lambda n: 2.0, **kw), clock


def test_idle_by_default_and_scene_from_context():
    b, _ = brain()
    assert b.current() == "idle"
    b.handle(E.Event(E.CONTEXT, data={"scene": "coding"}))
    assert b.current() == "coding"


def test_tests_run_then_celebrate_then_back_to_scene():
    b, clock = brain()
    b.handle(E.Event(E.CONTEXT, data={"scene": "coding"}))
    b.handle(E.Event(E.TESTS_START))
    assert b.current() == "testing"
    clock.t += 30
    assert b.current() == "testing"
    b.handle(E.Event(E.TESTS_PASS))
    assert b.current() == "celebrating"
    clock.t += 7
    assert b.current() == "coding"


def test_build_fail_collapses_then_recovers():
    b, clock = brain()
    b.handle(E.Event(E.BUILD_FAIL))
    assert b.current() == "failure"
    clock.t += 2.1
    assert b.current() == "recovery"
    clock.t += 2.1
    assert b.current() == "idle"


def test_agent_task_builds_and_finishes_with_victory():
    b, clock = brain()
    b.handle(E.Event(E.AGENT_START))
    assert b.current() == "building"
    b.handle(E.Event(E.TASK_COMPLETE))
    assert b.current() == "victory"
    clock.t += 9
    assert b.current() == "idle"


def test_inactivity_sleeps_and_activity_wakes():
    b, clock = brain(sleep_after=60)
    clock.t += 61
    assert b.current() == "sleeping"
    b.handle(E.Event(E.ACTIVITY))
    assert b.current() == "wake"
    clock.t += 2.1
    assert b.current() == "idle"


def test_project_start_wakes():
    b, _ = brain()
    b.handle(E.Event("start"))
    assert b.current() == "wake"


def test_low_priority_reaction_does_not_interrupt_victory():
    b, _ = brain()
    b.handle(E.Event(E.TASK_COMPLETE))
    b.handle(E.Event(E.COMMIT))
    assert b.current() == "victory"


def test_aliases_normalise():
    assert E.Event("Tests-Pass").kind == E.TESTS_PASS
    assert E.Event("done").kind == E.TASK_COMPLETE


def test_level_curve_is_monotonic():
    assert xp_for_level(1) == 0
    assert all(xp_for_level(n + 1) > xp_for_level(n) for n in range(1, 40))
    assert level_for_xp(xp_for_level(7)) == 7
    assert form_for_level(1) == 0 and form_for_level(30) == 4


def test_xp_is_never_lost_and_comebacks_pay():
    p = Progress()
    p.record(E.Event(E.TESTS_FAIL, project="keebo", ts=1000))
    assert p.xp == 0
    g = p.record(E.Event(E.TESTS_PASS, project="keebo", ts=1010))
    assert g.xp == 15 + 10
    assert "bandage" in g.unlocked and "partyhat" in g.unlocked


def test_breaks_are_rewarded_not_penalised():
    p = Progress()
    p.record(E.Event(E.COMMIT, ts=1000))
    g = p.record(E.Event(E.COMMIT, ts=1000 + 6 * 3600))
    assert g.xp > 5 and g.note == "well rested"


def test_levels_unlock_accessories_and_forms():
    p = Progress()
    gains = [p.record(E.Event(E.TASK_COMPLETE, project="p%d" % (i % 3), ts=10_000 + i * 60)) for i in range(40)]
    assert p.level >= 8 and p.form >= 2
    assert any(g.evolved for g in gains)
    assert "hardhat" in p.unlocked and "shades" in p.unlocked
    assert len(p.history()) == 3


def test_progress_roundtrips_json():
    p = Progress()
    p.record(E.Event(E.TASK_COMPLETE, project="x", ts=5000))
    q = Progress.from_json(p.to_json())
    assert q.xp == p.xp and q.projects["x"].tasks == 1
