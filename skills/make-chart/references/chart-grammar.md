# Chart Grammar: Recipes and Native PowerPoint Charts

The chart grammar is the set of chart kinds that a native, editable PowerPoint chart can draw: a chart whose "Edit Data" opens its embedded Excel workbook. The deck kit lists its kinds in [`chart.schema.json`](../../make-deck/template/chart.schema.json), a language-neutral JSON Schema for one chart and its `ChartData`. Tests fail when that schema, the HTML renderer and the pptx renderer disagree.

Design a new deck chart kind backward from this grammar. First find its native pptx route. Then add it to the schema, the HTML renderer and the pptx renderer in one change.

The table maps each `chart_style.py` recipe to its deck kind and its pptx route. A **direct** route uses one python-pptx chart type as it is. A **trick** route bends a chart type, such as a hidden series. Routes for recipes without a deck kind are planned, not built.

| Recipe                       | Deck kind                 | Native pptx route                                                             |
| ---------------------------- | ------------------------- | ----------------------------------------------------------------------------- |
| `example_lines`              | `line`                    | `LINE_MARKERS`, direct                                                        |
| `example_waterfall`          | `waterfall`               | `COLUMN_STACKED` with a hidden base series, trick                             |
| `example_diverging_bars`     | `diverging_bar`           | `BAR_CLUSTERED`, direct                                                       |
| `example_stacked_columns`    | `stacked100`, as bars     | `BAR_STACKED_100`, direct                                                     |
| `example_grouped_columns`    | `column`, one series only | `COLUMN_CLUSTERED`, direct                                                    |
| `example_highlight_bar`      | None                      | `BAR_CLUSTERED` with one point recolored, direct                              |
| `example_scatter_outlier`    | None                      | `XY_SCATTER`, direct                                                          |
| `example_histogram`          | None                      | `COLUMN_CLUSTERED` of pre-binned counts with no gap, direct                   |
| `example_slope`              | None                      | `LINE_MARKERS` over two categories, direct                                    |
| `example_ranked_dots`        | None                      | `XY_SCATTER`, direct                                                          |
| `example_small_multiples`    | None                      | One native chart per panel, direct                                            |
| `example_dumbbell`           | None                      | `XY_SCATTER` with one line per row, trick                                     |
| `example_annotated_timeline` | None                      | `LINE_MARKERS` plus text boxes, trick                                         |
| `example_fan_chart`          | None                      | `AREA_STACKED` bands, trick; the median line needs a combo chart (unverified) |
| `example_target_line`        | None                      | Column plus line combo chart; python-pptx has no combo API (unverified)       |

python-pptx 1.0.2 writes only the classic chart types. It cannot write the Office 2016 chart types (waterfall, histogram, box and whisker, treemap), so those stay tricks.
