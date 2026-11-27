"""Sample deck with one slide per layout, every chart kind and a two-tab slide.

The content is about an online grocer's weekly orders, regions, delivery times and prices.
Every number is a Num or a chart value computed here from the inline tables.
Run ``python3 gallery.py <out_dir>`` to write ``gallery.html`` and ``gallery.pptx``.
"""

from __future__ import annotations

import sys
from collections.abc import Iterable, Sequence
from pathlib import Path

from charts import ChartData
from render_html import render_html
from render_pptx import render_pptx
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
    validate,
)
from theme import HOUSE

SOURCE: str = "sample data, gallery.py"
WEEKS: tuple[str, ...] = ("Wk 33", "Wk 34", "Wk 35", "Wk 36")
REGIONS: tuple[str, ...] = ("North", "South", "East", "West")
CHANNELS: tuple[str, ...] = ("App", "Web", "Phone")
ORDERS: dict[str, tuple[int, ...]] = {
    "North": (4200, 4480, 4710, 5010),
    "South": (3100, 3190, 3350, 3420),
    "East": (2650, 2720, 2880, 3010),
    "West": (3300, 3420, 3560, 3730),
}
DELIVERY_WK33: dict[str, float] = {
    "North": 40.0,
    "South": 41.0,
    "East": 42.0,
    "West": 37.0,
}
DELIVERY_WK36: dict[str, float] = {
    "North": 36.0,
    "South": 42.0,
    "East": 39.0,
    "West": 34.0,
}
BASKET_USD: tuple[float, ...] = (58.40, 59.10, 60.25, 61.90)
BASKET_WK36: dict[str, float] = {
    "North": 64.10,
    "South": 60.20,
    "East": 57.80,
    "West": 63.50,
}
CHANNEL_SHARE: dict[str, tuple[float, ...]] = {
    "North": (62.0, 30.0, 8.0),
    "South": (55.0, 36.0, 9.0),
    "East": (48.0, 41.0, 11.0),
    "West": (70.0, 22.0, 8.0),
}
ORDER_TARGET: float = 14000.0


def num(value: float, fmt: str) -> Num:
    """Wrap a computed value as a Num that cites this file."""
    return Num(value, fmt, SOURCE)


def floats(values: Iterable[float]) -> tuple[float, ...]:
    """Return the values as a tuple of floats, for chart series."""
    return tuple(float(value) for value in values)


def weekly_totals() -> tuple[int, ...]:
    """Return total orders per week, summed over all regions."""
    return tuple(
        sum(ORDERS[region][week] for region in REGIONS) for week in range(len(WEEKS))
    )


def growth_rate(series: Sequence[float]) -> float:
    """Return the change from the first value to the last, as a fraction."""
    return series[-1] / series[0] - 1


def region_change(region: str) -> int:
    """Return the order change for one region from week 33 to week 36."""
    return ORDERS[region][-1] - ORDERS[region][0]


def delivery_change(region: str) -> float:
    """Return the change in median delivery minutes for one region, week 33 to week 36."""
    return DELIVERY_WK36[region] - DELIVERY_WK33[region]


def para(*texts: str) -> Text:
    """Build a text block with one paragraph per argument."""
    return Text(tuple(Para((Run(text),)) for text in texts))


def bullets(heading: str, *items: tuple[str, str]) -> Bullets:
    """Build a bullet list from (lead, text) pairs, with an optional heading."""
    return Bullets(tuple(Bullet(lead, text) for lead, text in items), heading=heading)


def column(
    name: str,
    categories: tuple[str, ...],
    values: tuple[float, ...],
    highlight: int = -1,
) -> Chart:
    """Build a column chart with one series and an optional highlighted bar."""
    data: ChartData = ChartData(
        categories, ((name, values),), highlight=highlight, source=SOURCE
    )
    return Chart("column", data)


