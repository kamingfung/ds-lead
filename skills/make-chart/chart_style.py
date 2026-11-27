"""Chart style for matplotlib: palette, chart header, labels and 15 chart recipes.

Colors come from `palette.css`, or from the file named by the environment variable
CHART_STYLE_PALETTE when that variable is set before this module is imported.
Each recipe draws on one axes and calls `chart_header`, so a recipe can be copied
and given new data.
"""

from __future__ import annotations

import os
import re
from collections.abc import Callable, Iterable, Sequence
from pathlib import Path
from typing import Any

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.colors import to_hex, to_rgb
from matplotlib.figure import Figure
from matplotlib.patches import Circle, Rectangle
from matplotlib.transforms import offset_copy

MINUS: str = "\u2212"
SOURCE_PREFIX: str = "Source: "
SUBTITLE_GID: str = "chart-subtitle"
SOURCE_GID: str = "chart-source"
DEFAULT_PALETTE: Path = Path(__file__).with_name("palette.css")
CONTEXT_SCALE: dict[str, float] = {
    "paper": 0.8,
    "notebook": 1.0,
    "talk": 1.3,
    "poster": 1.6,
}
FONT_FAMILY: list[str] = ["Arial", "Helvetica", "DejaVu Sans"]
_SOURCE: str = "Source: Synthetic illustrative data"
_TOKEN: re.Pattern[str] = re.compile(r"--([a-z]+)\s*:\s*(#[0-9a-fA-F]{6})\s*;")
_COMMENT: re.Pattern[str] = re.compile(r"/\*.*?\*/", re.DOTALL)
_NEGATIVE: re.Pattern[str] = re.compile(r"(?<!\w)-(?=\d)")
_MACHADO: dict[str, np.ndarray] = {
    "protan": np.array(
        [
            [0.152286, 1.052583, -0.204868],
            [0.114503, 0.786281, 0.099216],
            [-0.003882, -0.048116, 1.051998],
        ]
    ),
    "deutan": np.array(
        [
            [0.367322, 0.860646, -0.227968],
            [0.280085, 0.672501, 0.047413],
            [-0.011820, 0.042940, 0.968881],
        ]
    ),
    "tritan": np.array(
        [
            [1.255528, -0.076749, -0.178779],
            [-0.078411, 0.930809, 0.147602],
            [0.004733, 0.691367, 0.303900],
        ]
    ),
}


def read_palette(path: str | os.PathLike[str] = DEFAULT_PALETTE) -> dict[str, str]:
    """Read the color tokens from a palette CSS file.

    Args:
        path: CSS file with declarations such as `--ink: #3b1a18;`.

    Returns:
        Map from token name without the leading dashes, such as "ink", to a
        lowercase hex color.
    """
    text: str = _COMMENT.sub("", Path(path).read_text(encoding="utf-8"))
    return {name: value.lower() for name, value in _TOKEN.findall(text)}


PALETTE: dict[str, str] = read_palette(
    os.environ.get("CHART_STYLE_PALETTE", DEFAULT_PALETTE)
)
INK: str = PALETTE["ink"]
PAPER: str = PALETTE["paper"]
PANEL: str = PALETTE["panel"]
TINT: str = PALETTE["tint"]
LIGHT: str = PALETTE["light"]
INDIGO: str = PALETTE["blue"]
RUST: str = PALETTE["red"]
OCHRE: str = PALETTE["orange"]
SIENNA: str = PALETTE["purple"]
SAGE: str = PALETTE["green"]
SKY: str = PALETTE["sky"]
LOSSTINT: str = PALETTE["losstint"]
GREY: str = PALETTE["grey"]
HIGHLIGHT_COLOR: str = PALETTE["highlight"]
MUTED_COLOR: str = LIGHT
GAIN_COLOR: str = INDIGO
LOSS_COLOR: str = RUST
CATEGORICAL: list[str] = [INK, INDIGO, SKY, SAGE, SIENNA]
LIGHT_PALETTE: list[str] = [PAPER, PANEL, TINT, LIGHT]
SEQUENTIAL: list[str] = [PAPER, TINT, SKY, INDIGO, INK]
DIVERGING: list[str] = [RUST, LOSSTINT, PAPER, SKY, INDIGO]
SEMANTIC: dict[str, str] = {
    "ink": INK,
    "paper": PAPER,
    "panel": PANEL,
    "tint": TINT,
    "light": LIGHT,
    "indigo": INDIGO,
    "rust": RUST,
    "ochre": OCHRE,
    "highlight": HIGHLIGHT_COLOR,
    "sage": SAGE,
    "sienna": SIENNA,
    "grey": GREY,
}
PALETTE_SETS: dict[str, list[str]] = {
    "categorical": CATEGORICAL,
    "light": LIGHT_PALETTE,
    "sequential": SEQUENTIAL,
    "diverging": DIVERGING,
}


def _minus(text: str) -> str:
    """Replace the hyphen that starts a negative number with a true minus sign.

    Args:
        text: Label or tick text.

    Returns:
        The text with U+2212 in place of each negative sign.
    """
    return _NEGATIVE.sub(MINUS, text)


def set_chart_style(context: str = "notebook", font_scale: float = 1.0) -> None:
    """Apply the house style to matplotlib's global rcParams.

    Args:
        context: Where the chart is seen: "paper", "notebook", "talk" or "poster".
        font_scale: Extra multiplier on fonts and line widths.

    Raises:
        ValueError: If context is not one of the four names.
    """
    if context not in CONTEXT_SCALE:
        raise ValueError(
            f"context must be one of {sorted(CONTEXT_SCALE)}, got {context!r}"
        )
    k: float = CONTEXT_SCALE[context] * font_scale
    matplotlib.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": FONT_FAMILY,
            "font.size": 10 * k,
            "axes.titlesize": 12 * k,
            "axes.titleweight": "bold",
            "axes.labelsize": 10 * k,
            "xtick.labelsize": 9 * k,
            "ytick.labelsize": 9 * k,
            "legend.fontsize": 9 * k,
            "text.color": INK,
            "axes.labelcolor": INK,
            "axes.edgecolor": INK,
            "axes.facecolor": PAPER,
            "axes.linewidth": 0.8 * k,
            "axes.grid": False,
            "axes.axisbelow": True,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.unicode_minus": True,
            "grid.color": LIGHT,
            "grid.linewidth": 0.5 * k,
            "xtick.color": INK,
            "ytick.color": INK,
            "lines.linewidth": 1.6 * k,
            "lines.markersize": 5 * k,
            "patch.linewidth": 0.8 * k,
            "patch.edgecolor": INK,
            "figure.facecolor": PAPER,
            "savefig.facecolor": PAPER,
        }
    )


def reset_style() -> None:
    """Restore matplotlib's default rcParams."""
    matplotlib.rcdefaults()


def set_chart_seaborn_theme(context: str = "notebook", font_scale: float = 1.0) -> None:
    """Apply seaborn's white theme, then the house style on top of it.

    Seaborn is imported here, so this module works without it.

    Args:
        context: Where the chart is seen: "paper", "notebook", "talk" or "poster".
        font_scale: Extra multiplier on fonts and line widths.
    """
    import seaborn as sns

    sns.set_theme(style="white", context=context, font_scale=font_scale)
    set_chart_style(context, font_scale)


def _swatch_row(ax: Axes, colors: Sequence[str], labels: Sequence[str]) -> None:
    """Draw one row of color swatches with a hex or name label under each."""
    for i, (color, label) in enumerate(zip(colors, labels)):
        ax.add_patch(
            Rectangle((i, 0), 0.9, 1, facecolor=color, edgecolor=INK, linewidth=0.6)
        )
        ax.text(i + 0.45, -0.15, label, ha="center", va="top", fontsize=8, color=INK)
    ax.set_xlim(-0.1, len(colors))
    ax.set_ylim(-0.6, 1.1)
    ax.set_axis_off()


def show_color_palette(
    palette_name: str = "categorical", figsize: tuple[float, float] = (12, 2)
) -> Figure:
    """Draw the swatches of one palette.

    Args:
        palette_name: "categorical", "light", "sequential" or "diverging".
        figsize: Figure size in inches.

    Returns:
        The new figure.

    Raises:
        ValueError: If palette_name is unknown.
    """
    if palette_name not in PALETTE_SETS:
        raise ValueError(
            f"palette_name must be one of {sorted(PALETTE_SETS)}, got {palette_name!r}"
        )
    colors: list[str] = PALETTE_SETS[palette_name]
    fig, ax = plt.subplots(figsize=figsize, facecolor=PAPER)
    _swatch_row(ax, colors, colors)
    ax.set_title(f"{palette_name.title()} palette", loc="left", fontweight="bold")
    return fig


def show_all_palettes(figsize: tuple[float, float] = (14, 12)) -> Figure:
    """Draw the semantic tokens, every palette, and the three color-vision simulations.

    Args:
        figsize: Figure size in inches.

    Returns:
        The new figure.
    """
    fig, axes = plt.subplots(8, 1, figsize=figsize, facecolor=PAPER)
    rows: list[tuple[str, list[str], list[str]]] = [
        ("Semantic tokens", list(SEMANTIC.values()), list(SEMANTIC.keys())),
        ("Categorical", CATEGORICAL, CATEGORICAL),
        ("Light", LIGHT_PALETTE, LIGHT_PALETTE),
        ("Sequential", SEQUENTIAL, SEQUENTIAL),
        ("Diverging", DIVERGING, DIVERGING),
    ]
    for kind in ("deutan", "protan", "tritan"):
        simulated: list[str] = [simulate_vision(color, kind) for color in CATEGORICAL]
        rows.append((f"Categorical, {kind}anopia simulation", simulated, simulated))
    for ax, (title, colors, labels) in zip(axes, rows):
        _swatch_row(ax, colors, labels)
        ax.set_title(title, loc="left", fontsize=10, fontweight="bold")
    fig.tight_layout()
    return fig


def simulate_vision(hex_color: str, kind: str) -> str:
    """Simulate how a color looks with one color-vision deficiency.

    Uses the Machado, Oliveira and Fernandes (2009) matrices at full severity,
    applied to linear sRGB.

    Args:
        hex_color: Color such as "#1d4a62".
        kind: "deutan", "protan" or "tritan".

    Returns:
        The simulated color as a lowercase hex string.

    Raises:
        ValueError: If kind is unknown.
    """
    if kind not in _MACHADO:
        raise ValueError(f"kind must be one of {sorted(_MACHADO)}, got {kind!r}")
    linear: np.ndarray = np.array(to_rgb(hex_color))
    linear = np.where(
        linear <= 0.04045, linear / 12.92, ((linear + 0.055) / 1.055) ** 2.4
    )
    out: np.ndarray = np.clip(_MACHADO[kind] @ linear, 0, 1)
    srgb: np.ndarray = np.where(
        out <= 0.0031308, 12.92 * out, 1.055 * out ** (1 / 2.4) - 0.055
    )
    return to_hex(np.clip(srgb, 0, 1))


def chart_header(
    ax: Axes,
    title: str,
    subtitle: str | None = None,
    source: str | None = None,
    source_dy: float = 30,
) -> None:
    """Write a flush-left title, a subtitle above the axes, and a source line below.

    Args:
        ax: Axes to label.
        title: Finding, written as a full sentence.
        subtitle: Metric, unit and window.
        source: Source line; must start with "Source: ".
        source_dy: Distance in points between the axes bottom and the source line.

    Raises:
        ValueError: If source does not start with "Source: ".
    """
    if source is not None and not source.startswith(SOURCE_PREFIX):
        raise ValueError(f"source must start with {SOURCE_PREFIX!r}, got {source!r}")
    font_size: float = matplotlib.rcParams["font.size"]
    pad: float = 8 + 1.3 * font_size if subtitle is not None else 6
    ax.set_title(title, loc="left", fontweight="bold", color=INK, pad=pad)
    if subtitle is not None:
        ax.text(
            0,
            1,
            subtitle,
            transform=offset_copy(ax.transAxes, ax.figure, y=4, units="points"),
            ha="left",
            va="bottom",
            fontsize=font_size,
            color=INK,
            gid=SUBTITLE_GID,
        )
    if source is not None:
        ax.text(
            0,
            0,
            source,
            transform=offset_copy(
                ax.transAxes, ax.figure, y=-source_dy, units="points"
            ),
            ha="left",
            va="top",
            fontsize=0.8 * font_size,
            color=INK,
            gid=SOURCE_GID,
        )


def _display_xy(text: Any) -> tuple[float, float]:
    """Return a text artist's position in display pixels."""
    x, y = text.get_position()
    return tuple(text.get_transform().transform((x, y)))


def align_headers(fig: Figure) -> None:
    """Line up the subtitles and source lines of the axes in each row of a grid.

    Subtitles in a row move to the highest one, and source lines move to the lowest
    one. Horizontal positions do not change.

    Args:
        fig: Figure whose axes carry headers from `chart_header`.
    """
    rows: dict[float, list[Axes]] = {}
    for ax in fig.axes:
        rows.setdefault(round(ax.get_position().y1, 3), []).append(ax)
    for axes in rows.values():
        for gid, pick in ((SUBTITLE_GID, max), (SOURCE_GID, min)):
            texts = [t for ax in axes for t in ax.texts if t.get_gid() == gid]
            if not texts:
                continue
            target: float = pick(_display_xy(t)[1] for t in texts)
            for t in texts:
                x_disp: float = _display_xy(t)[0]
                t.set_transform(fig.transFigure)
                t.set_position((x_disp / fig.bbox.width, target / fig.bbox.height))


def highlight_bars(
    ax: Axes,
    bars: Sequence[Rectangle],
    highlight: Iterable[int],
    color: str = HIGHLIGHT_COLOR,
    muted: str = MUTED_COLOR,
) -> None:
    """Color the highlighted bars and mute the rest. Bars start the value axis at zero.

    Args:
        ax: Axes that holds the bars.
        bars: Bars from `ax.bar`, in order.
        highlight: Indices of the bars that carry the message.
        color: Fill of highlighted bars. Each one also gets an ink edge.
        muted: Fill of the other bars.
    """
    marked: set[int] = set(highlight)
    for i, bar in enumerate(bars):
        if i in marked:
            bar.set_facecolor(color)
            bar.set_edgecolor(INK)
        else:
            bar.set_facecolor(muted)
            bar.set_edgecolor("none")
    if all(bar.get_height() >= 0 for bar in bars):
        ax.set_ylim(bottom=0)


def label_bars(
    ax: Axes,
    bars: Sequence[Rectangle],
    highlight: Iterable[int] = (),
    fmt: str = "{:.0f}",
) -> None:
    """Write each vertical bar's value just past its end. Bold the highlighted labels.

    Args:
        ax: Axes that holds the bars.
        bars: Vertical bars, in order.
        highlight: Indices of the bars whose labels are bold.
        fmt: Format string for the value, such as "{:.1f}".
    """
    marked: set[int] = set(highlight)
    for i, bar in enumerate(bars):
        value: float = bar.get_height()
        above: bool = value >= 0
        ax.annotate(
            _minus(fmt.format(value)),
            xy=(bar.get_x() + bar.get_width() / 2, value),
            xytext=(0, 3 if above else -3),
            textcoords="offset points",
            ha="center",
            va="bottom" if above else "top",
            color=INK,
            fontweight="bold" if i in marked else "normal",
        )


def direct_label(
    ax: Axes, x: float, y: float, text: str, color: str, dy: float = 0, **kwargs: Any
) -> Any:
    """Write a label at a mark, so the reader need not look up a legend.

    Args:
        ax: Axes to draw on.
        x: Horizontal data position.
        y: Vertical data position.
        text: Label text. A leading hyphen before a number becomes a minus sign.
        color: Text color, from the palette.
        dy: Vertical offset in data units.
        **kwargs: Passed to `Axes.text`. The default vertical alignment is "center".

    Returns:
        The text artist.
    """
    kwargs.setdefault("va", "center")
    return ax.text(x, y + dy, _minus(text), color=color, **kwargs)


def _grid(ax: Axes, axis: str) -> None:
    """Show the gridlines of one axis, in the light palette color."""
    ax.grid(True, axis=axis)


def hide_value_axis(ax: Axes, axis: str = "y") -> None:
    """Hide the value axis spine, ticks, tick labels and gridlines. The zero baseline stays.

    Use it on bar charts whose bars all carry a direct value label. The axis title stays.

    Args:
        ax: Bar chart axes.
        axis: "y" for vertical bars, "x" for horizontal bars.
    """
    spine: str = "left" if axis == "y" else "bottom"
    label_flag: str = "labelleft" if axis == "y" else "labelbottom"
    ax.spines[spine].set_visible(False)
    ax.tick_params(axis=axis, which="both", length=0, **{label_flag: False})
    ax.grid(False, axis=axis)


def example_lines(ax: Axes) -> None:
    """Draw four lines with distinct markers and dash styles, labeled at their ends.

    Args:
        ax: Axes to draw on.
    """
    x: np.ndarray = np.arange(0, 11)
    series: list[tuple[str, list[float], str, str, str]] = [
        (
            "Product A",
            [1.2, 1.5, 1.9, 2.3, 2.8, 3.2, 3.6, 3.9, 4.2, 4.5, 4.8],
            INDIGO,
            "o",
            "-",
        ),
        (
            "Product B",
            [1.0, 1.1, 1.3, 1.2, 1.4, 1.5, 1.4, 1.6, 1.5, 1.7, 1.6],
            SIENNA,
            "s",
            "--",
        ),
        (
            "Product C",
            [0.8, 0.9, 0.8, 1.0, 0.9, 1.1, 1.0, 1.1, 1.2, 1.1, 1.2],
            GREY,
            "^",
            ":",
        ),
        (
            "Product D",
            [0.6, 0.5, 0.7, 0.6, 0.7, 0.6, 0.8, 0.7, 0.8, 0.7, 0.8],
            RUST,
            "D",
            "-.",
        ),
    ]
    for name, values, color, marker, style in series:
        ax.plot(x, values, color=color, marker=marker, markersize=4.5, linestyle=style)
        direct_label(
            ax,
            x[-1] + 0.3,
            values[-1],
            f"{name} {values[-1]:.1f}",
            color,
            fontweight="bold" if color == INDIGO else "normal",
        )
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 5.5)
    _grid(ax, "y")
    chart_header(
        ax,
        "Product A pulls ahead of the other three lines",
        "Demand index by week, weeks 0 to 10; axis starts at 0",
        _SOURCE,
    )


def example_highlight_bar(ax: Axes) -> None:
    """Draw five bars with the top bar highlighted and labeled.

    Args:
        ax: Axes to draw on.
    """
    cats: list[str] = ["Item A", "Item B", "Item C", "Item D", "Item E"]
    vals: list[float] = [24, 46, 58, 81, 33]
    bars = ax.bar(cats, vals, width=0.55)
    highlight_bars(ax, bars, highlight=[3])
    label_bars(ax, bars, highlight=[3])
    ax.set_ylim(0, 95)
    hide_value_axis(ax)
    chart_header(
        ax,
        "Item D outsells every other item",
        "Shipments, thousand units; highlighted bar is the focal item",
        _SOURCE,
    )


def example_scatter_outlier(ax: Axes, rng: np.random.Generator | None = None) -> None:
    """Draw three groups of points and call out one outlier with a ring and a note.

    Args:
        ax: Axes to draw on.
        rng: Random generator for the synthetic points. Defaults to a seed of 42.
    """
    rng = np.random.default_rng(42) if rng is None else rng
    g1: np.ndarray = rng.normal([1.0, 1.2], [0.8, 0.7], size=(18, 2))
    g2: np.ndarray = rng.normal([2.2, 2.0], [0.7, 0.8], size=(16, 2))
    g3: np.ndarray = rng.normal([0.2, 2.5], [0.6, 0.6], size=(14, 2))
    ax.scatter(
        g1[:, 0], g1[:, 1], marker="o", s=28, color=INDIGO, alpha=0.8, label="Tier 1"
    )
    ax.scatter(
        g2[:, 0], g2[:, 1], marker="s", s=28, color=OCHRE, alpha=0.85, label="Tier 2"
    )
    ax.scatter(
        g3[:, 0], g3[:, 1], marker="^", s=30, color=GREY, alpha=0.85, label="Tier 3"
    )
    ax.scatter([5.4], [-1.2], marker="o", s=36, color=RUST, zorder=5)
    ax.add_patch(
        Circle(
            (5.4, -1.2),
            radius=0.55,
            fill=False,
            edgecolor=RUST,
            linewidth=1.4,
            linestyle="--",
        )
    )
    ax.annotate(
        _minus("Outlier (5.4, -1.2)"),
        xy=(5.4, -1.2),
        xytext=(3.7, -2.1),
        color=RUST,
        fontsize=8,
        fontweight="bold",
        arrowprops={"arrowstyle": "->", "color": RUST, "lw": 1.0},
    )
    ax.set_xlim(-1.5, 6.5)
    ax.set_ylim(-2.6, 4.2)
    ax.set_xlabel("Metric X, index points")
    ax.set_ylabel("Metric Y, index points")
    ax.legend(frameon=False, loc="upper left", ncol=3)
    n: int = len(g1) + len(g2) + len(g3) + 1
    chart_header(
        ax,
        "One account sits far from the pack",
        f"Metric Y against Metric X by tier, n = {n} accounts",
        _SOURCE,
        source_dy=45,
    )


