#!/usr/bin/env python3
"""Warn about gaps in a one-page report, as HTML or Markdown.

Usage: check_report.py <report.html|report.md> | --selftest
Warnings only: exit 0 for a readable file, 2 for a missing one.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

ACRONYM_ALLOWLIST = frozenset({"OK", "US", "AM", "PM"})
BLOCK_TAGS = frozenset(
    "p li h1 h2 h3 h4 h5 h6 figcaption caption td th div section blockquote dt dd".split()
)
CODE_TAGS = frozenset({"code", "pre"})
SKIP_TAGS = frozenset({"style", "script", "svg"})  # diagram labels are not prose
OUTCOME_FIELDS = ("Outcome", "What changes", "Next action", "Decided")
ALL_CHECKS = frozenset(
    "title acronym figure-position figure-number tons outcome-block "
    "unsourced-number local-path placeholder".split()
)
ACRONYM = re.compile(r"\b[A-Z]{2,}[0-9]*s?\b(?!-\d)")
TICKET_KEY = re.compile(r"\b[A-Z]+-\d+\b")
FIG_REF = re.compile(r"\b(Figure|Table) (\d+)\b")
FIG_TOKEN = re.compile(r"\b(?:Figure|Table) \d+\b")
CAPTION = re.compile(r"^(Figure|Table) (\d+)[.:]")
FIG_POSITION = re.compile(
    r"\b(?:chart|figure|table)\s+(?:below|above)\b|\bbelow\s+(?:chart|figure|table)\b"
    r"|\bthe following (?:figure|chart|table)\b",
    re.IGNORECASE,
)
TONS = re.compile(r"\b\d[\d,.]*\s*(?:t|tons?|tonnes?|MT)\b", re.IGNORECASE)
PLACEHOLDER = re.compile(r"\bTODO\b|\bTBD\b|\bXXX\b|<[a-z ]+>")
SOURCE_WORD = re.compile(r"\b(?:source|query|run|table|figure)s?\b", re.IGNORECASE)
ISO_DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
YEAR = re.compile(r"\b(?:19|20)\d{2}\b")
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
CODE_SPAN = re.compile(r"`[^`]*`")
LINK_TARGET = re.compile(r"\]\([^)]*\)")
LOCAL_PATH_MARKERS = ("/Users/", "/home/", "/tmp/", "C:\\", "file://", "OneDrive-")


@dataclass
class Block:
    """Visible text of one paragraph, heading, list item or table cell."""

    tag: str
    line: int
    parts: list[str] = field(default_factory=list)
    link: bool = False

    @property
    def text(self) -> str:
        return " ".join("".join(self.parts).split())


@dataclass(frozen=True)
class Finding:
    check: str
    detail: str
    line: int


class _BlockCollector(HTMLParser):
    """Collects the visible text of each block element, with its start line."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks: list[Block] = []
        self._open: list[Block] = []
        self._skip = self._code = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in SKIP_TAGS:
            self._skip += 1
        elif tag in CODE_TAGS:
            self._code += 1
        elif tag == "a" and self._open and any(name == "href" for name, _ in attrs):
            self._open[-1].link = True
        elif tag in BLOCK_TAGS:
            self.blocks.append(Block(tag, self.getpos()[0]))
            self._open.append(self.blocks[-1])

    def handle_endtag(self, tag: str) -> None:
        if tag in SKIP_TAGS:
            self._skip = max(0, self._skip - 1)
        elif tag in CODE_TAGS:
            self._code = max(0, self._code - 1)
        elif tag in BLOCK_TAGS and any(block.tag == tag for block in self._open):
            while self._open.pop().tag != tag:
                pass

    def handle_data(self, data: str) -> None:
        if self._open and not (self._skip or self._code):
            self._open[-1].parts.append(data)


def parse_html(source: str) -> list[Block]:
    collector = _BlockCollector()
    collector.feed(source)
    collector.close()
    return [block for block in collector.blocks if block.text]


def parse_markdown(source: str) -> list[Block]:
    blocks: list[Block] = []
    in_fence = False
    for number, raw in enumerate(source.splitlines(), start=1):
        line = re.sub(
            r"^(?:[-*]|\d+\.)\s+", "", raw.strip()
        )  # list markers are not numbers
        if line.startswith("```"):
            in_fence = not in_fence
        elif line and not in_fence:
            heading = HEADING.match(line)
            tag = (
                f"h{len(heading.group(1))}"
                if heading
                else ("td" if line.startswith("|") else "p")
            )
            body = heading.group(2) if heading else line
            visible = LINK_TARGET.sub("]", CODE_SPAN.sub(" ", body))
            blocks.append(
                Block(tag, number, [visible], "](" in body or "<a href" in body)
            )
    return [block for block in blocks if block.text]