def slide(layout: str, title: str, regions: dict[str, object], lead: str = "") -> Slide:
    """Build a slide whose kicker names its layout id and whose lead names the content."""
    return Slide(layout=layout, title=title, kicker=layout, lead=lead, regions=regions)


def _cover_and_section() -> tuple[Slide, Slide]:
    growth: Num = num(growth_rate(weekly_totals()), ".1%")
    cover: Slide = slide(
        "cover",
        f"Weekly orders rose {growth.text()} in four weeks, and the North added the most",
        {
            "subtitle": para(
                "Orders, regions, delivery times and prices for an online grocer."
            ),
            "meta": para(
                "Sample deck for the make-deck template. All figures are sample data."
            ),
        },
    )
    section: Slide = slide(
        "section",
        "Week 36 was the strongest week in the four-week run",
        {"lead": para("Orders, delivery and pricing from week 33 to week 36.")},
    )
    return cover, section


def _findings() -> tuple[Slide, Slide]:
    cards: tuple[Card, ...] = (
        Card(
            "Orders",
            "North added the most orders",
            "Orders added in the North, week 33 to week 36.",
            metric=num(region_change("North"), "+,.0f"),
        ),
        Card(
            "Delivery",
            "Median delivery fell in three regions",
            "North median minutes, week 33 to week 36.",
            metric=num(delivery_change("North"), "+.0f min"),
        ),
        Card(
            "Basket",
            "Average basket value rose",
            "Average order value in USD, week 33 to week 36.",
            metric=num(growth_rate(BASKET_USD), "+.1%"),
        ),
    )
    cards3: Slide = slide(
        "cards3",
        "Three signals explain the growth: more orders, faster routes and bigger baskets",
        {"cards": cards},
        lead="Change from week 33 to week 36, all regions",
    )
    brief: Slide = slide(
        "brief",
        "Grow North orders and keep median delivery under 40 minutes",
        {
            "body": (
                Text(
                    (
                        Para(
                            (
                                Run(
                                    "North orders are the lever, and late picks are the constraint.",
                                    bold=True,
                                ),
                                Run(" The fix is capacity at the evening cut-off."),
                            )
                        ),
                        Para(
                            (
                                Run(
                                    "The South has the slowest median delivery in week 36. "
                                    "The North gained the most orders."
                                ),
                            )
                        ),
                    )
                ),
                Bullets(
                    (
                        Bullet(
                            "Goal",
                            "Keep weekly order growth above target in every region.",
                            "1",
                        ),
                        Bullet(
                            "Risk",
                            "Late picks push orders past the evening cut-off.",
                            "2",
                        ),
                        Bullet(
                            "Ask",
                            "Approve a second evening shift for two weeks, then check basket value.",
                            "3",
                        ),
                    ),
                    heading="Next steps",
                ),
            )
        },
        lead="Proposed plan for the evening window",
    )
    return cards3, brief


def _kpi() -> Slide:
    totals: tuple[int, ...] = weekly_totals()
    avg_delivery: float = sum(DELIVERY_WK36.values()) / len(DELIVERY_WK36)
    tiles: tuple[Tile, ...] = (
        Tile(num(totals[-1], ",.0f"), "Orders, week 36", "Up from week 33"),
        Tile(num(growth_rate(totals), "+.1%"), "Order growth", "Week 33 to week 36"),
        Tile(
            num(avg_delivery, ",.1f"), "Median delivery, min", "Average of four regions"
        ),
        Tile(num(BASKET_USD[-1], ",.2f"), "Average basket, USD", "Week 36"),
    )
    return slide(
        "kpi_split",
        "Orders, delivery and basket value all improved from week 33 to week 36",
        {
            "tiles": tiles,
            "left": bullets(
                "",
                ("Volume", "Order growth came from every region."),
                ("Routes", "East and West sped up."),
            ),
            "right": bullets(
                "",
                ("Basket", "Basket value rose in each week."),
                ("Mix", "The app share is highest in the North."),
            ),
            "note": para(
                "Week 36 values unless marked. Medians are minutes from dispatch to drop-off."
            ),
        },
        lead="Week 36 totals and the change from week 33, all regions",
    )


