"""Local HTTP endpoint (127.0.0.1 only) for hooks, scripts and agents.

    POST /event        {"kind": "tests_pass", "project": "keebo"}
    GET  /event?kind=tests_pass&project=keebo
    GET  /state        JSON: mood, level, xp, unlocks
    GET  /now.gif      the clip currently showing
    GET  /             a live pixel-perfect preview page
"""
from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable, Dict
from urllib.parse import parse_qs, urlparse

from ..engine.events import Event

DEFAULT_PORT = 7428  # "KB" on a phone keypad-ish; arbitrary but memorable

PAGE = b"""<!doctype html><meta charset=utf-8><title>Keebo</title>
<style>body{margin:0;height:100vh;display:grid;place-items:center;background:#15122b;color:#c9a7ff;
font:14px ui-monospace,monospace}img{width:384px;height:384px;image-rendering:pixelated;border-radius:18px;
box-shadow:0 0 0 6px #2a2450,0 20px 60px #000}p{opacity:.7;text-align:center}</style>
<div><img id=k src=/now.gif><p id=s>keebo</p></div><script>
let last='';async function poll(){try{const s=await (await fetch('/state')).json();
document.getElementById('s').textContent=`${s.mood}  \xc2\xb7  LV ${s.level}  \xc2\xb7  ${s.xp} XP`;
if(s.mood+s.look!==last){last=s.mood+s.look;document.getElementById('k').src='/now.gif?'+Date.now()}}catch(e){}
setTimeout(poll,1000)}poll()</script>"""


def make_handler(emit: Callable[[Event], None], state: Callable[[], Dict], gif: Callable[[], bytes]):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a) -> None:  # quiet
            pass

        def _send(self, code: int, body: bytes, ctype: str = "application/json") -> None:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _event(self, d: Dict) -> None:
            ev = Event.from_dict(d)
            if not ev.kind:
                self._send(400, b'{"error":"missing kind"}')
                return
            emit(ev)
            self._send(202, json.dumps({"ok": True, "kind": ev.kind}).encode())

        def do_GET(self) -> None:
            u = urlparse(self.path)
            if u.path == "/event":
                q = {k: v[0] for k, v in parse_qs(u.query).items()}
                self._event(q)
            elif u.path == "/state":
                self._send(200, json.dumps(state()).encode())
            elif u.path == "/now.gif":
                self._send(200, gif(), "image/gif")
            elif u.path == "/":
                self._send(200, PAGE, "text/html; charset=utf-8")
            else:
                self._send(404, b'{"error":"not found"}')

        def do_POST(self) -> None:
            if urlparse(self.path).path != "/event":
                self._send(404, b'{"error":"not found"}')
                return
            n = int(self.headers.get("Content-Length") or 0)
            try:
                d = json.loads(self.rfile.read(n) or b"{}")
            except ValueError:
                self._send(400, b'{"error":"bad json"}')
                return
            self._event(d if isinstance(d, dict) else {})

    return Handler


def serve(emit, state, gif, port: int = DEFAULT_PORT) -> ThreadingHTTPServer:
    srv = ThreadingHTTPServer(("127.0.0.1", port), make_handler(emit, state, gif))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv
