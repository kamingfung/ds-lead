"""Tests for chart data, the SVG renderers and the to_svg dispatcher."""

import xml.etree.ElementTree as ET

import pytest

from charts import ChartData, fmt_value, nice_ticks, svg_column, svg_line, to_svg
from spec import Chart
from theme import HOUSE

NS: str = "{http://www.w3.org/2000/svg}"
WEEKS: tuple[str, ...] = ("Wk 1", "Wk 2", "Wk 3", "Wk 4")
LINE_DATA: ChartData = ChartData(
    WEEKS,
    (("Orders", (120.0, 135.0, 150.0, 160.0)), ("Target", (110.0, 115.0, 125.0, 130.0)),
     ("Returns", (14.0, 12.0, 11.0, 9.0))),
    unit="orders",
    reference=100.0,
)
DIVERGING_DATA: ChartData = ChartData(
    ("North", "South", "East", "West"), (("Revenue change", (4.2, -1.5, 2.8, -0.6)),), unit="%"
)
WATERFALL_DATA: ChartData = ChartData(
    ("Start", "Price", "Volume", "Mix", "End"), (("Margin", (100.0, 5.0, -12.0, 3.0, 96.0)),)
)
STACKED_DATA: ChartData = ChartData(
    ("Retail", "Wholesale"),
    (("Direct", (62.0, 48.0)), ("Partner", (33.0, 45.0)), ("Other", (5.0, 7.0))),
)
COLUMN_DATA: ChartData = ChartData(
    ("Mon", "Tue", "Wed", "Thu", "Fri"),
    (("Orders", (410.0, 388.0, 455.0, 602.0, 530.0)),),
    highlight=3,
)


def _fills(svg: str) -> list[str]:
    """Return the fill of every rectangle, background included, in drawing order."""
    return [element.get("fill", "") for element in ET.fromstring(svg).iter(f"{NS}rect")]


def _text_fills(svg: str) -> dict[str, str]:
    """Map each text node to its fill color."""
    nodes = ET.fromstring(svg).iter(f"{NS}text")
    return {node.text: node.get("fill", "") for node in nodes if node.text}


def test_fmt_value_groups_digits_adds_unit_and_uses_true_minus() -> None:
    arranged: list[tuple[float, str]] = [(1234.5, "USD"), (-12.0, ""), (42.0, "%"), (-0.04, "")]

    actual: list[str] = [fmt_value(value, unit) for value, unit in arranged]

    assert actual == ["1,234.5 USD", "\u221212", "42%", "0"]


def test_line_chart_draws_gray_reference_and_starts_axis_at_zero() -> None:
    svg: str = to_svg(Chart("line", LINE_DATA), 640, 360, HOUSE)

    assert ET.fromstring(svg).get("viewBox") == "0 0 640 360"
    assert f'stroke="{HOUSE.gray}" stroke-width="1.0" stroke-dasharray="3 3"' in svg
    assert 'stroke-dasharray="6 4"' in svg
    assert "axis starts" not in svg
    assert "Orders 160" in _text_fills(svg)


def test_line_chart_notes_when_the_axis_does_not_start_at_zero() -> None:
    far_data: ChartData = ChartData(
        ("Jan", "Feb", "Mar"), (("Revenue", (9000.0, 9200.0, 9400.0)),), unit="USD"
    )

    svg: str = svg_line(far_data, 640, 360, HOUSE)

    fills: dict[str, str] = _text_fills(svg)
    assert fills["Axis does not start at zero"] == HOUSE.gray
    assert fills["USD"] == HOUSE.ink


def test_line_note_sits_24_px_below_the_category_labels_and_inside_the_canvas() -> None:
    far_data: ChartData = ChartData(
        ("Jan", "Feb", "Mar"), (("Revenue", (9000.0, 9200.0, 9400.0)),), unit="USD"
    )

    svg: str = svg_line(far_data, 640, 360, HOUSE)

    ys: dict[str, float] = {
        node.text or "": float(node.get("y") or 0) for node in ET.fromstring(svg).iter(f"{NS}text")
    }
    assert ys["Axis does not start at zero"] == ys["Jan"] + 24
    assert ys["Axis does not start at zero"] <= 360

    assert nice_ticks(0, 598) == [0, 100, 200, 300, 400, 500, 600]


def test_line_axis_from_400_to_560_skips_zero_and_says_so() -> None:
    data: ChartData = ChartData(("Jan", "Feb", "Mar"), (("Sales", (400.0, 480.0, 560.0)),))

    svg: str = svg_line(data, 640, 360, HOUSE)

    texts: list[str] = [node.text or "" for node in ET.fromstring(svg).iter(f"{NS}text")]
    assert "0" not in texts
    assert "Axis does not start at zero" in texts


def test_end_labels_of_close_values_are_18_px_apart() -> None:
    data: ChartData = ChartData(
        ("Wk 1", "Wk 2"), (("Actual", (500.0, 534.0)), ("Plan", (500.0, 532.0)))
    )

    svg: str = svg_line(data, 640, 360, HOUSE)

    ys: dict[str, float] = {
        node.text or "": float(node.get("y", "0"))
        for node in ET.fromstring(svg).iter(f"{NS}text")
    }
    assert ys["Plan 532"] - ys["Actual 534"] >= 18.0


def test_reference_label_reads_target_at_left_above_the_line() -> None:
    data: ChartData = ChartData(
        ("Wk 1", "Wk 2"), (("Sales", (400.0, 560.0)),), reference=500.0
    )

    svg: str = svg_line(data, 640, 360, HOUSE)

    label: ET.Element = next(
        node for node in ET.fromstring(svg).iter(f"{NS}text") if node.text == "Target 500"
    )
    assert label.get("fill") == HOUSE.gray
    assert float(label.get("x", "0")) < 100.0