def _two_col() -> Slide:
    totals: tuple[int, ...] = weekly_totals()
    share: Num = num(
        (region_change("North") + region_change("West")) / (totals[-1] - totals[0]),
        ".1%",
    )
    return slide(
        "two_col",
        f"North and West delivered {share.text()} of the order growth",
        {
            "left": bullets(
                "Gained most",
                ("North", "Largest gain, with the most new weekly orders."),
                ("West", "Second-largest gain, led by the app."),
            ),
            "right": bullets(
                "Gained least",
                ("South", "Smallest gain, and the slowest median delivery in week 36."),
                ("East", "Smaller gain, with the lowest app share."),
            ),
            "summary": para(
                "Next, test route changes in East and West and the app share in the North."
            ),
        },
        lead="Order growth by region, week 33 to week 36",
    )


def _big_number() -> Slide:
    growth: Num = num(growth_rate(weekly_totals()), ".1%")
    return slide(
        "big_number",
        f"Weekly orders grew {growth.text()} from week 33 to week 36",
        {
            "number": growth,
            "caption": para(
                "Completed orders per week, all regions, week 36 against week 33."
            ),
            "note": para(
                "The week 33 total is the starting point for the growth rate."
            ),
        },
        lead="Weekly order growth, all regions",
    )


def _table() -> Slide:
    rows: tuple[tuple[str | Num, ...], ...] = tuple(
        (
            region,
            num(ORDERS[region][0], ",.0f"),
            num(ORDERS[region][-1], ",.0f"),
            num(growth_rate(ORDERS[region]), "+.1%"),
        )
        for region in REGIONS
    )
    return slide(
        "table",
        "Every region grew orders, and the North added the most",
        {
            "table": Table(
                ("Region", "Week 33 orders", "Week 36 orders", "Change"),
                rows,
                ("left", "right", "right", "right"),
            ),
            "note": para(
                "Completed orders per week. Change is week 36 against week 33."
            ),
        },
        lead="Completed orders per week by region, week 33 and week 36",
    )


def _grid4() -> Slide:
    blocks: tuple[Bullets, ...] = (
        bullets(
            "Before the first shift",
            ("Stock", "Check chiller temperatures and log them."),
            ("Vans", "Confirm each van has a driver."),
        ),
        bullets(
            "Pick list",
            ("Sort", "Sort pick lists by aisle, not by order."),
            ("Cut-off", "Lock lists at the afternoon cut-off."),
        ),
        bullets(
            "Loading",
            ("Order", "Load cold items last, nearest the door."),
            ("Bags", "Use insulated bags for frozen items."),
        ),
        bullets(
            "Evening",
            ("Review", "Compare late drops with the route plan."),
            ("Log", "Record the cause of each late drop."),
        ),
    )
    return slide(
        "grid4",
        "Four routine checks keep the routes on time",
        {"blocks": blocks},
        lead="Routine checks, by part of the shift",
    )


def _trend_charts() -> tuple[Slide, Slide]:
    totals: tuple[float, ...] = floats(weekly_totals())
    line: ChartData = ChartData(
        WEEKS,
        (("Orders", totals),),
        reference=ORDER_TARGET,
        reference_label="Target",
        source=SOURCE,
    )
    steps: tuple[float, ...] = floats(region_change(region) for region in REGIONS)
    waterfall: ChartData = ChartData(
        ("Week 33", *REGIONS, "Week 36"),
        (("Orders", (totals[0], *steps, totals[-1])),),
        source=SOURCE,
    )
    target: Slide = slide(
        "chart_3to1",
        "Orders passed the weekly target in week 35 and kept rising",
        {
            "chart": Chart("line", line),
            "takeaways": bullets(
                "",
                ("Below target", "The first two weeks sat under the target line."),
                ("Above target", "The last two weeks beat it, and the gap widened."),
            ),
        },
        lead="Completed orders per week, all regions, weeks 33 to 36",
    )
    steps_slide: Slide = slide(
        "chart_2to1",
        "The North and West added most of the growth from week 33 to week 36",
        {
            "chart": Chart("waterfall", waterfall),
            "takeaways": bullets(
                "",
                ("North", "Largest step up."),
                ("West", "Second-largest step up."),
                ("East", "Third-largest step up."),
                ("South", "Smallest step up."),
            ),
        },
        lead="Change in completed orders by region, week 33 total to week 36 total",
    )
    return target, steps_slide


