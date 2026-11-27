"""Tests for the HTML renderer: layouts, sourced numbers, tabs, diagrams and print rules."""

import re
from html.parser import HTMLParser

from charts import ChartData
from layouts import LAYOUTS, chrome
from render_html import HERE, render_html
from spec import (
    Bar,
    Bullet,
    Bullets,
    Card,
    Chart,
    Cycle,
    Deck,
    Flow,
    Gantt,
    Matrix,
    Num,
    Panel,
    Para,
    Run,
    Slide,
    Table,
    Tabs,
    Text,
    Tile,
    Timeline,
    Tree,
    all_nums,
    lead_in,
)
from theme import HOUSE

SECTION: re.Pattern[str] = re.compile(
    r'<section class="slide[^"]*" data-layout="(\w+)">(.*?)</section>', re.S
)
REGION: re.Pattern[str] = re.compile(
    r'<div class="region r-(\w+)" style="left:(\d+)px;top:(\d+)px;width:(\d+)px;height:(\d+)px"'
)
WEEKS: tuple[str, ...] = ("Wk 44", "Wk 45", "Wk 46")
SOURCE: str = "Warehouse extract, week 46"


def _num() -> Num:
    return Num(1234.0, ",.0f USD", SOURCE)


def _chart() -> Chart:
    data: ChartData = ChartData(
        WEEKS, (("Orders", (310.0, 325.0, 342.0)),), "orders", source=SOURCE
    )
    return Chart("column", data)


def _sample(accepts: tuple[str, ...], name: str) -> object:
    """Build one valid block for a region, chosen by the region's first accepted type."""
    samples: dict[str, object] = {
        "Text": Text((lead_in("Lead", "Sample sentence."),)),
        "Bullets": Bullets((Bullet("Lead", "Sample item", footnote="1"),)),
        "Card": Card(
            "Option",
            "Statement",
            "Body text",
            metric=_num(),
            rows=(Bullet("Row", "Detail"),),
        ),
        "Tile": Tile(_num(), "Orders", "Week 46"),
        "Table": Table(
            ("Region", "Orders"), (("North", _num()),), ("left", "right"), note="Sample"
        ),
        "Chart": _chart(),
        "Matrix": Matrix(
            "Effort",
            "Impact",
            ("Quick wins", "Major", "Fill-ins", "Avoid"),
            (("Item", 0),),
        ),
        "Flow": Flow(
            (("Plan", "Scope"), ("Build", "Code"), ("Ship", "Release")), highlight=1
        ),
        "Cycle": Cycle(("Plan", "Do", "Check", "Act"), "Loop"),
        "Gantt": Gantt(
            ("Jan", "Feb", "Mar"),
            (("Build", (Bar(0.0, 1.5, "Plan", True),)),),
            ((2.0, "Launch"),),
        ),
        "Tree": Tree("Revenue", (("North", ("Store",)), ("South", ("Web",)))),
        "Timeline": Timeline(
            (
                ("Nov 3", "Pilot", "kept"),
                ("Nov 10", "Scope", "dropped"),
                ("Nov 17", "Pricing", "open"),
            )
        ),
        "Tabs": Tabs(
            (("Weekly", (_chart(), _chart())), ("Monthly", (_chart(), _chart())))
        ),
        "Num": _num(),
        "Panel": Panel("Questions"),
    }
    return samples[accepts[0]]


def _layout_slide(layout: str) -> Slide:
    regions: dict[str, object] = {}
    for name, region in LAYOUTS[layout].items():
        if region.accepts[0] == "str":
            continue
        block: object = _sample(region.accepts, name)
        regions[name] = (block,) if region.unit == "block" else block
    return Slide(
        layout,
        f"{layout} title",
        kicker="Kicker",
        lead="Lead",
        regions=regions,
        footer="Note",
    )


def _deck(*slides: Slide) -> Deck:
    return Deck("Sample deck", "Sample", "2026-11-20", slides)


def _all_layouts_html() -> str:
    return render_html(_deck(*(_layout_slide(name) for name in LAYOUTS)), HOUSE)


class _Balance(HTMLParser):
    """Track open and close tags; record any close tag that does not match the open stack."""

    VOID: frozenset[str] = frozenset({"meta", "br", "img", "input", "link", "hr"})

    def __init__(self) -> None:
        super().__init__()
        self.stack: list[str] = []
        self.errors: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(tag)
        elif self.stack:
            self.stack.pop()


