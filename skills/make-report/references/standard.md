# Report standard

These rules add to `debrief`. Do not restate its rules here. Read its "Shape", "Numbers and evidence" and "Plain words" sections first.

## Front matter

- The title states the answer. Follow `debrief`, "Shape".
- The summary runs 150 to 200 words and sits directly under the title.
- The summary has no formulas and no tables.
- The summary opens with a one-sentence takeaway. Then it gives the question, the answer and what changes.
- Do not add a chronological recap of the steps taken.
- Add an ownership line under the summary: author or team, date, and the ticket or pull request (PR) link.

## Body

- Give results before discussion.
- Put limits and next steps in the closing section.
- Use at most three heading levels. Number the top-level sections when the report runs past one screen.
- Make the report reproducible from the report alone. State:
  - the data source and the pull date;
  - the branch and commit;
  - run ids and parameter values;
  - the metric formulas;
  - the exact rerun command.
- Give every improvement claim its number, baseline, metric and window.
- Link each source at first mention. Never write "the previous analysis showed".
- Verify every citation against a primary source. Omit a digital object identifier (DOI) or page you have not checked.
- Keep results that a data refresh can change in a dated report, not in a stable method document.

## Business language

- Lead with the "so what".
- Say what happens in the field, not the data-science term. Write "daily weather spikes", not "high-frequency noise".
- Write plans, not possibilities.
- Use the positive form: state what is.
- Use parallel form in lists and headings.
- Put the decisive number or term at the end of the sentence.
- Use one tense, usually the present.

## Figures and tables

- Generate every figure from a committed script.
- Use one chart per figure.
- Make each caption state what is plotted, the unit and the data window.
- Refer to figures by number ("Figure 1"), never by position ("the chart below").
- Drop a figure that repeats another figure or the text. Then renumber.
- Pair every color with a second encoding: a marker, a line style or a label.
- Draw flow diagrams as text-based diagrams (Mermaid, Graphviz or inline SVG (scalable vector graphics)) so they diff.
- Tables: put a lead-in sentence or caption above. Put units in column headers. Keep one decimal precision within each column. Put footnotes directly below.
- Equations: define every symbol, with its unit, in a `where` list below the equation.

## Numbers in generated reports

- When a script builds the report, compute every number in titles and prose from the same tables the figures use.
- Never hardcode a number.
- Cross-check each figure that two outputs share, such as the page and the deck.

## Outcome block

Put this table near the top, right after the summary and the ownership line. Its four fields let a reader tell a finished analysis from an abandoned one.

| Field        | Value                                                                       |
| ------------ | --------------------------------------------------------------------------- |
| Outcome      | Adopted, Rejected, Open or No action needed                                 |
| What changes | The pull request or code path, or "Nothing, because ..."                    |
| Next action  | One step, with owner and ticket, or "None". An Open outcome needs a ticket. |
| Decided      | Who decided, and the date                                                   |

## Back matter (long reports only)

- Add a back matter when the report runs past one screen.
- Use these headings: Data availability, Code availability, Contributors, Related documents.
- Write "Not applicable" under a heading that does not apply. Do not drop the heading.
- Put large tables and plots in an appendix after the back matter.
