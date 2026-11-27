"""Tests for the gallery deck: layout coverage, chart kinds, sources and both renderers."""

from io import BytesIO
from pathlib import Path

from pptx import Presentation

from gallery import SOURCE, gallery_deck, main
from layouts import LAYOUTS
from render_html import render_html
from render_pptx import render_pptx
from spec import Chart, Deck, Slide, Tabs, all_nums, sources_slides, validate
from theme import HOUSE


def _slide(deck: Deck, layout: str) -> Slide:
    """Return the one main slide that uses the given layout."""
    return next(slide for slide in deck.slides if slide.layout == layout)


def test_deck_has_one_slide_per_layout_in_table_order() -> None:
    # Arrange
    deck: Deck = gallery_deck()

    # Act
    layouts: list[str] = [slide.layout for slide in deck.slides]

    # Assert
    assert len(layouts) == 24
    assert layouts == list(LAYOUTS)


def test_deck_passes_validate() -> None:
    # Arrange
    deck: Deck = gallery_deck()

    # Act and Assert: validate raises ValueError on any broken slide.
    validate(deck)


def test_each_kicker_names_its_layout_and_each_title_is_a_sentence() -> None:
    # Arrange
    deck: Deck = gallery_deck()

    # Act
    pairs: list[tuple[str, str, str]] = [
        (s.kicker, s.layout, s.title) for s in deck.slides
    ]

    # Assert
    assert all(kicker == layout for kicker, layout, _ in pairs)
    assert all(len(title.split()) >= 6 for _, _, title in pairs)


def test_chart_slides_use_the_chart_kinds_the_brief_names() -> None:
    # Arrange
    deck: Deck = gallery_deck()

    # Act
    kinds: dict[str, str] = {
        layout: _slide(deck, layout).regions["chart"].kind
        for layout in ("chart_3to1", "chart_2to1", "chart_1to1", "chart_table")
    }

    # Assert
    assert kinds == {
        "chart_3to1": "line",
        "chart_2to1": "waterfall",
        "chart_1to1": "stacked100",
        "chart_table": "diverging_bar",
    }
    line: Chart = _slide(deck, "chart_3to1").regions["chart"]
    assert line.data.reference is not None


def test_tabs_slide_has_two_tabs_with_two_column_charts_each() -> None:
    # Arrange
    tabs: Tabs = _slide(gallery_deck(), "tabs").regions["tabs"]

    # Act
    charts_per_tab: list[tuple[str, list[str]]] = [
        (label, [chart.kind for chart in charts]) for label, charts in tabs.tabs
    ]

    # Assert
    assert [label for label, _ in charts_per_tab] == ["Orders", "Basket"]
    assert all(kinds == ["column", "column"] for _, kinds in charts_per_tab)


def test_every_num_cites_the_gallery_source() -> None:
    # Arrange
    deck: Deck = gallery_deck()

    # Act
    sources: set[str] = {num.source for _, _, num in all_nums(deck)}

    # Assert
    assert len(all_nums(deck)) >= 20
    assert sources == {SOURCE}


def test_sources_slides_list_every_num_once() -> None:
    # Arrange
    deck: Deck = gallery_deck()

    # Act
    listed: int = sum(
        len(slide.regions["table"].rows) for slide in sources_slides(deck)
    )

    # Assert
    assert listed == len(all_nums(deck))


def test_html_renderer_puts_every_layout_on_a_slide() -> None:
    # Arrange
    deck: Deck = gallery_deck()

    # Act
    html: str = render_html(deck, HOUSE)

    # Assert
    assert all(f'data-layout="{layout}"' in html for layout in LAYOUTS)
    assert html.startswith("<!doctype html>")


def test_pptx_renderer_writes_one_slide_per_slide_plus_tab_and_sources() -> None:
    # Arrange
    deck: Deck = gallery_deck()
    extra_tabs: int = 1
    expected: int = len(deck.slides) + extra_tabs + len(sources_slides(deck))

    # Act
    presentation: Presentation = Presentation(BytesIO(render_pptx(deck, HOUSE)))

    # Assert
    assert len(presentation.slides) == expected


def test_cli_writes_gallery_html_and_pptx_to_the_out_dir(tmp_path: Path) -> None:
    # Arrange
    out_dir: Path = tmp_path / "out"

    # Act
    code: int = main(["gallery.py", str(out_dir)])

    # Assert
    assert code == 0
    assert (out_dir / "gallery.html").stat().st_size > 0
    assert (out_dir / "gallery.pptx").stat().st_size > 0


def test_cli_without_an_out_dir_returns_usage_code() -> None:
    # Arrange
    argv: list[str] = ["gallery.py"]

    # Act
    code: int = main(argv)

    # Assert
    assert code == 2


def test_every_slide_but_cover_and_section_has_a_lead() -> None:
    # Arrange
    deck: Deck = gallery_deck()

    # Act
    missing: list[str] = [
        slide.layout
        for slide in deck.slides
        if slide.layout not in ("cover", "section") and not slide.lead
    ]

    # Assert
    assert missing == []


def test_card_metrics_and_tile_values_are_at_most_seven_characters() -> None:
    # Arrange
    deck: Deck = gallery_deck()

    # Act
    texts: list[str] = [
        num.text()
        for _, path, num in all_nums(deck)
        if path.endswith(("metric", "value"))
    ]

    # Assert
    assert len(texts) >= 7
    assert all(len(text) <= 7 for text in texts), texts


def test_chart_units_are_at_most_three_characters() -> None:
    # Arrange
    deck: Deck = gallery_deck()
    units: list[str] = []
    for slide in deck.slides:
        for value in slide.regions.values():
            if isinstance(value, Chart):
                units.append(value.data.unit)
            elif isinstance(value, Tabs):
                units.extend(
                    chart.data.unit for _, charts in value.tabs for chart in charts
                )

    # Act and Assert
    assert len(units) >= 6
    assert all(len(unit) <= 3 for unit in units), units


def test_discussion_title_is_a_question() -> None:
    # Arrange
    deck: Deck = gallery_deck()

    # Act
    title: str = _slide(deck, "discussion").title

    # Assert
    assert title.endswith("?")
