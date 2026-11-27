"""Tests for numbers, text blocks, source listing and slide validation."""

import pytest

from spec import Bullet, Bullets, Card, Deck, Flow, Num, Para, Run, Slide, Text, Tile, all_nums, lead_in, minus
from spec import slide_sources, sources_slides, validate


def _text(line: str) -> Text:
    return Text((Para((Run(line),)),))


def _big(value: float, source: str) -> Slide:
    regions: dict[str, object] = {
        "number": Num(value, ".1%", source),
        "caption": _text("Share of weekly cohorts still active."),
        "note": _text("Weekly cohorts, March to May."),
    }
    return Slide("big_number", "Retention", regions=regions)


def _deck(*slides: Slide) -> Deck:
    return Deck("Q1 review", "Q1", "2026-11-26", slides)


def test_minus_and_num_text_format_for_display() -> None:
    assert minus("-18 pts (-4) 2026-11-25 a - b") == "\u221218 pts (\u22124) 2026-11-25 a - b"
    assert Num(12345.6, ",.0f", "q1").text() == "12,346"
    assert Num(-18, ".0f pts", "q2").text() == "\u221218 pts"
    assert Num(-0.18, "+.0%", "q3").text() == "\u221218%"


def test_lead_in_bolds_only_the_lead() -> None:
    assert lead_in("Churn", "fell in March").runs == (Run("Churn:", bold=True), Run(" fell in March"))


def test_all_nums_lists_path_and_sources_pack_nine_per_slide() -> None:
    assert all_nums(_deck(_big(0.42, "q9"))) == [(1, "regions.number", Num(0.42, ".1%", "q9"))]
    pages: tuple[Slide, ...] = sources_slides(_deck(*(_big(i / 100, f"q{i}") for i in range(1, 14))))
    assert [len(page.regions["table"].rows) for page in pages] == [9, 4]
    assert pages[0].regions["table"].rows[0] == ("1", "number", "1.0%", "q1")
    validate(_deck(*pages))


def test_sources_table_labels_name_the_region_position_and_field() -> None:
    cards: Slide = Slide("cards3", "Cards", regions={
        "cards": (Card("Tag", "Statement", "Body", metric=Num(1.0, ".0f", "q1")),),
    })
    assert sources_slides(_deck(cards))[0].regions["table"].rows[0][1] == "cards 1 \u00b7 metric"
    tiles: Slide = Slide("kpi_split", "Tiles", regions={
        "tiles": tuple(Tile(Num(1.0, ".0f", f"q{i}"), "Orders") for i in range(3)),
    })
    assert sources_slides(_deck(tiles))[0].regions["table"].rows[2][1] == "tiles 3 \u00b7 value"


def test_validate_names_an_unknown_layout() -> None:
    with pytest.raises(ValueError, match="slide 2: unknown layout 'poster'"):
        validate(_deck(_big(0.42, "q9"), Slide("poster", "Oops")))


def test_validate_raises_on_missing_region_and_wrong_block() -> None:
    missing: Slide = Slide("big_number", "R", regions={"number": Num(0.4, ".1%", "q1")})
    wrong: Slide = Slide("big_number", "R", regions={"number": _text("x"), "caption": _text("x"), "note": _text("y")})
    with pytest.raises(ValueError, match="slide 1: missing required region 'caption'"):
        validate(_deck(missing))
    with pytest.raises(ValueError, match="region 'number' takes Num, not Text"):
        validate(_deck(wrong))


def test_validate_raises_when_tiles_exceed_capacity() -> None:
    tiles: tuple[Tile, ...] = tuple(Tile(Num(i, ",.0f", "q1"), "Weeks") for i in range(5))
    bullets: Bullets = Bullets((Bullet("Lead", "Short text."),))
    slide: Slide = Slide("kpi_split", "Weeks", regions={"tiles": tiles, "left": bullets, "right": bullets, "note": _text("n")})
    with pytest.raises(ValueError, match="slide 1: region 'tiles' holds 4 at most"):
        validate(_deck(slide))


def test_validate_counts_bullet_items_and_checks_flow_steps() -> None:
    items: tuple[Bullet, ...] = tuple(Bullet("Lead", f"Point {i}.") for i in range(4))
    with pytest.raises(ValueError, match="region 'body' holds 3 at most"):
        validate(_deck(Slide("brief", "Summary", regions={"body": (_text("x"), Bullets(items))})))
    flow: Flow = Flow((("Sign up", "Day 0"), ("Trial", "Day 7")))
    with pytest.raises(ValueError, match="slide 1: flow needs 3 to 6 steps"):
        validate(_deck(Slide("flow", "Path", regions={"diagram": flow, "note": _text("n")})))


def test_slide_sources_lists_each_source_once_in_order():
    # Arrange
    slide = Slide(layout="kpi_split", title="Orders rose", regions={"tiles": (
        Tile(Num(534, ",.0f", "orders query, 2026-11-20"), "Orders"),
        Tile(Num(0.3, ".0%", "orders query, 2026-11-20"), "Growth"),
        Tile(Num(-18, ",.0f pts", "margin file, 2026-11-21"), "Margin"),
    )})
    # Act
    text = slide_sources(slide)
    # Assert
    assert text == "orders query, 2026-11-20; margin file, 2026-11-21"
