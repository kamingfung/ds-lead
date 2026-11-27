"""Native PowerPoint renderer: draws a Deck as editable shapes and charts with python-pptx.

Every region becomes shapes at its layout box, so the slide matches the HTML geometry in pixels.
"""

from __future__ import annotations

import math
import re
import zipfile
from dataclasses import dataclass, replace
from io import BytesIO
from typing import Any, Callable, NamedTuple, Sequence

from lxml import etree
from pptx import Presentation
from pptx.chart.chart import Chart as PptxChart
from pptx.chart.data import CategoryChartData
from pptx.chart.point import Point
from pptx.chart.series import BarSeries, LineSeries
from pptx.dml.color import RGBColor
from pptx.enum.chart import (
    XL_CHART_TYPE,
    XL_LABEL_POSITION,
    XL_LEGEND_POSITION,
    XL_MARKER_STYLE,
    XL_TICK_LABEL_POSITION,
)
from pptx.enum.dml import MSO_LINE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.parts.image import Image as PptxImage
from pptx.shapes.autoshape import Shape
from pptx.shapes.connector import Connector
from pptx.shapes.shapetree import GroupShapes, SlideShapes
from pptx.slide import Slide as PptxSlide
from pptx.table import _Cell
from pptx.text.text import TextFrame
from pptx.util import Emu, Inches, Pt

from charts import DARK_LUMA, ChartData, fmt_value, label_step
from layouts import (
    BODY_BOTTOM,
    BODY_TOP,
    BODY_W,
    GUTTER,
    LAYOUTS,
    MARGIN,
    Region,
    chrome,
)
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
    Image,
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
    lead_in,
    slide_sources,
    sources_slides,
)
from theme import Theme, fit_px, points

EMU_PER_PX: int = 9525
CAP_SHARE: float = 0.08
TOP_SHARE: float = 1.10
MIN_PERCENT_LABEL: float = 6.0
METRIC_PX: float = 80.0
LABEL_H: float = 28.0
NOTE_H: float = 32.0
CARD_PAD: float = 24.0
TILE_PAD: float = 12.0
TILE_PX: float = 56.0
GRID_PX: float = 24.0
RECOMMEND_PAD: float = 16.0
CYCLE_W: float = 170.0
CYCLE_H: float = 72.0
LEGEND_W: float = 110.0
MIN_LABEL_PX: float = 14.0
UNIT_MAX: int = 3
TICK_FORMAT: str = "#,##0"
FOOTER_Y: float = 676.0
FOOTER_GAP: float = 8.0
FOOTER_H: float = 24.0
TITLE_LAYOUTS: tuple[str, ...] = ("cover", "section")
DASH_STYLES: dict[str, MSO_LINE] = {
    "solid": MSO_LINE.SOLID,
    "dashed": MSO_LINE.DASH,
    "dotted": MSO_LINE.ROUND_DOT,
    "dash-dot": MSO_LINE.DASH_DOT,
}


class Box(NamedTuple):
    """A box in CSS pixels: left, top, width and height."""

    x: float
    y: float
    w: float
    h: float


@dataclass(frozen=True)
class Style:
    """A text role: size in CSS pixels, color, font, alignment, bold and the gap after a paragraph."""

    px: float
    color: str
    font: str = "Arial"
    align: PP_ALIGN = PP_ALIGN.LEFT
    bold: bool = False
    gap: float = 8.0


def emu(px: float) -> Emu:
    """Convert CSS pixels to EMU at 1 px = 9525 EMU."""
    return Emu(round(px * EMU_PER_PX))


def rgb(color: str) -> RGBColor:
    """Convert a hex color such as "#1d4a62" to an RGBColor."""
    return RGBColor.from_string(color.lstrip("#").upper())


def box_of(region: Region) -> Box:
    """Return the pixel box of a layout region."""
    return Box(region.x, region.y, region.w, region.h)