def _share_charts() -> tuple[Slide, Slide]:
    channels: tuple[tuple[str, tuple[float, ...]], ...] = tuple(
        (channel, tuple(CHANNEL_SHARE[region][index] for region in REGIONS))
        for index, channel in enumerate(CHANNELS)
    )
    changes: tuple[float, ...] = tuple(delivery_change(region) for region in REGIONS)
    share: Slide = slide(
        "chart_1to1",
        "The app carries most orders in three of four regions",
        {
            "chart": Chart("stacked100", ChartData(REGIONS, channels, source=SOURCE)),
            "takeaways": bullets(
                "",
                ("App", "Leads in the North, South and West."),
                ("Web", "Strongest in the East."),
                ("Phone", "Highest in the East, where phone orders are most common."),
            ),
        },
        lead="Share of orders by channel in each region, percent, week 36",
    )
    delivery: Slide = slide(
        "chart_table",
        "Delivery got faster in three regions and slower only in the South",
        {
            "chart": Chart(
                "diverging_bar",
                ChartData(
                    REGIONS,
                    (("Change in minutes", changes),),
                    unit="min",
                    source=SOURCE,
                ),
            ),
            "table": Table(
                ("Region", "Week 36 median"),
                tuple((r, num(DELIVERY_WK36[r], ",.0f min")) for r in REGIONS),
                ("left", "right"),
            ),
            "note": para("Median minutes from dispatch to drop-off."),
        },
        lead="Change in median delivery minutes by region, week 33 to week 36",
    )
    return share, delivery


def _note() -> Slide:
    growth: Num = num(growth_rate(BASKET_USD), ".1%")
    return slide(
        "note",
        f"Average basket value rose {growth.text()} from week 33 to week 36",
        {
            "heading": para("What changed"),
            "body": para(
                "Basket value rose in each of the four weeks, led by larger orders in the North."
            ),
            "print_note": para("Print view: values are as of week 36."),
        },
        lead="Average order value in USD, all regions, week 33 to week 36",
    )


def _tabs() -> Slide:
    totals: tuple[float, ...] = floats(weekly_totals())
    orders_wk36: tuple[float, ...] = floats(ORDERS[region][-1] for region in REGIONS)
    basket_wk36: tuple[float, ...] = floats(BASKET_WK36[region] for region in REGIONS)
    tabs: Tabs = Tabs(
        (
            (
                "Orders",
                (
                    column("Orders", WEEKS, totals, highlight=3),
                    column("Orders", REGIONS, orders_wk36, highlight=0),
                ),
            ),
            (
                "Basket",
                (
                    column("Basket", WEEKS, BASKET_USD, highlight=3),
                    column("Basket", REGIONS, basket_wk36),
                ),
            ),
        )
    )
    return slide(
        "tabs",
        "Weekly orders rose every week, and the North was the largest region each week",
        {
            "tabs": tabs,
            "takeaways": bullets(
                "",
                ("Orders", "Each week beat the one before."),
                ("Regions", "The North is the largest region in every week."),
                (
                    "Basket",
                    "Basket value rose each week, and the North is highest in week 36.",
                ),
            ),
            "note": para("Each tab shows a weekly total and a regional split."),
        },
        lead="Completed orders per week and average basket in USD, weeks 33 to 36",
    )


