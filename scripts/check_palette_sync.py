#!/usr/bin/env python3
"""Fail when the deck theme and the chart palette disagree on a shared color.

The chart palette is `skills/make-chart/palette.css`. The deck theme is `Theme` in
`skills/make-deck/template/theme.py`. Each skill keeps its own copy so it installs alone;
this check keeps the copies equal for the roles in ROLES. `gray` is left out on purpose:
the deck uses a darker grey so small text passes the contrast check.

    python3 scripts/check_palette_sync.py
    python3 scripts/check_palette_sync.py --selftest
"""

import argparse
import re
import sys
from pathlib import Path

# deck field -> chart token, for each color that plays the same role in both skills
ROLES: dict[str, str] = {
    "ink": "ink",
    "accent": "blue",
    "loss": "red",
    "ochre": "orange",
    "sage": "green",
    "sienna": "purple",
    "highlight": "highlight",
    "light": "light",
    "panel": "panel",
    "tint": "tint",
    "paper": "paper",
}
CHART_CSS = Path("skills/make-chart/palette.css")
DECK_THEME = Path("skills/make-deck/template/theme.py")
CHART_TOKEN = re.compile(r"--(\w+):\s*(#[0-9a-fA-F]{6})")
DECK_FIELD = re.compile(r'^\s+(\w+): str = "(#[0-9a-fA-F]{6})"', re.MULTILINE)


def read_colors(text: str, pattern: re.Pattern[str]) -> dict[str, str]:
    """Return name -> lowercase hex for every match of pattern in text."""
    return {name: value.lower() for name, value in pattern.findall(text)}


def differences(deck: dict[str, str], chart: dict[str, str]) -> list[str]:
    """Return one message for each shared role that is missing or has two values."""
    problems: list[str] = []
    for deck_name, chart_name in ROLES.items():
        if deck_name not in deck:
            problems.append(f"theme.py has no field `{deck_name}`")
        elif chart_name not in chart:
            problems.append(f"palette.css has no token `--{chart_name}`")
        elif deck[deck_name] != chart[chart_name]:
            problems.append(
                f"`{deck_name}` is {deck[deck_name]} in theme.py but "
                f"`--{chart_name}` is {chart[chart_name]} in palette.css"
            )
    return problems


def selftest() -> int:
    """Check `differences` on equal, drifted and missing colors."""
    chart = {"ink": "#111111", "blue": "#222222"}
    cases = [
        (
            {"ink": "#111111", "accent": "#222222"},
            9,
        ),  # the other nine roles are missing
        ({"ink": "#111111", "accent": "#999999"}, 10),  # plus one drifted color
        ({}, 11),
    ]
    for deck, expected in cases:
        got = len(differences(deck, chart))
        if got != expected:
            print(f"selftest failed for {deck}: got {got}, expected {expected}")
            return 1
    full_chart = {chart_name: "#abcdef" for chart_name in ROLES.values()}
    full_deck = {deck_name: "#abcdef" for deck_name in ROLES}
    if differences(full_deck, full_chart):
        print("selftest failed: equal colors were flagged")
        return 1
    if read_colors('    ink: str = "#ABCDEF"\n', DECK_FIELD) != {"ink": "#abcdef"}:
        print("selftest failed: read_colors did not lowercase a hex value")
        return 1
    full_deck["loss"] = "#000000"
    if len(differences(full_deck, full_chart)) != 1:
        print("selftest failed: one drifted color was not flagged once")
        return 1
    print("selftest ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--selftest", action="store_true")
    if parser.parse_args().selftest:
        return selftest()
    deck = read_colors(DECK_THEME.read_text(encoding="utf-8"), DECK_FIELD)
    chart = read_colors(CHART_CSS.read_text(encoding="utf-8"), CHART_TOKEN)
    problems = differences(deck, chart)
    for problem in problems:
        print(f"check_palette_sync: {problem}")
    if problems:
        print(f"Change both files together: {DECK_THEME} and {CHART_CSS}.")
        return 1
    print(f"check_palette_sync: OK ({len(ROLES)} shared colors match)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