def _cells(box: Box, count: int, columns: int) -> list[Box]:
    rows: int = math.ceil(count / columns)
    width: float = (box.w - GUTTER * (columns - 1)) / columns
    height: float = (box.h - GUTTER * (rows - 1)) / rows
    return [
        Box(
            box.x + (i % columns) * (width + GUTTER),
            box.y + (i // columns) * (height + GUTTER),
            width,
            height,
        )
        for i in range(count)
    ]


def _plain(shape: Any) -> None:
    style: Any = shape._element.find(qn("p:style"))
    if style is not None:
        shape._element.remove(style)


def _fill(shape: Any, color: str) -> None:
    if color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = rgb(color)
    else:
        shape.fill.background()


def _textbox(
    shapes: SlideShapes | GroupShapes, box: Box, pad: float = 0.0, fill: str = ""
) -> Shape:
    shape: Shape = shapes.add_textbox(emu(box.x), emu(box.y), emu(box.w), emu(box.h))
    _fill(shape, fill)
    frame: TextFrame = shape.text_frame
    frame.word_wrap = True
    frame.auto_size = MSO_AUTO_SIZE.NONE
    frame.margin_left = frame.margin_right = frame.margin_top = frame.margin_bottom = (
        emu(pad)
    )
    return shape


def _run(para: Any, text: str, style: Style, bold: bool = False) -> None:
    piece: Any = para.add_run()
    piece.text = text
    piece.font.name = style.font
    piece.font.size = Pt(points(style.px))
    piece.font.bold = bold or style.bold
    piece.font.color.rgb = rgb(style.color)


def _write_para(frame: TextFrame, runs: Sequence[Run], style: Style) -> None:
    fresh: bool = len(frame.paragraphs) == 1 and not frame.paragraphs[0].runs
    para: Any = frame.paragraphs[0] if fresh else frame.add_paragraph()
    para.alignment = style.align
    para.space_after = Pt(points(style.gap))
    for run in runs:
        _run(para, run.text, style, run.bold)


def _paragraphs(
    shapes: SlideShapes | GroupShapes,
    box: Box,
    paras: Sequence[Sequence[Run]],
    style: Style,
    pad: float = 0.0,
) -> Shape:
    shape: Shape = _textbox(shapes, box, pad)
    for runs in paras:
        _write_para(shape.text_frame, runs, style)
    return shape


def _words(
    shapes: SlideShapes | GroupShapes, box: Box, text: str, style: Style
) -> Shape:
    return _paragraphs(shapes, box, [(Run(text),)], style)


def _shape(
    shapes: SlideShapes | GroupShapes,
    kind: MSO_SHAPE,
    box: Box,
    fill: str,
    line: str = "",
    dash: MSO_LINE = MSO_LINE.SOLID,
) -> Shape:
    shape: Shape = shapes.add_shape(
        kind, emu(box.x), emu(box.y), emu(box.w), emu(box.h)
    )
    _plain(shape)
    _fill(shape, fill)
    if line:
        shape.line.color.rgb = rgb(line)
        shape.line.width = Pt(0.75)
        shape.line.dash_style = dash
    else:
        shape.line.fill.background()
    return shape


def _node(
    shapes: SlideShapes | GroupShapes,
    kind: MSO_SHAPE,
    box: Box,
    paras: Sequence[Sequence[Run]],
    style: Style,
    fill: str,
    line: str = "",
) -> Shape:
    shape: Shape = _shape(shapes, kind, box, fill, line)
    shape.text_frame.margin_left = shape.text_frame.margin_right = emu(8)
    shape.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    shape.text_frame.word_wrap = True
    for runs in paras:
        _write_para(shape.text_frame, runs, style)
    return shape


def _connector(
    shapes: SlideShapes | GroupShapes,
    kind: MSO_CONNECTOR,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    color: str,
    width: float = 0.75,
    arrow: bool = False,
) -> Connector:
    line: Connector = shapes.add_connector(kind, emu(x1), emu(y1), emu(x2), emu(y2))
    _plain(line)
    line.line.color.rgb = rgb(color)
    line.line.width = Pt(width)
    if arrow:
        line.line._get_or_add_ln().append(
            etree.Element(qn("a:tailEnd"), type="triangle")
        )
    return line


def _group(shapes: SlideShapes, name: str) -> GroupShapes:
    group: Any = shapes.add_group_shape()
    group.name = name
    return group.shapes


def _skip_labels(chart: PptxChart, step: int) -> None:
    """Label every step-th category, as the SVG chart does, so long series stay legible."""
    if step <= 1:
        return
    for axis in chart._chartSpace.xpath(".//c:catAx"):
        skip: Any = etree.Element(qn("c:tickLblSkip"), val=str(step))
        later: list[Any] = axis.xpath(
            "./c:tickMarkSkip | ./c:noMultiLvlLbl | ./c:extLst"
        )
        if later:
            later[0].addprevious(skip)
        else:
            axis.append(skip)


def _no_border(chart: PptxChart) -> None:
    space: Any = chart._chartSpace
    old: Any = space.find(qn("c:spPr"))
    if old is not None:
        space.remove(old)
    sp: Any = etree.Element(qn("c:spPr"))
    etree.SubElement(sp, qn("a:noFill"))
    etree.SubElement(etree.SubElement(sp, qn("a:ln")), qn("a:noFill"))
    space.find(qn("c:chart")).addnext(sp)


def _label(point: Point, text: str, position: XL_LABEL_POSITION, style: Style) -> None:
    label: Any = point.data_label
    label.position = position
    label.text_frame.text = text
    font: Any = label.text_frame.paragraphs[0].runs[0].font
    font.name = style.font
    font.size = Pt(points(style.px))
    font.bold = style.bold
    font.color.rgb = rgb(style.color)


def _fill_point(point: Point, color: str) -> None:
    point.format.fill.solid()
    point.format.fill.fore_color.rgb = rgb(color)


def _waterfall_spans(values: Sequence[float]) -> list[tuple[float, float]]:
    spans: list[tuple[float, float]] = [(0.0, values[0])]
    level: float = values[0]
    for step in values[1:-1]:
        following: float = level + step
        spans.append((min(level, following), max(level, following)))
        level = following
    if not math.isclose(values[-1], level, abs_tol=1e-6):
        raise ValueError(f"waterfall end {values[-1]} is not start plus steps {level}")
    return [*spans, (0.0, values[-1])]


def _bullet_runs(item: Bullet) -> tuple[Run, ...]:
    body: tuple[Run, ...] = (
        lead_in(item.lead, item.text).runs if item.lead else (Run(item.text),)
    )
    note: tuple[Run, ...] = (Run(f" ({item.footnote})"),) if item.footnote else ()
    return (Run("\u2022 "), *body, *note)


def _expand_tabs(slides: Sequence[Slide]) -> list[Slide]:
    expanded: list[Slide] = []
    for slide in slides:
        tabs: object = slide.regions.get("tabs")
        if not isinstance(tabs, Tabs):
            expanded.append(slide)
            continue
        for name, charts in tabs.tabs:
            regions: dict[str, object] = {**slide.regions, "tabs": charts}
            expanded.append(
                replace(slide, title=f"{slide.title} \u00b7 {name}", regions=regions)
            )
    return expanded


def _luma(color: str) -> float:
    red, green, blue = (int(color[i : i + 2], 16) for i in (1, 3, 5))
    return 0.299 * red + 0.587 * green + 0.114 * blue


def _short(unit: str) -> str:
    """Return the unit for in-chart value labels: "%" or a unit of at most three characters, else nothing."""
    return unit if unit == "%" or len(unit) <= UNIT_MAX else ""


def _takeaways_heading(layout: str, name: str, value: object) -> object:
    """Give an unheaded takeaways list the heading "Takeaways" on chart and tabs layouts."""
    chart_like: bool = layout.startswith("chart_") or layout == "tabs"
    if (
        chart_like
        and name == "takeaways"
        and isinstance(value, Bullets)
        and not value.heading
    ):
        return replace(value, heading="Takeaways")
    return value


def _recommend_runs(runs: tuple[Run, ...]) -> tuple[Run, ...]:
    """Start a recommendation with a bold "Recommendation:" unless the text already starts with it."""
    text: str = "".join(run.text for run in runs)
    if text.startswith("Recommendation:"):  # bold the existing lead-in
        return (Run("Recommendation:", bold=True), Run(text[len("Recommendation:") :]))
    return (Run("Recommendation: ", bold=True), *runs)


def _numbered(blocks: Sequence[Any]) -> tuple[Text, ...]:
    """Number every paragraph of the text blocks: "1. ", "2. " and so on."""
    paras: list[Para] = [para for block in blocks for para in block.paras]
    return (
        Text(
            tuple(
                Para((Run(f"{n}. "), *para.runs))
                for n, para in enumerate(paras, start=1)
            )
        ),
    )


def _cycle_boxes(box: Box) -> tuple[Box, Box, Box, Box]:
    """Return the top, right, bottom and left node boxes, centered on an ellipse inset by half a node."""
    cx: float = box.x + box.w / 2
    cy: float = box.y + box.h / 2
    rx: float = (box.w - CYCLE_W) / 2
    ry: float = (box.h - CYCLE_H) / 2
    w, h = CYCLE_W, CYCLE_H
    return (
        Box(cx - w / 2, cy - ry - h / 2, w, h),
        Box(cx + rx - w / 2, cy - h / 2, w, h),
        Box(cx - w / 2, cy + ry - h / 2, w, h),
        Box(cx - rx - w / 2, cy - h / 2, w, h),
    )


def _marker(
    shapes: SlideShapes | GroupShapes, status: str, box: Box, theme: Theme
) -> None:
    """Draw a timeline status from shapes: a sage circle with a check, a loss square with a cross, or an ochre diamond with two bars."""
    if status == "open":
        _shape(shapes, MSO_SHAPE.DIAMOND, box, theme.ochre)
        for center in (0.34, 0.66):
            _shape(
                shapes,
                MSO_SHAPE.RECTANGLE,
                Box(
                    box.x + box.w * (center - 0.05),
                    box.y + box.h * 0.25,
                    box.w * 0.1,
                    box.h * 0.5,
                ),
                theme.white,
            )
        return
    kind, fill, glyph = (
        (MSO_SHAPE.OVAL, theme.sage, "\u2713")
        if status == "kept"
        else (MSO_SHAPE.RECTANGLE, theme.loss, "\u00d7")
    )
    frame: TextFrame = _shape(shapes, kind, box, fill).text_frame
    frame.margin_left = frame.margin_right = frame.margin_top = frame.margin_bottom = 0
    frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    frame.word_wrap = False
    _write_para(
        frame,
        (Run(glyph, bold=True),),
        Style(box.h * 0.7, theme.white, align=PP_ALIGN.CENTER, bold=True, gap=0),
    )


def _legend(shapes: SlideShapes | GroupShapes, box: Box, theme: Theme) -> None:
    """Draw the marker key at the bottom-right of the body: Kept, Dropped and Open."""
    x: float = box.x + box.w - 3 * LEGEND_W
    y: float = box.y + box.h - LABEL_H
    for index, (status, word) in enumerate(
        (("kept", "Kept"), ("dropped", "Dropped"), ("open", "Open"))
    ):
        left: float = x + index * LEGEND_W
        _marker(shapes, status, Box(left, y + 4, 20, 20), theme)
        _words(
            shapes,
            Box(left + 28, y, LEGEND_W - 28, LABEL_H),
            word,
            Style(theme.small_px, theme.ink),
        )


class _Painter:
    """Draws one slide: chrome, regions, the chart rule and the speaker notes."""

    def __init__(self, slide: PptxSlide, theme: Theme) -> None:
        self.slide: PptxSlide = slide
        self.theme: Theme = theme
        self.shapes: SlideShapes = slide.shapes

    def draw(self, spec: Slide, page: int) -> None:
        """Draw every part of one slide. The layout must exist in LAYOUTS."""
        if spec.layout == "cover":
            self._dark_cover()
        self._chrome(spec)
        self._footer(spec, page)
        for name, region in LAYOUTS[spec.layout].items():
            value: object = spec.regions.get(name)
            if (
                value is None
                and name in ("title", "heading")
                and spec.layout in TITLE_LAYOUTS
            ):
                value = spec.title
            value = _takeaways_heading(spec.layout, name, value)
            if value is not None:
                self._region(spec.layout, name, region, value)
        self._rule(spec.layout)
        sources: str = slide_sources(spec)
        parts: list[str] = [
            p for p in (spec.notes, f"Sources: {sources}" if sources else "") if p
        ]
        if parts:
            self.slide.notes_slide.notes_text_frame.text = "\n".join(parts)

    def _dark_cover(self) -> None:
        # the cover sits on an ink ground; its text switches to the light tokens
        fill: Any = self.slide.background.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor.from_string(self.theme.ink.lstrip("#"))
        self.theme = replace(
            self.theme,
            ink=self.theme.paper,
            gray=self.theme.light,
            accent=self.theme.highlight,
        )

    def _chrome(self, spec: Slide) -> None:
        t: Theme = self.theme
        chart_title: bool = spec.layout.startswith("chart_") or spec.layout == "tabs"
        texts: dict[str, tuple[str, Style]] = {
            "kicker": (spec.kicker, Style(t.small_px, t.accent, bold=True)),
            "title": (spec.title, Style(t.title_px, t.ink, bold=True)),
            "lead": (spec.lead, Style(t.body_px, t.ink, bold=chart_title)),
        }
        for name, region in chrome(spec.layout).items():
            if name == "footer":
                continue
            text, style = texts[name]
            if text:
                _words(self.shapes, box_of(region), text, style)

    def _footer(self, spec: Slide, page: int) -> None:
        """Draw the rule, the "Source: " line and the page number on every slide except the cover."""
        if spec.layout == "cover":
            return
        t: Theme = self.theme
        _connector(
            self.shapes,
            MSO_CONNECTOR.STRAIGHT,
            MARGIN,
            FOOTER_Y,
            MARGIN + BODY_W,
            FOOTER_Y,
            t.light,
            0.75,
        )
        box: Box = Box(MARGIN, FOOTER_Y + FOOTER_GAP, BODY_W, FOOTER_H)
        sources: str = slide_sources(spec)
        if sources:
            _words(self.shapes, box, f"Source: {sources}", Style(t.small_px, t.gray))
        _words(
            self.shapes, box, str(page), Style(t.small_px, t.gray, align=PP_ALIGN.RIGHT)
        )

    def _region(self, layout: str, name: str, region: Region, value: object) -> None:
        box: Box = box_of(region)
        if isinstance(value, str):
            _words(
                self.shapes,
                box,
                value,
                Style(self.theme.display_px, self.theme.ink, bold=True),
            )
            return
        elements: tuple[Any, ...] = value if isinstance(value, tuple) else (value,)
        if not elements or self._own_look(layout, name, box, elements):
            return
        if region.unit == "item" and all(
            isinstance(e, (Text, Bullets)) for e in elements
        ):
            self._flow(box, elements)
            return
        for cell, element in zip(_cells(box, len(elements), len(elements)), elements):
            self._element(cell, element)

    def _own_look(
        self, layout: str, name: str, box: Box, elements: tuple[Any, ...]
    ) -> bool:
        """Draw a region that has its own look. Return False for every other region."""
        if layout == "grid4":
            self._grid4(box, elements)
        elif (layout, name) == ("note", "heading"):
            self._heading(box, elements)
        elif name == "recommendation":
            self._recommendation(box, elements)
        elif layout == "references":
            self._flow(box, _numbered(elements))
        else:
            return False
        return True

    def _grid4(self, box: Box, blocks: Sequence[Bullets]) -> None:
        """Draw a 2 by 2 grid: each block number and its heading on one line, then the bullets."""
        t: Theme = self.theme
        for index, (cell, block) in enumerate(zip(_cells(box, len(blocks), 2), blocks)):
            frame: TextFrame = _textbox(self.shapes, cell).text_frame
            head: Style = Style(GRID_PX, t.accent, bold=True)
            _write_para(frame, (Run(str(index + 1), bold=True),), head)
            if block.heading:
                _run(
                    frame.paragraphs[0],
                    f"  {block.heading}",
                    replace(head, color=t.ink),
                    bold=True,
                )
            for item in block.items:
                _write_para(frame, _bullet_runs(item), Style(t.body_px, t.ink))

    def _heading(self, box: Box, texts: Sequence[Text]) -> None:
        """Draw a note heading: 24 px bold ink."""
        frame: TextFrame = _textbox(self.shapes, box).text_frame
        for text in texts:
            for para in text.paras:
                _write_para(
                    frame,
                    para.runs,
                    Style(self.theme.subheading_px, self.theme.ink, bold=True),
                )

    def _recommendation(self, box: Box, texts: Sequence[Text]) -> None:
        """Draw the recommendation strip on a tint fill with 16 px padding."""
        frame: TextFrame = _textbox(
            self.shapes, box, RECOMMEND_PAD, self.theme.tint
        ).text_frame
        for para in texts[0].paras:
            _write_para(
                frame,
                _recommend_runs(para.runs),
                Style(self.theme.body_px, self.theme.ink),
            )

    def _element(self, box: Box, element: object) -> None:
        if isinstance(element, (Text, Bullets)):
            self._flow(box, (element,))
            return
        drawers: dict[type, Callable[[Box, Any], None]] = {
            Card: self._card,
            Tile: self._tile,
            Chart: self._chart,
            Image: self._image,
            Table: self._table,
            Panel: self._panel,
            Flow: self._flow_diagram,
            Cycle: self._cycle,
            Matrix: self._matrix,
            Gantt: self._gantt,
            Tree: self._tree,
            Timeline: self._timeline,
            Num: self._big_number,
        }
        drawer: Callable[[Box, Any], None] | None = drawers.get(type(element))
        if drawer is None:
            raise ValueError(f"no renderer for {type(element).__name__}")
        drawer(box, element)

    def _big_number(self, box: Box, num: Num) -> None:
        # the big_number layout's focal figure, centered like the HTML renderer
        text: str = num.text()
        px: float = fit_px(text, box.w, self.theme.big_number_px)
        _words(
            self.shapes,
            box,
            text,
            Style(px, self.theme.accent, align=PP_ALIGN.CENTER, bold=True),
        )

    def _flow(self, box: Box, elements: Sequence[object]) -> None:
        t: Theme = self.theme
        frame: TextFrame = _textbox(self.shapes, box).text_frame
        for element in elements:
            if not isinstance(element, (Text, Bullets)):
                continue
            if element.heading:
                _write_para(
                    frame,
                    (Run(element.heading, bold=True),),
                    Style(t.subheading_px, t.accent),
                )
            if isinstance(element, Text):
                for para in element.paras:
                    _write_para(frame, para.runs, Style(t.body_px, t.ink))
            else:
                for item in element.items:
                    _write_para(frame, _bullet_runs(item), Style(t.body_px, t.ink))

    def _card(self, box: Box, card: Card) -> None:
        t: Theme = self.theme
        shape: Shape = _shape(self.shapes, MSO_SHAPE.RECTANGLE, box, t.panel)
        frame: TextFrame = shape.text_frame
        frame.word_wrap = True
        frame.auto_size = MSO_AUTO_SIZE.NONE
        frame.vertical_anchor = MSO_ANCHOR.TOP
        frame.margin_left = frame.margin_right = frame.margin_top = (
            frame.margin_bottom
        ) = emu(24)
        tag: str = (card.tag + (f"  {card.badge}" if card.badge else "")).upper()
        _write_para(
            frame, (Run(tag, bold=True),), Style(t.small_px, t.accent, bold=True)
        )
        if card.metric is not None:
            text: str = card.metric.text()
            px: float = fit_px(text, box.w - 2 * CARD_PAD, METRIC_PX)
            _write_para(frame, (Run(text, bold=True),), Style(px, t.ink, bold=True))
        _write_para(
            frame, (Run(card.statement, bold=True),), Style(t.subheading_px, t.ink)
        )
        _write_para(frame, (Run(card.body),), Style(t.body_px, t.ink))
        for row in card.rows:
            _write_para(frame, _bullet_runs(row), Style(t.body_px, t.ink))

    def _tile(self, box: Box, tile: Tile) -> None:
        t: Theme = self.theme
        frame: TextFrame = _textbox(self.shapes, box, TILE_PAD, t.panel).text_frame
        text: str = tile.value.text()
        px: float = fit_px(text, box.w - 2 * TILE_PAD, TILE_PX)
        _write_para(frame, (Run(text, bold=True),), Style(px, t.accent, bold=True))
        _write_para(
            frame, (Run(tile.label, bold=True),), Style(t.small_px, t.ink, bold=True)
        )
        if tile.caption:
            _write_para(frame, (Run(tile.caption),), Style(t.small_px, t.gray))

    def _panel(self, box: Box, panel: Panel) -> None:
        _shape(
            self.shapes, MSO_SHAPE.RECTANGLE, box, "", self.theme.light, MSO_LINE.DASH
        )
        _words(
            self.shapes,
            box,
            panel.label,
            Style(self.theme.body_px, self.theme.ink, bold=True),
        )

    def _table(self, box: Box, table: Table) -> None:
        t: Theme = self.theme
        note_h: float = NOTE_H if table.note else 0.0
        grid_h: float = box.h - note_h
        rows: int = len(table.rows) + 1
        grid: Any = self.shapes.add_table(
            rows, len(table.columns), emu(box.x), emu(box.y), emu(box.w), emu(grid_h)
        ).table
        for column in grid.columns:
            column.width = emu(box.w / len(table.columns))
        for row in grid.rows:
            row.height = emu(grid_h / rows)
        for col, title in enumerate(table.columns):
            self._cell(
                grid.cell(0, col),
                title,
                table.align[col],
                t.panel,
                Style(t.small_px, t.ink, bold=True),
            )
        for r, row in enumerate(table.rows, start=1):
            for col, value in enumerate(row):
                self._cell(
                    grid.cell(r, col),
                    value,
                    table.align[col],
                    t.paper,
                    Style(t.small_px, t.ink),
                )
        if table.note:
            _words(
                self.shapes,
                Box(box.x, box.y + grid_h, box.w, note_h),
                table.note,
                Style(t.small_px, t.gray),
            )

    def _cell(
        self, cell: _Cell, value: str | Num, align: str, fill: str, base: Style
    ) -> None:
        is_num: bool = isinstance(value, Num)
        cell.fill.solid()
        cell.fill.fore_color.rgb = rgb(fill)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.margin_left = cell.margin_right = emu(8)
        font: str = self.theme.mono_font_pptx if is_num else base.font
        right: bool = is_num or align == "right"
        style: Style = replace(
            base, font=font, align=PP_ALIGN.RIGHT if right else PP_ALIGN.LEFT, gap=0.0
        )
        _write_para(
            cell.text_frame,
            (Run(value.text() if isinstance(value, Num) else value),),
            style,
        )

    def _chart(self, box: Box, chart: Chart) -> None:
        builders: dict[str, Callable[[Box, ChartData], None]] = {
            "line": self._line_chart,
            "diverging_bar": self._diverging_chart,
            "waterfall": self._waterfall_chart,
            "stacked100": self._stacked_chart,
            "column": self._column_chart,
        }
        builder: Callable[[Box, ChartData], None] | None = builders.get(chart.kind)
        if builder is None:
            raise ValueError(f"unknown chart kind {chart.kind!r}")
        builder(box, chart.data)

    def _image(self, box: Box, image: Image) -> None:
        """Place a PNG at its own aspect ratio, as large as fits and centered in the box."""
        width, height = PptxImage.from_file(image.path).size
        scale: float = min(box.w / width, box.h / height)
        w: float = width * scale
        h: float = height * scale
        picture: Any = self.shapes.add_picture(
            image.path,
            emu(box.x + (box.w - w) / 2),
            emu(box.y + (box.h - h) / 2),
            emu(w),
            emu(h),
        )
        picture._element.nvPicPr.cNvPr.set("descr", image.alt)

    def _add_chart(
        self,
        box: Box,
        kind: XL_CHART_TYPE,
        categories: Sequence[str],
        series: Sequence[tuple[str, Sequence[float]]],
        legend: XL_LEGEND_POSITION | None,
        axis_format: str = TICK_FORMAT,
    ) -> PptxChart:
        data: CategoryChartData = CategoryChartData()
        data.categories = list(categories)
        for name, values in series:
            data.add_series(name, list(values))
        chart: PptxChart = self.shapes.add_chart(
            kind, emu(box.x), emu(box.y), emu(box.w), emu(box.h), data
        ).chart
        _skip_labels(chart, label_step(categories, box.w))
        chart.font.name = "Arial"
        chart.font.size = Pt(12)
        chart.font.color.rgb = rgb(self.theme.ink)
        chart.has_legend = legend is not None
        if legend is not None:
            chart.legend.position = legend
            chart.legend.include_in_layout = False
        chart.value_axis.has_major_gridlines = True
        chart.value_axis.major_gridlines.format.line.color.rgb = rgb(self.theme.grid)
        chart.value_axis.tick_labels.number_format = axis_format
        chart.value_axis.tick_labels.number_format_is_linked = False
        _no_border(chart)
        return chart

    def _line_chart(self, box: Box, data: ChartData) -> None:
        t: Theme = self.theme
        series: list[tuple[str, tuple[float, ...]]] = list(data.series)
        if data.reference is not None:
            series.append(
                (data.reference_label, tuple(data.reference for _ in data.categories))
            )
        chart: PptxChart = self._add_chart(
            box, XL_CHART_TYPE.LINE_MARKERS, data.categories, series, None
        )
        last: int = len(data.categories) - 1
        for index, line in enumerate(chart.series):
            name, values = series[index]
            is_data: bool = index < len(data.series)
            color: str = t.series[index] if is_data else t.gray
            dash: MSO_LINE = (
                DASH_STYLES[t.line_styles[index % len(t.line_styles)]]
                if is_data
                else MSO_LINE.DASH
            )
            _style_line(
                line,
                color,
                dash,
                XL_MARKER_STYLE.CIRCLE if is_data else XL_MARKER_STYLE.NONE,
            )
            text: str = f"{name} {fmt_value(values[-1], _short(data.unit))}"
            _label(
                line.points[last],
                text,
                XL_LABEL_POSITION.RIGHT,
                Style(t.small_px, color),
            )

    def _diverging_chart(self, box: Box, data: ChartData) -> None:
        t: Theme = self.theme
        name, values = data.series[0]
        order: list[int] = sorted(
            range(len(values)), key=lambda i: values[i], reverse=True
        )
        ranked: tuple[float, ...] = tuple(values[i] for i in order)
        chart: PptxChart = self._add_chart(
            box,
            XL_CHART_TYPE.BAR_CLUSTERED,
            [data.categories[i] for i in order],
            [(name, ranked)],
            None,
        )
        chart.category_axis.reverse_order = True
        chart.category_axis.tick_label_position = XL_TICK_LABEL_POSITION.LOW
        bars: BarSeries = chart.series[0]
        for index, number in enumerate(ranked):
            _fill_point(bars.points[index], t.accent if number >= 0 else t.loss)
            _label(
                bars.points[index],
                fmt_value(number, _short(data.unit)),
                XL_LABEL_POSITION.OUTSIDE_END,
                Style(t.small_px, t.ink, bold=True),
            )

    def _waterfall_chart(self, box: Box, data: ChartData) -> None:
        t: Theme = self.theme
        values: tuple[float, ...] = data.series[0][1]
        spans: list[tuple[float, float]] = _waterfall_spans(values)
        peak: float = max(high for _, high in spans)
        top: float = max(TOP_SHARE * max(values[0], values[-1]), peak / (1 - CAP_SHARE))
        last: int = len(values) - 1
        caps: list[float] = [
            0.0 if i in (0, last) or values[i] < 0 else CAP_SHARE * top
            for i in range(len(values))
        ]
        chart: PptxChart = self._add_chart(
            box,
            XL_CHART_TYPE.COLUMN_STACKED,
            data.categories,
            [
                ("base", [low for low, _ in spans]),
                ("value", [high - low for low, high in spans]),
                ("label", caps),
            ],
            None,
        )
        base, bars, caps_series = chart.series
        for series in (base, caps_series):
            series.format.fill.background()
            series.format.line.fill.background()
        bars.format.line.fill.background()
        chart.plots[0].gap_width = 60
        chart.value_axis.minimum_scale = 0.0
        chart.value_axis.maximum_scale = top
        for index, number in enumerate(values):
            if index in (0, last):
                _fill_point(bars.points[index], t.ink)
                _label(
                    bars.points[index],
                    fmt_value(number, _short(data.unit)),
                    XL_LABEL_POSITION.INSIDE_END,
                    Style(t.small_px, t.paper, bold=True),
                )
            else:
                _fill_point(bars.points[index], t.accent if number >= 0 else t.loss)
                sign: str = "+" if number > 0 else ""
                # An increase is labeled above its bar (on the cap series); a decrease
                # below it, at the top end of the hidden base series.
                holder, position = (
                    (caps_series, XL_LABEL_POSITION.INSIDE_BASE)
                    if number >= 0
                    else (base, XL_LABEL_POSITION.INSIDE_END)
                )
                _label(
                    holder.points[index],
                    sign + fmt_value(number, _short(data.unit)),
                    position,
                    Style(t.small_px, t.ink, bold=True),
                )

    def _stacked_chart(self, box: Box, data: ChartData) -> None:
        t: Theme = self.theme
        chart: PptxChart = self._add_chart(
            box,
            XL_CHART_TYPE.BAR_STACKED_100,
            data.categories,
            data.series,
            XL_LEGEND_POSITION.TOP,
            axis_format="0%",
        )
        chart.category_axis.reverse_order = True
        for index, segment in enumerate(chart.series):
            color: str = t.series[index]
            segment.format.fill.solid()
            segment.format.fill.fore_color.rgb = rgb(color)
            text_color: str = t.white if _luma(color) < DARK_LUMA else t.ink
            for row, number in enumerate(data.series[index][1]):
                if number >= MIN_PERCENT_LABEL:
                    _label(
                        segment.points[row],
                        fmt_value(number, "%"),
                        XL_LABEL_POSITION.CENTER,
                        Style(t.small_px, text_color),
                    )

    def _column_chart(self, box: Box, data: ChartData) -> None:
        t: Theme = self.theme
        chart: PptxChart = self._add_chart(
            box, XL_CHART_TYPE.COLUMN_CLUSTERED, data.categories, data.series, None
        )
        columns: BarSeries = chart.series[0]
        for index, number in enumerate(data.series[0][1]):
            _fill_point(
                columns.points[index], t.highlight if index == data.highlight else t.ink
            )
            _label(
                columns.points[index],
                fmt_value(number, _short(data.unit)),
                XL_LABEL_POSITION.OUTSIDE_END,
                Style(t.small_px, t.ink),
            )

    def _flow_diagram(self, box: Box, flow: Flow) -> None:
        t: Theme = self.theme
        shapes: GroupShapes = _group(self.shapes, "Flow")
        cells: list[Box] = _cells(
            Box(box.x, box.y + (box.h - 160) / 2, box.w, 160),
            len(flow.steps),
            len(flow.steps),
        )
        for index, (label, detail) in enumerate(flow.steps):
            current: bool = index == flow.highlight
            style: Style = Style(
                t.body_px, t.paper if current else t.ink, align=PP_ALIGN.CENTER
            )
            node: Shape = _node(
                shapes,
                MSO_SHAPE.ROUNDED_RECTANGLE,
                cells[index],
                [(Run(label, bold=True),)],
                style,
                t.accent if current else t.panel,
            )
            detail_px: float = fit_px(
                detail, cells[index].w - 16, t.body_px, MIN_LABEL_PX
            )
            _write_para(node.text_frame, (Run(detail),), replace(style, px=detail_px))
        mid: float = cells[0].y + cells[0].h / 2
        for left, right in zip(cells, cells[1:]):
            _connector(
                shapes,
                MSO_CONNECTOR.STRAIGHT,
                left.x + left.w,
                mid,
                right.x,
                mid,
                t.ink,
                arrow=True,
            )

    def _cycle(self, box: Box, cycle: Cycle) -> None:
        # plain shapes only: an outline ellipse, the four nodes on it, and a triangle between each pair
        # pointing clockwise. Curved connectors render unpredictably inside groups in PowerPoint.
        t: Theme = self.theme
        shapes: GroupShapes = _group(self.shapes, "Cycle")
        cx: float = box.x + box.w / 2
        cy: float = box.y + box.h / 2
        rx: float = (box.w - CYCLE_W) / 2
        ry: float = (box.h - CYCLE_H) / 2
        ring: Shape = _shape(
            shapes, MSO_SHAPE.OVAL, Box(cx - rx, cy - ry, 2 * rx, 2 * ry), "", t.ink
        )
        ring.line.width = Pt(1.25)
        for quarter in range(4):
            angle: float = math.radians(-45 + 90 * quarter)
            px: float = cx + rx * math.cos(angle)
            py: float = cy + ry * math.sin(angle)
            dx: float = -rx * math.sin(angle)
            dy: float = ry * math.cos(angle)
            head: Shape = _shape(
                shapes, MSO_SHAPE.ISOSCELES_TRIANGLE, Box(px - 9, py - 9, 18, 18), t.ink
            )
            head.rotation = math.degrees(math.atan2(dx, -dy))
        for spot, label in zip(_cycle_boxes(box), cycle.nodes):
            _node(
                shapes,
                MSO_SHAPE.ROUNDED_RECTANGLE,
                spot,
                [(Run(label),)],
                Style(t.small_px, t.ink, align=PP_ALIGN.CENTER),
                t.panel,
                t.accent,
            )
        _words(
            shapes,
            Box(cx - 120, cy - 16, 240, 32),
            cycle.center,
            Style(t.body_px, t.ink, align=PP_ALIGN.CENTER, bold=True),
        )

    def _matrix(self, box: Box, matrix: Matrix) -> None:
        t: Theme = self.theme
        shapes: GroupShapes = _group(self.shapes, "Matrix")
        grid: Box = Box(box.x, box.y + LABEL_H, box.w, box.h - 2 * LABEL_H)
        for index, cell in enumerate(_cells(grid, 4, 2)):
            body: Style = Style(t.small_px, t.ink)
            node: Shape = _node(
                shapes,
                MSO_SHAPE.RECTANGLE,
                cell,
                [(Run(matrix.quadrants[index], bold=True),)],
                body,
                t.panel,
            )
            for label, quadrant in matrix.items:
                if quadrant == index:
                    px: float = fit_px(label, cell.w - 16, t.small_px, MIN_LABEL_PX)
                    _write_para(
                        node.text_frame, (Run(f"\u2022 {label}"),), replace(body, px=px)
                    )
        axis: Style = Style(t.small_px, t.gray, align=PP_ALIGN.CENTER)
        _words(shapes, Box(box.x, box.y, box.w, LABEL_H), matrix.y_axis, axis)
        _words(
            shapes,
            Box(box.x, box.y + box.h - LABEL_H, box.w, LABEL_H),
            matrix.x_axis,
            axis,
        )

    def _gantt(self, box: Box, gantt: Gantt) -> None:
        t: Theme = self.theme
        shapes: GroupShapes = _group(self.shapes, "Gantt")
        label_w: float = 200.0
        x0: float = box.x + label_w
        slot: float = (box.w - label_w) / len(gantt.periods)
        for index, period in enumerate(gantt.periods):
            _words(
                shapes,
                Box(x0 + index * slot, box.y, slot, LABEL_H),
                period,
                Style(t.small_px, t.gray, align=PP_ALIGN.CENTER),
            )
        lane_top: float = box.y + LABEL_H + 8
        lane_h: float = min(
            64.0, (box.y + box.h - LABEL_H - lane_top) / len(gantt.lanes)
        )
        lanes_bottom: float = lane_top + lane_h * len(gantt.lanes)
        for index in range(
            len(gantt.lanes) + 1
        ):  # header rule, then one rule under each lane
            y: float = lane_top + index * lane_h
            _connector(
                shapes,
                MSO_CONNECTOR.STRAIGHT,
                box.x,
                y,
                box.x + box.w,
                y,
                t.light,
                0.75,
            )
        for index, (name, bars) in enumerate(gantt.lanes):
            self._gantt_lane(
                shapes,
                Box(box.x, lane_top + index * lane_h, box.w, lane_h),
                x0,
                slot,
                name,
                bars,
            )
        for at, label in gantt.milestones:
            cx: float = x0 + at * slot
            rule: Connector = _connector(
                shapes,
                MSO_CONNECTOR.STRAIGHT,
                cx,
                lane_top,
                cx,
                lanes_bottom + 8,
                t.accent,
                1.0,
            )
            rule.line.dash_style = MSO_LINE.DASH
            _shape(
                shapes, MSO_SHAPE.DIAMOND, Box(cx - 9, lane_top - 9, 18, 18), t.accent
            )
            _words(
                shapes,
                Box(cx + 8, lanes_bottom + 10, 220, LABEL_H),
                label,
                Style(t.small_px, t.gray),
            )

    def _gantt_lane(
        self,
        shapes: GroupShapes,
        lane: Box,
        x0: float,
        slot: float,
        name: str,
        bars: Sequence[Bar],
    ) -> None:
        """Draw one lane: its bold name, solid bars for actual work, dashed outlines for planned work."""
        t: Theme = self.theme
        label: Shape = _words(
            shapes,
            Box(lane.x + 8, lane.y, 190, lane.h),
            name,
            Style(t.small_px, t.ink, bold=True),
        )
        label.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        bar_h: float = min(26.0, lane.h * 0.45)
        for bar in bars:
            rect: Box = Box(
                x0 + bar.start * slot,
                lane.y + (lane.h - bar_h) / 2,
                (bar.end - bar.start) * slot,
                bar_h,
            )
            if bar.planned:
                node: Shape = _node(
                    shapes,
                    MSO_SHAPE.ROUNDED_RECTANGLE,
                    rect,
                    [(Run(bar.label),)],
                    Style(t.small_px, t.ink),
                    "",
                    t.accent,
                )
                node.line.dash_style = MSO_LINE.DASH
                node.line.width = Pt(1.25)
            else:
                _node(
                    shapes,
                    MSO_SHAPE.ROUNDED_RECTANGLE,
                    rect,
                    [(Run(bar.label),)],
                    Style(t.small_px, t.paper),
                    t.accent,
                )

    def _tree(self, box: Box, tree: Tree) -> None:
        # root on the left, groups in the middle, leaves on the right, as in the HTML renderer;
        # links are straight horizontal and vertical lines, not elbow connectors
        t: Theme = self.theme
        shapes: GroupShapes = _group(self.shapes, "Tree")
        leaf_h, gap = 42.0, 16.0
        rows_total: int = sum(
            max(1, len(group)) for _, group in tree.children
        )  # a leafless group keeps one row
        top: float = box.y + (box.h - rows_total * leaf_h - (rows_total - 1) * gap) / 2
        cols: tuple[float, float, float] = (
            box.x,
            box.x + box.w * 0.32,
            box.x + box.w * 0.64,
        )
        widths: tuple[float, float, float] = (230.0, 270.0, box.w * 0.36)
        centers: list[float] = []
        row: int = 0
        for label, group in tree.children:
            slots: list[float] = [
                top + (row + i) * (leaf_h + gap) + leaf_h / 2
                for i in range(max(1, len(group)))
            ]
            row += len(slots)
            ys: list[float] = slots[: len(group)]
            mid: float = sum(slots) / len(slots)
            centers.append(mid)
            if ys:
                self._links(shapes, cols[1] + widths[1], mid, cols[2], ys)
            _node(
                shapes,
                MSO_SHAPE.ROUNDED_RECTANGLE,
                Box(cols[1], mid - 21, widths[1], 42),
                [(Run(label, bold=True),)],
                Style(t.small_px, t.ink, align=PP_ALIGN.CENTER),
                t.panel,
                t.accent,
            )
            for leaf, y in zip(group, ys):
                _node(
                    shapes,
                    MSO_SHAPE.ROUNDED_RECTANGLE,
                    Box(cols[2], y - leaf_h / 2, widths[2], leaf_h),
                    [(Run(leaf),)],
                    Style(t.small_px, t.ink, align=PP_ALIGN.CENTER),
                    t.panel,
                    t.accent,
                )
        root_y: float = sum(centers) / len(centers)
        self._links(shapes, cols[0] + widths[0], root_y, cols[1], centers)
        _node(
            shapes,
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Box(cols[0], root_y - 22, widths[0], 44),
            [(Run(tree.root, bold=True),)],
            Style(t.body_px, t.paper, align=PP_ALIGN.CENTER),
            t.accent,
        )

    def _links(
        self,
        shapes: GroupShapes,
        x1: float,
        y1: float,
        x2: float,
        targets: Sequence[float],
    ) -> None:
        """Join one parent edge to several children: out, down the spine, then across to each child."""
        spine: float = (x1 + x2) / 2
        ink: str = self.theme.ink
        _connector(shapes, MSO_CONNECTOR.STRAIGHT, x1, y1, spine, y1, ink, 1.0)
        _connector(
            shapes,
            MSO_CONNECTOR.STRAIGHT,
            spine,
            min(targets),
            spine,
            max(targets),
            ink,
            1.0,
        )
        for y in targets:
            _connector(shapes, MSO_CONNECTOR.STRAIGHT, spine, y, x2, y, ink, 1.0)

    def _timeline(self, box: Box, timeline: Timeline) -> None:
        t: Theme = self.theme
        shapes: GroupShapes = _group(self.shapes, "Timeline")
        slot: float = box.w / len(timeline.nodes)
        mid: float = box.y + box.h / 2
        _connector(
            shapes, MSO_CONNECTOR.STRAIGHT, box.x, mid, box.x + box.w, mid, t.light, 2.0
        )
        for index, (label, when, status) in enumerate(timeline.nodes):
            left: float = box.x + index * slot + 8
            cx: float = box.x + (index + 0.5) * slot
            center: Style = Style(t.small_px, t.ink, align=PP_ALIGN.CENTER, bold=True)
            _paragraphs(
                shapes,
                Box(left, mid - 120, slot - 16, 96),
                [(Run(label, bold=True),)],
                center,
            )
            _marker(shapes, status, Box(cx - 11, mid - 11, 22, 22), t)
            _paragraphs(
                shapes,
                Box(left, mid + 24, slot - 16, 56),
                [(Run(when),), (Run(status),)],
                Style(t.small_px, t.gray, align=PP_ALIGN.CENTER),
            )
        _legend(shapes, box, t)

    def _rule(self, layout: str) -> None:
        regions: dict[str, Region] = LAYOUTS[layout]
        if "takeaways" not in regions:
            return
        area: Region = regions["chart"] if "chart" in regions else regions["tabs"]
        x: float = area.x + area.w + GUTTER / 2
        _connector(
            self.shapes,
            MSO_CONNECTOR.STRAIGHT,
            x,
            BODY_TOP,
            x,
            BODY_BOTTOM,
            self.theme.light,
        )


def _style_line(
    series: LineSeries, color: str, dash: MSO_LINE, marker: XL_MARKER_STYLE
) -> None:
    series.smooth = False
    series.format.line.color.rgb = rgb(color)
    series.format.line.width = Pt(2.0)
    series.format.line.dash_style = dash
    series.marker.style = marker
    series.marker.size = 7
    series.marker.format.fill.solid()
    series.marker.format.fill.fore_color.rgb = rgb(color)


def render_pptx(deck: Deck, theme: Theme) -> bytes:
    """Render a deck to .pptx bytes.

    The file holds one slide per deck slide, one extra slide per tab beyond the first, and the
    backup sources slides at the end.

    Args:
        deck: The validated deck to render.
        theme: Colors, fonts and sizes.

    Returns:
        The .pptx file contents.
    """
    presentation: Any = Presentation()
    presentation.slide_width = Inches(13.333)
    presentation.slide_height = Inches(7.5)
    blank: Any = presentation.slide_layouts[6]
    slides: tuple[Slide, ...] = (*_expand_tabs(deck.slides), *sources_slides(deck))
    for page, spec in enumerate(slides, start=1):
        _Painter(presentation.slides.add_slide(blank), theme).draw(spec, page)
    buffer: BytesIO = BytesIO()
    presentation.save(buffer)
    return _without_timestamps(buffer.getvalue())


_FIXED_ZIP_TIME: tuple[int, int, int, int, int, int] = (1980, 1, 1, 0, 0, 0)
_CORE_DATE: re.Pattern[bytes] = re.compile(
    rb"(<dcterms:(?:created|modified)[^>]*>)[^<]*"
)


def _without_timestamps(package: bytes) -> bytes:
    """Rewrite a zip package with fixed times, so the same deck always gives the same bytes.

    python-pptx stamps each zip entry with the save time, and each embedded chart workbook is
    itself a zip with a creation date in its core properties.
    """
    source: zipfile.ZipFile = zipfile.ZipFile(BytesIO(package))
    out: BytesIO = BytesIO()
    with zipfile.ZipFile(out, "w") as target:
        for info in source.infolist():
            data: bytes = source.read(info)
            if info.filename.endswith(".xlsx"):
                data = _without_timestamps(data)
            elif info.filename == "docProps/core.xml":
                data = _CORE_DATE.sub(rb"\g<1>2000-01-01T00:00:00Z", data)
            fixed: zipfile.ZipInfo = zipfile.ZipInfo(info.filename, _FIXED_ZIP_TIME)
            fixed.compress_type = info.compress_type
            target.writestr(fixed, data)
    return out.getvalue()