def _process_diagrams() -> tuple[Slide, Slide, Slide, Slide]:
    matrix: Slide = slide(
        "matrix",
        "Earlier cut-offs are the quickest win for late deliveries",
        {
            "diagram": Matrix(
                "Effort",
                "Impact",
                ("Quick wins", "Major projects", "Fill-ins", "Thankless tasks"),
                (
                    ("Earlier cut-off", 0),
                    ("Route re-sequencing", 1),
                    ("Second evening shift", 1),
                    ("Bag labels", 2),
                    ("Manual dispatch", 3),
                ),
            ),
        },
        lead="Candidate fixes by effort and impact",
    )
    flow: Slide = slide(
        "flow",
        "Picking is the handoff to fix first in the order flow",
        {
            "diagram": Flow(
                (
                    ("Order placed", "Customer checks out"),
                    ("Picked", "Store team picks"),
                    ("Packed", "Insulated cold bags"),
                    ("Delivered", "Handoff in window"),
                ),
                highlight=1,
            ),
            "note": para(
                "Highlighted step: picking, where the fixes in this deck start."
            ),
        },
        lead="Order flow from checkout to handoff",
    )
    cycle: Slide = slide(
        "cycle",
        "Weekly planning runs as a four-step loop that feeds the next forecast",
        {
            "diagram": Cycle(
                ("Forecast demand", "Plan picks", "Dispatch routes", "Review returns"),
                "Weekly planning",
            ),
        },
        lead="Weekly planning loop",
    )
    return matrix, flow, cycle


def _plan_diagrams() -> tuple[Slide, Slide, Slide]:
    gantt: Slide = slide(
        "gantt",
        "The van refit ends before week 35 and new routes go live in week 36",
        {
            "diagram": Gantt(
                WEEKS,
                (
                    ("Chiller vans", (Bar(0.0, 2.0, "Refit", False),)),
                    (
                        "New routes",
                        (
                            Bar(2.0, 3.0, "Design", False),
                            Bar(3.0, 4.0, "Rollout", True),
                        ),
                    ),
                    ("Pickers", (Bar(1.0, 2.0, "Training", False),)),
                    ("Dispatch", (Bar(2.0, 3.0, "Dispatch tests", True),)),
                ),
                ((3.0, "Routes live"),),
            ),
            "legend": para("Solid bars are actual work; dashed outlines are planned."),
        },
        lead="Planned and actual work, weeks 33 to 36",
    )
    tree: Slide = slide(
        "tree",
        "Order growth came from more customers and larger baskets",
        {
            "diagram": Tree(
                "Order growth",
                (
                    ("New customers", ("Sign-ups in the North", "Repeat buyers")),
                    ("Basket value", ("Larger baskets", "Fewer refunds")),
                ),
            ),
        },
        lead="Drivers of order growth, week 33 to week 36",
    )
    timeline: Slide = slide(
        "timeline",
        "Three of four weekly pilots are settled, and route redesign is still open",
        {
            "diagram": Timeline(
                (
                    ("Wk 33", "Price freeze pilot", "kept"),
                    ("Wk 34", "Lunch slot pilot", "dropped"),
                    ("Wk 35", "Chiller refit", "kept"),
                    ("Wk 36", "Route redesign", "open"),
                )
            ),
        },
        lead="Weekly pilots, week 33 to week 36",
    )
    return gantt, tree, timeline


