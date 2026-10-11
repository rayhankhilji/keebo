"""``keebo wrap -- <command>``: run a command and tell Keebo how it went.

The kind of work is guessed from the command (tests, build or coding agent)
and can be forced with ``--kind``."""
from __future__ import annotations

import os
import subprocess
from typing import List, Optional

from . import client

TEST_WORDS = ("pytest", "jest", "vitest", "mocha", "rspec", "phpunit", "tox", "nox", "ctest", "playwright",
              "cypress", "unittest")
TEST_PHRASES = ("npm test", "npm run test", "yarn test", "pnpm test", "bun test", "go test", "cargo test",
                "swift test", "mix test", "make test", "make check", "gradle test", "./gradlew test",
                "mvn test", "dotnet test", "rails test", "deno test")
BUILD_WORDS = ("make", "tsc", "xcodebuild", "webpack", "vite", "gradle", "mvn", "bazel", "cmake", "ninja",
               "docker", "next", "turbo")
BUILD_PHRASES = ("npm run build", "yarn build", "pnpm build", "bun run build", "cargo build", "go build",
                 "swift build", "docker build", "brew install")
AGENT_WORDS = ("claude", "codex", "aider", "devin", "gemini", "goose", "opencode", "amp", "cursor-agent")

KINDS = {
    "test": ("tests_start", "tests_pass", "tests_fail"),
    "build": ("build_start", "build_pass", "build_fail"),
    "agent": ("agent_start", "agent_done", "build_fail"),
    "task": ("agent_start", "task_complete", "build_fail"),
}


def guess_kind(argv: List[str]) -> str:
    line = " ".join(argv).lower()
    exe = os.path.basename(argv[0]).lower() if argv else ""
    if any(p in line for p in TEST_PHRASES) or exe in TEST_WORDS or "pytest" in line:
        return "test"
    if exe in AGENT_WORDS:
        return "agent"
    if any(p in line for p in BUILD_PHRASES) or exe in BUILD_WORDS:
        return "build"
    return "task"


def run(argv: List[str], kind: Optional[str] = None, project: Optional[str] = None) -> int:
    if not argv:
        raise SystemExit("usage: keebo wrap [--kind test|build|agent|task] -- <command> [args...]")
    kind = kind or guess_kind(argv)
    start, ok, bad = KINDS[kind]
    project = project or client.project_name()
    client.emit(start, project, {"cmd": argv[0]})
    try:
        code = subprocess.call(argv)
    except FileNotFoundError:
        client.emit("confused", project, {"cmd": argv[0]})
        print("keebo: command not found: %s" % argv[0])
        return 127
    except KeyboardInterrupt:
        client.emit("confused", project)
        return 130
    client.emit(ok if code == 0 else bad, project, {"cmd": argv[0], "code": code})
    return code
