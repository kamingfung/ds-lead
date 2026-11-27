# Page Types

The canvas is 1280 × 720 CSS pixels. Side margins are 56 px, and the gutter between columns is 32 px. The header holds the kicker (y 28, 22 px tall), the title (y 52, 84 px tall) and the lead line (y 140, 40 px tall). The body runs from y 192 to y 660. The footer sits at y 676 and is 24 px tall. Every box in the table below comes from `layouts.py`. "Items" counts bullets. "Blocks" counts top-level blocks.

| Layout        | Use it for                                                                  | Regions                                                                                        |
| ------------- | --------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `cover`       | Opening slide on a dark ground                                              | `title` (text, optional), `subtitle` (Text), `meta` (Text)                                     |
| `section`     | Divider between parts of a deck, with the footer only                       | `heading` (text, optional), `lead` (Text)                                                      |
| `cards3`      | Three parallel findings, each with a metric                                 | `cards` (up to 3 Card blocks)                                                                  |
| `brief`       | Prose or up to three bullets, with no chart                                 | `body` (Text or Bullets, up to 3 bullet items)                                                 |
| `kpi_split`   | Four headline tiles above two bullet lists                                  | `tiles` (up to 4 Tile blocks), `left` and `right` (Bullets, up to 4 items each), `note` (Text) |
| `two_col`     | Two bullet lists side by side, such as pros and cons                        | `left` and `right` (Bullets, up to 4 items each), `summary` (Text, optional)                   |
| `big_number`  | One headline figure with a caption                                          | `number` (Num), `caption` (Text), `note` (Text)                                                |
| `table`       | Detail in one table                                                         | `table` (Table), `note` (Text)                                                                 |
| `grid4`       | Four short bullet blocks in a 2 by 2 grid                                   | `blocks` (up to 4 Bullets blocks)                                                              |
| `chart_3to1`  | A chart with takeaways, three quarters for the chart (use `line`)           | `chart` (Chart), `takeaways` (Bullets, up to 3 items)                                          |
| `chart_2to1`  | A chart with takeaways, two thirds for the chart (use `waterfall`)          | `chart` (Chart), `takeaways` (Bullets, up to 4 items)                                          |
| `chart_1to1`  | A chart with takeaways, half for each (use `stacked100`)                    | `chart` (Chart), `takeaways` (Bullets, up to 3 items)                                          |
| `chart_table` | A chart beside a table, such as gain and loss by item (use `diverging_bar`) | `chart` (Chart), `table` (Table), `note` (Text)                                                |
| `note`        | Prose with a heading, and a print-only note                                 | `heading` (Text), `body` (Text), `print_note` (Text)                                           |
| `matrix`      | Items placed on two axes in four quadrants, for prioritization              | `diagram` (Matrix)                                                                             |
| `flow`        | A process of 3 to 6 steps, with a note                                      | `diagram` (Flow), `note` (Text)                                                                |
| `cycle`       | A loop of four nodes around a center                                        | `diagram` (Cycle)                                                                              |
| `gantt`       | A plan with up to 5 lanes and 2 milestones, with a legend                   | `diagram` (Gantt), `legend` (Text)                                                             |
| `tree`        | Drivers under one root                                                      | `diagram` (Tree)                                                                               |
| `timeline`    | History of decisions, up to 6 nodes, each kept, dropped or open             | `diagram` (Timeline)                                                                           |
| `options3`    | Three options, with a recommendation strip below                            | `cards` (up to 3 Card blocks), `recommendation` (Text)                                         |
| `discussion`  | Workshop prompts with a notes panel for the room                            | `prompts` (Bullets, up to 3 items), `notes` (Panel)                                            |
| `tabs`        | Scenarios, one per tab, each tab with two charts                            | `tabs` (Tabs, two Chart blocks per tab), `takeaways` (Bullets, up to 3 items), `note` (Text)   |
| `references`  | A numbered list of sources                                                  | `body` (Text, one paragraph per source)                                                        |

## Slide Anatomy

- Kicker: a short label above the title, in 16 px bold accent. It is optional.
- Title: the claim, in 32 px bold ink. Keep it to two lines in the title box. Cover and section titles use the same field, at display size.
- Lead: one line under the title, in 19 px ink. On chart and tabs layouts, the lead is bold and names the chart: metric, unit and window.
- Body: the regions of the layout, inside y 192 to 660.
- Footer: a rule, then the source line on the left and the page number on the right. The cover has no footer. A section has only the page number.

## Footer and Backup

The source line lists the distinct `Num` sources on the slide, in the order they first appear, joined by semicolons. A slide with no `Num` has no source text.

The deck ends with `Backup · Sources` slides. Each one holds up to 9 rows of slide number, item, value and source, and each shows the note "Values as of" followed by the deck's `as_of` value. The pptx also gets one slide per tab, titled with the tab name after a middle dot.
