"""Chart data model and pure SVG renderers for deck charts.

Each renderer takes chart data, a width and height in pixels, and a Theme, and returns the
same SVG string for the same input. to_svg dispatches on the chart kind.
"""

from __future__ import annotations

from collections.abc import Sequence

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable
from xml.sax.saxutils import escape

from theme import Theme

if TYPE_CHECKING:
    from spec import Chart

MINUS: str = "\u2212"
NO_HIGHLIGHT: int = -1
MAX_ITEMS: int = 40
MARGIN_LEFT: float = 72.0
MARGIN_RIGHT: float = 24.0
MARGIN_TOP: float = 36.0
MARGIN_BOTTOM: float = 44.0
LINE_END_ROOM: float = 150.0
NOTE_ROOM: float = 24.0
VALUE_ROOM: float = 64.0
LABEL_CHAR_PX: float = 9.0
LABEL_GAP: float = 12.0
END_LABEL_GAP: float = 18.0
NICE_STEPS: tuple[float, ...] = (1.0, 2.0, 2.5, 5.0, 10.0)
BAR_SHARE: float = 0.6
PAD: float = 0.12
MIN_PERCENT_LABEL: float = 6.0
DARK_LUMA: float = 150.0
DASHES: tuple[str, ...] = ("", "6 4", "2 3")
KIND_LABELS: dict[str, str] = {
    "line": "Line",
    "diverging_bar": "Diverging bar",
    "waterfall": "Waterfall",
    "stacked100": "100% stacked bar",
    "column": "Column",
}


@dataclass(frozen=True)
class ChartData:
    """Categories, named series and labels for one chart."""

    categories: tuple[str, ...]
    series: tuple[tuple[str, tuple[float, ...]], ...]
    unit: str = ""
    reference: float | None = None
    highlight: int = -1
    source: str = ""
    reference_label: str = "Target"


@dataclass(frozen=True)
class Frame:
    """Pixel box of a plot and the data range mapped onto it."""

    left: float
    right: float
    top: float
    bottom: float
    low: float
    high: float

    def x(self, value: float) -> float:
        """Map a data value to a horizontal pixel position."""
        span: float = self.high - self.low
        return self.left + (value - self.low) / span * (self.right - self.left)

    def y(self, value: float) -> float:
        """Map a data value to a vertical pixel position, larger values higher up."""
        span: float = self.high - self.low
        return self.bottom - (value - self.low) / span * (self.bottom - self.top)


def fmt_value(value: float, unit: str) -> str:
    """Format a label value: grouped digits, one decimal when needed, true minus, unit.

    A unit starting with "%" joins the number directly. Other units follow a space.

    Returns:
        The label text, for example "1,234.5 USD" or "\u221212".
    """
    rounded: float = round(value, 1) + 0.0
    number: str = f"{rounded:,.0f}" if rounded.is_integer() else f"{rounded:,.1f}"
    text: str = number.replace("-", MINUS)
    if not unit:
        return text
    return text + unit if unit.startswith("%") else f"{text} {unit}"


def label_unit(unit: str) -> str:
    """Return the unit a value label may carry: "%" or at most 3 characters, otherwise nothing.

    A longer unit such as "orders" is left out of value labels because the chart title names it.
    """
    return unit if len(unit) <= 3 else ""


def _n(value: float) -> str:
    return f"{value:.2f}"


def _rect(x: float, y: float, width: float, height: float, fill: str) -> str:
    attrs: str = f'x="{_n(x)}" y="{_n(y)}" width="{_n(width)}" height="{_n(height)}"'
    return f'<rect {attrs} fill="{fill}"/>'


def _line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    color: str,
    dash: str = "",
    width: float = 1.0,
) -> str:
    style: str = f' stroke-dasharray="{dash}"' if dash else ""
    coords: str = f'x1="{_n(x1)}" y1="{_n(y1)}" x2="{_n(x2)}" y2="{_n(y2)}"'
    return f'<line {coords} stroke="{color}" stroke-width="{width}"{style}/>'


def _text(
    x: float,
    y: float,
    label: str,
    theme: Theme,
    anchor: str = "middle",
    bold: bool = False,
    color: str = "",
) -> str:
    weight: str = ' font-weight="bold"' if bold else ""
    fill: str = color or theme.ink
    return (
        f'<text x="{_n(x)}" y="{_n(y)}" text-anchor="{anchor}" font-family="{theme.body_font}" '
        f'font-size="{theme.small_px}" fill="{fill}"{weight}>{escape(label)}</text>'
    )


def _open(kind: str, data: ChartData, w: int, h: int, theme: Theme) -> list[str]:
    """Open an SVG with its viewBox, a title and a paper ground."""
    if w <= 0 or h <= 0:
        raise ValueError(f"chart size must be positive, got {w}x{h}")
    names: list[str] = [name for name, _ in data.series if name] or list(
        data.categories
    )
    title: str = f"{KIND_LABELS[kind]} chart: {', '.join(names)}"
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
        f"<title>{escape(title)}</title>",
        _rect(0, 0, w, h, theme.paper),
    ]


def _finish(parts: list[str]) -> str:
    parts.append("</svg>")
    return "".join(parts)


def _check_shape(
    data: ChartData, series: tuple[int, int], categories: tuple[int, int]
) -> None:
    """Raise ValueError when series or category counts fall outside the allowed ranges."""
    count: int = len(data.series)
    points: int = len(data.categories)
    if not series[0] <= count <= series[1]:
        raise ValueError(f"expected {series[0]} to {series[1]} series, got {count}")
    if not categories[0] <= points <= categories[1]:
        raise ValueError(
            f"expected {categories[0]} to {categories[1]} categories, got {points}"
        )
    for name, values in data.series:
        if len(values) != points:
            raise ValueError(
                f"series {name!r} has {len(values)} values for {points} categories"
            )


def _check_highlight(data: ChartData) -> None:
    if data.highlight != NO_HIGHLIGHT and not 0 <= data.highlight < len(
        data.categories
    ):
        raise ValueError(
            f"highlight {data.highlight} is outside {len(data.categories)} categories"
        )


def _check_rows_sum(data: ChartData) -> None:
    """Raise ValueError when the series values of any row do not sum to 100 within 0.5."""
    for row, name in enumerate(data.categories):
        total: float = sum(values[row] for _, values in data.series)
        if abs(total - 100.0) > 0.5:
            raise ValueError(f"row {name!r} sums to {total}, not 100 +/- 0.5")


def _all_values(data: ChartData) -> list[float]:
    values: list[float] = [
        value for _, series_values in data.series for value in series_values
    ]
    if data.reference is not None:
        values.append(data.reference)
    return values


def _zero_bounds(values: list[float]) -> tuple[float, float]:
    """Return an axis range that includes zero, padded so labels fit past the bars."""
    low: float = min(0.0, min(values))
    high: float = max(0.0, max(values))
    if high == low:
        high = low + 1.0
    pad: float = (high - low) * PAD
    return (low - pad if low < 0 else low, high + pad if high > 0 else high)


def nice_ticks(low: float, high: float, count: int = 5) -> list[float]:
    """Return evenly spaced tick values covering [low, high], about ``count`` intervals.

    The step is 1, 2, 2.5 or 5 times a power of ten. The first tick is at or below ``low``
    and the last is at or above ``high``.
    """
    raw: float = (high - low or 1.0) / (count + 1)
    magnitude: float = 10.0 ** math.floor(math.log10(raw))
    step: float = next(
        mult * magnitude for mult in NICE_STEPS if mult * magnitude >= raw
    )
    first: int = math.floor(low / step)
    last: int = math.ceil(high / step)
    return [round((first + index) * step, 10) for index in range(last - first + 1)]


