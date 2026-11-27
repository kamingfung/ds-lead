"""Render a Deck as one self-contained HTML file: inline CSS, JavaScript and SVG."""

from __future__ import annotations

import math
import re
from dataclasses import fields, replace
from html import escape
from pathlib import Path

from charts import to_svg
from layouts import GUTTER, LAYOUTS, Region, chrome
from spec import (
    STATUSES,
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
    slide_sources,
    sources_slides,
)
from theme import Theme, fit_px

HERE: Path = Path(__file__).resolve().parent
XMLNS: str = ' xmlns="http://www.w3.org/2000/svg"'
TAB_BAR_H: int = 44
TEXT_ROLES: dict[str, str] = {
    "small": "gray",
    "axis": "gray",
    "inverse": "white",
    "actual": "white",
}


def render_html(deck: Deck, theme: Theme) -> str:
    """Render the deck and its sources slides as one HTML document.

    Args:
        deck: The validated deck to render.
        theme: Theme whose scalar tokens become CSS variables.

    Returns:
        A complete HTML page with inline CSS, JavaScript and SVG.
    """
    slides: tuple[Slide, ...] = deck.slides + sources_slides(deck)
    sections: list[str] = [
        html
        for number, slide in enumerate(slides, 1)
        for html in _sections(slide, number, theme)
    ]
    css: str = _root_vars(theme) + (HERE / "deck.css").read_text(encoding="utf-8")
    script: str = (HERE / "deck.js").read_text(encoding="utf-8")
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            f"<title>{escape(deck.title)}</title>",
            f"<style>\n{css}\n</style>",
            "</head>",
            "<body>",
            '<main class="viewport"><div class="stage" id="stage">'
            + "".join(sections)
            + "</div></main>",
            '<div class="hint" id="hint" aria-live="polite"></div>',
            f"<script>\n{script}\n</script>",
            "</body>",
            "</html>",
            "",
        ]
    )


def _root_vars(theme: Theme) -> str:
    decls: list[str] = []
    for item in fields(theme):
        value: object = getattr(theme, item.name)
        if isinstance(value, tuple):
            continue
        text: str = f"{value}px" if isinstance(value, int) else str(value)
        if "font" in item.name:
            text = f"'{value}'"
        decls.append(f"--{item.name.replace('_', '-')}: {text};")
    return ":root{" + "".join(decls) + "}\n"


def _sections(slide: Slide, number: int, theme: Theme) -> list[str]:
    tabs: Tabs | None = next(
        (v for v in slide.regions.values() if isinstance(v, Tabs)), None
    )
    if tabs is None:
        return [_section(slide, number, theme, "slide", None)]
    copies: list[str] = [
        _section(slide, number, theme, "slide print-only", i)
        for i in range(len(tabs.tabs))
    ]
    return [_section(slide, number, theme, "slide tabbed", None), *copies]


def _section(
    slide: Slide, number: int, theme: Theme, css: str, panel: int | None
) -> str:
    boxes: dict[str, Region] = {**LAYOUTS[slide.layout], **chrome(slide.layout)}
    texts: dict[str, str] = {
        "kicker": slide.kicker,
        "title": slide.title,
        "heading": slide.title,
        "lead": slide.lead,
    }
    parts: list[str] = []
    if "chart" in boxes:
        chart: Region = boxes["chart"]
        x: int = chart.x + chart.w + GUTTER // 2
        parts.append(
            f'<div class="region r-vline" style="left:{x}px;top:{chart.y}px;width:0;height:{chart.h}px"></div>'
        )
    for name, box in boxes.items():
        if name == "footer":
            body: str = _footer(slide, number)
        elif name in slide.regions:
            body = _region(slide, name, box, theme, panel)
        elif texts.get(name):
            body = f"<p>{escape(texts[name])}</p>"
        else:
            continue
        style: str = f"left:{box.x}px;top:{box.y}px;width:{box.w}px;height:{box.h}px"
        parts.append(f'<div class="region r-{name}" style="{style}">{body}</div>')
    return (
        f'<section class="{css}" data-layout="{slide.layout}">'
        + "".join(parts)
        + "</section>"
    )