def example_waterfall(ax: Axes) -> None:
    """Draw a profit bridge: totals in ink, increases in indigo, decreases in rust.

    Args:
        ax: Axes to draw on.
    """
    labels: list[str] = ["2024", "Volume", "Price", "Returns", "FX", "2025"]
    deltas: list[int] = [100, 24, 9, -7, -5, 121]
    last: int = len(deltas) - 1
    ax.bar(0, deltas[0], width=0.55, color=INK)
    ax.text(
        0,
        deltas[0] - 3,
        str(deltas[0]),
        ha="center",
        va="top",
        color=PAPER,
        fontweight="bold",
    )
    level: int = deltas[0]
    ends: list[int] = [level]
    for i in range(1, last):
        change: int = deltas[i]
        base: int = level if change >= 0 else level + change
        ax.bar(
            i,
            abs(change),
            bottom=base,
            width=0.55,
            color=INDIGO if change >= 0 else RUST,
        )
        # increases are labeled above the bar, decreases below it, so the label sits where the bar moves
        label_y: float = base + abs(change) + 2 if change >= 0 else base - 2
        ax.text(
            i,
            label_y,
            _minus(f"{change:+d}"),
            ha="center",
            va="bottom" if change >= 0 else "top",
        )
        level += change
        ends.append(level)
    ax.bar(last, level, width=0.55, color=INK)
    ax.text(
        last,
        level - 3,
        str(level),
        ha="center",
        va="top",
        color=PAPER,
        fontweight="bold",
    )
    for i in range(last):
        ax.plot([i + 0.275, i + 0.725], [ends[i], ends[i]], color=LIGHT, linewidth=0.8)
    ax.set_xticks(range(len(labels)), labels)
    ax.set_ylim(0, 140)
    hide_value_axis(ax)
    chart_header(
        ax,
        f"Volume added {deltas[1]}, more than the net gain of {level - deltas[0]}",
        "Profit bridge 2024 to 2025, USD million; indigo up, rust down",
        _SOURCE,
    )


def example_target_line(ax: Axes) -> None:
    """Draw a monthly series against a target line and shade the months above target.

    Args:
        ax: Axes to draw on.
    """
    months: list[str] = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
    xm: np.ndarray = np.arange(len(months))
    actual: np.ndarray = np.array([64, 67, 73, 69, 78, 72, 68, 74, 66, 65, 69, 71])
    target: int = 70
    ax.axhline(target, color=INK, linestyle="--", linewidth=1.0)
    direct_label(ax, -0.2, target, f"Target {target}", INK, dy=1.0, ha="left")
    ax.plot(xm, actual, color=INDIGO, marker="o", markersize=4)
    ax.fill_between(
        xm,
        actual,
        target,
        where=actual >= target,
        interpolate=True,
        color=INDIGO,
        alpha=0.22,
    )
    peak: int = 4
    ax.annotate(
        f"May: {actual[peak]} ({actual[peak] - target:+d})",
        xy=(peak, actual[peak]),
        xytext=(peak + 0.6, 80.5),
        color=INDIGO,
        fontsize=8,
        fontweight="bold",
        arrowprops={"arrowstyle": "->", "color": INDIGO, "lw": 1.0},
    )
    ax.set_xticks(xm, months)
    ax.set_ylim(55, 86)
    _grid(ax, "y")
    above: int = int(np.sum(actual >= target))
    chart_header(
        ax,
        f"Throughput cleared the target in {above} of 12 months",
        "Monthly index, 2025; axis starts at 55; shading = above target",
        _SOURCE,
    )


def example_dumbbell(ax: Axes) -> None:
    """Draw target and actual values per region, joined by a segment.

    An open circle marks the target and a filled circle marks the actual value.
    The segment and the signed label show the direction.

    Args:
        ax: Axes to draw on.
    """
    regions: list[str] = [
        "Region North",
        "Region Central",
        "Region East",
        "Region South",
        "Region West",
    ]
    target: np.ndarray = np.array([70, 80, 68, 72, 75])
    actual: np.ndarray = np.array([68, 76, 65, 75, 81])
    ys: np.ndarray = np.arange(len(regions))
    for y, tgt, act in zip(ys, target, actual):
        color: str = INDIGO if act >= tgt else RUST
        ax.plot([tgt, act], [y, y], color=color, linewidth=2.0)
        ax.scatter([tgt], [y], facecolors=PAPER, edgecolors=INK, s=40, zorder=4)
        ax.scatter([act], [y], color=color, s=40, zorder=5)
        direct_label(ax, 86, y, f"{act - tgt:+d}", color, fontweight="bold")
    ax.set_yticks(ys, regions)
    ax.set_xlim(60, 90)
    _grid(ax, "y")  # one light guide line per region
    beat: int = int(np.sum(actual >= target))
    chart_header(
        ax,
        f"{beat} of five regions beat their target",
        "Score against target, 2025; open circle = target, filled = actual",
        _SOURCE,
    )


def example_histogram(ax: Axes, rng: np.random.Generator | None = None) -> None:
    """Draw an order-size histogram and shade the bins above a threshold.

    Args:
        ax: Axes to draw on.
        rng: Random generator for the synthetic orders. Defaults to a seed of 42.
    """
    rng = np.random.default_rng(42) if rng is None else rng
    samples: np.ndarray = rng.gamma(shape=5.0, scale=11.0, size=400)
    thresh: float = 70.0
    med: float = float(np.median(samples))
    share: float = 100.0 * float(np.mean(samples > thresh))
    counts, edges, patches = ax.hist(
        samples, bins=22, color=LIGHT, edgecolor=PAPER, linewidth=0.5
    )
    for edge, patch in zip(edges[:-1], patches):
        if edge >= thresh:
            patch.set_facecolor(INDIGO)
    ax.axvline(med, color=INK, linestyle="--", linewidth=1.2)
    direct_label(ax, med + 2.0, max(counts) * 0.9, f"Median {med:.0f}", INK)
    top_right: float = float(counts[edges[:-1] >= thresh].max())
    direct_label(
        ax,
        thresh + 6.0,
        top_right + 0.04 * max(counts),
        f"{share:.0f}% above {thresh:.0f}",
        INDIGO,
        va="bottom",
        fontweight="bold",
    )
    ax.set_ylim(0, max(counts) * 1.15)
    ax.set_xlabel("Order size, units")
    ax.set_ylabel("Orders")
    _grid(ax, "y")
    chart_header(
        ax,
        f"{share:.0f}% of orders are larger than {thresh:.0f} units",
        f"Order size, n = {len(samples)} orders; indigo bins lie above {thresh:.0f} units",
        _SOURCE,
        source_dy=45,
    )


