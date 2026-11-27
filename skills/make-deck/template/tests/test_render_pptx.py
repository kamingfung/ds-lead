"""Tests for the native PowerPoint renderer: geometry, native charts, fonts and sources."""

import time
import xml.etree.ElementTree as ET
from dataclasses import fields, is_dataclass
from io import BytesIO
from typing import Iterator

import pytest
from pptx import Presentation
from lxml import etree
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.shapes import MSO_SHAPE, MSO_SHAPE_TYPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

from charts import RENDERERS, ChartData
from layouts import BODY_H, BODY_TOP, LAYOUTS, MARGIN
from render_pptx import EMU_PER_PX, render_pptx
from spec import (
    Bullet,
    Bullets,
    Card,
    Chart,
    Cycle,
    Deck,
    Flow,
    Gantt,
    Bar,
    Matrix,
    Num,
    Para,
    Run,
    Slide,
    Table,
    Tabs,
    Text,
    Tile,
    Timeline,
    Tree,
    sources_slides,
)
from theme import HOUSE

WEEKS: tuple[str, ...] = ("Wk 33", "Wk 34", "Wk 35", "Wk 36")
LINE_DATA: ChartData = ChartData(
    WEEKS,
    (("Orders", (120.0, 135.0, 150.0, 160.0)),),
    unit="orders",
    reference=140.0,
    source="Orders warehouse extract, wk 33-36",
)
WATERFALL_DATA: ChartData = ChartData(
    ("Start", "Price", "Volume", "Mix", "End"),
    (("Margin", (100.0, 5.0, -12.0, 3.0, 96.0)),),
    unit="USD",
)
DIVERGING_DATA: ChartData = ChartData(
    ("North", "South", "East", "West"),
    (("Revenue change", (4.2, -1.5, 2.8, -0.6)),),
    unit="%",
)
STACKED_DATA: ChartData = ChartData(
    ("Retail", "Wholesale"),
    (("Direct", (62.0, 48.0)), ("Partner", (33.0, 45.0)), ("Other", (5.0, 7.0))),
)
COLUMN_DATA: ChartData = ChartData(
    ("Mon", "Tue", "Wed"),
    (("Orders", (410.0, 388.0, 455.0)),),
    highlight=2,
)
TEXT_BULLETS: Bullets = Bullets(
    (
        Bullet("Volume", "Orders rose 8% in week 36"),
        Bullet("Returns", "Fell to 9 units"),
    ),
    heading="Takeaways",
)


