# Chart Plotting Examples

Rendered outputs from [`skills/make-chart/chart_style.py`](../../skills/make-chart/chart_style.py) using the Fall palette in [`skills/make-chart/palette.css`](../../skills/make-chart/palette.css).

- [`chart_palettes.png`](chart_palettes.png) — `show_all_palettes()`: semantic tokens, `CATEGORICAL`, `LIGHT_PALETTE`, `SEQUENTIAL`, `DIVERGING`, and CVD/grayscale simulations.
- [`chart_examples.png`](chart_examples.png) — `create_example_plots()`: 15 chart recipes (line, highlight bar, scatter, waterfall, shaded target, dumbbell, histogram, grouped bar, forecast fan, small multiples, slopegraph, dot plot, diverging bar, stacked bar, event-annotated line).
- [`chart_contexts.png`](chart_contexts.png) — `create_context_demo()`: font and stroke scaling across `paper`, `notebook`, `slide`, and `poster`.

## Regenerate

```bash
cd examples/make-chart
uv run --with matplotlib --with seaborn --with numpy python ../../skills/make-chart/chart_style.py
```
