# Style

Every color, size and chart rule below comes from `theme.py`, `charts.py`, `render_html.py`, `render_pptx.py` and `deck.css`. Where the HTML and the pptx differ, the text says so.

## Colors

| Token       | Hex       | Use                                                                                                                                   |
| ----------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `ink`       | `#3b1a18` | Body text, the first chart series, total bars in a waterfall, zero lines and the cover ground.                                        |
| `accent`    | `#1d4a62` | Kickers, headings, metrics, gain bars, the second series, the fill of a highlighted flow step and of a tree root.                     |
| `loss`      | `#a04b2d` | Loss bars in waterfall and diverging charts, and the dropped-status marker.                                                           |
| `ochre`     | `#d69a2e` | The third chart series and the open-status marker.                                                                                    |
| `sage`      | `#95a87f` | The fourth chart series and the kept-status marker.                                                                                   |
| `sienna`    | `#6c2b27` | The fifth series color. No chart reaches it: line takes up to three series and stacked100 takes up to four.                           |
| `highlight` | `#7fb3cc` | The highlighted column in a column chart. The pptx cover also uses it as the accent color.                                            |
| `light`     | `#c6beb3` | Footer rule, waterfall connector lines, diagram connectors, the dashed outline of a panel, and dimmed cover text.                     |
| `panel`     | `#f2ece1` | Fill for cards in `cards3` and `options3`, the `Panel` block, diagram boxes, matrix quadrants, pptx table headers and pptx KPI tiles. |
| `grid`      | `#e5ddd0` | Chart gridlines and table row rules.                                                                                                  |
| `gray`      | `#767676` | Source line, page number, captions, axis text and the reference line.                                                                 |
| `paper`     | `#fbf8f3` | Slide background, text inside total bars, and text on accent fills (flow step, tree root, Gantt bars).                                |
| `tint`      | `#e6eff3` | The recommendation strip under `options3`, and the badge on a card.                                                                   |
| `loss_tint` | `#dfb8a6` | Not used. No renderer reads this token.                                                                                               |
| `white`     | `#ffffff` | KPI tile fill in HTML, and white labels on dark bars and dark stacked segments.                                                       |
| `surround`  | `#29221e` | Background behind the HTML stage when the window is not 16:9.                                                                         |

## Type

Headings and body use Arial. The pptx sets numbers in table cells in Consolas. The theme also names Menlo for mono text, but no CSS rule uses it, so HTML numbers stay in Arial with tabular figures.

Sizes are in CSS pixels. In pptx, each pixel is 0.75 points (`points()`), so a 19 px body line is 14.25 pt.

| Role        | Size         | Notes                                                 |
| ----------- | ------------ | ----------------------------------------------------- |
| Display     | 64 px        | Cover and section headings.                           |
| Title       | 32 px        | Bold. Two lines at most.                              |
| Subheading  | 24 px        | Card, panel and note headings.                        |
| Body        | 19 px        | Bullets, text and the lead line.                      |
| Small       | 16 px        | Kicker, source line, page number and chart axis text. |
| Big number  | up to 120 px | `big_number`, sized by `fit_px` to the width.         |
| Card metric | 80 px        | `cards3` and `options3`.                              |
| Tile value  | up to 56 px  | `kpi_split`, sized by `fit_px` to the tile width.     |

`fit_px(text, width_px, max_px)` returns the largest size, up to `max_px`, at which bold Arial text fits one line. It assumes 0.6 em per glyph and never goes below `min_px` (24 px by default). This is an estimate, so leave a margin.

## Charts

- Series use the colors in order: `ink`, `accent`, `ochre`, `sage` and `sienna`.
- Line charts add a second encoding. Series 1 is solid, series 2 dashed and series 3 dotted. Each point has a circle marker, and each series ends in a label.
- A gray dashed line marks a reference, such as a target, with its label.
- A waterfall shows the start and end totals as ink bars, with each value inside in paper. Each change bar is `accent` when positive and `loss` when negative. Its signed value sits above the bar for an increase and below it for a decrease.
- Put the unit in the lead line, which is the chart title. Value labels carry a unit only when it is `%` or three characters or fewer.
- HTML line charts also print the unit above the plot. The pptx does not.
- A line chart whose axis does not start at zero says so. The HTML prints "Axis does not start at zero" under the plot. The pptx prints no such note.

## Cover and Panels

- The cover sits on an ink ground. Its text switches to paper, and its meta line switches to `light`.
- Cards in `cards3` and `options3` use the panel fill with no border. The `Panel` block uses the panel fill with a dashed light outline.
- The recommendation under `options3` sits on a tint strip with 16 px padding. Its lead-in is bold.

## Interactivity

- Right, Down, Page Down and Space go to the next slide. Left, Up and Page Up go back.
- Number keys 1 to 9 select a tab on the current slide. A click on a tab also selects it.
- A swipe of 40 px or more moves to the next or previous slide.
- Printing the HTML gives one page per slide, sized 1280 × 720 px. A tabbed slide prints one page per tab.