def _ticks_for(values: list[float]) -> list[float]:
    """Return line-chart ticks: zero-based when the minimum is under 40% of the maximum."""
    low: float = min(values)
    high: float = max(values)
    if low <= 0 or low < 0.4 * high:
        return nice_ticks(*_zero_bounds(values))
    span: float = (high - low) or abs(high) or 1.0
    return nice_ticks(low - span * 0.1, high)


def _diverging_bounds(values: list[float]) -> tuple[float, float]:
    """Return the range [min(0, smallest) * 1.15, max(0, largest) * 1.15]."""
    low: float = min(0.0, min(values)) * 1.15
    high: float = max(0.0, max(values)) * 1.15
    return (low, high) if high > low else (low, low + 1.0)


def _label_plot_left(names: tuple[str, ...]) -> float:
    """Return the plot's left edge: just past the widest category label plus a gap."""
    widest: float = max(len(name) for name in names) * LABEL_CHAR_PX
    return MARGIN_LEFT + widest + LABEL_GAP


def _grid(frame: Frame, ticks: list[float], theme: Theme) -> list[str]:
    """Draw a gridline and a tick label at each tick value."""
    parts: list[str] = []
    for value in ticks:
        y: float = frame.y(value)
        parts.append(_line(frame.left, y, frame.right, y, theme.grid))
        parts.append(
            _text(frame.left - 8, y + 5, fmt_value(value, ""), theme, anchor="end")
        )
    return parts


def _axis_note(unit: str, frame: Frame, theme: Theme) -> list[str]:
    """Label the value axis with its unit above the plot."""
    if not unit:
        return []
    return [_text(frame.left, frame.top - 14, unit, theme, anchor="start")]


