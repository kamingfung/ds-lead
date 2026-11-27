"""Canvas geometry, shared chrome and region boxes for every slide layout (CSS pixels)."""

from __future__ import annotations

from dataclasses import dataclass

CANVAS_W: int = 1280
CANVAS_H: int = 720
MARGIN: int = 56
GUTTER: int = 32
BODY_TOP: int = 192
BODY_BOTTOM: int = 660
BODY_W: int = CANVAS_W - 2 * MARGIN
BODY_H: int = BODY_BOTTOM - BODY_TOP
NOTE_Y: int = BODY_BOTTOM - 32
TABLE_H: int = BODY_H - 40


@dataclass(frozen=True)
class Region:
    """A box that holds one kind of block. Unit "item" counts bullets, "block" counts blocks."""

    x: int
    y: int
    w: int
    h: int
    accepts: tuple[str, ...]
    capacity: int = 1
    required: bool = True
    unit: str = "item"


KICKER: Region = Region(MARGIN, 28, BODY_W, 22, ("str",))
TITLE: Region = Region(MARGIN, 52, BODY_W, 84, ("str",))
LEAD: Region = Region(MARGIN, 140, BODY_W, 40, ("str",))
FOOTER: Region = Region(MARGIN, 676, BODY_W, 24, ("str",))


def split(a: int, b: int) -> tuple[int, int]:
    """Split the body width at ratio a:b; the left part rounds down."""
    total: int = BODY_W - GUTTER
    left: int = total * a // (a + b)
    return left, total - left


HALF_W: int = split(1, 1)[0]
RIGHT_X: int = MARGIN + HALF_W + GUTTER
SQUARE_X: int = MARGIN + (BODY_W - BODY_H) // 2
CHART_W, SIDE_W = split(2, 1)
SIDE_X: int = MARGIN + CHART_W + GUTTER
TABS_W: int = split(3, 1)[0]


def _chart(a: int, b: int, takeaways: int) -> dict[str, Region]:
    """Return the chart and takeaway regions for one split ratio."""
    left: int = split(a, b)[0]
    text_x: int = MARGIN + left + GUTTER + 24
    return {
        "chart": Region(MARGIN, BODY_TOP, left, BODY_H, ("Chart",)),
        "takeaways": Region(
            text_x,
            BODY_TOP,
            CANVAS_W - MARGIN - text_x,
            BODY_H,
            ("Bullets",),
            takeaways,
        ),
    }