def _deck() -> Deck:
    """Build a deck with a cover, a KPI slide, four chart layouts, a tabs slide and every diagram."""
    tabs: Tabs = Tabs(
        (
            (
                "Region",
                (Chart("diverging_bar", DIVERGING_DATA), Chart("column", COLUMN_DATA)),
            ),
            (
                "Channel",
                (Chart("stacked100", STACKED_DATA), Chart("column", COLUMN_DATA)),
            ),
        )
    )
    slides: tuple[Slide, ...] = (
        Slide(
            "cover",
            "Weekly orders review",
            regions={
                "subtitle": Text((Para((Run("Weeks 33 to 36"),)),)),
            },
        ),
        Slide(
            "kpi_split",
            "Orders grew in week 36",
            kicker="Summary",
            lead="Four weeks of orders",
            regions={
                "tiles": (
                    Tile(
                        Num(160.0, ",.0f", "Orders warehouse extract"),
                        "Orders",
                        "Week 36",
                    ),
                    Tile(Num(-3.5, ".1f %", "Returns extract"), "Returns", "Week 36"),
                ),
                "left": TEXT_BULLETS,
                "right": TEXT_BULLETS,
            },
        ),
        Slide(
            "chart_3to1",
            "Orders beat target",
            lead="Orders by week",
            regions={
                "chart": Chart("line", LINE_DATA),
                "takeaways": TEXT_BULLETS,
            },
        ),
        Slide(
            "chart_2to1",
            "Margin bridge",
            notes="Read left to right.",
            regions={
                "chart": Chart("waterfall", WATERFALL_DATA),
                "takeaways": TEXT_BULLETS,
            },
        ),
        Slide(
            "chart_1to1",
            "Revenue change by region",
            regions={
                "chart": Chart("diverging_bar", DIVERGING_DATA),
                "takeaways": TEXT_BULLETS,
            },
        ),
        Slide(
            "tabs",
            "Mix",
            regions={"tabs": tabs, "takeaways": TEXT_BULLETS, "note": Text(())},
        ),
        Slide(
            "table",
            "Orders by region",
            regions={
                "table": Table(
                    ("Region", "Orders"),
                    (("North", Num(1204.0, ",.0f", "Orders extract")),),
                    ("left", "right"),
                ),
                "note": Text((Para((Run("Values as of week 36."),)),)),
            },
        ),
        Slide(
            "cards3",
            "Three levers",
            regions={
                "cards": tuple(
                    Card(
                        f"Lever {n}",
                        f"Lever {n} statement",
                        "Body text.",
                        metric=Num(float(n), ".0f", "Plan"),
                    )
                    for n in (1, 2, 3)
                ),
            },
        ),
        Slide(
            "flow",
            "Order flow",
            regions={
                "diagram": Flow(
                    (
                        ("Receive", "Order file"),
                        ("Check", "Stock"),
                        ("Ship", "Carrier"),
                    ),
                    highlight=1,
                ),
            },
        ),
        Slide(
            "cycle",
            "Weekly loop",
            regions={
                "diagram": Cycle(("Plan", "Pick", "Ship", "Review"), "Weekly loop"),
            },
        ),
        Slide(
            "matrix",
            "Priorities",
            regions={
                "diagram": Matrix(
                    "Effort",
                    "Impact",
                    ("Quick wins", "Big bets", "Fill-ins", "Parked"),
                    (("Faster picks", 0), ("Carrier SLA", 1)),
                ),
            },
        ),
        Slide(
            "gantt",
            "Rollout",
            regions={
                "diagram": Gantt(
                    ("Q1", "Q2", "Q3"),
                    (("Build", (Bar(0.0, 1.5, "Build", False),)),),
                    ((2.0, "Go live"),),
                ),
            },
        ),
        Slide(
            "tree",
            "Scope",
            regions={
                "diagram": Tree("Orders", (("North", ("Stores",)), ("South", ()))),
            },
        ),
        Slide(
            "timeline",
            "Milestones",
            regions={
                "diagram": Timeline(
                    (("Pilot", "Wk 33", "kept"), ("Rollout", "Wk 36", "open"))
                ),
            },
        ),
    )
    return Deck("Weekly orders", "Orders", "week 36", slides)


def _open(deck: Deck) -> Presentation:
    """Render a deck and open the bytes again."""
    return Presentation(BytesIO(render_pptx(deck, HOUSE)))


def _shapes(shapes: object) -> Iterator[object]:
    """Yield every shape, descending into group shapes."""
    for shape in shapes:  # type: ignore[attr-defined]
        yield shape
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from _shapes(shape.shapes)


def _slide_with_title(prs: Presentation, title: str) -> object:
    """Return the first slide whose text includes the given title."""
    for slide in prs.slides:
        texts: list[str] = [s.text_frame.text for s in slide.shapes if s.has_text_frame]
        if title in texts:
            return slide
    raise AssertionError(f"no slide titled {title!r}")


def _charts(prs: Presentation) -> list[object]:
    """Return every chart shape in the presentation."""
    return [s for slide in prs.slides for s in slide.shapes if s.has_chart]


def _chart_xml(shape: object) -> ET.Element:
    """Return the parsed chart XML of a chart shape."""
    from lxml import etree

    return ET.fromstring(etree.tostring(shape.chart._chartSpace))  # type: ignore[attr-defined]


