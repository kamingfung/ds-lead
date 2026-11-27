"""House palette, type scale and series encoding for every renderer."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    """Hex colors, fonts and type sizes in CSS pixels."""

    ink: str = "#3b1a18"
    accent: str = "#1d4a62"
    loss: str = "#a04b2d"
    ochre: str = "#d69a2e"
    sage: str = "#95a87f"
    sienna: str = "#6c2b27"
    highlight: str = "#7fb3cc"
    light: str = "#c6beb3"
    panel: str = "#f2ece1"
    grid: str = "#e5ddd0"
    gray: str = "#767676"
    paper: str = "#fbf8f3"
    tint: str = "#e6eff3"
    loss_tint: str = "#dfb8a6"
    white: str = "#ffffff"
    surround: str = "#29221e"
    head_font: str = "Arial"
    body_font: str = "Arial"
    mono_font_html: str = "Menlo"
    mono_font_pptx: str = "Consolas"
    title_px: int = 32
    subheading_px: int = 24
    body_px: int = 19
    small_px: int = 16
    display_px: int = 64
    big_number_px: int = 120
    line_styles: tuple[str, ...] = ("solid", "dashed", "dotted", "dash-dot")
    markers: tuple[str, ...] = ("circle", "square", "triangle", "diamond")

    @property
    def series(self) -> tuple[str, ...]:
        """Series colors in order: ink, accent, ochre, sage, sienna."""
        return (self.ink, self.accent, self.ochre, self.sage, self.sienna)

    def series_style(self, index: int) -> tuple[str, str, str]:
        """Return (color, line style, marker) for a zero-based series index."""
        return (
            self.series[index % len(self.series)],
            self.line_styles[index % len(self.line_styles)],
            self.markers[index % len(self.markers)],
        )


def points(px: float) -> float:
    """Convert CSS pixels to PowerPoint points at 1 px = 0.75 pt."""
    return px * 0.75


HOUSE: Theme = Theme()


def fit_px(text: str, width_px: float, max_px: float, min_px: float = 24.0) -> float:
    """Return the largest font size, up to max_px, at which bold Arial text fits width_px on one line.

    Uses an average glyph width of 0.6 em for bold Arial; this is an estimate, so leave a margin.
    """
    if not text:
        return max_px
    size: float = width_px / (0.6 * len(text))
    return max(min_px, min(max_px, size))
