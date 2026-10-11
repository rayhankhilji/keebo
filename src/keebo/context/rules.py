"""Map apps, bundle ids, URLs and window titles to scenes.

Rules are checked in order; the first match wins. Users can prepend their
own in ``~/.keebo/contexts.json``::

    [{"scene": "music", "apps": ["Tidal"]},
     {"scene": "coding", "urls": ["github.com/*/pull/*"]}]
"""
from __future__ import annotations

import fnmatch
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional


@dataclass(frozen=True)
class Context:
    app: str = ""
    bundle: str = ""
    url: str = ""
    title: str = ""
    idle_seconds: float = 0.0


@dataclass
class Rule:
    scene: str
    apps: List[str] = field(default_factory=list)       # app names, case-insensitive globs
    bundles: List[str] = field(default_factory=list)    # bundle id globs
    urls: List[str] = field(default_factory=list)       # url globs, scheme stripped
    titles: List[str] = field(default_factory=list)     # window/tab title globs

    def matches(self, ctx: Context) -> bool:
        def any_glob(value: str, pats: Iterable[str]) -> bool:
            v = value.lower()
            return bool(v) and any(fnmatch.fnmatch(v, p.lower()) for p in pats)

        url = ctx.url.split("://", 1)[-1]
        if url.startswith("www."):
            url = url[4:]
        return (any_glob(ctx.app, self.apps) or any_glob(ctx.bundle, self.bundles)
                or any_glob(url, self.urls) or any_glob(ctx.title, self.titles))


# Browser rules (urls/titles) come first so a tab beats the generic "browsing" scene.
DEFAULT_RULES: List[Rule] = [
    Rule("watching", urls=["youtube.com/*", "youtu.be/*", "netflix.com/*", "twitch.tv/*", "disneyplus.com/*",
                           "primevideo.com/*", "vimeo.com/*", "tv.apple.com/*", "max.com/*", "hulu.com/*"],
         apps=["TV", "IINA", "VLC", "QuickTime Player", "Netflix", "Infuse"]),
    Rule("writing", urls=["docs.google.com/document/*", "mail.google.com/*", "outlook.live.com/*",
                          "outlook.office.com/*", "notion.so/*", "*.notion.site/*", "medium.com/new-story*",
                          "substack.com/publish/*"],
         apps=["Microsoft Outlook", "Mail", "Microsoft Word", "Pages", "Notion", "Bear", "Obsidian",
               "Notes", "Ulysses", "iA Writer", "Spark", "Superhuman", "TextEdit"]),
    Rule("music", urls=["open.spotify.com/*", "music.youtube.com/*", "soundcloud.com/*", "music.apple.com/*"],
         apps=["Spotify", "Music", "Tidal", "Logic Pro", "GarageBand", "Ableton Live*"]),
    Rule("meeting", urls=["meet.google.com/*", "*.zoom.us/*", "teams.microsoft.com/*", "whereby.com/*"],
         apps=["zoom.us", "Microsoft Teams*", "Webex", "FaceTime", "Around"]),
    Rule("chatting", urls=["app.slack.com/*", "discord.com/*", "web.whatsapp.com/*", "web.telegram.org/*",
                           "messenger.com/*", "x.com/messages*"],
         apps=["Slack", "Discord", "Messages", "WhatsApp", "Telegram", "Signal", "Microsoft Teams (work*"]),
    Rule("designing", urls=["figma.com/*", "canva.com/*", "excalidraw.com/*", "miro.com/*"],
         apps=["Figma", "Sketch", "Adobe Photoshop*", "Adobe Illustrator*", "Pixelmator*", "Affinity*",
               "Aseprite", "Blender", "Procreate"]),
    Rule("reading", urls=["*.pdf", "arxiv.org/*", "read.amazon.com/*", "news.ycombinator.com/*",
                          "*.readthedocs.io/*", "developer.apple.com/documentation/*"],
         apps=["Preview", "Books", "Kindle", "Skim", "PDF Expert", "Reeder", "NetNewsWire"]),
    Rule("gaming", urls=["store.steampowered.com/*", "chess.com/*", "lichess.org/*"],
         apps=["Steam", "Minecraft", "Epic Games Launcher", "OpenEmu", "Battle.net", "League of Legends"]),
    Rule("coding", urls=["github.com/*", "gitlab.com/*", "app.devin.ai/*", "replit.com/*", "codesandbox.io/*",
                         "stackoverflow.com/*", "vercel.com/*", "localhost:*", "127.0.0.1:*", "chatgpt.com/*",
                         "claude.ai/*"],
         apps=["Code", "Visual Studio Code*", "Cursor", "Windsurf", "Zed", "Xcode", "IntelliJ IDEA*", "PyCharm*",
               "WebStorm", "GoLand", "CLion", "RubyMine", "Android Studio", "Sublime Text", "Nova", "BBEdit",
               "Devin", "Claude", "ChatGPT", "Fleet", "MacVim", "Emacs", "Neovide"],
         bundles=["com.microsoft.vscode*", "com.todesktop.*", "com.jetbrains.*", "dev.zed.*"]),
    Rule("terminal", apps=["Terminal", "iTerm2", "iTerm", "Warp", "Alacritty", "kitty", "WezTerm", "Ghostty",
                           "Hyper", "Tabby"]),
    Rule("browsing", apps=["Safari", "Google Chrome*", "Arc", "Firefox*", "Brave Browser*", "Microsoft Edge*",
                           "Opera*", "Vivaldi", "Orion", "Zen*", "Dia"]),
]


def load_rules(path: Optional[Path] = None) -> List[Rule]:
    from ..engine.progression import home

    path = path or home() / "contexts.json"
    user: List[Rule] = []
    if path.exists():
        for d in json.loads(path.read_text()):
            user.append(Rule(scene=d["scene"], apps=d.get("apps", []), bundles=d.get("bundles", []),
                             urls=d.get("urls", []), titles=d.get("titles", [])))
    return user + DEFAULT_RULES


def classify(ctx: Context, rules: Optional[List[Rule]] = None) -> Optional[str]:
    for rule in rules if rules is not None else DEFAULT_RULES:
        if rule.matches(ctx):
            return rule.scene
    return None
