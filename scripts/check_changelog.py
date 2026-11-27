"""Fail a push unless the branch changes CHANGELOG.md compared with a base ref.

pre-commit runs this as a pre-push hook (see .pre-commit-config.yaml):
``python3 scripts/check_changelog.py --base origin/main``.
``--selftest`` checks the helpers against a throwaway git repo.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

CHANGELOG = "CHANGELOG.md"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that CHANGELOG.md changed since a base ref."
    )
    parser.add_argument(
        "--base", default="origin/main", help="base ref to compare with"
    )
    parser.add_argument(
        "--selftest", action="store_true", help="run the built-in tests and exit"
    )
    args = parser.parse_args()
    if args.selftest:
        selftest()
        print("selftest OK")
        return 0
    try:
        changed: list[str] = changed_files(args.base)
    except subprocess.CalledProcessError as err:
        print(err.stderr, end="", file=sys.stderr)
        return err.returncode
    if not changed:
        print(f"check_changelog: no changes since {args.base}")
        return 0
    if changelog_touched(changed):
        print("check_changelog: OK")
        return 0
    print(
        f"check_changelog: CHANGELOG.md is not changed since {args.base}. "
        'Add one line under "## Unreleased": what changed for a user, then the PR link and ticket key. '
        "Procedure: CONTRIBUTING.md",
        file=sys.stderr,
    )
    return 1


def changelog_touched(changed: list[str]) -> bool:
    """Return True when the root CHANGELOG.md is in the changed paths."""
    return CHANGELOG in changed


def changed_files(base: str, cwd: str | None = None) -> list[str]:
    """Return paths changed on HEAD since the merge base with ``base``."""
    result: subprocess.CompletedProcess[str] = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD"],
        check=True,
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    return [line for line in result.stdout.splitlines() if line]


def selftest() -> None:
    """Build a git repo with a base and a feature branch, then assert the helpers."""
    identity = [
        "-c",
        "user.name=t",
        "-c",
        "user.email=t@t",
        "-c",
        "commit.gpgsign=false",
    ]
    with tempfile.TemporaryDirectory() as tmp:
        cwd = Path(tmp)

        def git(*args: str) -> None:
            subprocess.run(
                ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
            )

        def commit(name: str, text: str) -> None:
            (cwd / name).write_text(text)
            git("add", "-A")
            git(*identity, "commit", "-qm", f"edit {name}")

        git("init", "-q", "-b", "base")
        commit("README.md", "base\n")
        git("checkout", "-q", "-b", "feature")
        # base gains a changelog line after the branch point: three-dot diff must ignore it
        git("checkout", "-q", "base")
        commit(CHANGELOG, "- base entry\n")
        git("checkout", "-q", "feature")
        assert changed_files("base", cwd=tmp) == []
        commit("README.md", "feature\n")
        assert not changelog_touched(changed_files("base", cwd=tmp))
        commit(CHANGELOG, "- entry\n")
        assert changelog_touched(changed_files("base", cwd=tmp))
    assert not changelog_touched(["docs/CHANGELOG.md"])


if __name__ == "__main__":
    sys.exit(main())