def check_title(blocks: list[Block]) -> list[Finding]:
    heads = [block for block in blocks if block.tag == "h1"]
    if not heads:
        return [Finding("title", "no title found", 1)]
    title, words = heads[0], len(heads[0].text.split())
    findings = (
        [Finding("title", "title is a question, not the answer", title.line)]
        if "?" in title.text
        else []
    )
    if words < 6:
        findings.append(
            Finding(
                "title",
                f"title has {words} word(s); state the answer in 6 or more",
                title.line,
            )
        )
    return findings


def check_acronyms(blocks: list[Block]) -> list[Finding]:
    seen: set[str] = set()
    findings = []
    for block in blocks:
        for match in ACRONYM.finditer(block.text):
            key = match.group(0)
            if key.endswith("s") and re.fullmatch(r"[A-Z]{2,}[0-9]*", key[:-1]):
                key = key[:-1]  # APIs and API share one key
            if key in seen or key in ACRONYM_ALLOWLIST:
                continue
            seen.add(key)
            text, start, end = block.text, match.start(), match.end()
            if text[end : end + 2] != " (" and text[start - 1 : start] != "(":
                findings.append(
                    Finding(
                        "acronym", f"{key} is used before it is defined", block.line
                    )
                )
    return findings


def check_figures(blocks: list[Block]) -> list[Finding]:
    captions: dict[str, int] = {}
    references: list[tuple[str, int]] = []
    for block in blocks:
        caption = CAPTION.match(block.text)
        if caption:
            captions.setdefault(f"{caption.group(1)} {caption.group(2)}", block.line)
        else:
            references += [
                (f"{m.group(1)} {m.group(2)}", block.line)
                for m in FIG_REF.finditer(block.text)
            ]
    referenced = {key for key, _ in references}
    return [
        Finding("figure-number", f"{key} is referenced but has no caption", line)
        for key, line in references
        if key not in captions
    ] + [
        Finding("figure-number", f"{key} caption is never referenced", line)
        for key, line in captions.items()
        if key not in referenced
    ]


def check_pattern(
    blocks: list[Block], pattern: re.Pattern[str], check: str, message: str
) -> list[Finding]:
    return [
        Finding(check, message.format(match.group(0)), block.line)
        for block in blocks
        for match in pattern.finditer(block.text)
    ]


def check_outcome(blocks: list[Block]) -> list[Finding]:
    """Each field must open a block (a table cell, row or list item), not sit inside prose."""
    starts = [block.text.lstrip("| *").lower() for block in blocks]
    return [
        Finding("outcome-block", f"missing field '{name}'", 1)
        for name in OUTCOME_FIELDS
        if not any(start.startswith(name.lower()) for start in starts)
    ]


def check_uncaptioned(source: str, blocks: list[Block], html: bool) -> list[Finding]:
    """Warn when the report holds more figures and tables than numbered captions."""
    if html:
        items = len(re.findall(r"<(?:figure|table)\b", source, re.IGNORECASE))
    else:
        items = len(re.findall(r"^\s*!\[", source, re.MULTILINE)) + len(
            re.findall(r"^\s*\|\s*:?-{3,}", source, re.MULTILINE)
        )
    captions = sum(1 for block in blocks if CAPTION.match(block.text))
    return (
        [
            Finding(
                "figure-number",
                f"{items} figure(s) or table(s) but {captions} numbered caption(s)",
                1,
            )
        ]
        if items > captions
        else []
    )


def check_unsourced(blocks: list[Block]) -> list[Finding]:
    findings = []
    for block in blocks:
        bare = YEAR.sub(" ", FIG_TOKEN.sub(" ", ISO_DATE.sub(" ", block.text)))
        sourced = TICKET_KEY.search(block.text) or SOURCE_WORD.search(block.text)
        if (
            block.tag in ("p", "li")
            and not block.link
            and re.search(r"\d", bare)
            and not sourced
        ):
            findings.append(
                Finding(
                    "unsourced-number",
                    f"number with no source: '{block.text[:60]}'",
                    block.line,
                )
            )
    return findings


