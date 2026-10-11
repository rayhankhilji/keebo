"""Installers and snippets for git, zsh and coding agents."""
from __future__ import annotations

import json
import stat
import subprocess
from pathlib import Path

MARK = "# keebo"

GIT_HOOK = """{mark}
command -v keebo >/dev/null 2>&1 && (keebo emit commit --quiet >/dev/null 2>&1 &)
"""

ZSH = r"""# --- keebo: paste into ~/.zshrc -------------------------------------------
# Wake Keebo when you cd into a git project, and react to test/build commands.
_keebo_chpwd() {
  local top; top=$(git rev-parse --show-toplevel 2>/dev/null) || return
  [[ "$top" == "$_KEEBO_LAST" ]] && return
  _KEEBO_LAST="$top"; (keebo emit project_start --project "${top:t}" --quiet &) 2>/dev/null
}
autoload -Uz add-zsh-hook && add-zsh-hook chpwd _keebo_chpwd
# Run tests through keebo so it can cheer (or collapse): `kt pytest -q`
alias kt='keebo wrap --kind test --'
alias kb='keebo wrap --kind build --'
alias ka='keebo wrap --kind agent --'
# ---------------------------------------------------------------------------
"""

CLAUDE_HOOKS = {
    "hooks": {
        "UserPromptSubmit": [{"hooks": [{"type": "command", "command": "keebo emit agent_start --quiet"}]}],
        "Stop": [{"hooks": [{"type": "command", "command": "keebo emit agent_done --quiet"}]}],
        "PostToolUseFailure": [{"hooks": [{"type": "command", "command": "keebo emit confused --quiet"}]}],
    }
}


def install_git(repo: Path) -> Path:
    gitdir = subprocess.run(["git", "rev-parse", "--git-path", "hooks"], cwd=repo, capture_output=True,
                            text=True, check=True).stdout.strip()
    hook = (repo / gitdir / "post-commit").resolve()
    hook.parent.mkdir(parents=True, exist_ok=True)
    text = hook.read_text() if hook.exists() else "#!/bin/sh\n"
    if MARK not in text:
        text = text.rstrip("\n") + "\n" + GIT_HOOK.format(mark=MARK)
        hook.write_text(text)
    hook.chmod(hook.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return hook


def claude_settings() -> str:
    return json.dumps(CLAUDE_HOOKS, indent=2)