def test_every_layout_renders_one_slide_each() -> None:
    html: str = _all_layouts_html()
    layouts: list[str] = [name for name, _ in SECTION.findall(html)]
    assert set(layouts) == set(LAYOUTS)
    assert (
        len(layouts) == len(LAYOUTS) + 2 + 1
    )  # two tabs print copies, one sources slide
    assert layouts.count("tabs") == 3


def test_html_has_no_http_url() -> None:
    html: str = _all_layouts_html()
    assert "http" not in html


def test_every_region_sits_at_its_layout_box() -> None:
    html: str = _all_layouts_html()
    for layout, body in SECTION.findall(html):
        boxes = {**LAYOUTS[layout], **chrome(layout)}
        for name, x, y, w, h in REGION.findall(body):
            if name == "vline":
                continue
            box = boxes[name]
            assert (int(x), int(y), int(w), int(h)) == (box.x, box.y, box.w, box.h), (
                layout,
                name,
            )


def test_every_num_has_a_source_title() -> None:
    deck: Deck = _deck(*(_layout_slide(name) for name in LAYOUTS))
    html: str = render_html(deck, HOUSE)
    spans: list[str] = re.findall(r'<span class="num"[^>]*>', html)
    assert len(spans) == len(all_nums(deck))
    assert all(
        re.match(r'<span class="num" title="Source: [^"]+"', span) for span in spans
    )


def test_tab_panels_are_present_for_each_tab() -> None:
    html: str = _all_layouts_html()
    assert html.count('role="tab" ') == 2
    assert html.count('class="tab-panel') == 4
    assert 'data-panel="0"' in html and 'data-panel="1"' in html
    assert html.count('class="slide print-only"') == 2


def test_output_parses_with_balanced_tags() -> None:
    parser: _Balance = _Balance()
    parser.feed(_all_layouts_html())
    parser.close()
    assert parser.errors == []
    assert parser.stack == []


def test_chart_layouts_draw_a_divider_region() -> None:
    html: str = _all_layouts_html()
    assert html.count('class="region r-vline"') == 4
    assert "border-left:1px solid var(--light)" in (HERE / "deck.css").read_text(
        encoding="utf-8"
    )


def test_theme_tokens_become_css_variables() -> None:
    html: str = _all_layouts_html()
    assert "--ink: #3b1a18;" in html
    assert "--title-px: 32px;" in html
    assert "--head-font: 'Arial';" in html


def test_css_reads_variables_only_and_sets_print_and_reduced_motion() -> None:
    css: str = (HERE / "deck.css").read_text(encoding="utf-8")
    assert re.search(r"#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(", css) is None
    assert (
        "@page{size:1280px 720px;margin:0}" in css and "prefers-reduced-motion" in css
    )


def test_footer_has_source_left_and_page_number_right_counting_sources_slides() -> None:
    html: str = render_html(
        _deck(_layout_slide("grid4"), _layout_slide("table")), HOUSE
    )
    sections: list[tuple[str, str]] = SECTION.findall(html)
    footer: str = (
        f'<div class="region r-footer" style="left:56px;top:676px;width:1168px;height:24px">'
        f'<span>Source: {SOURCE}</span><span class="pg">2</span></div>'
    )
    assert footer in sections[1][1]
    assert (
        '<span class="pg">3</span></div>' in sections[2][1]
        and "Backup \u00b7 Sources" in html
    )
    assert "Note" not in html


def test_lead_is_ink_and_bold_on_chart_and_tabs_layouts() -> None:
    css: str = (HERE / "deck.css").read_text(encoding="utf-8")
    base: str = re.search(r"\.r-lead\{([^}]*)\}", css)[1]
    assert "color:var(--ink)" in base and "font-weight" not in base
    assert (
        '[data-layout^="chart_"] .r-lead,.slide[data-layout="tabs"] .r-lead{font-weight:700}'
        in css
    )
    assert 'class="region r-lead"' in render_html(
        _deck(_layout_slide("chart_3to1")), HOUSE
    )