def _region(
    slide: Slide, name: str, box: Region, theme: Theme, panel: int | None
) -> str:
    """Render one region, with the treatments a layout needs: grid4 cells, numbered references,
    the options3 recommendation strip, and a default "Takeaways" heading on chart and tabs slides."""
    value: object = slide.regions[name]
    if slide.layout == "grid4":
        return _grid4(value)
    if slide.layout == "references" and isinstance(value, Text):
        return "".join(
            _para(p, f"{number}. ") for number, p in enumerate(value.paras, 1)
        )
    if slide.layout == "options3" and name == "recommendation":
        return f'<div class="strip">{_block(_recommendation(value), box.w, box.h, theme, panel)}</div>'
    takeaways: bool = slide.layout.startswith("chart_") or slide.layout == "tabs"
    if (
        takeaways
        and name == "takeaways"
        and isinstance(value, Bullets)
        and not value.heading
    ):
        value = replace(value, heading="Takeaways")
    return _block(value, box.w, box.h, theme, panel)


def _grid4(value: object) -> str:
    """Render up to four Bullets blocks as a 2 x 2 grid: block number, heading on one line, then bullets."""
    blocks: tuple[Bullets, ...] = value if isinstance(value, tuple) else (value,)
    cells: str = "".join(
        f'<div class="cell"><h3><span class="n">{number}</span>{escape(block.heading)}</h3><ul>'
        + "".join(_bullet(item) for item in block.items)
        + "</ul></div>"
        for number, block in enumerate(blocks, 1)
    )
    return f'<div class="grid4">{cells}</div>'


def _recommendation(value: object) -> object:
    """Start the recommendation with a bold "Recommendation:" unless its first paragraph already does."""
    if not isinstance(value, Text) or not value.paras:
        return value
    first: tuple[Run, ...] = value.paras[0].runs
    text: str = "".join(run.text for run in first)
    if text.startswith("Recommendation:"):  # bold the existing lead-in
        lead: Para = Para(
            (Run("Recommendation:", bold=True), Run(text[len("Recommendation:") :]))
        )
        return Text((lead, *value.paras[1:]), value.heading)
    lead = Para((Run("Recommendation:", bold=True), Run(" "), *first))
    return Text((lead, *value.paras[1:]), value.heading)


def _footer(slide: Slide, number: int) -> str:
    """Return the footer: the sources on the left (omitted when empty) and the page number on the right."""
    source: str = slide_sources(slide)
    left: str = f"<span>Source: {escape(source)}</span>" if source else ""
    return f'{left}<span class="pg">{number}</span>'


def _block(value: object, w: int, h: int, theme: Theme, panel: int | None) -> str:
    """Render one region value: a string, one block, or a tuple of blocks side by side."""
    match value:
        case str():
            return f"<p>{escape(value)}</p>"
        case tuple() if all(isinstance(v, (Text, Bullets)) for v in value):
            # prose blocks stack top to bottom in one column, as the pptx renderer flows them
            return (
                '<div class="stack">'
                + "".join(_block(v, w, h, theme, panel) for v in value)
                + "</div>"
            )
        case tuple():
            cell_w: int = (w - GUTTER * (len(value) - 1)) // len(value)
            return (
                '<div class="multi">'
                + "".join(_block(v, cell_w, h, theme, panel) for v in value)
                + "</div>"
            )
        case Tabs():
            return _tabs(value, w, h, theme, panel)
        case Chart():
            return to_svg(value, w, h, theme).replace(XMLNS, "", 1)
        case Num():
            return f'<div class="big">{_num(value, w, 120.0)}</div>'
        case Text():
            head: str = f"<h3>{escape(value.heading)}</h3>" if value.heading else ""
            return head + "".join(_para(p) for p in value.paras)
        case Bullets():
            head = f"<h3>{escape(value.heading)}</h3>" if value.heading else ""
            return head + "<ul>" + "".join(_bullet(i) for i in value.items) + "</ul>"
        case Card():
            return _card(value, w)
        case Tile():
            caption: str = (
                f'<div class="caption">{escape(value.caption)}</div>'
                if value.caption
                else ""
            )
            return (
                f'<div class="tile"><div class="kpi">{_num(value.value, w - 40, 56.0)}</div>'
                f'<div class="label">{escape(value.label)}</div>{caption}</div>'
            )
        case Table():
            return _table(value)
        case Panel():
            return f'<aside class="panel">{escape(value.label)}</aside>'
        case Matrix() | Flow() | Cycle() | Gantt() | Tree() | Timeline():
            return _diagram(value, w, h, theme)
        case _:
            raise TypeError(f"no renderer for {type(value).__name__}")


