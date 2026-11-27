"""Tests for chart_style: every recipe renders, carries its header, and uses palette colors."""

from __future__ import annotations

import itertools
import re
from pathlib import Path

import chart_style as cs
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pytest  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.axes import Axes  # noqa: E402
from matplotlib.colors import to_hex, to_rgb, to_rgba  # noqa: E402
from matplotlib.text import Text  # noqa: E402

HEX: re.Pattern[str] = re.compile(r"^#[0-9a-f]{6}$")
HYPHEN_NEGATIVE: re.Pattern[str] = re.compile(r"(?<!\w)-\d")
CONTEXTS: list[str] = ["paper", "notebook", "talk", "poster"]


def _header(ax: Axes, gid: str) -> list[str]:
    """Return the text of the header artists on one axes that carry gid."""
    return [t.get_text() for t in ax.texts if t.get_gid() == gid]


def _drawn_colors(fig: plt.Figure) -> set[str]:
    """Return every visible face, edge, line and grid color drawn in a figure, without alpha."""
    colors: list = []
    for ax in fig.findobj(Axes):
        for patch in ax.patches:
            colors += [patch.get_facecolor(), patch.get_edgecolor()]
        for coll in ax.collections:
            colors += list(coll.get_facecolors()) + list(coll.get_edgecolors())
        for line in ax.lines:
            colors += [
                line.get_color(),
                line.get_markerfacecolor(),
                line.get_markeredgecolor(),
            ]
        colors += [spine.get_edgecolor() for spine in ax.spines.values()]
        colors += [g.get_color() for g in ax.get_xgridlines() + ax.get_ygridlines()]
    return {to_hex(c) for c in colors if to_rgba(c)[3] > 0}


def test_public_api_is_present() -> None:
    names: list[str] = [
        "read_palette",
        "set_chart_style",
        "reset_style",
        "set_chart_seaborn_theme",
        "show_color_palette",
        "show_all_palettes",
        "highlight_bars",
        "label_bars",
        "direct_label",
        "simulate_vision",
        "chart_header",
        "align_headers",
        "create_example_plots",
        "create_context_demo",
    ]
    for name in names:
        assert callable(getattr(cs, name)), name


def test_read_palette_parses_tokens() -> None:
    palette: dict[str, str] = cs.read_palette(cs.DEFAULT_PALETTE)
    assert palette["ink"] == "#3b1a18"
    assert palette["highlight"] == "#7fb3cc"
    assert all(HEX.match(v) for v in palette.values())


@pytest.mark.parametrize("context", CONTEXTS)
def test_example_plots_render_for_each_context(context: str, tmp_path: Path) -> None:
    fig = cs.create_example_plots(context)
    fig.savefig(tmp_path / "grid.png", dpi=40)
    assert sum(1 for ax in fig.axes if ax.get_title(loc="left")) == 15
    plt.close(fig)


def test_context_demo_renders() -> None:
    fig = cs.create_context_demo()
    assert len(fig.axes) == 4
    plt.close(fig)


@pytest.mark.parametrize("recipe", cs.RECIPES, ids=lambda f: f.__name__)
def test_recipe_has_title_subtitle_and_source(recipe) -> None:
    cs.set_chart_style()
    fig, ax = plt.subplots()
    recipe(ax)
    assert ax.get_title(loc="left").strip()
    subtitles: list[str] = _header(ax, cs.SUBTITLE_GID)
    sources: list[str] = _header(ax, cs.SOURCE_GID)
    assert len(subtitles) == 1 and subtitles[0].strip()
    assert len(sources) == 1 and sources[0].startswith("Source: ")
    plt.close(fig)


def test_no_text_uses_a_hyphen_for_a_negative_number() -> None:
    fig = cs.create_example_plots()
    fig.canvas.draw()
    texts: list[str] = [t.get_text() for t in fig.findobj(Text)]
    assert not [t for t in texts if HYPHEN_NEGATIVE.search(t)]
    assert any(cs.MINUS in t for t in texts)
    plt.close(fig)


def test_minus_helper_converts_only_negative_numbers() -> None:
    assert cs._minus("-7") == f"{cs.MINUS}7"
    assert cs._minus("Outlier (5.4, -1.2)") == f"Outlier (5.4, {cs.MINUS}1.2)"
    assert cs._minus("2024 to 2025") == "2024 to 2025"


@pytest.mark.parametrize("recipe", cs.RECIPES, ids=lambda f: f.__name__)
def test_recipe_colors_come_from_palette(recipe) -> None:
    cs.set_chart_style()
    fig, ax = plt.subplots()
    recipe(ax)
    fig.canvas.draw()
    palette: set[str] = set(cs.read_palette(cs.DEFAULT_PALETTE).values())
    assert _drawn_colors(fig) <= palette
    plt.close(fig)


