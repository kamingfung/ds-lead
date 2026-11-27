# Visualization Guide

## Colorblind Safety and Encoding

- The palette is a hand-picked fall palette. Its hue roles follow the eight Okabe-Ito colors, which stay distinct for readers with color-vision deficiency. Only yellow and black are Okabe-Ito values; [README.md](../README.md) maps the others and lists the measured color distances.
- `simulate_vision(hex_color, kind)` shows a color as a viewer with `deutan`, `protan` or `tritan` vision sees it. It applies the Machado matrices at full severity to linear sRGB. `show_all_palettes()` draws the three simulations of the categorical palette.
- Every color needs a second cue: a marker shape, a line style, a direct label or a bold weight.

## Choose the Chart Form

| Comparison type           | Recipe                                                                                    |
| ------------------------- | ----------------------------------------------------------------------------------------- |
| Change over time          | `example_lines`, `example_target_line`, `example_fan_chart`, `example_annotated_timeline` |
| Ranking                   | `example_ranked_dots`, `example_highlight_bar`                                            |
| Part to whole             | `example_stacked_columns`                                                                 |
| Bridge between two totals | `example_waterfall`                                                                       |
| Before and after          | `example_slope`, `example_dumbbell`                                                       |
| Gain and loss             | `example_diverging_bars`                                                                  |
| Distribution              | `example_histogram`                                                                       |
| Relationship              | `example_scatter_outlier`                                                                 |
| Several groups            | `example_small_multiples`, `example_grouped_columns`                                      |

## Diagrams as Text

- For a flow or a structure in a Markdown doc, write a Mermaid diagram in a fenced `mermaid` block instead of an image.
- Keep each diagram to one idea, such as one flow or one hierarchy.