def _options() -> Slide:
    return slide(
        "options3",
        "Option B gives the largest delivery gain for no new van spend",
        {
            "cards": (
                Card(
                    "Option A",
                    "Add a second evening shift",
                    "Covers the late window at higher labor cost.",
                    metric=num(-2.0, "+.0f min"),
                    rows=(
                        Bullet("Upside", "Covers the late window within a week."),
                        Bullet("Fails if", "Staff cannot be hired in time."),
                    ),
                ),
                Card(
                    "Option B",
                    "Re-sequence routes by drop zone",
                    "Shortens drives with no new vans.",
                    metric=num(-3.0, "+.0f min"),
                    badge="Recommended",
                    rows=(
                        Bullet("Upside", "Keeps van spend flat."),
                        Bullet(
                            "Fails if",
                            "Drop zones change faster than routes are redrawn.",
                        ),
                    ),
                ),
                Card(
                    "Option C",
                    "Lease a third chiller van",
                    "Adds cold capacity for the North route.",
                    metric=num(-2.0, "+.0f min"),
                    rows=(
                        Bullet("Upside", "Adds cold capacity for the North route."),
                        Bullet("Fails if", "The chiller van is not repaired in time."),
                    ),
                ),
            ),
            "recommendation": para(
                "Recommendation: fund Option B for the next two weeks."
            ),
        },
        lead="Three options for late deliveries, with estimated median gain",
    )


def _discussion_and_references() -> tuple[Slide, Slide]:
    discussion: Slide = slide(
        "discussion",
        "Which three questions should we settle before we change the route plan?",
        {
            "prompts": bullets(
                "Prompts",
                ("Cut-off", "Is the afternoon cut-off right for same-day slots?"),
                ("Vans", "Do we lease a third chiller van?"),
                ("Staffing", "Who covers the evening shift?"),
            ),
            "notes": Panel("Notes from the room"),
        },
        lead="Questions for the group, with prompts and notes",
    )
    references: Slide = slide(
        "references",
        "Every figure here traces to the sample tables in gallery.py",
        {
            "body": para(
                "gallery.py, ORDERS: completed orders per week, pulled 2025-09-08 (sample).",
                "gallery.py, DELIVERY_WK33 and DELIVERY_WK36: median minutes, pulled 2025-09-08 (sample).",
                "gallery.py, BASKET_USD and BASKET_WK36: average order value in USD, pulled 2025-09-08 (sample).",
                "gallery.py, CHANNEL_SHARE: channel split of orders by region, pulled 2025-09-08 (sample).",
            ),
        },
        lead="Sources for the figures in this deck",
    )
    return discussion, references


def gallery_deck() -> Deck:
    """Build the gallery deck: one slide per layout, in layout-table order.

    Returns:
        A deck with 24 main slides that passes ``validate``.
    """
    cover, section = _cover_and_section()
    cards3, brief = _findings()
    big: Slide = _big_number()
    chart_3to1, chart_2to1 = _trend_charts()
    chart_1to1, chart_table = _share_charts()
    matrix, flow, cycle = _process_diagrams()
    gantt, tree, timeline = _plan_diagrams()
    discussion, references = _discussion_and_references()
    slides: tuple[Slide, ...] = (
        cover,
        section,
        cards3,
        brief,
        _kpi(),
        _two_col(),
        big,
        _table(),
        _grid4(),
        chart_3to1,
        chart_2to1,
        chart_1to1,
        chart_table,
        _note(),
        matrix,
        flow,
        cycle,
        gantt,
        tree,
        timeline,
        _options(),
        discussion,
        _tabs(),
        references,
    )
    return Deck(
        title="Weekly grocery orders: layout gallery",
        short_title="Gallery",
        as_of="week 36",
        slides=slides,
    )


def write_outputs(deck: Deck, out_dir: Path) -> None:
    """Write gallery.html and gallery.pptx into out_dir, creating it when missing."""
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "gallery.html").write_text(render_html(deck, HOUSE), encoding="utf-8")
    (out_dir / "gallery.pptx").write_bytes(render_pptx(deck, HOUSE))


def main(argv: list[str]) -> int:
    """Validate the gallery and write its outputs to the folder named in argv[1].

    Returns:
        0 on success, 2 when the folder argument is missing.
    """
    if len(argv) != 2:
        print("usage: python3 gallery.py <out_dir>", file=sys.stderr)
        return 2
    deck: Deck = gallery_deck()
    validate(deck)
    write_outputs(deck, Path(argv[1]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
