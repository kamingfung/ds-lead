# Decisions

This file records the repository-wide decisions: architecture, platform and data contracts. Each entry gives the date, what was chosen, what was considered and rejected with the reason, and one evidence line. The format follows the `session` skill (`skills/session/SKILL.md`, section 4).

Rules:

- Append new entries at the end. Never edit a past entry.
- To reverse a decision, append an entry that names the date and title of the one it replaces.
- Record the why. The diff shows the what.

## 2026-11-27: Deck charts stay native PowerPoint charts, drawn by their own renderers

**Chosen.** The deck keeps two chart renderers: hand-written SVG in `charts.py` for HTML, and native python-pptx charts in `render_pptx.py` for pptx. `make-chart` (matplotlib) stays separate, for notebooks and reports. A native chart keeps PowerPoint's "Edit Data", which opens the chart's embedded Excel workbook. Users value that.

**Considered and rejected.**

| Option                                                            | Why it was rejected                                                                                                                                                                                                                  |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Draw deck charts with `make-chart` and embed them as SVG          | python-pptx 1.0.2 cannot add an SVG picture: `add_picture` raises `UnidentifiedImageError`. Any picture also loses "Edit Data". The 15 recipes are demos with hard-coded data, not functions that take `ChartData`.                  |
| Add seaborn to `make-chart`                                       | It is already supported: `set_chart_seaborn_theme` in `skills/make-chart/chart_style.py`.                                                                                                                                            |
| Write the SVG picture XML (SVGBlip) by hand on top of python-pptx | The result is still a picture, so "Edit Data" is still lost.                                                                                                                                                                         |
| Build charts with Python in Excel, then embed them                | It runs only in Microsoft's cloud, needs internet, and returns plots as images, not native charts. The kit already writes the workbook itself: python-pptx embeds `ppt/embeddings/Microsoft_Excel_Sheet1.xlsx` in each chart.        |
| Rewrite in JS (PptxGenJS), Rust (ppt-rs, deckmint) or .NET        | No free library writes more native chart types than python-pptx. Only paid .NET libraries (DevExpress, Syncfusion, Aspose) write the Office 2016 waterfall. `make-chart` stays in Python, so a rewrite gives two languages, not one. |
| Add Plotly as a third chart tool                                  | It adds hover and zoom, which matter in exploration, not in decks or reports. It needs a large JS bundle in every page and a third palette to keep in sync, and it writes no native pptx charts.                                     |

**Evidence.** https://github.com/kamingfung/ds-lead/pull/14 (Why section); [Python in Excel introduction](https://support.microsoft.com/en-us/office/introduction-to-python-in-excel-55643c2e-ff56-4168-b1ce-9428c8308545).

## 2026-11-27: The deck has the five gallery chart kinds, and tests guard them

**Chosen.** The deck draws five chart kinds: `line`, `column`, `waterfall`, `diverging_bar` and `stacked100`. That is enough for the general case. Tests fail when the SVG renderers (`RENDERERS` in `charts.py`), the chart labels (`KIND_LABELS`) and the kinds drawn by the pptx test deck differ.

The test for a new kind: would a person change its numbers by hand in PowerPoint?

- Yes: it can be a native chart kind.
- Its numbers are computed, such as histogram bins or model quantiles: it is a picture.

**Considered and rejected.**

| Option                                                                                                                                   | Why it was rejected                                                                                                                                   |
| ---------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Map all 15 `make-chart` recipes to native pptx routes (`chart-grammar.md`, drafted in PR #14 and deleted before merge)                   | It planned 10 kinds nobody needs. Two routes depend on combo charts, which python-pptx has no API for.                                                |
| A "native but fragile" group: waterfall-style tricks, dumbbells, drawn target lines                                                      | Edits in PowerPoint break them. The waterfall stays, because it is built, tested and common. Its hidden base series must be recomputed after an edit. |
| A language-neutral JSON Schema of the kinds and the `ChartData` fields (`chart.schema.json`, drafted in PR #14 and deleted before merge) | Only tests read it. The kit stays in Python, so no renderer in another language needs a contract.                                                     |
| An image block, so a `make-chart` picture can go on a kit slide                                                                          | No deck needs one yet. Add it in its own PR when one does.                                                                                            |

**Evidence.** `test_every_renderer_has_a_kind_label` in `skills/make-deck/template/tests/test_charts.py`; `test_test_deck_draws_every_html_chart_kind` in `skills/make-deck/template/tests/test_render_pptx.py`.

## 2026-11-27: Take nothing from think-cell for now

**Chosen.** No think-cell feature joins the kit.

**Considered and rejected.**

| Option                                                                                      | Why it was rejected                                                                                                                                                                            |
| ------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Reuse `github.com/think-cell/think-cell-library`                                            | It is a C++ library of ranges and containers, with nothing on charts.                                                                                                                          |
| Copy think-cell's markings: difference arrows, growth (CAGR) arrows, totals on stacked bars | They stay correct only because the think-cell add-in redraws them from its data sheet. Without the add-in they are plain shapes that break when someone edits the data. The kit has no add-in. |
| Mekko and Gantt charts                                                                      | PowerPoint has no native type for either. think-cell builds both from shapes.                                                                                                                  |

**Kept for later, not adopted.** Keep only raw numbers in the chart data, and compute each derived number in Python. Write a derived number, such as a growth rate, in the slide's lead line instead of drawing it.

**Evidence.** [think-cell chart decorations](https://www.thinkcell.com/en/resources/manual/chartdecorations); [think-cell compatibility](https://www.thinkcell.com/en/resources/manual/compatibility).