def _num(num: Num, width: float = 0.0, max_px: float = 0.0) -> str:
    """Return a sourced number span. With max_px, the font size is fitted to width, at most max_px."""
    text: str = num.text()
    style: str = (
        f' style="font-size:{fit_px(text, width, max_px):.1f}px"' if max_px else ""
    )
    return f'<span class="num" title="{escape("Source: " + num.source)}"{style}>{escape(text)}</span>'


def _para(para: Para, prefix: str = "") -> str:
    runs: list[str] = [
        f"<strong>{escape(r.text)}</strong>" if r.bold else escape(r.text)
        for r in para.runs
    ]
    return "<p>" + prefix + "".join(runs) + "</p>"


def _bullet(item: Bullet) -> str:
    lead: str = (
        f"<strong>{escape(item.lead.rstrip(':'))}:</strong> " if item.lead else ""
    )
    note: str = (
        f' <span class="fn">{escape(item.footnote)}</span>' if item.footnote else ""
    )
    return f"<li>{lead}{escape(item.text)}{note}</li>"


def _card(card: Card, w: int) -> str:
    badge: str = (
        f'<span class="badge">{escape(card.badge)}</span>' if card.badge else ""
    )
    metric: str = (
        f'<div class="metric">{_num(card.metric, w - 48, 80.0)}</div>'
        if card.metric is not None
        else ""
    )
    rows: str = (
        "<ul>" + "".join(_bullet(r) for r in card.rows) + "</ul>" if card.rows else ""
    )
    return (
        f'<article class="card"><div class="tag">{escape(card.tag)}{badge}</div>{metric}'
        f"<h3>{escape(card.statement)}</h3><p>{escape(card.body)}</p>{rows}</article>"
    )


def _table(table: Table) -> str:
    head: str = "".join(
        f'<th class="a-{a}">{escape(c)}</th>'
        for c, a in zip(table.columns, table.align)
    )
    body: str = ""
    for row in table.rows:
        cells: str = "".join(
            f'<td class="a-{a}">{_num(c) if isinstance(c, Num) else escape(c)}</td>'
            for c, a in zip(row, table.align)
        )
        body += f"<tr>{cells}</tr>"
    note: str = f'<p class="note">{escape(table.note)}</p>' if table.note else ""
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>{note}"


def _tabs(block: Tabs, w: int, h: int, theme: Theme, panel: int | None) -> str:
    """Render tab buttons and every tab panel, or only the chosen panel for a print copy."""
    active: int = 0 if panel is None else panel
    bar: str = ""
    if panel is None:
        buttons: str = "".join(
            f'<button type="button" role="tab" data-tab="{i}" '
            f'aria-selected="{str(i == active).lower()}">{escape(label)}</button>'
            for i, (label, _) in enumerate(block.tabs)
        )
        bar = f'<div class="tab-bar" role="tablist">{buttons}</div>'
    shown: range | list[int] = range(len(block.tabs)) if panel is None else [panel]
    chart_w: int = (w - 24) // 2
    panels: str = "".join(
        f'<div class="tab-panel{" is-active" if i == active else ""}" role="tabpanel" data-panel="{i}">'
        '<div class="pair">'
        + "".join(
            _block(c, chart_w, h - TAB_BAR_H, theme, None) for c in block.tabs[i][1]
        )
        + "</div></div>"
        for i in shown
    )
    return bar + panels


