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

# A shell line is a chain of commands joined by these separators. Each command is checked alone.
SEPARATORS = re.compile(r"&&|\|\||[;&|(){}\n]")
# Words that can sit in front of a command without changing what it does.
WRAPPERS = {
    "sudo",
    "time",
    "command",
    "exec",
    "nohup",
    "env",
    "then",
    "do",
    "else",
    "!",
}
ENV_ASSIGNMENT = re.compile(r"\w+=\S*")
# git accepts options between "git" and the subcommand, such as -C <dir> or -c k=v.
GIT_OPTIONS = r"(?:\s+(?:-C|-c)\s+\S+|\s+--[\w-]+(?:=\S+)?)*"
GIT_PUSH = re.compile(r"git" + GIT_OPTIONS + r"\s+push\b")
GH_WRITE = re.compile(
    r"gh\s+(?:pr|issue)\s+"
    r"(?:create|comment|review|merge|edit|close|ready|reopen|lock|unlock|delete|transfer|pin|unpin)\b"
)
# A dry run changes nothing on the server.
DRY_RUN = re.compile(r"\s(?:-n|--dry-run)\b")

REASON = (
    "This command writes to a remote. Push only when a unit of work is complete "
    "(skill `write-pr`, Push and Post), and ask the user first."
)


def command_start(segment: str) -> str:
    """Return the segment without leading env assignments and wrapper words."""
    words = segment.split()
    while words and (words[0] in WRAPPERS or ENV_ASSIGNMENT.fullmatch(words[0])):
        words = words[1:]
    return " ".join(words)


def writes_to_remote(command: str) -> bool:
    """Return True when any command in the line pushes, or posts to GitHub, and is not a dry run."""
    for segment in SEPARATORS.split(command):
        text = command_start(segment)
        if (GIT_PUSH.match(text) or GH_WRITE.match(text)) and not DRY_RUN.search(text):
            return True
    return False


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
        "gh pr ready 7",
        "gh pr reopen 7",
        "GIT_SSH_COMMAND=ssh git push",
        "sudo git push",
        "git push -n && git push",
        "git push origin main && tail -n 5 log",
        "if true; then git push; fi",
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
        "git push -n && ls -l",
        "ls -n; git status",
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
