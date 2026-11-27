---
name: make-chart
description: "Use when making or restyling a matplotlib or seaborn figure, or changing chart colors; it gives a style setter, a chart header, axis rules and 15 recipes on a colorblind-safe palette."
author: Ka Ming Fung
license: MIT
---

# Make a Chart

## Steps

1. Call `set_chart_style(context)` with one of four contexts: `paper`, `notebook`, `talk` or `poster`.
2. Copy the nearest recipe from `chart_style.py` and put your data in it. The 15 recipes are `example_lines`, `example_highlight_bar`, `example_scatter_outlier`, `example_waterfall`, `example_target_line`, `example_dumbbell`, `example_histogram`, `example_grouped_columns`, `example_fan_chart`, `example_small_multiples`, `example_slope`, `example_ranked_dots`, `example_diverging_bars`, `example_stacked_columns` and `example_annotated_timeline`.
3. Write the header with `chart_header(ax, title, subtitle, source)`. Make the title a bold claim. Put the metric, units, time window and encoding rules in the subtitle. Start the source with `Source: `.
4. Use palette names, not hex codes. Give the focal series and gains to indigo, losses to rust, further series to ochre and burnt-sienna, and baseline or peer series to light grey.
5. Reserve sky for the one mark that carries the message, such as a highlighted bar or an outlier.
6. Hide the value axis of a bar chart that labels each bar: call `hide_value_axis(ax)`. It hides the axis line, ticks and gridlines and keeps the zero baseline.
7. Leave gridlines off on scatter, waterfall and dot charts. Give a dumbbell chart one light horizontal guide line per row, keep the value axis on a diverging bar chart, and on other charts add only the gridlines readers need with `ax.grid(True, axis="y")`.
8. Align time axes. Set explicit month or period ticks on each panel. Call `align_headers(fig)` on a grid of charts so the subtitles and source lines line up.
9. Check label clearance. Place direct labels in open space, and widen the axis limits for labels that sit outside the data.
10. Save the figure, open the PNG, and look for overlapping labels, clipped text and marks hidden under labels.

## Rules

- Write negative numbers with a true minus sign (U+2212). `label_bars` and `direct_label` convert a leading hyphen for you.
- In a waterfall, label an increase above its bar and a decrease below it.
- Start the value axis of a bar chart at zero. `highlight_bars` does this for bars that are all non-negative.
- If a line chart does not start at zero, say so in the subtitle.
- Never use color as the only cue. Pair it with a marker shape, a line style or a direct label.
- Make one message per chart. The title states that message in one sentence.

## Reference

- Functions: the docstring at the top of [`chart_style.py`](chart_style.py) lists every public function and what it does.
- Palette: [`palette.css`](palette.css) holds the color tokens; [README.md](README.md) gives its provenance and the steps to change it. Set `CHART_STYLE_PALETTE` to another file with the same token names before you import `chart_style`.
- Tests: run `pytest test_chart_style.py` from `skills/make-chart/`. The tests render every recipe.
- Rendered recipes: [`examples/make-chart/`](../../examples/make-chart/).
- Chart choice and encoding: [references/visualization.md](references/visualization.md).

## Gotchas

- Labels placed at fixed coordinates can collide when new data moves the marks. Render the PNG and move the label with `dy`, `xytext` or the axis limits.
- Do not keep a four-sided box with a full grid on every plot. The style already hides the top and right spines, so hide the left spine or drop gridlines when they add nothing.
