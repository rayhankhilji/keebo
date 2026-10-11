"""Send events to a running Keebo. Never raises: hooks must not break your work."""
from __future__ import annotations

import json
import os
import subprocess
import urllib.request
from pathlib import Path
from typing import Optional

from .server import DEFAULT_PORT


def port() -> int:
    return int(os.environ.get("KEEBO_PORT", DEFAULT_PORT))


def project_name(cwd: Optional[str] = None) -> str:
    cwd = cwd or os.getcwd()
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=cwd, capture_output=True,
                             text=True, timeout=2)
        if top.returncode == 0 and top.stdout.strip():
            return Path(top.stdout.strip()).name
    except (OSError, subprocess.TimeoutExpired):
        pass
    return Path(cwd).name


def emit(kind: str, project: Optional[str] = None, data: Optional[dict] = None, timeout: float = 3.0) -> bool:
    body = json.dumps({"kind": kind, "project": project or project_name(), "data": data or {}}).encode()
    req = urllib.request.Request("http://127.0.0.1:%d/event" % port(), data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return 200 <= r.status < 300
    except OSError:
        return False


def state(timeout: float = 1.0) -> Optional[dict]:
    try:
        with urllib.request.urlopen("http://127.0.0.1:%d/state" % port(), timeout=timeout) as r:
            return json.loads(r.read())
    except (OSError, ValueError):
        return None