def _diagram(block: object, w: int, h: int, theme: Theme) -> str:
    """Draw a diagram block as an inline SVG sized to its region, with text fills set as attributes."""
    parts: list[str] = [
        f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img">'
    ]
    match block:
        case Matrix():
            parts += _matrix(block, w, h)
        case Flow():
            parts += _flow(block, w, h)
        case Cycle():
            parts += _cycle(block, w, h)
        case Gantt():
            parts += _gantt(block, w, h)
        case Tree():
            parts += _tree(block, w, h)
        case Timeline():
            parts += _timeline(block, w, h)
    svg: str = "".join(parts) + "</svg>"
    return re.sub(r'fill="@(\w+)"', lambda m: f'fill="{getattr(theme, m[1])}"', svg)


def _text(
    x: float,
    y: float,
    value: str,
    anchor: str = "middle",
    css: str = "",
    size: float = 0.0,
) -> str:
    """Return a text element whose fill attribute is a theme role, resolved by _diagram.

    A size in px is set inline, which overrides the stylesheet's svg text size.
    """
    role: str = next(
        (TEXT_ROLES[token] for token in css.split() if token in TEXT_ROLES), "ink"
    )
    style: str = f' style="font-size:{size:.1f}px"' if size else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" fill="@{role}" '
        f'class="{css}"{style}>{escape(value)}</text>'
    )


def _fit(value: str, width: float, max_px: float) -> tuple[float, list[str]]:
    """Return the font size (max_px at most, 14 px at least) and the lines that wrap value to width."""
    size: float = fit_px(value, width, max_px, 14.0)
    limit: int = max(1, int(width / (0.6 * size)))
    lines: list[str] = []
    for word in value.split():
        if lines and len(lines[-1]) + 1 + len(word) <= limit:
            lines[-1] += " " + word
        else:
            lines.append(word)
    return size, lines or [""]


def _fit_text(
    x: float,
    y: float,
    value: str,
    width: float,
    css: str = "",
    anchor: str = "middle",
    max_px: float = 16.0,
) -> tuple[str, float]:
    """Return wrapped text markup inside width, and the height of the block of lines."""
    size, lines = _fit(value, width, max_px)
    step: float = size * 1.2
    markup: str = "".join(
        _text(x, y + index * step, line, anchor, css, size)
        for index, line in enumerate(lines)
    )
    return markup, step * len(lines)


def _rect(x: float, y: float, w: float, h: float, css: str = "box", rx: int = 8) -> str:
    return f'<rect class="{css}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}"/>'


def _line(x1: float, y1: float, x2: float, y2: float, css: str = "edge") -> str:
    return (
        f'<line class="{css}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>'
    )


def _diamond(x: float, y: float, size: float, css: str) -> str:
    pts: list[tuple[float, float]] = [
        (x, y - size),
        (x + size, y),
        (x, y + size),
        (x - size, y),
    ]
    return (
        f'<polygon class="{css}" points="'
        + " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
        + '"/>'
    )


def _head(x1: float, y1: float, x2: float, y2: float) -> str:
    """Return a filled arrowhead whose tip sits at (x2, y2)."""
    angle: float = math.atan2(y2 - y1, x2 - x1)
    wings: list[str] = [
        f"{x2 - 10 * math.cos(angle + s):.1f},{y2 - 10 * math.sin(angle + s):.1f}"
        for s in (-0.45, 0.45)
    ]
    return f'<polygon class="head" points="{x2:.1f},{y2:.1f} {wings[0]} {wings[1]}"/>'


def _arrow(x1: float, y1: float, x2: float, y2: float) -> str:
    """Return a line with a filled arrowhead whose tip sits at (x2, y2)."""
    return _line(x1, y1, x2, y2) + _head(x1, y1, x2, y2)