def test_bytes_open_with_widescreen_size() -> None:
    deck: Deck = _deck()

    prs: Presentation = _open(deck)

    assert prs.slide_width == Inches(13.333)
    assert prs.slide_height == Inches(7.5)


def test_same_deck_renders_to_identical_bytes(monkeypatch: pytest.MonkeyPatch) -> None:
    first: bytes = render_pptx(_deck(), HOUSE)
    monkeypatch.setattr(
        time,
        "localtime",
        lambda *_: time.struct_time((2031, 7, 9, 13, 5, 7, 2, 190, 0)),
    )
    assert render_pptx(_deck(), HOUSE) == first


def test_slide_count_is_html_slides_plus_extra_tabs_plus_sources() -> None:
    deck: Deck = _deck()
    expected: int = len(deck.slides) + 1 + len(sources_slides(deck))

    count: int = len(_open(deck).slides)

    assert count == expected


def test_waterfall_has_one_custom_label_per_bar_with_expected_positions() -> None:
    prs: Presentation = _open(_deck())
    waterfall: object = next(
        c for c in _charts(prs) if c.chart.chart_type == XL_CHART_TYPE.COLUMN_STACKED
    )

    labels: list[str] = [
        e.get("val")
        for e in _chart_xml(waterfall).iter(
            "{http://schemas.openxmlformats.org/drawingml/2006/chart}dLblPos"
        )
    ]

    assert len(labels) == 5
    assert labels.count("inEnd") == 3
    assert labels.count("inBase") == 2


def test_waterfall_decrease_label_sits_on_the_hidden_base_series() -> None:
    prs: Presentation = _open(_deck())
    waterfall: object = next(
        c for c in _charts(prs) if c.chart.chart_type == XL_CHART_TYPE.COLUMN_STACKED
    )
    chart_ns: str = "{http://schemas.openxmlformats.org/drawingml/2006/chart}"

    per_series: list[list[str]] = [
        [e.get("val") for e in ser.iter(f"{chart_ns}dLblPos")]
        for ser in _chart_xml(waterfall).iter(f"{chart_ns}ser")
    ]

    assert per_series == [["inEnd"], ["inEnd", "inEnd"], ["inBase", "inBase"]]


def _chart_kinds(node: object) -> set[str]:
    """Return the kind of every Chart anywhere inside a spec node."""
    if isinstance(node, Chart):
        return {node.kind}
    if is_dataclass(node):
        return _chart_kinds([getattr(node, f.name) for f in fields(node)])
    if isinstance(node, dict):
        return _chart_kinds(list(node.values()))
    if isinstance(node, (tuple, list)):
        return set().union(*(_chart_kinds(item) for item in node))
    return set()


def test_test_deck_draws_every_html_chart_kind() -> None:
    """Every pptx test renders _deck(), so this proves each HTML chart kind has a pptx builder."""
    assert _chart_kinds(_deck()) == set(RENDERERS)


def test_every_chart_is_native_and_of_the_right_type() -> None:
    prs: Presentation = _open(_deck())

    types: set[XL_CHART_TYPE] = {c.chart.chart_type for c in _charts(prs)}

    assert all(c.has_chart for c in _charts(prs))
    assert {
        XL_CHART_TYPE.LINE,
        XL_CHART_TYPE.BAR_CLUSTERED,
        XL_CHART_TYPE.COLUMN_STACKED,
        XL_CHART_TYPE.BAR_STACKED_100,
        XL_CHART_TYPE.COLUMN_CLUSTERED,
    } <= types
    line: object = next(
        c for c in _charts(prs) if c.chart.chart_type == XL_CHART_TYPE.LINE
    )
    assert (
        _chart_xml(line).find(
            ".//{http://schemas.openxmlformats.org/drawingml/2006/chart}lineChart"
        )
        is not None
    )