def test_font_resolves_to_arial_when_installed() -> None:
    cs.set_chart_style()
    assert matplotlib.rcParams["font.sans-serif"][0] == "Arial"
    installed: set[str] = {f.name for f in font_manager.fontManager.ttflist}
    if "Arial" not in installed:
        pytest.skip("Arial is not installed")
    path: str = font_manager.findfont(font_manager.FontProperties())
    assert Path(path).name.startswith("Arial")


def test_set_chart_style_scales_by_context_and_font_scale() -> None:
    cs.set_chart_style("talk", 1.0)
    assert matplotlib.rcParams["font.size"] == pytest.approx(13.0)
    cs.set_chart_style("paper", 2.0)
    assert matplotlib.rcParams["font.size"] == pytest.approx(16.0)
    with pytest.raises(ValueError):
        cs.set_chart_style("slide")
    cs.reset_style()
    cs.set_chart_style()


@pytest.mark.parametrize("kind", ["deutan", "protan", "tritan"])
def test_simulate_vision_returns_hex_and_keeps_grey(kind: str) -> None:
    assert HEX.match(cs.simulate_vision(cs.INDIGO, kind))
    grey: str = cs.simulate_vision("#808080", kind)
    assert HEX.match(grey)
    channels: list[int] = [int(grey[i : i + 2], 16) for i in (1, 3, 5)]
    assert max(channels) - min(channels) <= 2


def test_simulate_vision_rejects_unknown_kind() -> None:
    with pytest.raises(ValueError):
        cs.simulate_vision(cs.INDIGO, "achromat")


def test_chart_header_rejects_source_without_prefix() -> None:
    fig, ax = plt.subplots()
    with pytest.raises(ValueError):
        cs.chart_header(ax, "Title", "Subtitle", "Synthetic data")
    plt.close(fig)


def test_label_bars_writes_negative_values_with_minus_sign() -> None:
    cs.set_chart_style()
    fig, ax = plt.subplots()
    bars = ax.bar(range(2), [-3, 4])
    cs.label_bars(ax, bars, highlight=[1])
    texts: list[str] = [t.get_text() for t in ax.texts]
    assert f"{cs.MINUS}3" in texts and "4" in texts
    plt.close(fig)


def test_highlight_bars_colors_and_zero_baseline() -> None:
    fig, ax = plt.subplots()
    bars = ax.bar(range(3), [5, 2, 7])
    cs.highlight_bars(ax, bars, highlight=[2])
    assert to_hex(bars[2].get_facecolor()) == cs.HIGHLIGHT_COLOR
    assert to_hex(bars[0].get_facecolor()) == cs.MUTED_COLOR
    assert ax.get_ylim()[0] == 0
    plt.close(fig)


def test_direct_label_moves_by_dy() -> None:
    fig, ax = plt.subplots()
    label = cs.direct_label(ax, 1.0, 2.0, "Mark", cs.INDIGO, dy=0.5)
    assert label.get_position() == (1.0, 2.5)
    plt.close(fig)


def test_read_palette_is_used_for_module_colors() -> None:
    palette: dict[str, str] = cs.read_palette(cs.DEFAULT_PALETTE)
    assert cs.INK == palette["ink"]
    assert cs.INDIGO == palette["blue"]
    assert cs.HIGHLIGHT_COLOR == palette["highlight"]


def test_seaborn_theme_runs_when_seaborn_is_installed() -> None:
    pytest.importorskip("seaborn")
    cs.set_chart_seaborn_theme("talk")
    assert matplotlib.rcParams["font.size"] == pytest.approx(13.0)
    cs.set_chart_style()


def test_palette_figures_render() -> None:
    for name in cs.PALETTE_SETS:
        plt.close(cs.show_color_palette(name))
    with pytest.raises(ValueError):
        cs.show_color_palette("rainbow")
    plt.close(cs.show_all_palettes())


def _visible_grid(ax: Axes, axis: str) -> bool:
    """Return True when any gridline of one axis is visible."""
    lines = ax.get_xgridlines() if axis == "x" else ax.get_ygridlines()
    return any(line.get_visible() for line in lines)


def _rendered(recipe) -> tuple[plt.Figure, Axes]:
    """Draw one recipe on a fresh axes and render it."""
    cs.set_chart_style()
    fig, ax = plt.subplots()
    recipe(ax)
    fig.canvas.draw()
    return fig, ax


