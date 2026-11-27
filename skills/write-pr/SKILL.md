---
name: write-pr
description: "Use when writing or updating a pull request description, covering what changed (every new, changed and deleted function), why it changed, test commands that run, reviewer notes, and a results table when outputs can move."
---

# Write a PR Description

Write the description from the diff, not from memory. Read the commits and the changed code first. The reviewer should know what changed, why it changed, and how to check it before opening the code. Treat the description as a permanent record. Future readers find a change by searching its text, so the facts belong in the description, not only in the code. Start the first line with a short, complete imperative sentence.

## Collect the Facts

1. Run `git rev-parse --abbrev-ref HEAD` and stop if it prints `main`.
2. Run `git log origin/main..HEAD --oneline` to list the commits in the PR.
3. Run `git diff origin/main --stat` to size the change by files and lines.
4. List changed function definitions with `git diff origin/main -U0 | grep -E '^[+-][[:space:]]*def '`. For other languages, adapt the pattern.
5. List added files with `git diff origin/main --diff-filter=A --name-only`, and deleted files with `git diff origin/main --diff-filter=D --name-only`.
6. Find the tracker issue the PR belongs to. A key in the branch name or a commit subject is a hint, not proof; ask the author when no issue fits.

## Template

```markdown
## Summary

<One or two sentences: what the PR changes and why.>

## Changes

### Added

| Item                     | File                       | What and why                                       |
| ------------------------ | -------------------------- | -------------------------------------------------- |
| `build_monthly_totals()` | `pipelines/sales/nodes.py` | Sums weekly sales into monthly totals for reports. |

### Changed

| Item            | File                        | What and why                                                   |
| --------------- | --------------------------- | -------------------------------------------------------------- |
| `load_orders()` | `pipelines/orders/nodes.py` | Reads the new `region` column so reports can filter by region. |

### Removed

| Item                                       | Why                              |
| ------------------------------------------ | -------------------------------- |
| `legacy_export()` in `pipelines/export.py` | Replaced by the new export step. |

- Config: `conf/base/parameters.yml` adds the region filter key.
- Tests: `tests/test_orders.py` covers the new filter.
- Docs: `docs/sales.md` describes the monthly totals.

## Why

- Problem: <what was wrong or missing, and who it affected>.
- Issue: <tracker issue key>.
- Decision: <the choice, who made it, and when>.
- Trade-off: <the option rejected, why it was rejected, and what the choice costs>.

## Results

<Include this section only when outputs can move.>

| Metric       | Baseline | This PR |
| ------------ | -------- | ------- |
| Weekly sales | <value>  | <value> |

- Baseline: commit <sha>, run <run id>.
- This PR: commit <sha>, run <run id>.
- Evaluation window: <start> to <end>, <row count> rows.

<One paragraph that reads the numbers: the direction, the size, and any change that was not expected.>

## How to Test

1. Run <command from the entry point list> and compare the output with the expected result.

## Reviewer Notes

- Merge risk: <whether one revert undoes the change, and which outputs or users it affects>.
- Unit tests: <the result, for example the number passed and failed>.
- Limitations: <what the change does not handle>.
- Follow-ups: <issue keys for related work>.
- Read closely: <files or functions that need careful review>.
- Non-obvious choices: <decisions a reviewer would question, and why each was made>.
- Mechanical diffs: <large generated or renamed sections, and how they were checked>.
```

## Rules per Section

- Changes: list every added, changed and removed function or file, with its path. Take the list from the collection steps, not from memory.
- Drop a table that has no real rows. Never write a "none" row.
- Why: give each decision, who made it, and when. Name the option you rejected and the reason.
- Results: required when outputs can move. Name both runs by commit and run id. Give the metric table with the baseline, the evaluation window, and the row counts. Add one paragraph that reads the numbers. A pure refactor says that outputs are unchanged and how you checked.
- Reviewer Notes: always include the merge-risk line first, then the unit-test result.
- Keep the PR small enough to review in about 30 minutes. Split larger work into a stack of PRs.

## How to Test

1. Use the test steps the requester gave, if any. Check that each name in them exists.
2. Otherwise, find the entry points the diff touches: commands, pipeline steps, endpoints, and jobs.
3. Check every name with the project's own listing command before you write it. Never leave a placeholder.
4. Choose the checks by PR type:
   - Refactor: run the touched entry points in the reference environment on fixed inputs, save the outputs, rerun on the branch with the same inputs, and expect identical outputs.
   - Bug fix: do the same comparison, and state the expected difference.
   - New feature: give the command that runs it and what to look for in the output.
5. Leave out unit tests, because CI runs them. This section covers only checks that CI does not do.
6. When you cannot find the entry points, ask the author which ones to run, and name the file you read.
