import pytest

from keebo.context.rules import Context, Rule, classify


@pytest.mark.parametrize("ctx, scene", [
    (Context(app="Code"), "coding"),
    (Context(app="Cursor"), "coding"),
    (Context(app="Xcode"), "coding"),
    (Context(app="iTerm2"), "terminal"),
    (Context(app="Microsoft Outlook"), "writing"),
    (Context(app="Google Chrome", url="https://docs.google.com/document/d/abc/edit"), "writing"),
    (Context(app="Google Chrome", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"), "watching"),
    (Context(app="Safari", url="https://github.com/rayhankhilji/keebo"), "coding"),
    (Context(app="Safari", url="https://example.com"), "browsing"),
    (Context(app="Spotify"), "music"),
    (Context(app="zoom.us"), "meeting"),
    (Context(app="Slack"), "chatting"),
    (Context(app="Figma"), "designing"),
    (Context(app="Preview"), "reading"),
    (Context(app="Steam"), "gaming"),
    (Context(app="Finder"), None),
])
def test_default_rules(ctx, scene):
    assert classify(ctx) == scene


def test_user_rules_take_priority():
    rules = [Rule("music", apps=["Code"])]
    assert classify(Context(app="Code"), rules) == "music"
