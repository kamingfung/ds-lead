#!/usr/bin/env python3
"""Check drafted review comments and the summary against the review format.

Usage: python check_drafts.py <draft folder>
       python check_drafts.py --selftest

The folder holds summary.md and one *.md file per inline comment. Prints one FAIL line per
problem and returns 1; otherwise prints "drafts ok" and returns 0. Format: references/format.md.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SEVERITY_LINE: re.Pattern[str] = re.compile(
    r"^(❌ must-fix|⚠️ should-fix|🤔 nice-to-have) \((new in this PR|pre-existing); (read in code|traced|ran on data|ran)\): \S"
)
VERDICTS: dict[str, str] = {
    "✅ **Ready to merge**": "ready",
    "🔧 **Ready to merge after small fixes**": "small_fixes",
    "🛑 **Changes needed**": "changes",
    "⏸️ **Not ready: waiting on": "waiting",
}
COLORED_CIRCLES: str = "🔴🟠🟡🟢🔵🟣🟤⚫⚪"
MAX_INLINE: int = 15
SUMMARY_LABELS: tuple[str, ...] = (
    "**Evidence:**",
    "**Good:**",
    "**Key fix:**",
    "**Not run:**",
)
TIER: re.Pattern[str] = re.compile(r"Tier [0-3]: \S")
LINKED_COMMIT: re.Pattern[str] = re.compile(r"\]\([^)]*/commits?/[0-9a-f]{7,40}\)")
BARE_SHA: re.Pattern[str] = re.compile(
    r"\b(?=[0-9a-f]*\d)(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b"
)
ALLOWED_VERDICTS: dict[str, tuple[str, str]] = {
    "must-fix": ("changes", "waiting"),
    "should-fix": ("small_fixes", "waiting"),
    "nice-to-have": ("ready", "waiting"),
    "none": ("ready", "waiting"),
}
LINK: str = "([abc1234](https://git.example.com/org/repo/commits/abc1234))"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check drafted review comments against the format."
    )
    parser.add_argument("folder", nargs="?", type=Path)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        selftest()
        return 0
    if args.folder is None:
        parser.error("give a draft folder, or --selftest")
    if not args.folder.is_dir():
        raise SystemExit(f"draft folder not found: {args.folder}")
    files: dict[str, str] = {
        p.name: p.read_text(encoding="utf-8") for p in sorted(args.folder.glob("*.md"))
    }
    problems: list[str] = check(files)
    for problem in problems:
        print(f"FAIL {problem}")
    if problems:
        return 1
    print(
        f"drafts ok: {len(files) - ('summary.md' in files)} inline comments, summary ok"
    )
    return 0


def check(files: dict[str, str]) -> list[str]:
    problems: list[str] = []
    for name, text in files.items():
        if any(char in COLORED_CIRCLES for char in text):
            problems.append(f"{name}: colored circle; use the icon next to its word")
        sha: re.Match[str] | None = BARE_SHA.search(strip_code_and_links(text))
        if sha:
            problems.append(f"{name}: bare commit sha {sha.group(0)}; link it")
    inline: dict[str, str] = {
        name: text for name, text in files.items() if name != "summary.md"
    }
    for name, text in inline.items():
        if not valid_anchor(first_content_line(text)):
            problems.append(
                f'{name}: first line must be the anchor {{"inline": {{"path": ..., "to": <line>}}}}'
            )
    matches: dict[str, re.Match[str] | None] = {
        name: severity_match(text) for name, text in inline.items()
    }
    for name, match in matches.items():
        if match is None:
            problems.append(
                f"{name}: first line must be '<icon> <severity> (<new in this PR|pre-existing>; <check label>): <claim>'"
            )
        elif match.group(1).endswith("must-fix") and match.group(3) in (
            "read in code",
            "traced",
        ):
            problems.append(
                f"{name}: a must-fix needs 'ran' or 'ran on data'; post it as a question otherwise"
            )
    if len(inline) > MAX_INLINE:
        problems.append(
            f"summary.md: {len(inline)} inline comments, over {MAX_INLINE}; put the overflow in the summary"
        )
    if "summary.md" not in files:
        return problems + ["summary.md is missing"]
    severities: list[str] = [m.group(1).split()[-1] for m in matches.values() if m]
    return problems + check_summary(files["summary.md"], severities)


def strip_code_and_links(text: str) -> str:
    no_fences: str = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    no_code: str = re.sub(r"`[^`\n]*`", "", no_fences)
    return re.sub(r"\[[^\]]*\]\([^)]*\)", "", no_code)


def first_content_line(text: str) -> str:
    return next((line.strip() for line in text.splitlines() if line.strip()), "")


def valid_anchor(line: str) -> bool:
    """True for the API anchor: {"inline": {"path": str, "to": int}}, with an optional int start_to <= to."""
    try:
        inline: object = json.loads(line).get("inline")
    except (json.JSONDecodeError, AttributeError):
        return False
    if (
        not isinstance(inline, dict)
        or not isinstance(inline.get("path"), str)
        or type(inline.get("to")) is not int
    ):
        return False
    start: object = inline.get("start_to", inline["to"])
    return type(start) is int and start <= inline["to"]


def severity_match(text: str) -> re.Match[str] | None:
    """Match the first content line after the anchor line against the format."""
    for line in text.splitlines():
        stripped: str = line.strip()
        if stripped and not stripped.startswith(("{", '"inline"')):
            return SEVERITY_LINE.match(stripped)
    return None


def check_summary(text: str, severities: list[str]) -> list[str]:
    name: str = "summary.md"
    lines: list[str] = text.splitlines()
    first: str = next((line for line in lines if line.strip()), "")
    prefix: str | None = next((p for p in VERDICTS if first.startswith(p)), None)
    verdict: str | None = VERDICTS[prefix] if prefix else None
    problems: list[str] = []
    if verdict is None:
        problems.append(f"{name}: first line must be one verdict")
    if not LINKED_COMMIT.search(first):
        problems.append(f"{name}: link the reviewed head sha next to the verdict")
    if verdict != "waiting" and not TIER.search(first):
        problems.append(f"{name}: end the verdict line with 'Tier N: <reason>'")
    required: tuple[str, ...] = (
        ("**Evidence:**", "**Not run:**") if verdict == "waiting" else SUMMARY_LABELS
    )
    found: dict[str, int] = {
        label: next(i for i, line in enumerate(lines) if line.startswith(label))
        for label in SUMMARY_LABELS
        if any(line.startswith(label) for line in lines)
    }
    problems += [f"{name}: missing {label}" for label in required if label not in found]
    seen: list[str] = sorted(found, key=lambda label: found[label])
    if seen != [label for label in SUMMARY_LABELS if label in found]:
        problems.append(f"{name}: labels out of order")
    after: int = found.get("**Evidence:**", -2) + 1
    if "**Evidence:**" in found and (after >= len(lines) or lines[after].strip()):
        problems.append(f"{name}: put a blank line after **Evidence:**")
    if verdict is not None:
        worst: str = next(
            (s for s in ("must-fix", "should-fix", "nice-to-have") if s in severities),
            "none",
        )
        if verdict not in ALLOWED_VERDICTS[worst]:
            problems.append(
                f"{name}: verdict {verdict} does not match the worst finding {worst}"
            )
    return problems


def valid_files() -> dict[str, str]:
    summary: str = (
        f"🛑 **Changes needed** {LINK} Tier 2: risk path\n\n**Evidence:**\n\n- CI running\n\n"
        "**Good:** tests cover the new branch.\n\n**Key fix:** dedupe the rows.\n\n**Not run:** full backtest."
    )
    inline: str = (
        '{"inline": {"path": "a.py", "to": 3}}\n'
        "❌ must-fix (new in this PR; ran): rows duplicate.\n\n```suggestion\nabc1234f\n```\n"
    )
    return {"summary.md": summary, "1.md": inline}


def edit(files: dict[str, str], name: str, old: str, new: str) -> dict[str, str]:
    return {**files, name: files[name].replace(old, new, 1)}


def selftest() -> None:
    valid: dict[str, str] = valid_files()
    assert check(valid) == [], check(valid)
    waiting: str = f"⏸️ **Not ready: waiting on CI** {LINK}"
    cases: list[tuple[dict[str, str], str]] = [
        ({"1.md": valid["1.md"]}, "summary.md is missing"),
        (
            edit(valid, "1.md", "rows duplicate.", "rows duplicate 🔴."),
            "colored circle",
        ),
        (
            edit(valid, "1.md", "rows duplicate.", "rows duplicate, see abc1234f."),
            "bare commit sha",
        ),
        (
            edit(
                edit(valid, "1.md", "❌ must-fix (new in this PR; ran)", "❌ must-fix"),
                "summary.md",
                f"🛑 **Changes needed** {LINK}",
                waiting,
            ),
            "first line must be '<icon>",
        ),
        (
            edit(valid, "1.md", "(new in this PR; ran)", "(new in this PR; traced)"),
            "must-fix needs",
        ),
        ({**valid, **{f"{i}.md": valid["1.md"] for i in range(2, 17)}}, "over 15"),
        (
            edit(valid, "summary.md", "🛑 **Changes needed**", "**Changes needed**"),
            "first line must be one verdict",
        ),
        (edit(valid, "summary.md", LINK, "(reviewed)"), "link the reviewed head sha"),
        (edit(valid, "summary.md", " Tier 2: risk path", ""), "Tier N"),
        (edit(valid, "1.md", '"to": 3', '"to": "3"'), "must be the anchor"),
        (
            edit(valid, "1.md", '"to": 3', '"start_to": 5, "to": 3'),
            "must be the anchor",
        ),
        (
            edit(valid, "1.md", '{"inline": {"path": "a.py", "to": 3}}\n', ""),
            "must be the anchor",
        ),
        (
            edit(valid, "summary.md", "**Good:** tests cover the new branch.\n\n", ""),
            "missing **Good:**",
        ),
        (
            edit(
                valid,
                "summary.md",
                "**Key fix:** dedupe the rows.\n\n**Not run:** full backtest.",
                "**Not run:** full backtest.\n\n**Key fix:** dedupe the rows.",
            ),
            "labels out of order",
        ),
        (
            edit(
                valid,
                "summary.md",
                "**Evidence:**\n\n- CI running",
                "**Evidence:**\n- CI running",
            ),
            "blank line after **Evidence:**",
        ),
        (
            edit(valid, "summary.md", "🛑 **Changes needed**", "✅ **Ready to merge**"),
            "does not match the worst finding",
        ),
    ]
    for files, key in cases:
        problems: list[str] = check(files)
        assert len(problems) == 1 and key in problems[0], (key, problems)
    print("selftest ok")


if __name__ == "__main__":
    sys.exit(main())
