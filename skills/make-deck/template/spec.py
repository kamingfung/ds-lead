"""Deck content model: numbers from data, text blocks, diagrams and slides."""

from __future__ import annotations

import re
from dataclasses import dataclass, field, fields, is_dataclass
from typing import TYPE_CHECKING, Iterator

from layouts import LAYOUTS, Region

if TYPE_CHECKING:
    from charts import ChartData  # D2 module

MINUS: str = "\u2212"
ROWS_PER_SOURCE_SLIDE: int = 9
STATUSES: tuple[str, ...] = ("kept", "dropped", "open")
_NEGATIVE: re.Pattern[str] = re.compile(r"(^|[\s(\[/])-(?=\.?\d)")


def minus(text: str) -> str:
    """Replace each hyphen that starts a number with a true minus sign."""
    return _NEGATIVE.sub(lambda match: match.group(1) + MINUS, text)


@dataclass(frozen=True)
class Num:
    """A number from data. fmt is a format spec, optionally followed by a space and a unit."""

    value: float
    fmt: str
    source: str

    def text(self) -> str:
        """Format the number, with a true minus sign for negatives."""
        spec, _, unit = self.fmt.partition(" ")
        return minus(format(self.value, spec) + (f" {unit}" if unit else ""))


@dataclass(frozen=True)
class Run:
    text: str
    bold: bool = False


@dataclass(frozen=True)
class Para:
    runs: tuple[Run, ...]


def lead_in(lead: str, text: str) -> Para:
    """Build a paragraph whose first run is a bold lead-in followed by a colon."""
    return Para((Run(lead.rstrip(":") + ":", bold=True), Run(" " + text)))


@dataclass(frozen=True)
class Bullet:
    lead: str
    text: str
    footnote: str = ""


@dataclass(frozen=True)
class Bullets:
    items: tuple[Bullet, ...]
    heading: str = ""


@dataclass(frozen=True)
class Text:
    paras: tuple[Para, ...]
    heading: str = ""


@dataclass(frozen=True)
class Card:
    tag: str
    statement: str
    body: str
    metric: Num | None = None
    badge: str = ""
    rows: tuple[Bullet, ...] = ()


@dataclass(frozen=True)
class Tile:
    value: Num
    label: str
    caption: str = ""


@dataclass(frozen=True)
class Table:
    columns: tuple[str, ...]
    rows: tuple[tuple[str | Num, ...], ...]
    align: tuple[str, ...]
    note: str = ""


@dataclass(frozen=True)
class Chart:
    kind: str
    data: ChartData


@dataclass(frozen=True)
class Matrix:
    x_axis: str
    y_axis: str
    quadrants: tuple[str, str, str, str]
    items: tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class Flow:
    steps: tuple[tuple[str, str], ...]
    highlight: int = -1


@dataclass(frozen=True)
class Cycle:
    nodes: tuple[str, str, str, str]
    center: str


@dataclass(frozen=True)
class Bar:
    start: float
    end: float
    label: str
    planned: bool


@dataclass(frozen=True)
class Gantt:
    periods: tuple[str, ...]
    lanes: tuple[tuple[str, tuple[Bar, ...]], ...]
    milestones: tuple[tuple[float, str], ...]


@dataclass(frozen=True)
class Tree:
    root: str
    children: tuple[tuple[str, tuple[str, ...]], ...]


@dataclass(frozen=True)
class Timeline:
    nodes: tuple[tuple[str, str, str], ...]


@dataclass(frozen=True)
class Panel:
    label: str


@dataclass(frozen=True)
class Tabs:
    tabs: tuple[tuple[str, tuple[Chart, ...]], ...]


@dataclass(frozen=True)
class Slide:
    layout: str
    title: str
    kicker: str = ""
    lead: str = ""
    regions: dict[str, object] = field(default_factory=dict)
    footer: str = ""
    notes: str = ""


@dataclass(frozen=True)
class Deck:
    title: str
    short_title: str
    as_of: str
    slides: tuple[Slide, ...]


def _walk(node: object, path: str) -> Iterator[tuple[str, Num]]:
    """Yield (dotted path, Num) for every Num under a node, in field order."""
    if isinstance(node, Num):
        yield path, node
    elif is_dataclass(node) and not isinstance(node, type):
        for item in fields(node):
            yield from _walk(
                getattr(node, item.name), f"{path}.{item.name}" if path else item.name
            )
    elif isinstance(node, (tuple, list)):
        for index, child in enumerate(node):
            yield from _walk(child, f"{path}[{index}]")
    elif isinstance(node, dict):
        for key, child in node.items():
            yield from _walk(child, f"{path}.{key}" if path else str(key))


def all_nums(deck: Deck) -> list[tuple[int, str, Num]]:
    """List (1-based slide number, dotted path, Num) for every Num in the deck."""
    return [
        (number, path, num)
        for number, slide in enumerate(deck.slides, 1)
        for path, num in _walk(slide, "")
    ]


