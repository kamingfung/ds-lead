# Plan Template

Fill in this template to produce a single-page plan. Swap every placeholder for real content. Remove a section only if it is irrelevant, and give a one-line reason.

```text
Deadline: <milestone or meeting>, dated <YYYY-MM-DD>        (or: Deadline: name the milestone only)
Goal: <the outcome in one sentence>
Approver: <one person>

Why, with data
- <number, unit, scope> (source: <query, run, file or page>, <row count>; checked | hypothesis)
- <number, unit, scope> (source: ...; checked | hypothesis)

Alternatives
| Option | Cost | Risk | If we do nothing |
|---|---|---|---|
Recommendation: <option, and why>

Decisions
| Decision | Answer | Who, when |
|---|---|---|

Steps
| Step | Owner | Date and anchor | Points |
|---|---|---|---|

Outcomes
- Done: <pass-or-fail checks another reader can verify>
- Good: <metric> on <window>, against <baseline>; bar <value>; reader <who uses the result>

Out of scope
- <...>
```

## Rules for data lines

- State the unit and the scope for every number.
- Cite one source for each number, and make sure a reader can open it: a query, run, file or page.
- Mark a number `checked` only after you rerun the query or read the source. Otherwise mark it `hypothesis`.
- State the strongest rival explanation and the check that separates it from the main explanation.

## Done versus good

|            | Done                         | Good                                   |
| ---------- | ---------------------------- | -------------------------------------- |
| Answers    | Has the work been completed? | Does the result justify shipping?      |
| Form       | Yes-or-no checks             | A metric with a baseline and a bar     |
| Checked by | Anybody, by lookup           | The approver, measured against the bar |

The done checks become the work items' success criteria after approval.