def example_grouped_columns(ax: Axes) -> None:
    """Draw two years of values per region as paired columns with value labels.

    Args:
        ax: Axes to draw on.
    """
    regions: list[str] = ["Region North", "Region South", "Region East", "Region West"]
    y24: np.ndarray = np.array([42, 55, 38, 47])
    y25: np.ndarray = np.array([58, 57, 36, 52])
    xr: np.ndarray = np.arange(len(regions))
    width: float = 0.34
    ax.bar(xr - width / 2, y24, width=width, color=OCHRE, label="2024")
    ax.bar(xr + width / 2, y25, width=width, color=SIENNA, label="2025")
    for x, a, b in zip(xr, y24, y25):
        ax.text(x - width / 2, a + 1.0, str(a), ha="center", color=INK)
        ax.text(
            x + width / 2, b + 1.0, str(b), ha="center", color=SIENNA, fontweight="bold"
        )
    ax.set_xticks(xr, regions)
    ax.set_ylim(0, 68)
    ax.legend(frameon=False, loc="upper right", ncol=2)
    hide_value_axis(ax)
    best: int = int(np.argmax(y25 - y24))
    chart_header(
        ax,
        f"{regions[best]} posted the largest year-over-year gain",
        "Regional volume, thousand units, 2024 and 2025",
        _SOURCE,
    )


def example_fan_chart(ax: Axes) -> None:
    """Draw history, a dashed forecast and a shaded uncertainty band.

    Args:
        ax: Axes to draw on.
    """
    hist_x: np.ndarray = np.arange(2023, 2027)
    hist_y: np.ndarray = np.array([62.0, 67.5, 72.0, 76.5])
    fc_x: np.ndarray = np.arange(2026, 2029)
    fc_mid: np.ndarray = np.array([76.5, 82.0, 88.0])
    fc_lo: np.ndarray = np.array([76.5, 78.5, 82.5])
    fc_hi: np.ndarray = np.array([76.5, 85.5, 93.5])
    ax.plot(hist_x, hist_y, color=INDIGO, marker="o", markersize=4, linewidth=2.0)
    ax.plot(
        fc_x,
        fc_mid,
        color=INDIGO,
        linestyle="--",
        marker="o",
        markersize=4,
        linewidth=1.8,
    )
    ax.fill_between(fc_x, fc_lo, fc_hi, color=INDIGO, alpha=0.16)
    ax.axvline(2026, color=GREY, linestyle=":", linewidth=1.0)
    direct_label(ax, 2026.1, 61.5, "Forecast", GREY)
    direct_label(
        ax,
        2028,
        fc_mid[-1] + 6,
        f"{fc_mid[-1]:.0f}",
        INDIGO,
        ha="center",
        fontweight="bold",
    )
    ax.set_xticks(np.arange(2023, 2029))
    ax.set_ylim(58, 99)
    _grid(ax, "y")
    chart_header(
        ax,
        f"Projected output reaches {fc_mid[-1]:.0f} by 2028",
        "Index, 2023 to 2028; axis starts at 58; band = projection range",
        _SOURCE,
    )


def _panel(
    inset: Axes,
    name: str,
    focal: np.ndarray,
    peers: Sequence[np.ndarray],
    months: np.ndarray,
) -> None:
    """Draw one small-multiple panel: peers in light grey and the focal series in indigo."""
    for peer in peers:
        inset.plot(months, peer, color=LIGHT, linewidth=1.0)
    inset.plot(months, focal, color=INDIGO, linewidth=2.0)
    inset.scatter([months[-1]], [focal[-1]], color=INDIGO, s=22, zorder=5)
    direct_label(
        inset,
        months[-1] + 0.4,
        focal[-1],
        f"{focal[-1]:.0f}",
        INDIGO,
        fontsize=7.5,
        fontweight="bold",
    )
    inset.set_title(name, loc="left", fontsize=8.5, fontweight="bold", color=INK, pad=3)
    inset.set_xlim(1, 14.5)
    inset.set_ylim(94, 130)
    inset.set_yticks([])


def example_small_multiples(ax: Axes, rng: np.random.Generator | None = None) -> None:
    """Draw a 2 x 2 grid of panels, each with one focal region against its peers.

    The panels are inset axes inside one axes, so the header belongs to the whole grid.

    Args:
        ax: Axes to draw on.
        rng: Random generator for the synthetic series. Defaults to a seed of 42.
    """
    rng = np.random.default_rng(42) if rng is None else rng
    months: np.ndarray = np.arange(1, 13)
    names: list[str] = ["Region North", "Region South", "Region East", "Region West"]
    trends: list[np.ndarray] = [
        np.linspace(100, 124, 12),
        np.linspace(100, 106, 12),
        np.linspace(100, 99, 12),
        np.linspace(100, 109, 12),
    ]
    series: dict[str, np.ndarray] = {
        n: t + rng.normal(0, 1.5, 12) for n, t in zip(names, trends)
    }
    boxes: list[tuple[float, float]] = [
        (0.0, 0.5),
        (0.55, 0.5),
        (0.0, 0.0),
        (0.55, 0.0),
    ]
    for (x0, y0), name in zip(boxes, names):
        peers: list[np.ndarray] = [v for n, v in series.items() if n != name]
        inset: Axes = ax.inset_axes([x0, y0, 0.45, 0.38])
        _panel(inset, name, series[name], peers, months)
        if y0 == 0.0:
            inset.set_xticks(months, list("JFMAMJJASOND"))
            inset.tick_params(axis="x", length=2)
        else:
            inset.set_xticks([])
    ax.set_axis_off()
    chart_header(
        ax,
        "Region North ends the year highest of four regions",
        "Index, month 1 = 100; North in indigo, peer regions in light grey",
        _SOURCE,
    )