def _matrix(block: Matrix, w: int, h: int) -> list[str]:
    pad: float = 64.0
    qw: float = (
        w - 2 * pad
    ) / 2  # quadrants fill the region width, as in the pptx renderer
    qh: float = (h - 2 * pad) / 2
    parts: list[str] = []
    for index, name in enumerate(block.quadrants):
        qx: float = pad + (index % 2) * qw
        qy: float = pad + (index // 2) * qh
        parts.append(
            f'<rect class="quad" x="{qx:.1f}" y="{qy:.1f}" width="{qw:.1f}" height="{qh:.1f}"/>'
        )
        parts.append(_text(qx + 12, qy + 24, name, "start", "small"))
    used: list[float] = [0.0, 0.0, 0.0, 0.0]
    for name, quadrant in block.items:
        cx: float = pad + (quadrant % 2) * qw + 24
        cy: float = pad + (quadrant // 2) * qh + 56 + used[quadrant]
        label, height = _fit_text(cx + 14, cy + 5, name, qw - 52, anchor="start")
        used[quadrant] += max(30.0, height + 8)
        parts.append(f'<circle class="dot" cx="{cx:.1f}" cy="{cy:.1f}" r="6"/>')
        parts.append(label)
    right: float = pad + 2 * qw
    bottom: float = pad + 2 * qh
    parts.append(_arrow(pad, bottom + 24, right, bottom + 24))
    parts.append(_text(pad + qw, bottom + 50, block.x_axis, css="axis"))
    parts.append(_arrow(pad - 24, bottom, pad - 24, pad))
    parts.append(_text(pad - 24, pad - 16, block.y_axis, css="axis"))
    return parts


def _flow(block: Flow, w: int, h: int) -> list[str]:
    count: int = len(block.steps)
    gap: float = 56.0
    box_w: float = (w - gap * (count - 1)) / count
    top: float = (h - 180.0) / 2
    mid: float = top + 90.0
    parts: list[str] = []
    for index, (title, detail) in enumerate(block.steps):
        x: float = index * (box_w + gap)
        css: str = "box hot" if index == block.highlight else "box"
        parts.append(_rect(x, top, box_w, 180.0, css))
        parts.append(
            _fit_text(x + box_w / 2, mid - 8, title, box_w - 16, "strong", max_px=19.0)[
                0
            ]
        )
        parts.append(_fit_text(x + box_w / 2, mid + 22, detail, box_w - 16, "small")[0])
        if index < count - 1:
            parts.append(_arrow(x + box_w + 8, mid, x + box_w + gap - 8, mid))
    return parts


def _cycle(block: Cycle, w: int, h: int) -> list[str]:
    cx: float = w / 2
    cy: float = h / 2
    rx: float = w / 2 - 100.0
    ry: float = h / 2 - 32.0
    angles: list[float] = [-math.pi / 2, 0.0, math.pi / 2, math.pi]
    parts: list[str] = []
    for index in range(4):
        wrap: float = 2 * math.pi if index == 3 else 0.0
        start: float = angles[index] + 0.35
        stop: float = angles[(index + 1) % 4] + wrap - 0.35
        arc: list[tuple[float, float]] = [
            (cx + rx * math.cos(t), cy + ry * math.sin(t))
            for t in (start + (stop - start) * k / 29 for k in range(30))
        ]
        pts: str = " ".join(f"{px:.1f},{py:.1f}" for px, py in arc)
        parts.append(f'<polyline class="edge" points="{pts}"/>')
        parts.append(_head(*arc[-2], *arc[-1]))
    for angle, name in zip(angles, block.nodes):
        nx: float = cx + rx * math.cos(angle)
        ny: float = cy + ry * math.sin(angle)
        parts.append(_rect(nx - 100, ny - 32, 200, 64))
        parts.append(_text(nx, ny + 5, name))
    parts.append(_text(cx, cy + 5, block.center, css="strong"))
    return parts


def _gantt(block: Gantt, w: int, h: int) -> list[str]:
    count: int = len(block.periods)
    span: float = w - 216.0

    def at(value: float) -> float:
        return 200.0 + value / count * span

    parts: list[str] = []
    for index, period in enumerate(block.periods):
        parts.append(_text(at(index + 0.5), 24, period, css="small"))
    parts.append(_line(0, 40.0, w, 40.0, "grid"))
    for lane, (name, bars) in enumerate(block.lanes):
        top: float = 40.0 + lane * 56.0
        mid: float = top + 28.0
        parts.append(_text(8, mid + 5, name, "start", "strong"))
        parts.append(_line(0, top + 56.0, w, top + 56.0, "grid"))
        for bar in bars:
            kind: str = "planned" if bar.planned else "actual"
            x: float = at(bar.start)
            parts.append(_rect(x, mid - 11, at(bar.end) - x, 22, f"bar {kind}", 4))
            parts.append(_text(x + 8, mid + 5, bar.label, "start", f"inside {kind}"))
    for position, name in block.milestones:
        mark: float = at(position)
        parts.append(_line(mark, 40.0, mark, h - 24, "milestone"))
        parts.append(_diamond(mark, 40.0, 8, "diamond"))
        parts.append(_text(mark + 10, h - 6, name, "start", "small"))
    return parts


def _tree(block: Tree, w: int, h: int) -> list[str]:
    spans: list[int] = [max(len(leaves), 1) for _, leaves in block.children]
    starts: list[int] = [sum(spans[:i]) for i in range(len(spans))]
    top: float = (h - sum(spans) * 56.0) / 2
    child_ys: list[float] = [top + (s + n / 2) * 56.0 for s, n in zip(starts, spans)]
    root_y: float = (child_ys[0] + child_ys[-1]) / 2 if child_ys else h / 2
    parts: list[str] = [_rect(8, root_y - 20, 220, 40, "box root")]
    parts.append(_text(118, root_y + 5, block.root, css="strong inverse"))
    for (name, leaves), start, child_y in zip(block.children, starts, child_ys):
        parts.append(_elbow(228, root_y, 290, child_y))
        parts.append(_rect(290, child_y - 20, 260, 40))
        parts.append(_text(420, child_y + 5, name, css="strong"))
        for slot, leaf in enumerate(leaves):
            leaf_y: float = top + (start + slot + 0.5) * 56.0
            parts.append(_elbow(550, child_y, 640, leaf_y))
            parts.append(_rect(640, leaf_y - 20, 300, 40))
            parts.append(_text(790, leaf_y + 5, leaf))
    return parts


def _elbow(x1: float, y1: float, x2: float, y2: float) -> str:
    mid: float = (x1 + x2) / 2
    return f'<path class="edge" d="M{x1:.1f} {y1:.1f} H{mid:.1f} V{y2:.1f} H{x2:.1f}"/>'


def _timeline(block: Timeline, w: int, h: int) -> list[str]:
    step: float = w / len(block.nodes)
    mid: float = h / 2
    parts: list[str] = [_line(step / 2, mid, w - step / 2, mid)]
    for index, (date, name, status) in enumerate(block.nodes):
        x: float = (index + 0.5) * step
        date_y, name_y = (
            (mid - 82, mid - 54) if index % 2 == 0 else (mid + 60, mid + 88)
        )
        parts.append(_icon(x, mid, status))
        parts.append(_text(x, date_y, date, css="small"))
        parts.append(_text(x, name_y, name, css="strong"))
    for index, status in enumerate(STATUSES):
        legend_x: float = w - 360.0 + 120.0 * index
        parts.append(_icon(legend_x, h - 16.0, status))
        parts.append(
            _text(legend_x + 24, h - 11.0, status.capitalize(), "start", "small")
        )
    return parts


def _icon(x: float, y: float, status: str) -> str:
    """Draw a status marker from palette shapes: a sage circle with a white check, a loss square
    with a white cross, or an ochre diamond with two white bars."""
    if status == "kept":
        shape: str = (
            f'<circle class="icon kept" cx="{x:.1f}" cy="{y:.1f}" r="16"/>'
            f'<polyline class="mark" points="{x - 6:.1f},{y:.1f} {x - 2:.1f},{y + 4:.1f} {x + 6:.1f},{y - 4:.1f}"/>'
        )
    elif status == "dropped":
        shape = (
            _rect(x - 16, y - 16, 32, 32, "icon dropped", 0)
            + _line(x - 6, y - 6, x + 6, y + 6, "mark")
            + _line(x + 6, y - 6, x - 6, y + 6, "mark")
        )
    else:
        shape = (
            _diamond(x, y, 21, "icon open")
            + _rect(x - 6, y - 8, 4, 16, "mark-fill", 0)
            + _rect(x + 2, y - 8, 4, 16, "mark-fill", 0)
        )
    return f"<g><title>{escape(status)}</title>{shape}</g>"
