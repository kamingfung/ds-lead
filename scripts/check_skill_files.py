#!/usr/bin/env python3
"""Fail when a skill file is over 200 lines or two tracked files have the same bytes.

Both rules come from skill `write-skill`: "Hard ceiling: 200 lines" in Sizing
Guidelines, and "No duplicate files" in Write Skill Files Like Clean Code.
Run it from the repository root:

    python3 scripts/check_skill_files.py
    python3 scripts/check_skill_files.py --selftest
"""

import hashlib
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

MAX_LINES = 200


def tracked_files(root: Path) -> list[Path]:
    """Return the tracked files that exist on disk."""
    out = subprocess.run(
        ["git", "ls-files"], cwd=root, check=True, capture_output=True, text=True
    ).stdout
    return [root / f for f in out.splitlines() if (root / f).is_file()]


def too_long(paths: list[Path], root: Path) -> list[tuple[str, int]]:
    """Return (path, line count) for each skill Markdown file over MAX_LINES."""
    hits = []
    for path in paths:
        relative = path.relative_to(root)
        if relative.parts[0] == "skills" and path.suffix == ".md":
            lines = len(path.read_text(encoding="utf-8").splitlines())
            if lines > MAX_LINES:
                hits.append((str(relative), lines))
    return hits


def duplicates(paths: list[Path], root: Path) -> list[list[str]]:
    """Return groups of tracked non-empty files with identical bytes."""
    groups: dict[str, list[str]] = defaultdict(list)
    for path in paths:
        data = path.read_bytes()
        if data:
            groups[hashlib.sha256(data).hexdigest()].append(str(path.relative_to(root)))
    return [sorted(names) for names in groups.values() if len(names) > 1]


def selftest() -> int:
    """Check both rules on a small fake tree."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "skills" / "a").mkdir(parents=True)
        long = root / "skills" / "a" / "SKILL.md"
        long.write_text("x\n" * (MAX_LINES + 1), encoding="utf-8")
        ok = root / "skills" / "a" / "ok.md"
        ok.write_text("x\n" * MAX_LINES, encoding="utf-8")
        copy = root / "copy.txt"
        copy.write_bytes(b"same")
        (root / "other.txt").write_bytes(b"same")
        (root / "empty1").write_bytes(b"")
        (root / "empty2").write_bytes(b"")
        paths = [long, ok, copy, root / "other.txt", root / "empty1", root / "empty2"]
        if too_long(paths, root) != [("skills/a/SKILL.md", MAX_LINES + 1)]:
            print("selftest failed: line ceiling")
            return 1
        if duplicates(paths, root) != [["copy.txt", "other.txt"]]:
            print("selftest failed: duplicate files")
            return 1
    print("selftest ok")
    return 0


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    root = Path.cwd()
    paths = tracked_files(root)
    failures = 0
    for name, lines in too_long(paths, root):
        print(
            f"{name}: {lines} lines; split it by sub-domain or move examples to a reference file (limit {MAX_LINES})"
        )
        failures += 1
    for names in duplicates(paths, root):
        print(f"identical files: {', '.join(names)}; keep one and link to it")
        failures += 1
    if failures:
        print(f"check_skill_files: {failures} problem(s)")
        return 1
    print(f"check_skill_files: OK ({len(paths)} tracked files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