def example_slope(ax: Axes) -> None:
    """Draw a two-period slope graph with start and end values labeled.

    Args:
        ax: Axes to draw on.
    """
    items: list[str] = ["Line A", "Line B", "Line C", "Line D", "Line E"]
    v_start: list[int] = [42, 36, 31, 27, 22]
    v_end: list[int] = [58, 41, 35, 29, 18]
    for name, s0, s1 in zip(items, v_start, v_end):
        if name == "Line A":
            color, weight = INDIGO, "bold"
        else:
            color, weight = (GREY if s1 >= s0 else RUST), "normal"
        ax.plot(
            [0, 1],
            [s0, s1],
            color=color,
            marker="o",
            markersize=4.5,
            linewidth=2.2 if name == "Line A" else 1.4,
        )
        direct_label(ax, -0.06, s0, f"{name} {s0}", INK, ha="right", fontsize=7.8)
        direct_label(
            ax,
            1.06,
            s1,
            f"{s1} {name}",
            color,
            ha="left",
            fontsize=7.8,
            fontweight=weight,
        )
    ax.set_xticks([0, 1], ["2023", "2025"])
    ax.set_xlim(-0.6, 1.6)
    ax.set_ylim(12, 64)
    _grid(ax, "x")
    gain: int = v_end[0] - v_start[0]
    chart_header(
        ax,
        f"Line A gained {gain} units, the most of five lines",
        "Units by product line, 2023 and 2025; indigo = focal line",
        _SOURCE,
    )


def example_ranked_dots(ax: Axes) -> None:
    """Draw eight markets as sorted dots with the mean as a dashed reference line.

    Args:
        ax: Axes to draw on.
    """
    markets: list[str] = [f"Market {i}" for i in range(1, 9)]
    values: np.ndarray = np.array([18, 24, 29, 37, 44, 52, 61, 78])
    mean: float = float(np.mean(values))
    ys: np.ndarray = np.arange(len(markets))
    colors: list[str] = [INDIGO if v == values.max() else GREY for v in values]
    ax.hlines(ys, xmin=0, xmax=values, color=LIGHT, linewidth=1.6)
    ax.scatter(values, ys, color=colors, s=36, zorder=4)
    for y, v, c in zip(ys, values, colors):
        direct_label(
            ax,
            v + 1.5,
            y,
            f"{v}",
            c,
            fontsize=7.8,
            fontweight="bold" if c == INDIGO else "normal",
        )
    ax.axvline(mean, color=INK, linestyle="--", linewidth=1.1)
    direct_label(ax, mean + 1.2, -0.7, f"Mean {mean:.0f}", INK, fontsize=7.8)
    ax.set_ylim(-1.0, len(markets) - 0.5)
    ax.set_yticks(ys, markets)
    ax.set_xlim(0, 88)
    ax.set_xlabel("Sales volume, thousand units")
    gap: int = int(values[-1] - values[-2])
    chart_header(
        ax,
        f"Market 8 sells {gap} thousand units more than the next market",
        "Sales volume, thousand units, 2025; sorted; dashed line = mean",
        _SOURCE,
        source_dy=45,
    )


def example_diverging_bars(ax: Axes) -> None:
    """Draw signed changes as horizontal bars: gains in indigo, losses in rust.

    Args:
        ax: Axes to draw on.
    """
    names: list[str] = [f"Product {i}" for i in range(1, 7)]
    values: np.ndarray = np.array([-8.3, -4.6, -1.5, 3.2, 6.1, 12.4])
    ys: np.ndarray = np.arange(len(names))
    colors: list[str] = [INDIGO if v >= 0 else RUST for v in values]
    ax.barh(ys, values, color=colors, height=0.55)
    ax.axvline(0, color=INK, linewidth=0.9)
    for y, v, c in zip(ys, values, colors):
        if v >= 0:
            direct_label(
                ax,
                v + 0.4,
                y,
                f"{v:+.1f}",
                c,
                ha="left",
                fontsize=7.8,
                fontweight="bold",
            )
        else:
            direct_label(
                ax,
                v - 0.4,
                y,
                f"{v:+.1f}",
                c,
                ha="right",
                fontsize=7.8,
                fontweight="bold",
            )
    ax.set_yticks(ys, names)
    ax.set_xlim(-12, 16)
    ax.set_xlabel("Net change, percentage points")
    up: int = int(np.sum(values >= 0))
    chart_header(
        ax,
        f"{up} of {len(names)} products grew, and {len(names) - up} declined",
        "Change, percentage points, 2024 to 2025; gains indigo, losses rust",
        _SOURCE,
        source_dy=45,
    )