def check_local_paths(lines: list[str]) -> list[Finding]:
    return [
        Finding("local-path", f"local path '{marker}' in text or a link", number)
        for number, line in enumerate(lines, start=1)
        for marker in LOCAL_PATH_MARKERS
        if marker in line
    ]


def check_report(source: str, suffix: str) -> list[Finding]:
    html = suffix.lower() in (".html", ".htm")
    blocks = parse_html(source) if html else parse_markdown(source)
    return [
        *check_title(blocks),
        *check_acronyms(blocks),
        *check_pattern(
            blocks,
            FIG_POSITION,
            "figure-position",
            "'{}' points by position; use the number",
        ),
        *check_figures(blocks),
        *check_uncaptioned(source, blocks, html),
        *check_pattern(blocks, TONS, "tons", "'{}' is a mass in tons; give kg"),
        *check_outcome(blocks),
        *check_unsourced(blocks),
        *check_local_paths(source.splitlines()),
        *check_pattern(
            blocks, PLACEHOLDER, "placeholder", "placeholder '{}' left in text"
        ),
    ]


GOOD_MD = """# Weighted error fell from 18% to 14% in peak weeks
Question: does the new weighting cut the error in peak weeks (2025-01-06 to 2025-03-30)?
Answer: yes. Error fell from 18% to 14% (source: query q123, run r45). Figure 1 shows it.
Figure 1. Weekly error, baseline and new weighting, percent, 2025 window.
| Outcome | Adopted |
| What changes | The new switch is on. |
| Next action | Merge the switch (owner: data team, TICKET-123). |
| Decided | Team lead, 2026-03-02 |
"""

GOOD_HTML = """<!doctype html><html lang="en"><head><title>Weighting report</title></head><body>
<p>Forecasting · 2025 window</p><h1>Weighted error fell from 18% to 14% in peak weeks</h1>
<p>Answer: yes. Error fell from 18% to 14% (source: query q123, run r45). Table 1 lists the outcome.</p>
<figure><svg><text>NEW</text></svg><figcaption>Figure 1. Weekly error, baseline and new weighting, percent, 2025 window.</figcaption></figure>
<p>Figure 1 shows the weekly error (run r45).</p>
<table><caption>Table 1. Outcome fields.</caption><tr><th>Field</th><th>Value</th></tr>
<tr><td>Outcome</td><td>Adopted</td></tr><tr><td>What changes</td><td>The new switch is on.</td></tr>
<tr><td>Next action</td><td>Merge the switch (owner: data team, TICKET-123).</td></tr>
<tr><td>Decided</td><td>Team lead, 2026-03-02</td></tr></table></body></html>
"""

BAD_MD = """# Why?
The API returns MAE values in the summary.
See the chart below for the trend.
Figure 2 shows the weekly error.
Figure 3. Weekly volume in kg, 2025 window.
The crop was 1.2 Tons last week.
![chart](chart.png)
Data sits at /Users/me/report.csv
Owner: <owner name>, TODO.
"""


def run_selftest() -> None:
    for sample, suffix in ((GOOD_MD, ".md"), (GOOD_HTML, ".html")):
        findings = check_report(sample, suffix)
        if findings:
            raise AssertionError(f"clean {suffix} sample was flagged: {findings}")
    names = {finding.check for finding in check_report(BAD_MD, ".md")}
    if names != ALL_CHECKS:
        raise AssertionError(f"bad sample missed checks: {sorted(ALL_CHECKS - names)}")
    prose = "# Weighted error fell from 18% to 14% in peak weeks\nThe outcome, what changes, the next action and who decided are open.\n"
    if not any(f.check == "outcome-block" for f in check_report(prose, ".md")):
        raise AssertionError("outcome words in prose must not pass as a block")
    bare = GOOD_HTML.replace("</body>", "<figure><svg></svg></figure></body>")
    if not any(f.check == "figure-number" for f in check_report(bare, ".html")):
        raise AssertionError("a figure with no caption must warn")
    if main(["/nonexistent/report.md"]) != 2:
        raise AssertionError("a missing file must exit 2")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Warn about gaps in a one-page report."
    )
    parser.add_argument("report", nargs="?", type=Path)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        run_selftest()
        print("selftest ok")
        return 0
    if args.report is None:
        parser.error("give a report file, or --selftest")
    try:
        source = args.report.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        print(f"error: cannot read {args.report}: {error}", file=sys.stderr)
        return 2
    findings = check_report(source, args.report.suffix)
    for finding in findings:
        print(f"WARN {finding.check}: {finding.detail} (line {finding.line})")
    print(f"{len(findings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
