---
name: make-deck
description: "deck formatting and creation standards for any slide deck: a title-only outline first, action titles, 3 to 5 key numbers up front, the right visual for each relationship, a source for every number, and a three-pass review; when data is involved, build the deck from data with the kit, which writes HTML and a native, editable .pptx from one spec."
---

# Make a Deck

The deck kit lives in `template/`. It takes one `Deck` spec, places each slide in one of 24 layouts on a 1280 × 720 canvas, and writes an HTML deck and a native `.pptx`. Two renderers place the same boxes, so the HTML and the pptx match. Layout names and regions are in [page-types.md](page-types.md). Colors, type and chart rules are in [style.md](style.md).

## When to Use

- Use this skill for any slide deck: a readout, a workshop or an executive summary.
- Build the deck from data when it carries numbers. Every number then comes from a `Num` with a source.
- Write HTML first. Add a `.pptx` when someone asks for it. Both come from the same spec.

## Step 1: Outline Titles First

1. Write every slide title as a full-sentence claim before you write any body text.
2. Read the titles alone. Check that they tell the story in order.
3. Pick a layout for each slide with the table in Step 2.

## Step 2: Pick the Layout by Relationship

| Message                             | Layout                                                                | Chart or block             |
| ----------------------------------- | --------------------------------------------------------------------- | -------------------------- |
| Change over time                    | `chart_3to1`                                                          | `line`                     |
| Bridge between two totals           | `chart_2to1`                                                          | `waterfall`                |
| Part of a whole                     | `chart_1to1`                                                          | `stacked100`               |
| Gain and loss by item               | `chart_table`                                                         | `diverging_bar`            |
| Scenarios                           | `tabs`                                                                | `column` (two per tab)     |
| One headline figure                 | `big_number`                                                          | `Num`                      |
| 3 or 4 headline figures             | `kpi_split` or `cards3`                                               | `Tile` or `Card`           |
| Detail                              | `table`                                                               | `Table`                    |
| Prioritization                      | `matrix`                                                              | `Matrix`                   |
| A process                           | `flow`                                                                | `Flow`                     |
| A loop                              | `cycle`                                                               | `Cycle`                    |
| A plan                              | `gantt`                                                               | `Gantt`                    |
| Drivers                             | `tree`                                                                | `Tree`                     |
| History of decisions                | `timeline`                                                            | `Timeline`                 |
| Options                             | `options3`                                                            | `Card` (three)             |
| Workshop question                   | `discussion`                                                          | `Bullets` and `Panel`      |
| Opening, divider, prose, references | `cover`, `section`, `brief`, `two_col`, `grid4`, `note`, `references` | Text and bullets, no chart |

## Step 3: Build From Data

1. Compute each number as `Num(value, fmt, source)`. Set `fmt` to a Python format spec such as `,.0f` or `+.1%`, with an optional unit after a space. Set `source` to a query id, run id or file, with its pull date.
2. Build each slide as `Slide(layout, title, kicker=..., lead=..., regions={...})`. Name the regions as [page-types.md](page-types.md) lists them.
3. Collect the slides in `Deck(title, short_title, as_of, slides)`.
4. Call `validate(deck)`. It raises `ValueError` and names the slide number when a region has the wrong block type, too many items or no required block.
5. Write the string from `render_html(deck, HOUSE)` to an `.html` file.
6. Write the bytes from `render_pptx(deck, HOUSE)` to a `.pptx` file. Do this only when someone asks for a pptx.
7. Print the PDF with the headless Chrome command in `examples/deck-gallery/README.md`.

The footer source line and the `Backup · Sources` slides come from the `Num` sources. You do not write them by hand. To see every layout, run `python3 gallery.py <dir>` from `template/` with `PYTHONPATH=.`. The command writes a sample deck with one slide per layout.

## Two Modes

- **Readout**: a result for decision-makers. Use the full anatomy, with 3 to 5 key numbers up front.
- **Workshop**: a working session. Lead with graphics: `discussion`, `flow`, `cycle`, `timeline` and `options3`. Use one headline number at most. Question titles are allowed.

## Content Rules

- The title states the point in a full sentence.
- On chart layouts, the lead line is the chart title: metric, unit and window. The lead line is bold.
- Give each slide one message.
- Use at most 4 bullets per card or panel.
- Every number is a `Num`. Never type a number by hand.
- `Num.text()` writes a true minus sign (−) for negative values. Do not type a hyphen for a negative number.
- Name each term at its first use.

## Review in Three Passes

1. Story: read the titles alone. They should read as the summary of the deck.
2. Numbers: check that every figure has a source. The `Backup · Sources` slides list each one.
3. Design: open the HTML and the pptx. Check that no text overflows, that labels are clear and that charts render in PowerPoint.

## Files

| File                | Holds                                                                                                                                         |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `theme.py`          | `Theme` tokens (colors, fonts, type sizes), the `HOUSE` theme and `fit_px`.                                                                   |
| `spec.py`           | `Num`, the blocks, `Slide`, `Deck`, `validate` and the `Backup · Sources` slides.                                                             |
| `layouts.py`        | The canvas, the header and footer boxes and the 24 layouts in `LAYOUTS`.                                                                      |
| `charts.py`         | Chart data and the five SVG chart kinds: `line`, `column`, `waterfall`, `diverging_bar` and `stacked100`.                                     |
| `chart.schema.json` | The chart grammar as a JSON Schema: each chart kind, its native pptx type, and the `ChartData` fields. Tests keep it equal to both renderers. |
| `render_html.py`    | `render_html(deck, theme)`, which returns one self-contained HTML page.                                                                       |
| `deck.css`          | Styles for the HTML deck, including the print styles.                                                                                         |
| `deck.js`           | Keyboard, swipe and tab navigation for the HTML deck.                                                                                         |
| `render_pptx.py`    | `render_pptx(deck, theme)`, which returns the bytes of a native `.pptx`.                                                                      |
| `gallery.py`        | The sample deck with one slide per layout, and the command that writes it.                                                                    |

The pptx renderer needs `python-pptx`, which installs `lxml` with it. The tests live in `template/tests/`.