def test_diverging_zero_line_sits_left_of_center_for_12_and_minus_2() -> None:
    data: ChartData = ChartData(("A", "B"), (("Change", (12.0, -2.0)),))

    svg: str = to_svg(Chart("diverging_bar", data), 640, 360, HOUSE)

    zero_line: ET.Element = next(ET.fromstring(svg).iter(f"{NS}line"))
    assert float(zero_line.get("x1", "0")) < 640 / 2


def test_diverging_bar_sorts_by_value_and_colors_negatives_with_loss() -> None:
    svg: str = to_svg(Chart("diverging_bar", DIVERGING_DATA), 640, 360, HOUSE)

    names: list[str] = [node.text or "" for node in ET.fromstring(svg).iter(f"{NS}text")]
    order: list[str] = [name for name in names if name in DIVERGING_DATA.categories]
    assert order == ["North", "East", "West", "South"]
    assert _fills(svg)[1:] == [HOUSE.accent, HOUSE.accent, HOUSE.loss, HOUSE.loss]
    assert _text_fills(svg)["\u22121.5%"] == HOUSE.ink


def test_waterfall_labels_totals_inside_and_signed_deltas_outside() -> None:
    svg: str = to_svg(Chart("waterfall", WATERFALL_DATA), 640, 360, HOUSE)

    assert _text_fills(svg)["100"] == HOUSE.paper
    assert _text_fills(svg)["+5"] == HOUSE.ink
    assert _text_fills(svg)["\u221212"] == HOUSE.ink
    assert _fills(svg)[1:] == [HOUSE.ink, HOUSE.accent, HOUSE.loss, HOUSE.accent, HOUSE.ink]


def test_stacked100_labels_wide_segments_and_hides_those_under_six_percent() -> None:
    svg: str = to_svg(Chart("stacked100", STACKED_DATA), 640, 360, HOUSE)

    percents: dict[str, str] = {
        text: fill for text, fill in _text_fills(svg).items() if text.endswith("%")
    }
    assert percents == {
        "62%": HOUSE.white, "33%": HOUSE.white, "48%": HOUSE.white,
        "45%": HOUSE.white, "7%": HOUSE.ink,
    }


def test_column_colors_one_bar_as_highlight_and_labels_values() -> None:
    svg: str = svg_column(COLUMN_DATA, 640, 360, HOUSE)

    fills: list[str] = _fills(svg)
    assert fills.count(HOUSE.highlight) == 1
    assert fills.count(HOUSE.ink) == 4
    assert _text_fills(svg)["602"] == HOUSE.ink


@pytest.mark.parametrize(("chart", "message"), [
    (Chart("waterfall", ChartData(WATERFALL_DATA.categories,
                                  (("Margin", (100.0, 5.0, -12.0, 3.0, 97.0)),))),
     "is not start plus steps"),
    (Chart("stacked100", ChartData(("Retail", "Wholesale"),
                                   (("Direct", (60.0, 50.0)), ("Partner", (33.0, 45.0))))),
     "'Retail' sums to 93.0"),
    (Chart("column", ChartData(("Mon", "Tue"), (("Orders", (4.0, 5.0)),), highlight=7)),
     "highlight 7 is outside 2 categories"),
    (Chart("line", ChartData(("W1", "W2"), tuple((f"S{i}", (1.0, 2.0)) for i in range(4)))),
     "expected 1 to 3 series, got 4"),
    (Chart("pie", COLUMN_DATA), "unknown chart kind 'pie'"),
])
def test_invalid_data_raises_value_error(chart: Chart, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        to_svg(chart, 640, 360, HOUSE)


@pytest.mark.parametrize("chart", [
    Chart("line", LINE_DATA),
    Chart("diverging_bar", DIVERGING_DATA),
    Chart("waterfall", WATERFALL_DATA),
    Chart("stacked100", STACKED_DATA),
    Chart("column", COLUMN_DATA),
])
def test_every_kind_is_well_formed_titled_and_deterministic(chart: Chart) -> None:
    first: str = to_svg(chart, 640, 360, HOUSE)
    second: str = to_svg(chart, 640, 360, HOUSE)

    assert ET.fromstring(first).find(f"{NS}title") is not None
    assert first == second


def test_renderer_rejects_a_zero_size() -> None:
    with pytest.raises(ValueError, match="chart size must be positive"):
        svg_column(COLUMN_DATA, 0, 360, HOUSE)


def test_stacked100_labels_every_category_at_the_left_of_its_bar() -> None:
    svg: str = to_svg(Chart("stacked100", STACKED_DATA), 640, 360, HOUSE)

    texts: list[str] = [node.text or "" for node in ET.fromstring(svg).iter(f"{NS}text")]
    assert "Retail" in texts and "Wholesale" in texts
    assert all(node.get("text-anchor") == "end" for node in ET.fromstring(svg).iter(f"{NS}text")
               if node.text in ("Retail", "Wholesale"))


def test_long_category_axes_label_every_kth_year():
    # Arrange
    from charts import label_step
    years = tuple(str(y) for y in range(1961, 2001))  # 40 categories, the line-chart limit
    data = ChartData(years, (("Index", tuple(float(i) for i in range(len(years)))),))
    # Act
    svg = to_svg(Chart("line", data), 760, 440, HOUSE)
    # Assert
    assert label_step(years, 700) > 1
    assert svg.count(">1962<") == 0 and ">1961<" in svg
