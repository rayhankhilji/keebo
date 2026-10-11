"""macOS context probe: frontmost app, active browser tab and HID idle time.

Uses only built-in tools (``osascript`` and ``ioreg``). The first call asks
for Automation permission for System Events and each browser; grant it in
System Settings > Privacy & Security > Automation.
"""
from __future__ import annotations

import re
import subprocess
import sys
from typing import Optional, Tuple

from .rules import Context

_FRONT = '''
tell application "System Events"
    set p to first application process whose frontmost is true
    set n to name of p
    set b to ""
    try
        set b to bundle identifier of p
    end try
    set w to ""
    try
        set w to name of front window of p
    end try
end tell
return n & "\n" & b & "\n" & w
'''

_CHROMIUM = {"Google Chrome", "Google Chrome Beta", "Google Chrome Canary", "Brave Browser", "Microsoft Edge",
             "Arc", "Vivaldi", "Opera", "Chromium", "Dia"}
_SAFARI = {"Safari", "Safari Technology Preview", "Orion"}


def _osascript(src: str, timeout: float = 2.0) -> Optional[str]:
    try:
        out = subprocess.run(["osascript", "-e", src], capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return out.stdout.rstrip("\n") if out.returncode == 0 else None


def frontmost() -> Tuple[str, str, str]:
    out = _osascript(_FRONT)
    if not out:
        return "", "", ""
    parts = (out.split("\n") + ["", "", ""])[:3]
    return parts[0], parts[1], parts[2]


def browser_tab(app: str) -> Tuple[str, str]:
    """(url, title) of the active tab, if ``app`` is a scriptable browser."""
    if app in _CHROMIUM:
        src = 'tell application "%s" to return (URL of active tab of front window) & "\n" & ' \
              '(title of active tab of front window)' % app
    elif app in _SAFARI:
        src = 'tell application "%s" to return (URL of current tab of front window) & "\n" & ' \
              '(name of current tab of front window)' % app
    else:
        return "", ""
    out = _osascript(src)
    if not out:
        return "", ""
    url, _, title = out.partition("\n")
    return url, title


def idle_seconds() -> float:
    try:
        out = subprocess.run(["ioreg", "-c", "IOHIDSystem", "-d", "4"], capture_output=True, text=True,
                             timeout=2).stdout
    except (OSError, subprocess.TimeoutExpired):
        return 0.0
    m = re.search(r'"HIDIdleTime"\s*=\s*(\d+)', out)
    return int(m.group(1)) / 1e9 if m else 0.0


def probe() -> Context:
    if sys.platform != "darwin":
        return Context()
    app, bundle, title = frontmost()
    url, tab_title = browser_tab(app)
    return Context(app=app, bundle=bundle, url=url, title=tab_title or title, idle_seconds=idle_seconds())
