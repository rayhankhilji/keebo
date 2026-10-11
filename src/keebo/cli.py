"""``keebo`` command line."""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import List, Optional

from . import __version__


def _cmd_run(a) -> int:
    from .context import macos
    from .display.gif import FileDisplay
    from .engine import progression
    from .engine.runtime import Companion
    from .integrations import server

    displays = []
    for name in a.display:
        if name == "aula":
            from .display.aula import AulaDisplay
            displays.append(AulaDisplay(min_interval=a.min_upload_interval, max_frames=a.max_frames))
        elif name == "terminal":
            from .display.terminal import TerminalDisplay
            displays.append(TerminalDisplay())
        elif name == "file":
            displays.append(FileDisplay(progression.home() / "now.gif"))
    comp = Companion(displays, probe=None if a.no_context else macos.probe, poll=a.poll,
                     sleep_after=a.sleep_after * 60, show_hud=a.hud)
    srv = server.serve(comp.emit, comp.state, comp.now_gif, a.port)
    if "terminal" not in a.display:
        print("keebo %s is awake  ·  preview: http://127.0.0.1:%d  ·  displays: %s  ·  ctrl-c to stop"
              % (__version__, a.port, ", ".join(a.display) or "none"))
    try:
        comp.run()
    except KeyboardInterrupt:
        pass
    finally:
        srv.shutdown()
    return 0


def _look(a):
    from .animations.base import Look
    from .engine import progression

    if getattr(a, "mine", False):
        return progression.load().look(a.hud)
    return Look(skin=a.skin or "inky", form=a.form, hat=a.hat, face=a.face, neck=a.neck, back=a.back, show_hud=a.hud,
                projects=[{"name": "keebo", "trophy": "star"}, {"name": "builddit", "trophy": "cup"},
                          {"name": "duocorn", "trophy": "flag"}] if a.shelf else [])


def _cmd_list(a) -> int:
    from .animations import REGISTRY, load_all

    load_all()
    for kind in ("state", "transition", "scene"):
        print("\n%ss:" % kind)
        for spec in REGISTRY.values():
            if spec.kind == kind:
                print("  %-12s %s" % (spec.name, spec.description))
    return 0


def _cmd_render(a) -> int:
    from .animations import build
    from .display.gif import save_gif, sprite_sheet

    out = Path(a.out)
    for name in a.names:
        clip = build(name, _look(a))
        gif = save_gif(clip, out / ("%s.gif" % name), a.scale)
        sheet = out / ("%s.png" % name)
        sprite_sheet(clip, a.scale).save(sheet)
        print("%-12s %2d frames  %5d ms  -> %s, %s" % (name, len(clip), clip.duration_ms, gif, sheet))
    return 0


def _cmd_export(a) -> int:
    from .art.character import SKINS
    from .display.gif import export_all

    for skin in [a.skin] if a.skin else list(SKINS):
        a.skin = skin
        res = export_all(Path(a.out), _look(a), scale=a.scale, folder=skin)
        print("exported %d %s animations to %s" % (len(res), skin, a.out))
    return 0


def _cmd_preview(a) -> int:
    from .animations import build
    from .display.terminal import play

    try:
        sys.stdout.write("\x1b[2J")
        for name in a.names:
            play(build(name, _look(a)), loops=a.loops)
    except KeyboardInterrupt:
        pass
    return 0


def _cmd_emit(a) -> int:
    from .integrations import client

    ok = client.emit(a.kind, a.project)
    if not ok and not a.quiet:
        print("keebo isn't running (start it with `keebo run`)", file=sys.stderr)
    return 0


def _cmd_wrap(a) -> int:
    from .integrations import wrap

    argv = a.argv[1:] if a.argv and a.argv[0] == "--" else a.argv
    return wrap.run(argv, a.kind, a.project)


