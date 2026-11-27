#!/usr/bin/env python3
"""Claude Code PreToolUse hook: make every push or remote post ask the user first.

Claude Code runs it on each Bash call and sends the call as JSON on stdin. When the
command pushes or posts, the hook answers "ask", so the user sees a prompt even if an
allowlist would let the call through. Any other command passes with no output.

    python3 hooks/ask_before_push.py --selftest
"""

import json
import re
import sys

# A command starts at the beginning of the line or after ; & | ( or a newline.
START = r"(?:^|[;&|(\n])\s*"
# git accepts options between "git" and the subcommand, such as -C <dir> or -c k=v.
GIT_OPTIONS = r"(?:\s+(?:-C|-c)\s+\S+|\s+--[\w-]+(?:=\S+)?)*"
REMOTE_WRITE = re.compile(
    START + r"(?:git" + GIT_OPTIONS + r"\s+push|gh\s+(?:pr|issue)\s+"
    r"(?:create|comment|review|merge|edit|close))\b"
)
# A dry run changes nothing on the server.
DRY_RUN = re.compile(r"\s(?:-n|--dry-run)\b")

REASON = (
    "This command writes to a remote. Push only when a unit of work is complete "
    "(skill `defaults`, Remote Writes), and ask the user first."
)


def writes_to_remote(command: str) -> bool:
    """Return True when the command pushes, or posts to GitHub, and is not a dry run."""
    match = REMOTE_WRITE.search(command)
    return match is not None and not DRY_RUN.search(command)


def decide(event: dict) -> dict | None:
    """Return the hook answer for one PreToolUse event, or None to let it pass."""
    command = event.get("tool_input", {}).get("command", "")
    if event.get("tool_name") != "Bash" or not writes_to_remote(command):
        return None
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": REASON,
        }
    }


def selftest() -> int:
    """Check the hook on fixed commands, including the ways a push can be spelled."""
    asks = [
        "git push",
        "git push origin HEAD:main",
        "git -C ../repo push --force-with-lease",
        "git -c user.name=x push",
        "git --no-pager push",
        "cd repo && git push",
        "make test; git push origin main",
        "gh pr create --title x",
        "gh pr comment 7 --body hi",
        "gh issue close 3",
    ]
    passes = [
        "git status",
        "git log --oneline -10",
        "git pull --rebase",
        "git push --dry-run",
        "git push -n origin main",
        "echo git push",
        "gh pr view 7",
        "gh pr list",
        "grep -rn 'git push' skills",
    ]
    for command in asks:
        if decide({"tool_name": "Bash", "tool_input": {"command": command}}) is None:
            print(f"selftest failed: {command!r} should ask")
            return 1
    for command in passes:
        if (
            decide({"tool_name": "Bash", "tool_input": {"command": command}})
            is not None
        ):
            print(f"selftest failed: {command!r} should pass")
            return 1
    if decide({"tool_name": "Edit", "tool_input": {"command": "git push"}}) is not None:
        print("selftest failed: a non-Bash tool should pass")
        return 1
    print("selftest ok")
    return 0


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    answer = decide(json.load(sys.stdin))
    if answer is not None:
        print(json.dumps(answer))
    return 0


if __name__ == "__main__":
    sys.exit(main())