def test_svg_text_rules_in_css_set_no_fill() -> None:
    css: str = (HERE / "deck.css").read_text(encoding="utf-8")
    rules: list[str] = re.findall(r"svg text[^{]*\{([^}]*)\}", css)
    assert rules and all("fill" not in rule for rule in rules)


def test_waterfall_total_keeps_its_paper_fill_attribute() -> None:
    data: ChartData = ChartData(
        ("Start", "Step", "End"), (("Change", (100.0, 20.0, 120.0)),)
    )
    slide: Slide = Slide(
        "chart_3to1",
        "Bridge",
        regions={
            "chart": Chart("waterfall", data),
            "takeaways": Bullets((Bullet("Up", "20"),), heading="Takeaways"),
        },
    )
    html: str = render_html(_deck(slide), HOUSE)
    assert re.search(rf'<text [^>]*fill="{HOUSE.paper}"[^>]*>120</text>', html)
    assert 'fill="@' not in html

    html: str = _all_layouts_html()
    assert html.count('class="box hot"') == 1
    assert html.count('class="head"') >= 4
    assert (
        'class="icon kept"' in html
        and 'class="icon dropped"' in html
        and 'class="icon open"' in html
    )
    assert not re.search(r"[\U00002600-\U000027BF\U0001F000-\U0001FAFF]", html)
    assert (
        'class="bar planned"' in html
        and 'class="milestone"' in html
        and 'class="diamond"' in html
    )


def test_script_handles_navigation_keys_and_scaling() -> None:
    script: str = (HERE / "deck.js").read_text(encoding="utf-8")
    for key in ("ArrowRight", "PageDown", "PageUp", "ArrowLeft"):
        assert key in script
    assert '" "' in script and "--scale" in script and "touchend" in script


def _style_sizes(html: str, css: str) -> list[float]:
    return [
        float(size)
        for size in re.findall(
            rf'<[^>]*class="{css}"[^>]*style="font-size:([\d.]+)px"', html
        )
    ]


def test_card_metric_tile_and_big_number_sizes_stay_within_their_caps() -> None:
    long: Num = Num(1234567.0, ",.0f USD", SOURCE)
    slide: Slide = Slide(
        "cards3",
        "Caps",
        regions={
            "cards": (Card("A", "S", "B", metric=long),) * 3,
        },
    )
    html: str = render_html(
        _deck(slide, _layout_slide("kpi_split"), _layout_slide("big_number")), HOUSE
    )
    assert all(size <= 80.0 for size in _style_sizes(html, "num")[:3])
    assert max(_style_sizes(html, "num")) <= 120.0
    assert all(size >= 24.0 for size in _style_sizes(html, "num"))


def test_column_chart_tick_and_value_labels_drop_a_long_unit() -> None:
    html: str = render_html(_deck(_layout_slide("chart_3to1")), HOUSE)
    end_labels: list[str] = re.findall(r'text-anchor="end"[^>]*>([^<]*)</text>', html)
    assert end_labels and not any("orders" in label for label in end_labels)
    assert "Wk 46" in html and ">342</text>" in html and "342 orders" not in html


def test_grid4_renders_a_two_by_two_grid_of_numbered_cells() -> None:
    blocks: tuple[Bullets, ...] = tuple(
        Bullets((Bullet("Lead", "Item"),), heading=f"Block {n}") for n in range(4)
    )
    html: str = render_html(
        _deck(Slide("grid4", "Grid", regions={"blocks": blocks})), HOUSE
    )
    assert html.count('class="cell"') == 4
    assert all(f'<span class="n">{n}</span>' in html for n in range(1, 5))
    assert (
        'class="grid4"' in html and "multi" not in html.split('class="grid4"')[1][:200]
    )


def test_long_flow_detail_shrinks_to_14_px_then_wraps() -> None:
    long: str = (
        "Reconcile the weekly orders against the warehouse ledger and fix each gap"
    )
    slide: Slide = Slide(
        "flow",
        "Flow",
        regions={"diagram": Flow((("Plan", long), ("Ship", "Done"), ("Check", "Ok")))},
    )
    html: str = render_html(_deck(slide), HOUSE)
    assert "font-size:14.0px" in html
    assert "Reconcile the weekly orders against the" in html
    assert "Reconcile the weekly orders against the warehouse" not in html