def example_stacked_columns(ax: Axes) -> None:
    """Draw 100% stacked columns of three age brackets, with each share labeled.

    Args:
        ax: Axes to draw on.
    """
    years: list[str] = ["2021", "2022", "2023", "2024", "2025"]
    under_30: np.ndarray = np.array([46, 42, 38, 33, 28])
    mid: np.ndarray = np.array([32, 33, 34, 35, 36])
    over_50: np.ndarray = 100 - under_30 - mid
    xs: np.ndarray = np.arange(len(years))
    ax.bar(xs, under_30, width=0.52, color=OCHRE, label="Under 30")
    ax.bar(xs, mid, bottom=under_30, width=0.52, color=INDIGO, label="30 to 50")
    ax.bar(
        xs, over_50, bottom=under_30 + mid, width=0.52, color=SIENNA, label="Over 50"
    )
    for i in xs:
        ax.text(
            i,
            under_30[i] / 2,
            f"{under_30[i]}%",
            ha="center",
            va="center",
            color=INK,
            fontweight="bold",
        )
        ax.text(
            i,
            under_30[i] + mid[i] / 2,
            f"{mid[i]}%",
            ha="center",
            va="center",
            color=PAPER,
            fontweight="bold",
        )
        ax.text(
            i,
            under_30[i] + mid[i] + over_50[i] / 2,
            f"{over_50[i]}%",
            ha="center",
            va="center",
            color=PAPER,
            fontweight="bold",
        )
    ax.set_xticks(xs, years)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Share of buyers, %")
    ax.legend(frameon=False, loc="center left", bbox_to_anchor=(1.02, 0.5))
    hide_value_axis(ax)
    chart_header(
        ax,
        f"Buyers over 50 rise from {over_50[0]}% to {over_50[-1]}% of the total",
        "Share of total buyers by age bracket, %, 2021 to 2025",
        _SOURCE,
    )


def example_annotated_timeline(ax: Axes) -> None:
    """Draw a quarterly series with a price-reset marker and a projected tail.

    Args:
        ax: Axes to draw on.
    """
    t: np.ndarray = np.arange(0, 15)
    values: np.ndarray = np.array(
        [50, 52, 54, 53, 56, 59, 61, 68, 74, 76, 80, 84, 88, 92, 97]
    )
    ax.plot(t[:12], values[:12], color=INK, linewidth=1.8)
    ax.plot(t[11:], values[11:], color=INDIGO, linestyle="--", linewidth=1.8)
    ax.axvspan(11, 14, color=LIGHT, alpha=0.45)
    ax.axvline(6.5, color=RUST, linestyle=":", linewidth=1.2)
    ax.annotate(
        "Price reset",
        xy=(6.5, 65),
        xytext=(2.2, 74),
        color=RUST,
        fontsize=8,
        fontweight="bold",
        arrowprops={"arrowstyle": "->", "color": RUST, "lw": 1.0},
    )
    direct_label(
        ax,
        14,
        values[-1] + 1.5,
        f"{values[-1]}*",
        INDIGO,
        ha="center",
        fontsize=8.5,
        fontweight="bold",
    )
    ax.set_xticks([0, 3, 6, 9, 12], ["Q1 '22", "Q4 '22", "Q3 '23", "Q2 '24", "Q1 '25*"])
    ax.set_ylim(45, 105)
    _grid(ax, "y")
    chart_header(
        ax,
        "Sales rose every quarter after the price reset in late 2023",
        "Quarterly sales index, Q1 2022 to Q3 2025; * = projected",
        _SOURCE,
    )


RECIPES: list[Callable[..., None]] = [
    example_lines,
    example_highlight_bar,
    example_scatter_outlier,
    example_waterfall,
    example_target_line,
    example_dumbbell,
    example_histogram,
    example_grouped_columns,
    example_fan_chart,
    example_small_multiples,
    example_slope,
    example_ranked_dots,
    example_diverging_bars,
    example_stacked_columns,
    example_annotated_timeline,
]
_SEEDED: tuple[Callable[..., None], ...] = (
    example_scatter_outlier,
    example_histogram,
    example_small_multiples,
)


def create_example_plots(context: str = "notebook") -> Figure:
    """Draw the 15 chart recipes on one grid, styled for the given context.

    Args:
        context: Style context, passed to `set_chart_style`.

    Returns:
        The figure. The grid has three columns and five rows.
    """
    set_chart_style(context)
    rng: np.random.Generator = np.random.default_rng(42)
    fig, axes = plt.subplots(5, 3, figsize=(18.0, 21.0), facecolor=PAPER)
    for ax, recipe in zip(axes.flat, RECIPES):
        if recipe in _SEEDED:
            recipe(ax, rng)
        else:
            recipe(ax)
    fig.subplots_adjust(
        left=0.05, right=0.98, top=0.95, bottom=0.04, wspace=0.3, hspace=0.6
    )
    align_headers(fig)
    return fig


def create_context_demo(panel_size: tuple[float, float] = (5.2, 4.2)) -> Figure:
    """Draw one chart in each of the four contexts, to show font and stroke scaling.

    The style leaves matplotlib's rcParams set to the "notebook" context.

    Args:
        panel_size: Width and height of each panel in inches.

    Returns:
        The figure with a 2 x 2 grid of panels.
    """
    fig, axes = plt.subplots(
        2, 2, figsize=(panel_size[0] * 2, panel_size[1] * 2), facecolor=PAPER
    )
    for ax, context in zip(axes.flat, CONTEXT_SCALE):
        set_chart_style(context)
        example_highlight_bar(ax)
        ax.text(
            0.99,
            0.97,
            f"Context: {context}",
            transform=ax.transAxes,
            ha="right",
            va="top",
            color=INK,
            fontsize=8,
        )
    set_chart_style("notebook")
    fig.subplots_adjust(wspace=0.4, hspace=0.6)
    align_headers(fig)
    return fig
