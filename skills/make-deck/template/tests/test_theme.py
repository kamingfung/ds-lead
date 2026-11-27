"""Tests for the house palette, type scale and series encoding."""

from dataclasses import FrozenInstanceError

import pytest

from theme import HOUSE, points


def test_house_colors_fonts_and_sizes_match_the_brief() -> None:
    colors: tuple[str, ...] = (
        HOUSE.ink, HOUSE.accent, HOUSE.loss, HOUSE.ochre, HOUSE.sage, HOUSE.sienna, HOUSE.highlight,
        HOUSE.light, HOUSE.panel, HOUSE.grid, HOUSE.gray, HOUSE.paper, HOUSE.tint, HOUSE.loss_tint,
        HOUSE.white, HOUSE.surround,
    )
    assert colors == (
        "#3b1a18", "#1d4a62", "#a04b2d", "#d69a2e", "#95a87f", "#6c2b27", "#7fb3cc", "#c6beb3",
        "#f2ece1", "#e5ddd0", "#767676", "#fbf8f3", "#e6eff3", "#dfb8a6", "#ffffff", "#29221e",
    )
    assert (HOUSE.title_px, HOUSE.subheading_px, HOUSE.body_px, HOUSE.small_px) == (32, 24, 19, 16)
    assert (HOUSE.display_px, HOUSE.big_number_px) == (64, 120)
    assert (HOUSE.head_font, HOUSE.body_font, HOUSE.mono_font_html, HOUSE.mono_font_pptx) == (
        "Arial", "Arial", "Menlo", "Consolas")


def test_theme_is_frozen_and_points_convert_pixels() -> None:
    with pytest.raises(FrozenInstanceError):
        HOUSE.ink = "#000000"  # type: ignore[misc]
    assert points(32) == 24.0


def test_series_order_and_style_wrap_after_four() -> None:
    assert HOUSE.series == ("#3b1a18", "#1d4a62", "#d69a2e", "#95a87f", "#6c2b27")
    assert HOUSE.series_style(3) == ("#95a87f", "dash-dot", "diamond")
    assert HOUSE.series_style(4) == ("#6c2b27", "solid", "circle")