def test_chart_region_shape_sits_at_its_box_within_one_emu_per_pixel() -> None:
    prs: Presentation = _open(_deck())
    slide: object = _slide_with_title(prs, "Orders beat target")
    chart: object = next(s for s in slide.shapes if s.has_chart)  # type: ignore[attr-defined]

    left, top, height = chart.left, chart.top, chart.height  # type: ignore[attr-defined]

    assert abs(left - MARGIN * EMU_PER_PX) <= 1
    assert abs(top - BODY_TOP * EMU_PER_PX) <= 1
    assert abs(height - BODY_H * EMU_PER_PX) <= 1


def test_no_text_run_uses_a_font_other_than_arial_or_consolas() -> None:
    prs: Presentation = _open(_deck())

    fonts: set[str] = {
        run.font.name
        for slide in prs.slides
        for shape in _shapes(slide.shapes)
        if shape.has_text_frame
        for paragraph in shape.text_frame.paragraphs
        for run in paragraph.runs
    }

    assert fonts <= {"Arial", "Consolas"}
    assert fonts


def test_card_is_one_panel_text_box_with_four_run_sizes() -> None:
    prs: Presentation = _open(_deck())
    slide: object = _slide_with_title(prs, "Three levers")
    card: object = next(
        s for s in slide.shapes if s.has_text_frame and "Lever 1" in s.text_frame.text
    )  # type: ignore[attr-defined]

    sizes: list[float] = [
        run.font.size.pt for p in card.text_frame.paragraphs for run in p.runs
    ]  # type: ignore[attr-defined]

    assert sizes[:4] == [12.0, 60.0, 18.0, 14.25]


def test_flow_connectors_have_arrowheads_and_no_theme_style() -> None:
    prs: Presentation = _open(_deck())
    slide: object = _slide_with_title(prs, "Order flow")
    group: object = next(
        s for s in slide.shapes if s.shape_type == MSO_SHAPE_TYPE.GROUP
    )  # type: ignore[attr-defined]

    connectors: list[object] = [
        s for s in group.shapes if s.shape_type == MSO_SHAPE_TYPE.LINE
    ]  # type: ignore[attr-defined]

    assert len(connectors) == 2
    for connector in connectors:
        assert (
            connector._element.find(
                "{http://schemas.openxmlformats.org/presentationml/2006/main}style"
            )
            is None
        )  # type: ignore[attr-defined]
        assert connector._element.xpath(".//a:tailEnd[@type='triangle']")  # type: ignore[attr-defined]


def test_notes_carry_the_chart_source_as_sources_line() -> None:
    prs: Presentation = _open(_deck())
    slide: object = _slide_with_title(prs, "Orders beat target")

    notes: str = slide.notes_slide.notes_text_frame.text  # type: ignore[attr-defined]

    assert "Sources: Orders warehouse extract, wk 33-36" in notes


def test_each_extra_tab_gets_its_own_slide_with_the_tab_name() -> None:
    prs: Presentation = _open(_deck())

    titles: list[str] = [
        s.text_frame.text
        for slide in prs.slides
        for s in slide.shapes
        if s.has_text_frame and s.text_frame.text.startswith("Mix")
    ]

    assert titles == ["Mix \u00b7 Region", "Mix \u00b7 Channel"]


def test_numeric_table_cells_are_right_aligned_in_mono() -> None:
    prs: Presentation = _open(_deck())
    slide: object = _slide_with_title(prs, "Orders by region")
    table: object = next(s for s in slide.shapes if s.has_table)  # type: ignore[attr-defined]

    cell = table.table.cell(1, 1)  # type: ignore[attr-defined]
    run = cell.text_frame.paragraphs[0].runs[0]

    assert cell.text_frame.paragraphs[0].alignment == PP_ALIGN.RIGHT
    assert run.font.name == "Consolas"
    assert run.text == "1,204"