def _sources(node: object) -> Iterator[str]:
    """Yield every non-empty source field under a node (Num, chart data), in field order."""
    source: object = getattr(node, "source", None)
    if isinstance(source, str) and source:
        yield source
    if is_dataclass(node) and not isinstance(node, type):
        for item in fields(node):
            if item.name != "source":
                yield from _sources(getattr(node, item.name))
    elif isinstance(node, (tuple, list)):
        for child in node:
            yield from _sources(child)
    elif isinstance(node, dict):
        for child in node.values():
            yield from _sources(child)


def slide_sources(slide: Slide) -> str:
    """Return the footer source text: the distinct sources on a slide, in first-seen order, joined by "; "."""
    return "; ".join(dict.fromkeys(_sources(slide.regions)))


def item_label(path: str) -> str:
    """Return a reader label for a dotted path: "regions.cards[0].metric" becomes "cards 1 · metric".

    A path ending in an index (a table cell) gives only the region and position.
    """
    names: list[str] = [
        part for part in re.split(r"[.\[\]]", path) if part and not part.isdigit()
    ]
    indexes: list[str] = re.findall(r"\[(\d+)\]", path)
    head: str = names[1] + (f" {int(indexes[0]) + 1}" if indexes else "")
    if len(names) > 2 and not path.endswith("]"):
        return f"{head} \u00b7 {names[-1]}"
    return head


def sources_slides(deck: Deck) -> tuple[Slide, ...]:
    """Build "Backup · Sources" table slides, 12 rows each, for every number in the deck."""
    rows: tuple[tuple[str, str, str, str], ...] = tuple(
        (str(number), item_label(path), num.text(), num.source)
        for number, path, num in all_nums(deck)
    )
    return tuple(
        Slide(
            layout="table",
            title="Backup · Sources",
            regions={
                "table": Table(
                    ("Slide", "Item", "Value", "Source"),
                    rows[start : start + ROWS_PER_SOURCE_SLIDE],
                    ("left", "left", "right", "left"),
                ),
                "note": Text((Para((Run(f"Values as of {deck.as_of}."),)),)),
            },
        )
        for start in range(0, len(rows), ROWS_PER_SOURCE_SLIDE)
    )


def _elements(value: object) -> tuple[object, ...]:
    """Return the blocks in a region value, which is one block or a tuple of blocks."""
    return tuple(value) if isinstance(value, (tuple, list)) else (value,)


def _units(value: object, unit: str) -> int:
    """Count a region value: top-level blocks for "block", else bullet items."""
    if unit == "block":
        return len(_elements(value))
    return sum(
        len(e.items) if isinstance(e, Bullets) else 0 if isinstance(e, Text) else 1
        for e in _elements(value)
    )


def _shape_problem(value: object) -> str:
    """Return the size or shape limit a block breaks, or an empty string."""
    if isinstance(value, Flow) and not 3 <= len(value.steps) <= 6:
        return "flow needs 3 to 6 steps"
    if isinstance(value, Timeline) and (
        len(value.nodes) > 6 or any(n[2] not in STATUSES for n in value.nodes)
    ):
        return "timeline allows up to 6 nodes, each kept, dropped or open"
    if isinstance(value, Gantt) and (len(value.lanes) > 5 or len(value.milestones) > 2):
        return "gantt allows up to 5 lanes and 2 milestones"
    if isinstance(value, Matrix) and any(not 0 <= q <= 3 for _, q in value.items):
        return "matrix quadrant must be 0 to 3"
    if isinstance(value, Tabs) and any(len(charts) != 2 for _, charts in value.tabs):
        return "each tab needs 2 charts"
    return ""


def _check_region(number: int, name: str, region: Region, value: object) -> None:
    """Raise ValueError when a region holds the wrong block type, shape or count."""
    for element in _elements(value):
        kind: str = type(element).__name__
        if kind not in region.accepts:
            raise ValueError(
                f"slide {number}: region {name!r} takes {', '.join(region.accepts)}, not {kind}"
            )
        if problem := _shape_problem(element):
            raise ValueError(f"slide {number}: {problem}")
    if _units(value, region.unit) > region.capacity:
        raise ValueError(
            f"slide {number}: region {name!r} holds {region.capacity} at most"
        )


def _check_slide(number: int, slide: Slide) -> None:
    """Raise ValueError when a slide has an unknown layout, region or missing region."""
    if slide.layout not in LAYOUTS:
        raise ValueError(f"slide {number}: unknown layout {slide.layout!r}")
    regions: dict[str, Region] = LAYOUTS[slide.layout]
    for name in slide.regions:
        if name not in regions:
            raise ValueError(
                f"slide {number}: layout {slide.layout!r} has no region {name!r}"
            )
    for name, region in regions.items():
        if name not in slide.regions:
            if region.required:
                raise ValueError(f"slide {number}: missing required region {name!r}")
        else:
            _check_region(number, name, region, slide.regions[name])


def validate(deck: Deck) -> None:
    """Raise ValueError naming the 1-based slide number when a slide breaks the layout table."""
    for number, slide in enumerate(deck.slides, 1):
        _check_slide(number, slide)
