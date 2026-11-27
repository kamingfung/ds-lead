#!/usr/bin/env python3
"""Inventory check: verify every rule in a source skill set has a home in target repos.

Usage:
    rule_inventory.py --source DIR REF PATH... --target NAME DIR REF PATH... [--verdicts FILE] [--out FILE] [--min 0.6]
    rule_inventory.py --selftest

A rule is a bullet, numbered step, checklist item, or table row with 2+ content
words. Its home is the line with the highest content-word overlap across all
``--target`` specs. Overlap >= ``--min`` counts as "covered". Lines under
``--min`` need a hand verdict: ``--verdicts`` JSON maps ``"<path>:<rule text>"``
(or a folder ``"<dir>/"`` for every rule under it) to
``{"grade": "covered|partial|none|not-needed|differs", "home": "...", "note": "..."}``.
Reads git refs only; never writes to a repo.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

STOP: frozenset[str] = frozenset(
    "a an the and or of to in on for with is are be it its this that as by at "
    "from not no any each every one when then than only into via your you do "
    "does use uses".split()
)
RULE_RE = re.compile(r"^\s*(?:[-*]\s+(?:\[ \]\s+)?|\d+\.\s+|\|(?!\s*-))(.+)")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that every rule in a source skill set has a home in target repos."
    )
    parser.add_argument("--source", nargs="+", metavar="ARG", help="DIR REF PATH...")
    parser.add_argument(
        "--target",
        action="append",
        nargs="+",
        metavar="ARG",
        default=[],
        help="Repeatable: NAME DIR REF PATH...",
    )
    parser.add_argument(
        "--verdicts", type=Path, help="Optional JSON file of hand verdicts"
    )
    parser.add_argument("--out", type=Path, help="Optional output markdown path")
    parser.add_argument(
        "--min", type=float, default=0.6, help="Minimum overlap ratio (default: 0.6)"
    )
    parser.add_argument(
        "--selftest", action="store_true", help="Run built-in tests and exit"
    )
    args = parser.parse_args()

    if args.selftest:
        selftest()
        return 0
    if not args.source or len(args.source) < 3:
        parser.error("--source needs DIR REF PATH...")
    if not args.target:
        parser.error("provide at least one --target NAME DIR REF PATH...")

    targets: list[tuple[str, Path, str, list[str]]] = []
    for spec in args.target:
        if len(spec) < 4:
            parser.error("--target needs NAME DIR REF PATH...")
        name, repo_dir, ref, *paths = spec
        targets.append((name, Path(repo_dir), ref, paths))

    src_dir, src_ref, *src_paths = args.source
    verdicts: dict[str, Any] = (
        json.loads(args.verdicts.read_text())
        if args.verdicts and args.verdicts.exists()
        else {}
    )
    corpus = load_corpus([(n, d, r, ps) for n, d, r, ps in targets if d.is_dir()])
    rows = [
        match(rule, corpus, verdicts, args.min)
        for rule in source_rules(src_dir, src_ref, src_paths)
    ]
    text = report(rows, f"{src_dir} @ {src_ref}", args.min)
    if args.out:
        args.out.write_text(text)
    else:
        sys.stdout.write(text)
    unjudged = sum(r["grade"] == "UNJUDGED" for r in rows)
    print(
        f"{len(rows)} rules; {unjudged} weak matches without a verdict", file=sys.stderr
    )
    return 0


def git(repo_dir: str | Path, *args: str) -> str:
    """Run a read-only git command in ``repo_dir`` and return stdout."""
    return subprocess.run(
        ["git", "-C", str(repo_dir), *args],
        capture_output=True,
        text=True,
        check=False,
    ).stdout


def words(text: str) -> set[str]:
    """Return lowercase content words of length > 2 excluding stop words."""
    return {
        w
        for w in re.findall(r"[a-z][a-z0-9_]+", text.lower())
        if w not in STOP and len(w) > 2
    }


def load_corpus(
    targets: list[tuple[str, Path, str, list[str]]],
) -> list[tuple[str, str, set[str]]]:
    """Load target lines and their content-word sets from git refs."""
    out: list[tuple[str, str, set[str]]] = []
    for name, repo_dir, ref, paths in targets:
        for path in git(repo_dir, "ls-tree", "-r", "--name-only", ref, *paths).split():
            if path.endswith((".md", ".json")):
                for idx, line in enumerate(
                    git(repo_dir, "show", f"{ref}:{path}").splitlines(), 1
                ):
                    word_set = words(line)
                    if len(word_set) >= 2:
                        out.append((f"{name}:{path}:{idx}", line.strip(), word_set))
    return out


def source_rules(
    repo_dir: str | Path, ref: str, paths: list[str]
) -> list[tuple[str, int, str]]:
    """Extract rule-like lines from markdown files at ``ref``."""
    out: list[tuple[str, int, str]] = []
    for path in git(repo_dir, "ls-tree", "-r", "--name-only", ref, *paths).split():
        if path.endswith(".md"):
            for idx, line in enumerate(
                git(repo_dir, "show", f"{ref}:{path}").splitlines(), 1
            ):
                matched = RULE_RE.match(line)
                if matched and len(words(matched.group(1))) >= 2:
                    out.append((path, idx, line.strip()))
    return out


def match(
    rule: tuple[str, int, str],
    corpus: list[tuple[str, str, set[str]]],
    verdicts: dict[str, Any],
    minimum: float,
) -> dict[str, Any]:
    """Match a single source rule against the target corpus or hand verdicts."""
    path, line, text = rule
    word_set = words(text)
    best = max(corpus, key=lambda c: len(word_set & c[2]), default=("none", "", set()))
    score = round(len(word_set & best[2]) / len(word_set), 2) if word_set else 0.0
    verdict = verdicts.get(f"{path}:{text}") or next(
        (verdicts[k] for k in verdicts if k.endswith("/") and path.startswith(k)),
        None,
    )
    if verdict:
        grade = verdict["grade"]
        home = verdict.get("home", best[0])
        note = verdict.get("note", "")
    else:
        grade = "covered" if score >= minimum else "UNJUDGED"
        home = best[0]
        note = f"word match {score}"
    return {
        "path": path,
        "line": line,
        "rule": text,
        "grade": grade,
        "home": home,
        "note": note,
    }


def report(rows: list[dict[str, Any]], source: str, minimum: float) -> str:
    """Format matched rules as a markdown summary table."""
    order = {
        "UNJUDGED": 0,
        "none": 1,
        "partial": 2,
        "differs": 3,
        "not-needed": 4,
        "covered": 5,
    }
    sorted_rows = sorted(
        rows, key=lambda r: (order.get(r["grade"], 9), r["path"], r["line"])
    )
    counts = {g: sum(r["grade"] == g for r in sorted_rows) for g in order}
    lines = [
        f"Source: `{source}`. Covered = content-word overlap of {minimum} or more, or a hand verdict.",
        "",
        "| " + " | ".join(f"{g}: {n}" for g, n in counts.items() if n) + " |",
        "",
        "| Grade | Rule | Source line | Home | Note |",
        "|---|---|---|---|---|",
    ]
    for r in sorted_rows:
        cell = r["rule"].replace("|", "/")[:120]
        lines.append(
            f"| {r['grade']} | {cell} | `{r['path']}:{r['line']}` | `{r['home']}` | {r['note']} |"
        )
    return "\n".join(lines) + "\n"


def selftest() -> None:
    """Run offline self-tests against in-memory fixtures and a throwaway git repo."""
    corpus = [
        (
            "team:x.md:3",
            "- Guard clauses first: return or raise early",
            words("Guard clauses first: return or raise early"),
        )
    ]
    strong = match(("s.md", 1, "- Guard clauses first, return early"), corpus, {}, 0.6)
    weak = match(("s.md", 2, "- Never log secrets"), corpus, {}, 0.6)
    judged = match(
        ("s.md", 2, "- Never log secrets"),
        corpus,
        {"s.md:- Never log secrets": {"grade": "covered", "home": "team:y.md:9"}},
        0.6,
    )
    assert strong["grade"] == "covered" and weak["grade"] == "UNJUDGED", (strong, weak)
    assert judged["grade"] == "covered" and judged["home"] == "team:y.md:9", judged
    folder = match(
        ("skills/django/SKILL.md", 4, "- Use class-based views"),
        corpus,
        {"skills/django/": {"grade": "not-needed"}},
        0.6,
    )
    assert folder["grade"] == "not-needed", folder
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["git", "init", "-q", tmp], check=True)
        Path(tmp, "a.md").write_text(
            "# T\n\n- Keep functions short and pure\nplain text\n"
        )
        subprocess.run(["git", "-C", tmp, "add", "."], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                tmp,
                "-c",
                "user.email=t@t",
                "-c",
                "user.name=t",
                "commit",
                "-qm",
                "x",
            ],
            check=True,
        )
        assert source_rules(tmp, "HEAD", ["a.md"]) == [
            ("a.md", 3, "- Keep functions short and pure")
        ]
    assert report([strong, weak], "src", 0.6).count("| UNJUDGED |") == 1
    print("selftest OK")


if __name__ == "__main__":
    raise SystemExit(main())