@pytest.mark.parametrize(
    ("recipe", "axis"),
    [
        (cs.example_highlight_bar, "y"),
        (cs.example_grouped_columns, "y"),
        (cs.example_stacked_columns, "y"),
        (cs.example_waterfall, "y"),
    ],
    ids=lambda v: getattr(v, "__name__", v),
)
def test_bar_recipes_hide_value_axis_and_keep_baseline(recipe, axis: str) -> None:
    fig, ax = _rendered(recipe)
    value_axis = ax.yaxis if axis == "y" else ax.xaxis
    assert not ax.spines["left" if axis == "y" else "bottom"].get_visible()
    assert not value_axis.get_majorticklabels()
    assert not _visible_grid(ax, axis)
    assert ax.spines["bottom" if axis == "y" else "left"].get_visible()
    plt.close(fig)


@pytest.mark.parametrize(
    "recipe",
    [cs.example_scatter_outlier, cs.example_waterfall, cs.example_ranked_dots],
    ids=lambda f: f.__name__,
)
def test_no_gridlines_on_point_and_bridge_recipes(recipe) -> None:
    fig, ax = _rendered(recipe)
    assert not _visible_grid(ax, "x") and not _visible_grid(ax, "y")
    plt.close(fig)


@pytest.mark.parametrize(
    "recipe",
    [
        cs.example_lines,
        cs.example_target_line,
        cs.example_fan_chart,
        cs.example_annotated_timeline,
        cs.example_small_multiples,
    ],
    ids=lambda f: f.__name__,
)
def test_line_recipes_have_no_vertical_gridlines(recipe) -> None:
    fig, ax = _rendered(recipe)
    assert not _visible_grid(ax, "x")
    plt.close(fig)


def test_small_multiples_bottom_panels_carry_month_initials() -> None:
    fig, ax = _rendered(cs.example_small_multiples)
    panels = sorted(
        ax.child_axes, key=lambda a: (a.get_position().y0, a.get_position().x0)
    )
    bottom = [p for p in panels if p.get_position().y0 == panels[0].get_position().y0]
    assert len(bottom) == 2
    for panel in bottom:
        labels = [t.get_text() for t in panel.get_xticklabels()]
        assert len(labels) == 12 and labels == list("JFMAMJJASOND")
    for panel in panels[2:]:
        assert not panel.get_xticklabels()
    plt.close(fig)


def test_histogram_share_label_clear_of_bars() -> None:
    fig, ax = _rendered(cs.example_histogram)
    label = next(t for t in ax.texts if "above" in t.get_text())
    renderer = fig.canvas.get_renderer()
    box = label.get_window_extent(renderer)
    assert not [p for p in ax.patches if p.get_window_extent(renderer).overlaps(box)]
    plt.close(fig)


def test_diverging_bars_keep_the_x_axis() -> None:
    fig, ax = _rendered(cs.example_diverging_bars)
    assert ax.spines["bottom"].get_visible()
    assert ax.xaxis.get_majorticklabels()
    plt.close(fig)


def test_dumbbell_has_one_horizontal_guide_line_per_region() -> None:
    fig, ax = _rendered(cs.example_dumbbell)
    assert _visible_grid(ax, "y") and not _visible_grid(ax, "x")
    plt.close(fig)


def test_waterfall_labels_decreases_below_their_bar() -> None:
    fig, ax = _rendered(cs.example_waterfall)
    decreases = [t for t in ax.texts if t.get_text().startswith("\u2212")]
    assert decreases and all(t.get_va() == "top" for t in decreases)
    plt.close(fig)


def _lab(hex_color: str) -> np.ndarray:
    """Convert a hex color to CIELAB (D65 white), to measure color differences."""
    rgb: np.ndarray = np.array(to_rgb(hex_color))
    linear: np.ndarray = np.where(
        rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4
    )
    to_xyz: np.ndarray = np.array(
        [[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]
    )
    xyz: np.ndarray = to_xyz @ linear / np.array([0.95047, 1.0, 1.08883])
    f: np.ndarray = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


@pytest.mark.parametrize("kind", ["normal", "deutan", "protan", "tritan"])
def test_categorical_colors_stay_apart_for_every_vision_type(kind: str) -> None:
    """Every pair of series colors keeps a CIE 1976 color difference of at least 10."""
    colors: list[str] = (
        cs.CATEGORICAL
        if kind == "normal"
        else [cs.simulate_vision(c, kind) for c in cs.CATEGORICAL]
    )
    gaps: list[float] = [
        float(np.linalg.norm(_lab(a) - _lab(b)))
        for a, b in itertools.combinations(colors, 2)
    ]
    assert min(gaps) >= 10, f"{kind}: closest pair is {min(gaps):.1f} apart"