LAYOUTS: dict[str, dict[str, Region]] = {
    "cover": {
        "title": Region(
            MARGIN, 150, BODY_W, 240, ("str",), required=False
        ),  # room for three display lines
        "subtitle": Region(MARGIN, 404, BODY_W, 96, ("Text",)),
        "meta": Region(MARGIN, 640, BODY_W, 40, ("Text",)),
    },
    "section": {
        "heading": Region(MARGIN, 190, BODY_W, 180, ("str",), required=False),
        "lead": Region(MARGIN, 392, BODY_W, 60, ("Text",)),
    },
    "cards3": {
        "cards": Region(MARGIN, BODY_TOP, BODY_W, BODY_H, ("Card",), 3, unit="block")
    },
    "brief": {"body": Region(MARGIN, BODY_TOP, BODY_W, BODY_H, ("Text", "Bullets"), 3)},
    "kpi_split": {
        "tiles": Region(MARGIN, BODY_TOP, BODY_W, 150, ("Tile",), 4, unit="block"),
        "left": Region(MARGIN, 366, HALF_W, 254, ("Bullets",), 4),
        "right": Region(RIGHT_X, 366, HALF_W, 254, ("Bullets",), 4),
        "note": Region(MARGIN, NOTE_Y, BODY_W, 32, ("Text",)),
    },
    "two_col": {
        "left": Region(MARGIN, BODY_TOP, HALF_W, 428, ("Bullets",), 4),
        "right": Region(RIGHT_X, BODY_TOP, HALF_W, 428, ("Bullets",), 4),
        "summary": Region(MARGIN, 620, BODY_W, 40, ("Text",), required=False),
    },
    "big_number": {
        "number": Region(MARGIN, 308, BODY_W, 180, ("Num",)),
        "caption": Region(MARGIN, 496, BODY_W, 48, ("Text",)),
        "note": Region(MARGIN, NOTE_Y, BODY_W, 32, ("Text",)),
    },
    "table": {
        "table": Region(MARGIN, BODY_TOP, BODY_W, TABLE_H, ("Table",)),
        "note": Region(MARGIN, NOTE_Y, BODY_W, 32, ("Text",)),
    },
    "grid4": {
        "blocks": Region(
            MARGIN, BODY_TOP, BODY_W, BODY_H, ("Bullets",), 4, unit="block"
        )
    },
    "chart_3to1": _chart(3, 1, 3),
    "chart_2to1": _chart(2, 1, 4),
    "chart_1to1": _chart(1, 1, 3),
    "chart_table": {
        "chart": Region(MARGIN, BODY_TOP, CHART_W, BODY_H, ("Chart",)),
        "table": Region(SIDE_X, BODY_TOP, SIDE_W, TABLE_H, ("Table",)),
        "note": Region(SIDE_X, NOTE_Y, SIDE_W, 32, ("Text",)),
    },
    "note": {
        "heading": Region(MARGIN, BODY_TOP, BODY_W, 48, ("Text",)),
        "body": Region(MARGIN, BODY_TOP + 64, BODY_W, 360, ("Text",)),
        "print_note": Region(MARGIN, NOTE_Y, BODY_W, 32, ("Text",)),
    },
    "matrix": {
        "diagram": Region(
            MARGIN + (BODY_W - 760) // 2, BODY_TOP, 760, BODY_H, ("Matrix",)
        )
    },
    "flow": {
        "diagram": Region(MARGIN, BODY_TOP, BODY_W, 420, ("Flow",)),
        "note": Region(MARGIN, 620, BODY_W, 40, ("Text",)),
    },
    "cycle": {
        "diagram": Region(
            MARGIN + (BODY_W - 900) // 2, BODY_TOP, 900, BODY_H, ("Cycle",)
        )
    },
    "gantt": {
        "diagram": Region(MARGIN, BODY_TOP, BODY_W, 440, ("Gantt",)),
        "legend": Region(MARGIN, 632, BODY_W, 28, ("Text",)),
    },
    "tree": {"diagram": Region(MARGIN, BODY_TOP, BODY_W, BODY_H, ("Tree",))},
    "timeline": {"diagram": Region(MARGIN, BODY_TOP, BODY_W, BODY_H, ("Timeline",))},
    "options3": {
        "cards": Region(MARGIN, BODY_TOP, BODY_W, 404, ("Card",), 3, unit="block"),
        "recommendation": Region(MARGIN, 604, BODY_W, 56, ("Text",)),
    },
    "discussion": {
        "prompts": Region(MARGIN, BODY_TOP, HALF_W, BODY_H, ("Bullets",), 3),
        "notes": Region(RIGHT_X, BODY_TOP, HALF_W, BODY_H, ("Panel",)),
    },
    "tabs": {
        "tabs": Region(MARGIN, BODY_TOP, TABS_W, 428, ("Tabs",)),
        "takeaways": _chart(3, 1, 3)["takeaways"],
        "note": Region(MARGIN, NOTE_Y, TABS_W, 32, ("Text",)),
    },
    "references": {"body": Region(MARGIN, BODY_TOP, BODY_W, BODY_H, ("Text",))},
}


def chrome(layout: str) -> dict[str, Region]:
    """Return the header and footer regions: none for cover, footer only for section."""
    if layout == "cover":
        return {}
    if layout == "section":
        return {"footer": FOOTER}
    return {"kicker": KICKER, "title": TITLE, "lead": LEAD, "footer": FOOTER}
