import pytest

from keebo.animations import REGISTRY, build, load_all, names
from keebo.animations.base import Look

REQUIRED = ["idle", "sleeping", "coding", "thinking", "building", "celebrating", "confused", "frustrated",
            "evolving", "recovery", "victory", "wake", "testing", "failure", "writing", "watching"]


def test_all_required_states_are_registered():
    load_all()
    missing = [n for n in REQUIRED if n not in REGISTRY]
    assert not missing


@pytest.mark.parametrize("name", names())
def test_animation_builds_valid_frames(name):
    clip = build(name, Look(projects=[{"name": "a"}, {"name": "b", "trophy": "star"}], show_hud=True))
    assert 6 <= len(clip) <= 48
    for canvas, ms in clip.frames:
        assert canvas.data.shape == (64, 64)
        assert 30 <= ms <= 600
    # the picture actually moves
    assert len({c.data.tobytes() for c, _ in clip.frames}) > 2


def test_looks_change_the_render():
    plain = build("idle", Look()).frames[0][0].data
    fancy = build("idle", Look(form=4, hat="crown", back="cape")).frames[0][0].data
    assert (plain != fancy).any()


def test_evolving_shows_both_forms():
    clip = build("evolving", Look(form=2, from_form=1))
    assert len(clip) >= 12
