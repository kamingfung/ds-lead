---
name: make-report
description: Use when writing a one-page report someone acts on - an experiment report, a bug or incident report, or an analysis finding - as an HTML page for review or a wiki page.
---

# One-page report

A report is done when a reader who sees only the title and the first paragraph knows the answer, what changes and what they must decide.

## Steps

Finish each step and its gate before you start the next step.

1. **Pick the reader, the decision and the variant.** Follow `debrief`, step 1. Then pick the variant:

   - If it is an experiment report, read `references/experiment.md`, then go to step 2.
   - If it is a bug or incident report, read `references/bug-report.md`, then go to step 2.
   - If it is an analysis finding, no variant file applies. Go to step 2.

   If your team plugin adds report rules (a `reports.md` reference in its writing skill), read it now.
   Gate: the draft header names the reader, the decision and the variant.

2. **Frame the question.** Write one sentence with its scope: who, what and which window. Follow `debrief`, step 2. Then state the hypothesis, as `solve`, Step 1, item 6, describes.
   Gate: the question and the hypothesis each fit one sentence.

3. **Build the evidence table before the prose.** Write one row per claim: claim, number, baseline, metric, window, unit, source, and checked or hypothesis. Follow `debrief`, "Numbers and evidence". Keep the table in the draft until step 8.
   Gate: every row has a source a reader can open; every cause not yet confirmed says "hypothesis".

4. **Write the title, the summary and the outcome block.** Follow `debrief`, "Shape", and `references/standard.md`, "Front matter" and "Outcome block". The title states the answer with its key number. The summary gives the question, the answer and what changes. The outcome block sits right under the summary.
   Gate: the title states the answer with its key number; the summary gives question, answer and what changes; the outcome block has all four fields.

5. **Write the body in the variant's section order.** Follow `references/standard.md`, "Body". With no variant, write results, then what it means, then limits.
   Gate: every variant section is present, or says "Not applicable" with a reason.

6. **Add figures and tables.** Follow `references/standard.md`, "Figures and tables".
   Gate: every figure and table has a number, a caption with unit and window, and a reference by number in the text.

7. **Write the asks and the not-checked list.** Write each ask as `debrief`, "Decision asks", describes. State what you did not check. Update the outcome block if the body changed it.
   Gate: each ask has an owner and a date; the outcome block matches the body.

8. **Check, then get a second reader.** Run `python3 skills/make-report/scripts/check_report.py <report.html|report.md>`. The script only warns. Fix each hit, or write one line that says why it stays. Then run `references/checklist.md`. Ask one second reader, a peer or a review assistant, to read only the title and summary and say the answer back. Cut about a quarter of the words, as `debrief`, step 6, says.
   Gate: every script hit is fixed or explained; the second reader's answer matches the title.

9. **Publish.** Draft the report as an HTML (HyperText Markup Language) one-pager for local review, as `references/format-html.md` describes. Publish to the team's record, such as a wiki page, only after the reader confirms the draft. Reason: a local HTML edit is a small diff, while a wiki edit through a connector sends the whole page body through the writer's working context on every create, read and update.
   Gate: the published link is on the ticket, or the reader declined publishing.

## References

- [references/standard.md](references/standard.md): front matter, body, business language, figures, numbers, outcome block and back matter rules that the company plugin does not hold yet.
- [references/format-html.md](references/format-html.md): the layout and a skeleton for the HTML one-pager.
- [references/checklist.md](references/checklist.md): the checklist to run at step 8.
- [references/experiment.md](references/experiment.md): section order and rules for an experiment report.
- [references/bug-report.md](references/bug-report.md): section order and rules for a bug or incident report.
- [scripts/check_report.py](scripts/check_report.py): warns about gaps in a report's title, acronyms, figures, units, sources and placeholders. Run it with `--selftest` to test it.