def _cmd_status(a) -> int:
    from .engine import progression
    from .integrations import client

    p = progression.load()
    live = client.state()
    from .art.character import FORM_NAMES

    print("Keebo (%s)  ·  %s  ·  level %d  ·  %d XP  (%.0f%% to next)" % (p.skin, FORM_NAMES[p.form], p.level, p.xp,
                                                                     100 * p.level_frac))
    print("mood: %s" % (live["mood"] if live else "asleep (daemon not running)"))
    print("equipped: %s" % ", ".join("%s=%s" % kv for kv in p.equipped.items() if kv[1]) or "-")
    print("unlocked: %s" % (", ".join(p.unlocked) or "nothing yet: go ship something"))
    if p.projects:
        print("projects:")
        for proj in sorted(p.projects.values(), key=lambda x: -x.last_seen)[:8]:
            print("  %-20s %4d XP  %3d tasks  %s" % (proj.name, proj.xp, proj.tasks, proj.trophy))
    return 0


def _cmd_skin(a) -> int:
    from .art.character import SKINS
    from .engine import progression

    p = progression.load()
    if not a.name:
        for name in SKINS:
            print(("* " if name == p.skin else "  ") + name)
        return 0
    if a.name not in SKINS:
        print("unknown skin %r (try: %s)" % (a.name, ", ".join(SKINS)), file=sys.stderr)
        return 1
    p.skin = a.name
    progression.save(p)
    print("Keebo is now %s. Restart `keebo run` if it is running." % a.name)
    return 0


def _cmd_equip(a) -> int:
    from .engine import progression

    p = progression.load()
    try:
        if a.item in ("none", "off"):
            p.equip(None, a.slot)
        else:
            p.equip(a.item)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1
    progression.save(p)
    print("equipped: %s" % p.equipped)
    return 0