def test_footer_has_source_and_page_number_on_slide_two() -> None:
    prs: Presentation = _open(_deck())
    boxes: list[object] = [s for s in prs.slides[1].shapes if s.has_text_frame]  # type: ignore[attr-defined]

    assert any(b.text_frame.text.startswith("Source: ") for b in boxes)  # type: ignore[attr-defined]
    pages: list[object] = [b for b in boxes if b.text_frame.text == "2"]  # type: ignore[attr-defined]
    assert len(pages) == 1
    assert pages[0].text_frame.paragraphs[0].alignment == PP_ALIGN.RIGHT  # type: ignore[attr-defined]


def test_footer_rule_has_no_theme_style() -> None:
    prs: Presentation = _open(_deck())
    rules: list[object] = [
        s
        for s in prs.slides[1].shapes  # type: ignore[attr-defined]
        if s.shape_type == MSO_SHAPE_TYPE.LINE and abs(s.top - 676 * EMU_PER_PX) <= 1
    ]  # type: ignore[attr-defined]

    assert len(rules) == 1
    assert (
        rules[0]._element.find(
            "{http://schemas.openxmlformats.org/presentationml/2006/main}style"
        )
        is None
    )  # type: ignore[attr-defined]
    assert rules[0].line.width == Pt(0.75)  # type: ignore[attr-defined]


def test_chart_layout_lead_is_bold() -> None:
    prs: Presentation = _open(_deck())
    slide: object = _slide_with_title(prs, "Orders beat target")
    lead: object = next(
        s
        for s in slide.shapes
        if s.has_text_frame and s.text_frame.text == "Orders by week"
    )  # type: ignore[attr-defined]

    assert lead.text_frame.paragraphs[0].runs[0].font.bold is True  # type: ignore[attr-defined]


def test_card_paragraphs_come_in_tag_metric_statement_body_order() -> None:
    prs: Presentation = _open(_deck())
    slide: object = _slide_with_title(prs, "Three levers")
    card: object = next(
        s for s in slide.shapes if s.has_text_frame and "Lever 1" in s.text_frame.text
    )  # type: ignore[attr-defined]

    paragraphs: list[str] = [p.text for p in card.text_frame.paragraphs]  # type: ignore[attr-defined]

    assert paragraphs == ["LEVER 1", "1", "Lever 1 statement", "Body text."]


def test_line_chart_reference_series_is_named_from_reference_label() -> None:
    data: ChartData = ChartData(
        WEEKS,
        (("Orders", (120.0, 135.0, 150.0, 160.0)), ("Returns", (9.0, 8.0, 7.0, 6.0))),
        unit="orders",
        reference=140.0,
        source="Orders warehouse extract, wk 33-36",
    )
    deck: Deck = Deck(
        "Line",
        "Orders",
        "week 36",
        (
            Slide(
                "chart_3to1",
                "Orders beat target",
                regions={"chart": Chart("line", data), "takeaways": TEXT_BULLETS},
            ),
        ),
    )

    series: list[str] = [s.name for s in _charts(_open(deck))[0].chart.series]  # type: ignore[attr-defined]

    assert series[2] == "Target"


def _one(layout: str, regions: dict[str, object], title: str = "Check") -> Presentation:
    """Render a deck with one content slide and open it; the content slide is first."""
    return _open(
        Deck("Check", "Check", "week 36", (Slide(layout, title, regions=regions),))
    )


def _run_of(prs: Presentation, text: str) -> object:
    """Return the first text run, in any shape, whose text contains the given text."""
    for slide in prs.slides:
        for shape in _shapes(slide.shapes):
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    for run in para.runs:
                        if text in run.text:
                            return run
    raise AssertionError(f"no run contains {text!r}")


def _apart(a: object, b: object) -> bool:
    """Return True when two shapes do not overlap."""
    return (
        a.left + a.width <= b.left
        or b.left + b.width <= a.left  # type: ignore[attr-defined]
        or a.top + a.height <= b.top
        or b.top + b.height <= a.top
    )  # type: ignore[attr-defined]


