#!/usr/bin/env python3
"""Fail when a file points to a skill that does not exist.

A pointer is the text "skill `<name>`" or "skills `<name>`". Valid names are the skill
folders of this plugin plus the names listed in --also (for skills in other plugins).
Run it from the plugin root:

    python3 scripts/check_skill_refs.py --also-file scripts/known_skills.txt
    python3 scripts/check_skill_refs.py --selftest
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

POINTER = re.compile(r"\bskills? `([a-z0-9][a-z0-9-]*)`")


def local_skills(root: Path) -> set[str]:
    """Return the names of the skill folders under skills/."""
    return {p.parent.name for p in (root / "skills").glob("*/SKILL.md")}


def tracked_text_files(root: Path) -> list[Path]:
    """Return the tracked Markdown, JSON and Python files, except the changelog."""
    out = subprocess.run(
        ["git", "ls-files"], cwd=root, check=True, capture_output=True, text=True
    ).stdout
    keep = (".md", ".json", ".py")
    return [
        root / f
        for f in out.splitlines()
        if f.endswith(keep)
        and f not in ("CHANGELOG.md", "scripts/check_skill_refs.py")
        and (root / f).is_file()
    ]


def find_unknown(text: str, known: set[str]) -> list[tuple[int, str]]:
    """Return (line number, name) for each pointer to a name not in known."""
    hits = []
    for number, line in enumerate(text.splitlines(), start=1):
        for name in POINTER.findall(line):
            if name not in known:
                hits.append((number, name))
    return hits


def selftest() -> int:
    """Check the pointer pattern on fixed examples."""
    known = {"write-pr", "review-pr"}
    cases = [
        ("See skill `missing`.", [(1, "missing")]),
        ("See skill `write-pr`.", []),
        ("Skills `review-pr` and skill `gone`.", [(1, "gone")]),
        ("Run `review-pr` without the word.", []),
    ]
    for text, expected in cases:
        got = find_unknown(text, known)
        if got != expected:
            print(f"selftest failed for {text!r}: got {got}, expected {expected}")
            return 1
    print("selftest ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--also-file", help="file with one known skill name per line (other plugins)"
    )
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return selftest()

    root = Path.cwd()
    known = local_skills(root)
    if args.also_file:
        lines = Path(args.also_file).read_text(encoding="utf-8").splitlines()
        known |= {s.strip() for s in lines if s.strip() and not s.startswith("#")}

    failures = 0
    for path in tracked_text_files(root):
        for number, name in find_unknown(path.read_text(encoding="utf-8"), known):
            print(
                f"{path.relative_to(root)}:{number}: skill `{name}` does not exist; use one of the current skill names"
            )
            failures += 1
    if failures:
        print(f"check_skill_refs: {failures} pointer(s) to unknown skills")
        return 1
    print(f"check_skill_refs: OK ({len(known)} known skills)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
