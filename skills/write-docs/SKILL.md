---
name: write-docs
description: Use when writing or editing docs, changelogs, PR descriptions, wiki pages or chat replies. Not for a one-page report someone acts on (make-report).
---

# Document Writing Standards

Structure and formatting rules for technical documentation, model docs, experiment reports, and developer guides.

## 1. One Self-Contained Document

- Keep one document per model, report, experiment, or guide; do not force readers to stitch fragments across files.
- Start Markdown files longer than two screens with a Table of Contents matching the section headings.
- Store static images in an adjacent `img/` folder, one file per figure (never composite multi-chart images).
- Write for a reader who sees only this document: expand every acronym at first use and state the scope in the opening paragraph.

## 2. Terminology

- **Reuse before coining:** search existing `docs/` and code before inventing a new name.
- **Define at first use:** define every new or non-obvious term in one sentence or equation and link to its canonical definition.
- **One concept, one name:** use the exact same term across docs, docstrings, comments, PR descriptions, and slides; when the code identifier differs from the domain term, state the mapping once (`promotion ("cohort" in code)`).
- **Never redefine an existing term** with a different meaning.
- **Consistent math notation:** give each symbol one meaning per document and reuse canonical symbols across related docs.
- **Check before publishing:** look through the draft for any term used before its definition or under two different names.

## 3. Sentences & Steps (ASD-STE100 & Elements of Style)

Write in the spirit of ASD-STE100 (Simplified Technical English) and _The Elements of Style_ across docs, changelogs, PR descriptions, and chat replies:

- Write short, direct sentences in the active voice (~20 words for procedural steps, ~25 for descriptions).
- Give each procedural step one imperative action: `"Run the backtest."` then `"Compare the error metric."`, not both in one sentence.
- **Use positive form:** state what is rather than what is not (`"forgot"` over `"did not remember"`); reserve `"not"` for deliberate antithesis.
- **Omit needless words:** cut filler phrases (`"the fact that"`, `"in order to"`, `"who is"`, `"which was"`); make every word carry meaning.
- **Use parallel form:** express coordinate ideas in the same grammatical structure across lists, headings, and comparisons.
- **Keep related words together:** place modifiers next to the words they modify; keep subject, verb, and object close.
- **Keep one tense:** use a single consistent tense throughout a summary or description (typically present tense).
- **Place key words at the end:** put the decisive number, conclusion, or emphatic term at the end of the sentence.

## 4. Document Structure (Front Matter, Body, Back Matter)

- **Front matter:**
  - Give a page, report or deck a title that states its answer: the finding with its key number, or the decision. A topic label fails, and so does a question, even one with the answer after the "?".
  - Plain-language executive summary (~150–200 words, no formulas or tables) directly under the title: open with the single-sentence headline takeaway, state the question, the answer, and what changes as a result, and cut ~25% of words on revision (no chronological recaps of steps taken).
  - Ownership line: author/team, date, and issue/PR link.
- **Body:**
  - Use at most three heading levels; number top-level sections (`## 1. Overview`) so cross-references survive edits.
  - Include everything needed to reproduce results in Method/Setup: dataset names and pull dates, parameter values, branch/commit SHA, MLflow run IDs, metric formulas, and the exact rerun command.
  - Present results before discussion; state limitations and next steps in the closing section.
  - Every improvement claim must state the **number**, the **baseline**, the **metric**, and the **evaluation window**.
- **Back matter:**
  - Close technical/model reports with: `Data availability`, `Code availability`, `Contributors`, and `Related documents` (write `Not applicable` rather than omitting).
  - Keep volatile experiment tables and dated snapshots in changelogs or PR descriptions rather than stable method docs; place large tables/plots in an appendix after the back matter.

## 5. Figures, Tables, Equations & Formatting

- **Figures:** one chart per figure; caption states what is plotted, the unit, and the data window; refer by number (`Figure 1`), never by position (`the chart below`); follow [visualization.md](../make-chart/references/visualization.md).
- **Tables:** lead-in sentence or caption above; units in column headers; consistent decimal precision per column; footnotes directly below.
- **Equations:** display math in `$$ ... $$`, inline math in `$ ... $`; number only equations referenced in prose; define every symbol with units in a `where` list directly below.
- **Lists & emphasis:** numbered lists for ordered procedures, bullets for unordered items (`<=2` nesting levels); bold only for run-in labels at the start of a bullet or paragraph; one paragraph per line (no hard line wraps); quote file paths, flags, and parameter keys in backticks.
- **Cross-references:** link sources (issues, PRs, runs, docs) at first mention; never write bare claims like `"previous analysis showed"`.
- **Citations:** check each citation against a primary source before writing it, and never cite from recall. Leave out any DOI or page number you have not confirmed.
- **No repeated figures:** before you publish, remove any figure that duplicates another figure or what the text already states, then renumber the rest.

## 6. Wiki Pages

- On a page, cite every script and data file using the first option below that fits, with a link where it is cited:
  1. Read straight from a shared system: that location (table, object-store path, experiment-tracker run id).
  2. Smaller than about 20 MB: attach it to the page.
  3. Output of a local run: publish it to the shared experiment tracker, then cite that run id.
  4. None of these: a share link to a copy of the file.
- Never cite a local, scratch or synced-drive file path on a page; readers cannot open it. A share link is not a path.
- Scan the page body for local paths (`/Users`, `/tmp`, `C:\`, scratch and output folders) before you publish or edit it, and fix every hit.
- Remove the citation to any file that no longer exists, and do not recreate that file.
- Show a repository path on a page only beside a link to its branch or commit.
- Do not change another owner's page. Instead, leave a comment that asks the owner to correct it.

## 7. Requirements by Document Type

| Document type           | Primary home                    | Key requirement                                                                    |
| ----------------------- | ------------------------------- | ---------------------------------------------------------------------------------- |
| Model / pipeline doc    | `docs/`                         | Overview, method, parameters mirroring YAML, reproducibility commands, back matter |
| Experiment / PR summary | PR description or `changelogs/` | Hypothesis, arms, metric, baseline vs. branch result table, decision               |
| Developer guide         | `docs/developer_guides/*.md`    | Imperative voice, one rule per bullet, good/bad example only where ambiguous       |

## Document structure additions

- Make each document self-contained; do not make readers assemble it from fragments.
- Add a table of contents to a document longer than two screens.
- Keep headings to three levels and number top-level sections when cross-references need stable names.
- Put the question, answer and consequence in the executive summary before methods or detail.
- Put reproducibility details in method and setup sections: sources, date range, parameters, branch, commit and rerun command.
- Put results before discussion and state limitations and next steps at the end.
- Close reports with Data availability, Code availability, Contributors and Related documents; write `Not applicable` when needed.

## Tables, figures and equations additions

- Keep one chart per figure and state the unit and data window in its caption.
- Define error bars, bands and statistics in the caption.
- Put table captions or lead-ins above tables; include units, consistent precision and footnotes.
- Split a table that is too wide; do not shrink its font.
- Put equations in `$$ ... $$` or `$ ... $`; define every symbol and unit at first use.
- Put supporting material that interrupts the reading flow in an appendix after the back matter.

## Sources

- Strunk, W., Jr., and White, E. B. _The Elements of Style_ (first published 1920; E. B. White's revision, Macmillan, 1959). <https://en.wikipedia.org/wiki/The_Elements_of_Style>. Section 3 follows its rules on positive form, needless words, parallel form, related words together and emphatic words at the end of a sentence. The wording here is our own.