def test_long_card_metric_is_fit_below_the_80_px_cap() -> None:
    card: Card = Card(
        "Orders",
        "Long metric",
        "Body.",
        metric=Num(1234567.0, ",.0f orders in one week", "src"),
    )

    run: object = _run_of(
        _one("cards3", {"cards": (card, card, card)}), "orders in one week"
    )

    assert run.font.size.pt < 80 * 0.75  # type: ignore[attr-defined]


def test_tile_value_and_big_number_are_fit_to_their_caps() -> None:
    tile: Tile = Tile(Num(1234567.0, ",.0f orders in one week", "src"), "Orders")
    big: Num = Num(1234567890.0, ",.0f orders", "src")

    tile_run: object = _run_of(
        _one(
            "kpi_split", {"tiles": (tile,), "left": TEXT_BULLETS, "right": TEXT_BULLETS}
        ),
        "orders in one week",
    )
    big_run: object = _run_of(_one("big_number", {"number": big}), "orders")

    assert tile_run.font.size.pt <= 56 * 0.75  # type: ignore[attr-defined]
    assert big_run.font.size.pt < 120 * 0.75  # type: ignore[attr-defined]


def test_value_axis_has_no_unit_and_long_units_leave_chart_labels() -> None:
    data: ChartData = ChartData(
        ("Mon", "Tue"), (("Orders", (410.0, 388.0)),), unit="orders"
    )
    prs: Presentation = _one(
        "chart_1to1", {"chart": Chart("column", data), "takeaways": TEXT_BULLETS}
    )
    chart: object = _charts(prs)[0].chart  # type: ignore[attr-defined]

    xml: str = etree.tostring(chart._chartSpace).decode()  # type: ignore[attr-defined]

    assert chart.value_axis.tick_labels.number_format == "#,##0"  # type: ignore[attr-defined]
    assert "orders" not in xml


def test_short_units_stay_on_chart_labels_and_line_end_reads_series_and_value() -> None:
    data: ChartData = ChartData(
        WEEKS, (("Orders", (120.0, 135.0, 150.0, 160.0)),), unit="min"
    )
    prs: Presentation = _one(
        "chart_3to1", {"chart": Chart("line", data), "takeaways": TEXT_BULLETS}
    )
    xml: str = etree.tostring(_charts(prs)[0].chart._chartSpace).decode()  # type: ignore[attr-defined]

    assert "Orders 160 min" in xml


def test_grid4_draws_a_two_by_two_grid_with_numbered_headings() -> None:
    names: tuple[str, ...] = ("Alpha", "Beta", "Gamma", "Delta")
    blocks: tuple[Bullets, ...] = tuple(
        Bullets((Bullet("Lead", "text"),), heading=n) for n in names
    )
    prs: Presentation = _one("grid4", {"blocks": blocks})
    heads: list[object] = [
        s
        for s in _shapes(prs.slides[0].shapes)
        if s.has_text_frame and any(n in s.text_frame.text for n in names)
    ]

    assert [h.text_frame.paragraphs[0].text for h in heads] == [
        "1  Alpha",
        "2  Beta",
        "3  Gamma",
        "4  Delta",
    ]
    assert len({h.left for h in heads}) == 2
    assert len({h.top for h in heads}) == 2


def test_flow_sub_label_shrinks_to_14_px_before_it_wraps() -> None:
    long_detail: str = (
        "A very long detail that cannot fit on one line in the flow box at any size"
    )
    prs: Presentation = _one(
        "flow",
        {
            "diagram": Flow(
                (("Receive", long_detail), ("Check", "Stock"), ("Ship", "Carrier"))
            )
        },
    )

    run: object = _run_of(prs, "A very long detail")

    assert run.font.size.pt == 14 * 0.75  # type: ignore[attr-defined]


