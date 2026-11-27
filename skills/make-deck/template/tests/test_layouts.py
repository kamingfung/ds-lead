"""Tests for canvas geometry, shared chrome and layout regions."""

from layouts import (
    BODY_BOTTOM,
    BODY_TOP,
    CANVAS_H,
    CANVAS_W,
    LAYOUTS,
    MARGIN,
    Region,
    chrome,
    split,
)


def _overlaps(a: Region, b: Region) -> bool:
    return a.x < b.x + b.w and b.x < a.x + a.w and a.y < b.y + b.h and b.y < a.y + a.h


def test_regions_lie_inside_canvas_and_do_not_overlap_in_a_layout() -> None:
    inside: list[bool] = [
        r.x >= 0 and r.y >= 0 and r.x + r.w <= CANVAS_W and r.y + r.h <= CANVAS_H
        for layout in LAYOUTS.values()
        for r in layout.values()
    ]
    pairs: list[tuple[str, str]] = [
        (name_a, name_b)
        for layout in LAYOUTS.values()
        for name_a, a in layout.items()
        for name_b, b in layout.items()
        if name_a < name_b and _overlaps(a, b)
    ]
    assert all(inside) and pairs == []


def test_every_layout_except_cover_has_a_footer_and_section_has_no_header() -> None:
    assert [layout for layout in LAYOUTS if "footer" not in chrome(layout)] == ["cover"]
    assert set(chrome("section")) == {"footer"}


def test_three_to_one_split_and_takeaway_offset() -> None:
    assert split(3, 1) == (852, 284)
    assert LAYOUTS["chart_3to1"]["takeaways"].x == MARGIN + 852 + 32 + 24


def test_one_to_one_column_and_cards_geometry() -> None:
    assert (LAYOUTS["two_col"]["right"].x, LAYOUTS["two_col"]["right"].w) == (656, 568)
    cards: Region = LAYOUTS["cards3"]["cards"]
    assert (cards.y, cards.h, cards.capacity) == (BODY_TOP, BODY_BOTTOM - BODY_TOP, 3)