def _cmd_device(a) -> int:
    from .display import aula

    try:
        if a.action == "list":
            devs = aula.find()
            if not devs:
                print("no AULA F75 Max on USB. Connect the USB-C cable (the screen is wired-only).")
                return 1
            for d in devs:
                print("0c45:800a  usage page %04x  interface %d  %s" % (d.usage_page, d.interface, d.product))
            return 0
        # push
        from PIL import Image, ImageSequence

        from .animations import build
        from .animations.base import Clip

        if a.target.endswith(".gif"):
            im = Image.open(a.target)
            frames = [(f.convert("RGB").resize((128, 128), Image.NEAREST), f.info.get("duration", 100))
                      for f in ImageSequence.Iterator(im)]
            payload = aula.encode(aula.fit_frames(frames, a.max_frames))
        else:
            clip: Clip = build(a.target, _look(a))
            from .display.base import clip_images
            payload = aula.encode(aula.fit_frames(clip_images(clip), a.max_frames))
        if a.dry_run:
            print("payload: %d bytes, %d chunks (dry run, nothing sent)" % (len(payload), len(payload) // aula.CHUNK))
            return 0

        def bar(i, n):
            sys.stdout.write("\ruploading %3d%%" % (100 * i // n))
            sys.stdout.flush()

        with aula.AulaScreen(a.slot, verbose=a.verbose) as screen:
            screen.upload(payload, bar)
        print("\ndone")
        return 0
    except aula.AulaError as e:
        print("error: %s" % e, file=sys.stderr)
        return 1


def _cmd_hooks(a) -> int:
    from .integrations import hooks

    if a.target == "git":
        print("installed %s" % hooks.install_git(Path(a.repo)))
    elif a.target == "zsh":
        print(hooks.ZSH)
    elif a.target == "claude":
        print("# merge into ~/.claude/settings.json")
        print(hooks.claude_settings())
    return 0


def _cmd_context(a) -> int:
    from .context import macos
    from .context.rules import classify, load_rules

    ctx = macos.probe()
    print(json.dumps({"app": ctx.app, "bundle": ctx.bundle, "url": ctx.url, "title": ctx.title,
                      "idle_seconds": round(ctx.idle_seconds, 1), "scene": classify(ctx, load_rules())}, indent=2))
    return 0


def _add_look(p) -> None:
    p.add_argument("--skin", choices=["inky", "axo"], help="creature (default: inky; export: both)")
    p.add_argument("--form", type=int, default=1, help="0 Baby, 1 Buddy, 2 Clicky, 3 Mecha, 4 Legend")
    p.add_argument("--hat")
    p.add_argument("--face")
    p.add_argument("--neck")
    p.add_argument("--back")
    p.add_argument("--hud", action="store_true", help="show the XP strip")
    p.add_argument("--shelf", action="store_true", help="show sample project trophies")
    p.add_argument("--mine", action="store_true", help="use your saved progress (form, items, projects)")


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="keebo", description="A pixel-art companion for the AULA F75 Max screen.")
    ap.add_argument("--version", action="version", version="keebo " + __version__)
    ap.add_argument("-v", "--verbose", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("run", help="start the companion daemon")
    p.add_argument("--display", action="append", choices=["aula", "terminal", "file"],
                   help="where to show Keebo (repeatable; default: file)")
    p.add_argument("--port", type=int, default=7428)
    p.add_argument("--poll", type=float, default=2.0, help="context poll interval (s)")
    p.add_argument("--sleep-after", type=float, default=10, help="minutes idle before sleeping")
    p.add_argument("--min-upload-interval", type=float, default=20, help="seconds between keyboard uploads")
    p.add_argument("--max-frames", type=int, default=48)
    p.add_argument("--no-context", action="store_true", help="don't watch the frontmost app")
    p.add_argument("--hud", action="store_true", help="show level + XP strip")
    p.set_defaults(fn=_cmd_run)

    p = sub.add_parser("list", help="list animations and scenes")
    p.set_defaults(fn=_cmd_list)

    p = sub.add_parser("render", help="render animations to GIF + sprite sheet")
    p.add_argument("names", nargs="+")
    p.add_argument("-o", "--out", default="out")
    p.add_argument("--scale", type=int, default=2)
    _add_look(p)
    p.set_defaults(fn=_cmd_render)

    p = sub.add_parser("export", help="render every animation (assets/)")
    p.add_argument("-o", "--out", default="assets")
    p.add_argument("--scale", type=int, default=2)
    _add_look(p)
    p.set_defaults(fn=_cmd_export)

    p = sub.add_parser("preview", help="play animations in the terminal")
    p.add_argument("names", nargs="+")
    p.add_argument("--loops", type=int, default=3)
    _add_look(p)
    p.set_defaults(fn=_cmd_preview)

    p = sub.add_parser("emit", help="send an event to the running companion")
    p.add_argument("kind", help="e.g. project_start, agent_start, tests_start, tests_pass, build_fail, task_complete")
    p.add_argument("--project")
    p.add_argument("-q", "--quiet", action="store_true")
    p.set_defaults(fn=_cmd_emit)

    p = sub.add_parser("wrap", help="run a command and react to its result")
    p.add_argument("--kind", choices=["test", "build", "agent", "task"])
    p.add_argument("--project")
    p.add_argument("argv", nargs=argparse.REMAINDER)
    p.set_defaults(fn=_cmd_wrap)

    p = sub.add_parser("status", help="level, XP, unlocks and project history")
    p.set_defaults(fn=_cmd_status)

    p = sub.add_parser("skin", help="switch creature: inky (octopus) or axo (axolotl)")
    p.add_argument("name", nargs="?")
    p.set_defaults(fn=_cmd_skin)

    p = sub.add_parser("equip", help="wear an unlocked accessory (or `none --slot hat`)")
    p.add_argument("item")
    p.add_argument("--slot", choices=["hat", "face", "neck", "back"])
    p.set_defaults(fn=_cmd_equip)

    p = sub.add_parser("device", help="talk to the keyboard directly")
    p.add_argument("action", choices=["list", "push"])
    p.add_argument("target", nargs="?", default="idle", help="animation name or .gif file (push)")
    p.add_argument("--slot", type=int, default=1)
    p.add_argument("--max-frames", type=int, default=48)
    p.add_argument("--dry-run", action="store_true", help="encode only, don't touch the keyboard")
    _add_look(p)
    p.set_defaults(fn=_cmd_device)

    p = sub.add_parser("hooks", help="integrations: git hook, zsh snippet, Claude Code hooks")
    p.add_argument("target", choices=["git", "zsh", "claude"])
    p.add_argument("--repo", default=".")
    p.set_defaults(fn=_cmd_hooks)

    p = sub.add_parser("context", help="show what Keebo thinks you're doing right now")
    p.set_defaults(fn=_cmd_context)
    return ap


def main(argv: Optional[List[str]] = None) -> int:
    a = parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO if a.verbose else logging.WARNING, format="%(name)s: %(message)s")
    if a.cmd == "run" and not a.display:
        a.display = ["file"]
    return a.fn(a) or 0


if __name__ == "__main__":
    sys.exit(main())