def test_cycle_nodes_sit_inside_the_region_clear_of_the_center_and_arrows_are_four() -> (
    None
):
    prs: Presentation = _one(
        "cycle", {"diagram": Cycle(("Plan", "Pick", "Ship", "Review"), "Weekly loop")}
    )
    group: object = next(
        s for s in prs.slides[0].shapes if s.shape_type == MSO_SHAPE_TYPE.GROUP
    )  # type: ignore[attr-defined]
    children: list[object] = list(group.shapes)  # type: ignore[attr-defined]
    nodes: list[object] = [
        c
        for c in children
        if c.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE
        and c.auto_shape_type == MSO_SHAPE.ROUNDED_RECTANGLE
    ]  # type: ignore[attr-defined]
    center: object = next(
        c for c in children if c.has_text_frame and c.text_frame.text == "Weekly loop"
    )  # type: ignore[attr-defined]
    arrows: list[object] = [
        c
        for c in children
        if c.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE  # type: ignore[attr-defined]
        and c.auto_shape_type == MSO_SHAPE.ISOSCELES_TRIANGLE
    ]
    assert not [
        c for c in children if c.shape_type == MSO_SHAPE_TYPE.LINE
    ]  # no curved connectors  # type: ignore[attr-defined]

    assert len(nodes) == 4
    assert len(arrows) == 4
    region: object = LAYOUTS["cycle"]["diagram"]
    assert all(
        region.x * EMU_PER_PX <= n.left
        and n.left + n.width <= (region.x + region.w) * EMU_PER_PX  # type: ignore[attr-defined]
        for n in nodes
    )
    assert all(
        region.y * EMU_PER_PX <= n.top
        and n.top + n.height <= (region.y + region.h) * EMU_PER_PX  # type: ignore[attr-defined]
        for n in nodes
    )
    assert all(_apart(n, center) for n in nodes)


def test_timeline_markers_are_shapes_and_the_legend_has_no_emoji() -> None:
    prs: Presentation = _one(
        "timeline",
        {
            "diagram": Timeline(
                (
                    ("Pilot", "Wk 33", "kept"),
                    ("Rollout", "Wk 36", "dropped"),
                    ("Review", "Wk 36", "open"),
                )
            )
        },
    )
    texts: list[str] = [
        run.text
        for s in _shapes(prs.slides[0].shapes)
        if s.has_text_frame
        for p in s.text_frame.paragraphs
        for run in p.runs
    ]

    assert all(ord(ch) < 0x1F000 for text in texts for ch in text)
    assert {"Kept", "Dropped", "Open"} <= set(texts)


def test_options3_recommendation_strip_is_tinted_padded_and_leads_in_bold() -> None:
    cards: tuple[Card, ...] = (Card("Option A", "Statement", "Body."),)
    prs: Presentation = _one(
        "options3",
        {"cards": cards, "recommendation": Text((Para((Run("Fund Option B."),)),))},
    )
    strip: object = next(
        s
        for s in prs.slides[0].shapes
        if s.has_text_frame and s.text_frame.text.startswith("Recommendation:")
    )

    assert strip.text_frame.paragraphs[0].runs[0].font.bold is True  # type: ignore[attr-defined]
    assert strip.fill.fore_color.rgb == RGBColor.from_string("E6EFF3")  # type: ignore[attr-defined]
    assert strip.text_frame.margin_left == Emu(16 * EMU_PER_PX)  # type: ignore[attr-defined]


def test_chart_layout_without_a_takeaways_heading_gets_takeaways() -> None:
    takeaways: Bullets = Bullets((Bullet("Lead", "text"),))
    prs: Presentation = _one(
        "chart_3to1", {"chart": Chart("line", LINE_DATA), "takeaways": takeaways}
    )

    paragraphs: list[str] = [
        p.text
        for s in prs.slides[0].shapes
        if s.has_text_frame
        for p in s.text_frame.paragraphs
    ]

    assert "Takeaways" in paragraphs