def test_cycle_nodes_sit_inside_the_region_and_the_centre_stays_clear() -> None:
    html: str = render_html(_deck(_layout_slide("cycle")), HOUSE)
    boxes: list[tuple[float, ...]] = [
        tuple(float(v) for v in m)
        for m in re.findall(
            r'<rect class="box" x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"',
            html,
        )
    ]
    assert len(boxes) == 4
    for x, y, w, h in boxes:
        assert 0 <= x and 0 <= y and x + w <= 900 and y + h <= 468
        assert not (x <= 450 <= x + w and y <= 234 <= y + h)
    assert len(re.findall(r'<polyline class="edge"', html)) == 4


def test_timeline_markers_are_palette_shapes_with_a_legend() -> None:
    html: str = render_html(_deck(_layout_slide("timeline")), HOUSE)
    svg: str = re.search(r'data-layout="timeline">.*?</section>', html, re.S)[0]
    assert not re.search(r"[\U00002600-\U000027BF\U0001F000-\U0001FAFF]", svg)
    assert (
        'class="icon kept"' in svg
        and 'class="icon dropped"' in svg
        and 'class="icon open"' in svg
    )
    assert all(word in svg for word in ("Kept", "Dropped", "Open"))


def test_options3_recommendation_is_a_tinted_strip_with_a_bold_lead() -> None:
    slide: Slide = Slide(
        "options3",
        "Choose",
        regions={
            "cards": (Card("A", "S", "B"),) * 3,
            "recommendation": Text((Para((Run("Adopt the pilot."),)),)),
        },
    )
    html: str = render_html(_deck(slide), HOUSE)
    assert (
        '<div class="strip"><p><strong>Recommendation:</strong> Adopt the pilot.</p></div>'
        in html
    )
    assert ".strip{background:var(--tint);padding:16px" in (
        HERE / "deck.css"
    ).read_text(encoding="utf-8")


def test_takeaways_default_to_a_heading_on_chart_and_tabs_layouts() -> None:
    html: str = _all_layouts_html()
    assert html.count("<h3>Takeaways</h3>") >= 4


def test_references_are_numbered_from_one() -> None:
    paras: tuple[Para, ...] = tuple(Para((Run(f"Source {n}."),)) for n in range(1, 4))
    html: str = render_html(
        _deck(Slide("references", "Refs", regions={"body": Text(paras)})), HOUSE
    )
    assert "<p>1. Source 1.</p>" in html and "<p>3. Source 3.</p>" in html


def test_note_heading_is_24_px_bold_ink() -> None:
    css: str = (HERE / "deck.css").read_text(encoding="utf-8")
    assert (
        '.slide[data-layout="note"] .r-heading{font-size:var(--subheading-px);font-weight:700;color:var(--ink)}'
        in css
    )


def test_each_tab_panel_holds_two_charts() -> None:
    html: str = _all_layouts_html()
    panels: list[str] = re.findall(
        r'<div class="tab-panel[^"]*" role="tabpanel"[^>]*><div class="pair">(.*?)</div></div>',
        html,
        re.S,
    )
    assert len(panels) == 4
    assert all(panel.count("<svg") == 2 for panel in panels)


def test_prose_blocks_in_one_region_stack_in_one_column():
    # Arrange
    from spec import Bullet, Bullets, Deck, Para, Run, Slide, Text
    from theme import HOUSE

    slide = Slide(
        "brief",
        "Grow orders",
        lead="Plan",
        regions={
            "body": (
                Text((Para((Run("First point."),)),)),
                Bullets((Bullet("Ask", "Approve the shift."),)),
            )
        },
    )
    # Act
    html = render_html(Deck("t", "t", "2026-11-27", (slide,)), HOUSE)
    # Assert
    assert '<div class="stack">' in html and '<div class="multi">' not in html


def test_cover_slide_css_sets_an_ink_background():
    # Arrange
    css = (HERE / "deck.css").read_text()
    # Act / Assert
    assert '.slide[data-layout="cover"]{background:var(--ink)}' in css


def test_print_copies_of_a_tabs_slide_show_their_panel():
    # Arrange
    css = (HERE / "deck.css").read_text()
    # Act / Assert
    assert (
        ".slide.print-only .tab-panel{display:block!important;animation:none!important;opacity:1!important}"
        in css
    )
