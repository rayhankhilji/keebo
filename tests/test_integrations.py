import json
import urllib.request

from keebo.engine import events as E
from keebo.integrations import server
from keebo.integrations.wrap import guess_kind


def test_guess_kind():
    assert guess_kind(["pytest", "-q"]) == "test"
    assert guess_kind(["npm", "test"]) == "test"
    assert guess_kind(["cargo", "build"]) == "build"
    assert guess_kind(["claude", "-p", "fix it"]) == "agent"
    assert guess_kind(["./deploy.sh"]) == "task"


def test_http_server_accepts_events():
    got = []
    srv = server.serve(got.append, lambda: {"mood": "idle"}, lambda: b"GIF89a", port=0)
    port = srv.server_address[1]
    try:
        req = urllib.request.Request("http://127.0.0.1:%d/event" % port,
                                     data=json.dumps({"kind": "tests_pass", "project": "k"}).encode(),
                                     headers={"Content-Type": "application/json"})
        assert urllib.request.urlopen(req).status == 202
        urllib.request.urlopen("http://127.0.0.1:%d/event?kind=done" % port)
        state = json.loads(urllib.request.urlopen("http://127.0.0.1:%d/state" % port).read())
    finally:
        srv.shutdown()
    assert [e.kind for e in got] == [E.TESTS_PASS, E.TASK_COMPLETE]
    assert got[0].project == "k" and state["mood"] == "idle"