def test_references_paragraphs_are_numbered() -> None:
    body: Text = Text((Para((Run("First source."),)), Para((Run("Second source."),))))
    prs: Presentation = _one("references", {"body": body})

    texts: list[str] = [
        p.text
        for s in prs.slides[0].shapes
        if s.has_text_frame
        for p in s.text_frame.paragraphs
    ]

    assert "1. First source." in texts
    assert "2. Second source." in texts


def test_note_heading_is_24_px_bold_ink() -> None:
    prs: Presentation = _one(
        "note",
        {
            "heading": Text((Para((Run("What changed"),)),)),
            "body": Text((Para((Run("Body."),)),)),
        },
    )

    run: object = _run_of(prs, "What changed")

    assert run.font.size.pt == 24 * 0.75  # type: ignore[attr-defined]
    assert run.font.bold is True  # type: ignore[attr-defined]
    assert run.font.color.rgb == RGBColor.from_string("3B1A18")  # type: ignore[attr-defined]


def test_cover_has_an_ink_background_and_paper_title():
    # Arrange
    from io import BytesIO
    from pptx import Presentation
    from spec import Deck, Slide
    from theme import HOUSE

    deck = Deck("t", "t", "2026-11-27", (Slide("cover", "Orders rose 14.5%"),))
    # Act
    slide = Presentation(BytesIO(render_pptx(deck, HOUSE))).slides[0]
    # Assert
    assert str(slide.background.fill.fore_color.rgb) == HOUSE.ink.lstrip("#").upper()
    runs = [
        r
        for s in slide.shapes
        if s.has_text_frame
        for p in s.text_frame.paragraphs
        for r in p.runs
        if r.text
    ]
    assert runs and all(
        str(r.font.color.rgb) != HOUSE.ink.lstrip("#").upper() for r in runs
    )


def test_tree_runs_left_to_right_with_straight_links_only() -> None:
    from spec import Tree

    prs: Presentation = _one(
        "tree",
        {
            "diagram": Tree(
                "Orders", (("Customers", ("New", "Repeat")), ("Basket", ("Size",)))
            )
        },
    )
    group: object = next(
        s for s in prs.slides[0].shapes if s.shape_type == MSO_SHAPE_TYPE.GROUP
    )  # type: ignore[attr-defined]
    named: dict[str, object] = {
        c.text_frame.text: c
        for c in group.shapes
        if c.has_text_frame and c.text_frame.text
    }  # type: ignore[attr-defined]
    assert named["Orders"].left < named["Customers"].left < named["New"].left  # type: ignore[attr-defined]
    xml: str = group._element.xml  # type: ignore[attr-defined]
    assert "bentConnector" not in xml and "curvedConnector" not in xml


def test_gantt_has_lane_rules_a_dashed_milestone_line_and_dashed_planned_bars() -> None:
    gantt: Gantt = Gantt(
        ("Wk 1", "Wk 2"),
        (
            ("Vans", (Bar(0.0, 1.0, "Refit", False),)),
            ("Routes", (Bar(1.0, 2.0, "Rollout", True),)),
        ),
        ((1.0, "Live"),),
    )
    prs: Presentation = _one("gantt", {"diagram": gantt})
    group: object = next(
        s for s in prs.slides[0].shapes if s.shape_type == MSO_SHAPE_TYPE.GROUP
    )  # type: ignore[attr-defined]
    lines: list[object] = [
        c for c in group.shapes if c.shape_type == MSO_SHAPE_TYPE.LINE
    ]  # type: ignore[attr-defined]
    dashed: list[object] = [
        c for c in group.shapes if 'prstDash val="dash"' in c._element.xml
    ]  # type: ignore[attr-defined]
    assert len(lines) >= 4  # header rule, two lane rules, one milestone line
    names: set[str] = {c.text_frame.text for c in dashed if c.has_text_frame}  # type: ignore[attr-defined]
    assert "Rollout" in names and "Refit" not in names