def label_step(names: Sequence[str], width: float) -> int:
    """Return k so that labeling every k-th category keeps the labels from touching across width px."""
    if not names:
        return 1
    need: float = (
        max(len(name) for name in names) * 9.0 + 16.0
    )  # about 9 px per character at 16 px
    fits: int = max(2, int(width // need))
    return max(1, math.ceil(len(names) / fits))


def _category_labels(
    names: tuple[str, ...], xs: list[float], y: float, theme: Theme
) -> list[str]:
    width: float = (
        (xs[-1] - xs[0]) * len(xs) / max(1, len(xs) - 1) if len(xs) > 1 else 0.0
    )
    step: int = label_step(names, width) if len(xs) > 1 else 1
    last: int = len(names) - 1
    return [
        _text(x, y, name, theme)
        for i, (name, x) in enumerate(zip(names, xs))
        if i % step == 0 or (i == last and last % step >= step / 2)
    ]


def _is_dark(color: str) -> bool:
    red: int = int(color[1:3], 16)
    green: int = int(color[3:5], 16)
    blue: int = int(color[5:7], 16)
    return 0.299 * red + 0.587 * green + 0.114 * blue < DARK_LUMA


def _line_series(
    data: ChartData, index: int, xs: list[float], frame: Frame, theme: Theme
) -> list[str]:
    """Draw one series as a polyline with circle markers."""
    values: tuple[float, ...] = data.series[index][1]
    color: str = theme.series[index]
    ys: list[float] = [frame.y(value) for value in values]
    points: str = " ".join(f"{_n(x)},{_n(y)}" for x, y in zip(xs, ys))
    dash: str = f' stroke-dasharray="{DASHES[index]}"' if DASHES[index] else ""
    parts: list[str] = [
        f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2"{dash}/>'
    ]
    for x, y in zip(xs, ys):
        parts.append(f'<circle cx="{_n(x)}" cy="{_n(y)}" r="3.5" fill="{color}"/>')
    return parts


def _end_labels(data: ChartData, x: float, frame: Frame, theme: Theme) -> list[str]:
    """Label each series at its last point, pushing labels down until 18 px apart.

    Labels keep their top-to-bottom order by y; no label swaps place with another.
    """
    baselines: list[float] = [frame.y(values[-1]) + 5 for _, values in data.series]
    order: list[int] = sorted(range(len(baselines)), key=lambda index: baselines[index])
    placed: dict[int, float] = {}
    previous: float | None = None
    for index in order:
        y: float = baselines[index]
        if previous is not None:
            y = max(y, previous + END_LABEL_GAP)
        placed[index] = previous = y
    parts: list[str] = []
    for index, (name, values) in enumerate(data.series):
        label: str = f"{name} {fmt_value(values[-1], label_unit(data.unit))}"
        parts.append(_text(x + 8, placed[index], label, theme, anchor="start"))
    return parts


def svg_line(data: ChartData, w: int, h: int, theme: Theme) -> str:
    """Render 1 to 3 series over ordered categories, with an optional gray reference line.

    Series 1 is solid, series 2 dashed and series 3 dotted. Each series ends in a label.
    """
    _check_shape(data, (1, 3), (2, MAX_ITEMS))
    ticks: list[float] = _ticks_for(_all_values(data))
    notes_zero: bool = ticks[0] > 0
    frame: Frame = Frame(
        MARGIN_LEFT,
        w - LINE_END_ROOM,
        MARGIN_TOP,
        h - MARGIN_BOTTOM - (NOTE_ROOM if notes_zero else 0.0),
        ticks[0],
        ticks[-1],
    )
    count: int = len(data.categories)
    xs: list[float] = [
        frame.left + index * (frame.right - frame.left) / (count - 1)
        for index in range(count)
    ]
    parts: list[str] = _open("line", data, w, h, theme)
    parts.extend(_grid(frame, ticks, theme))
    parts.extend(_axis_note(data.unit, frame, theme))
    for index in range(len(data.series)):
        parts.extend(_line_series(data, index, xs, frame, theme))
    parts.extend(_end_labels(data, xs[-1], frame, theme))
    if data.reference is not None:
        y: float = frame.y(data.reference)
        label: str = (
            f"{data.reference_label} {fmt_value(data.reference, label_unit(data.unit))}"
        )
        parts.append(_line(frame.left, y, frame.right, y, theme.gray, dash="3 3"))
        parts.append(
            _text(frame.left + 4, y - 6, label, theme, anchor="start", color=theme.gray)
        )
    if notes_zero:
        note: str = "Axis does not start at zero"
        parts.append(
            _text(frame.left, frame.bottom + 48, note, theme, "start", color=theme.gray)
        )
    parts.extend(_category_labels(data.categories, xs, frame.bottom + 24, theme))
    return _finish(parts)


def svg_diverging_bar(data: ChartData, w: int, h: int, theme: Theme) -> str:
    """Render one series as horizontal bars from a vertical zero line, largest value first."""
    _check_shape(data, (1, 1), (1, MAX_ITEMS))
    ranked: list[tuple[str, float]] = sorted(
        zip(data.categories, data.series[0][1]), key=lambda pair: pair[1], reverse=True
    )
    bounds: tuple[float, float] = _diverging_bounds([value for _, value in ranked])
    left: float = _label_plot_left(data.categories)
    frame: Frame = Frame(
        left, w - VALUE_ROOM, MARGIN_TOP, h - MARGIN_BOTTOM, bounds[0], bounds[1]
    )
    band: float = (frame.bottom - frame.top) / len(ranked)
    bar_h: float = band * BAR_SHARE
    zero: float = frame.x(0.0)
    parts: list[str] = _open("diverging_bar", data, w, h, theme)
    parts.append(_line(zero, frame.top, zero, frame.bottom, theme.ink))
    for index, (name, value) in enumerate(ranked):
        cy: float = frame.top + (index + 0.5) * band
        end: float = frame.x(value)
        positive: bool = value >= 0
        color: str = theme.accent if positive else theme.loss
        label_x: float = end + 6 if positive else end - 6
        anchor: str = "start" if positive else "end"
        parts.append(_text(left - LABEL_GAP, cy + 5, name, theme, anchor="end"))
        parts.append(
            _rect(min(zero, end), cy - bar_h / 2, abs(end - zero), bar_h, color)
        )
        parts.append(
            _text(
                label_x,
                cy + 5,
                fmt_value(value, label_unit(data.unit)),
                theme,
                anchor,
                True,
            )
        )
    return _finish(parts)


def _waterfall_geometry(
    values: tuple[float, ...],
) -> tuple[list[tuple[float, float]], list[float]]:
    """Return each bar's (low, high) span and the running level after each bar."""
    spans: list[tuple[float, float]] = [(min(0.0, values[0]), max(0.0, values[0]))]
    levels: list[float] = [values[0]]
    running: float = values[0]
    for step in values[1:-1]:
        spans.append((min(running, running + step), max(running, running + step)))
        running += step
        levels.append(running)
    spans.append((min(0.0, values[-1]), max(0.0, values[-1])))
    levels.append(values[-1])
    return spans, levels


def svg_waterfall(data: ChartData, w: int, h: int, theme: Theme) -> str:
    """Render a start total, signed steps and an end total as floating bars.

    Raises:
        ValueError: If the end total is not the start total plus the steps.
    """
    _check_shape(data, (1, 1), (3, MAX_ITEMS))
    values: tuple[float, ...] = data.series[0][1]
    expected_end: float = values[0] + sum(values[1:-1])
    if not math.isclose(values[-1], expected_end, abs_tol=1e-6):
        raise ValueError(
            f"waterfall end {values[-1]} is not start plus steps {expected_end}"
        )
    spans: list[tuple[float, float]]
    levels: list[float]
    spans, levels = _waterfall_geometry(values)
    edges: list[float] = [edge for span in spans for edge in span]
    bounds: tuple[float, float] = _zero_bounds(edges)
    frame: Frame = Frame(
        MARGIN_LEFT,
        w - MARGIN_RIGHT,
        MARGIN_TOP + 12,
        h - MARGIN_BOTTOM,
        bounds[0],
        bounds[1],
    )
    count: int = len(values)
    slot: float = (frame.right - frame.left) / count
    bar_w: float = slot * BAR_SHARE
    centers: list[float] = [frame.left + (index + 0.5) * slot for index in range(count)]
    parts: list[str] = _open("waterfall", data, w, h, theme)
    for index in range(count - 1):
        y: float = frame.y(levels[index])
        x1: float = centers[index] + bar_w / 2
        x2: float = centers[index + 1] - bar_w / 2
        parts.append(_line(x1, y, x2, y, theme.light))
    for index, (span, center) in enumerate(zip(spans, centers)):
        top_y: float = frame.y(span[1])
        x: float = center - bar_w / 2
        height: float = frame.y(span[0]) - top_y
        if index in (0, count - 1):
            total: str = fmt_value(values[index], label_unit(data.unit))
            parts.append(_rect(x, top_y, bar_w, height, theme.ink))
            parts.append(
                _text(center, top_y + 20, total, theme, bold=True, color=theme.paper)
            )
            continue
        step: float = values[index]
        sign: str = "+" if step > 0 else ""
        color: str = theme.accent if step >= 0 else theme.loss
        parts.append(_rect(x, top_y, bar_w, height, color))
        parts.append(
            _text(
                center,
                top_y - 8,
                sign + fmt_value(step, label_unit(data.unit)),
                theme,
                bold=True,
            )
        )
    parts.extend(_category_labels(data.categories, centers, frame.bottom + 24, theme))
    return _finish(parts)


def svg_stacked100(data: ChartData, w: int, h: int, theme: Theme) -> str:
    """Render 2 to 4 series as horizontal bars that each sum to 100 percent.

    Raises:
        ValueError: If a row's values do not sum to 100 within 0.5.
    """
    _check_shape(data, (2, 4), (1, MAX_ITEMS))
    _check_rows_sum(data)
    left: float = _label_plot_left(data.categories)
    frame: Frame = Frame(left, w - MARGIN_RIGHT, MARGIN_TOP + 16, h - 16, 0.0, 100.0)
    band: float = (frame.bottom - frame.top) / len(data.categories)
    bar_h: float = band * BAR_SHARE
    parts: list[str] = _open("stacked100", data, w, h, theme)
    x: float = MARGIN_LEFT
    for index, (name, _) in enumerate(data.series):
        parts.append(_rect(x, MARGIN_TOP - 12, 12, 12, theme.series[index]))
        parts.append(_text(x + 18, MARGIN_TOP - 2, name, theme, anchor="start"))
        x += 18 + len(name) * 9 + 24
    for row, name in enumerate(data.categories):
        cy: float = frame.top + (row + 0.5) * band
        parts.append(_text(left - LABEL_GAP, cy + 5, name, theme, anchor="end"))
        start: float = 0.0
        for index, (_, values) in enumerate(data.series):
            value: float = values[row]
            seg_left: float = frame.x(start)
            right: float = frame.x(start + value)
            color: str = theme.series[index]
            parts.append(
                _rect(seg_left, cy - bar_h / 2, right - seg_left, bar_h, color)
            )
            if value >= MIN_PERCENT_LABEL:
                label_color: str = theme.white if _is_dark(color) else theme.ink
                label: str = fmt_value(value, "%")
                parts.append(
                    _text(
                        (seg_left + right) / 2, cy + 5, label, theme, color=label_color
                    )
                )
            start += value
    return _finish(parts)


def svg_column(data: ChartData, w: int, h: int, theme: Theme) -> str:
    """Render one series as vertical bars with value labels and one highlighted bar.

    Raises:
        ValueError: If the highlight index is outside the categories.
    """
    _check_shape(data, (1, 1), (2, 6))
    _check_highlight(data)
    values: tuple[float, ...] = data.series[0][1]
    ticks: list[float] = nice_ticks(*_zero_bounds(list(values)))
    frame: Frame = Frame(
        MARGIN_LEFT,
        w - MARGIN_RIGHT,
        MARGIN_TOP,
        h - MARGIN_BOTTOM,
        ticks[0],
        ticks[-1],
    )
    slot: float = (frame.right - frame.left) / len(values)
    bar_w: float = slot * BAR_SHARE
    centers: list[float] = [
        frame.left + (index + 0.5) * slot for index in range(len(values))
    ]
    parts: list[str] = _open("column", data, w, h, theme)
    parts.extend(_grid(frame, ticks, theme))
    zero: float = frame.y(0.0)
    parts.append(_line(frame.left, zero, frame.right, zero, theme.ink))
    for index, (center, value) in enumerate(zip(centers, values)):
        top_y: float = frame.y(max(value, 0.0))
        base_y: float = frame.y(min(value, 0.0))
        color: str = theme.highlight if index == data.highlight else theme.ink
        label_y: float = top_y - 8 if value >= 0 else base_y + 18
        parts.append(_rect(center - bar_w / 2, top_y, bar_w, base_y - top_y, color))
        parts.append(
            _text(center, label_y, fmt_value(value, label_unit(data.unit)), theme)
        )
    parts.extend(_category_labels(data.categories, centers, frame.bottom + 24, theme))
    return _finish(parts)


RENDERERS: dict[str, Callable[[ChartData, int, int, Theme], str]] = {
    "line": svg_line,
    "diverging_bar": svg_diverging_bar,
    "waterfall": svg_waterfall,
    "stacked100": svg_stacked100,
    "column": svg_column,
}


def to_svg(chart: Chart, w: int, h: int, theme: Theme) -> str:
    """Render a chart of any kind to an SVG string.

    Raises:
        ValueError: If the kind is unknown or the data does not fit the kind.
    """
    renderer: Callable[[ChartData, int, int, Theme], str] | None = RENDERERS.get(
        chart.kind
    )
    if renderer is None:
        raise ValueError(f"unknown chart kind {chart.kind!r}")
    return renderer(chart.data, w, h, theme)
