---
name: review-pr
description: Use when reviewing a pull request or report, answering review comments, running an AI reviewer or self-reviewing a branch before merge.
---

# Code Review

Two procedures: **Review a PR or Report** (steps 1–11) and **Answer a Review** (steps A1–A7). Run the steps in order. Each step ends in a gate: the check that must pass before the next step. A gate that is a command must exit 0; a gate that is a judgment is a checklist item you answer in the draft.

The steps point to the rules and never restate them:

| File                                                     | Holds                                                                                                 |
| -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| [references/standard.md](references/standard.md)         | The rules: referee posture, severities, testing on data, AI reviewers, pre-commit, posting, answering |
| [references/format.md](references/format.md)             | The layout of inline comments, the summary comment and replies                                        |
| [references/checklist.md](references/checklist.md)       | The review checklist                                                                                  |
| [references/verification.md](references/verification.md) | How a finding was checked, and when a verdict still holds                                             |
| `scripts/check_drafts.py`                                | The format gate on the drafted comments                                                               |

Write the drafts to a folder outside the repository: `summary.md` and one `.md` file per inline comment.

## Review a PR or Report

### 1. Check access

Fetch the branch and read the PR or page. Raise access blockers first (standard.md, Review Like a Referee).

- If a blocker stops the whole review, draft only a summary with the ⏸️ verdict that names it (format.md), and go to step 9.
- If a blocker stops part of the review, name that part in **Not run:** and go on.

**Gate:** the head sha you review is written in `summary.md`, and every blocker is named.

### 2. Set the tier

Read the diffstat (`git diff --stat <base>...<head>`) and count the risk flags: a shared table, an output that moves, logic that is not simple, a change that is hard to undo.

| Tier | When                                         | Step 5                                                            | Step 6 model           | Step 8                                         |
| ---- | -------------------------------------------- | ----------------------------------------------------------------- | ---------------------- | ---------------------------------------------- |
| 0    | Docs, comments or config text only           | Checklist, and every claim the docs make checked against the code | A fast, low-cost model | Only if a doc claim is about data values       |
| 1    | Code under about 100 changed lines, no flags | Checklist                                                         | A fast, low-cost model | For each data-sensitive must-fix or should-fix |
| 2    | Code over about 100 lines, or one flag       | Checklist                                                         | The strongest model    | For each data-sensitive must-fix or should-fix |
| 3    | Two or more flags                            | Checklist                                                         | The strongest model    | For each data-sensitive must-fix or should-fix |

**Gate:** `summary.md` holds `Tier N: <reason>`, kept for the verdict line (format.md, Summary Comment).

### 3. Check pre-commit

```bash
pre-commit run --from-ref <base> --to-ref <head>
```

Run it in your own checkout of the PR head, where the repository has a pre-commit config. If it fails, ask the author to run it and commit the fixes; review nothing that it checks (standard.md, Leave Mechanical Checks to Pre-commit).

**Gate:** the command exits 0, or the repository has no pre-commit config.

### 4. Read the CI status

| CI      | Then                                                        |
| ------- | ----------------------------------------------------------- |
| Red     | Draft a ❌ must-fix for the failing check; go on            |
| Running | Write "CI running" in **Evidence:**; go on, and do not wait |
| Green   | Write "CI green" in **Evidence:**; go on                    |

**Gate:** the CI state is in the **Evidence:** bullets.

### 5. Review like a referee

Review by standard.md, Review Like a Referee. Then walk [checklist.md](references/checklist.md). Add the tier's extra check from step 2.

**Gate:** every checklist section is marked pass, finding or not applicable, and every finding carries a severity and "new in this PR" or "pre-existing".

### 6. Run the AI reviewer

Run one AI reviewer at the tier's model (standard.md, AI Reviewers).

**Gate:** the run exits 0, and each AI finding is merged into your list or dropped with a reason.

### 7. Check each finding

Give each finding a check label from [verification.md](references/verification.md). Use the cheapest check that settles it.

- If a must-fix or should-fix is data-sensitive, go to step 8 (tier 0: see the step 2 table).
- If a must-fix has only "read in code" or "traced", run it, or post it as a question.
- Otherwise go to step 9.

**Gate:** each finding has a check label, and each must-fix has "ran" or "ran on data".

### 8. Test the finding on data

Test the finding by standard.md, Test a Finding on Data.

**Gate:** both results and the slice name are in the comment, or the run you could not do is named in **Not run:**.

### 9. Draft the comments and the summary

Write one file per inline comment and `summary.md` ([format.md](references/format.md)). Run:

```bash
python skills/review-pr/scripts/check_drafts.py <draft folder>
```

**Gate:** the script exits 0.

### 10. Post after approval

Show the drafts to the person who asked for the review. Post nothing until they say yes. Then post all comments in one go (standard.md, Post).

**Gate:** the PR shows one posted comment per draft file, with no duplicates.

### 11. Re-review a new push

When the author pushes, compare patch ids (verification.md, A Verdict Holds for a Diff).

| Patch id  | Round                    | Then                                                                        |
| --------- | ------------------------ | --------------------------------------------------------------------------- |
| Same      | any                      | Keep the verdict; write "verdict from <sha>; diff unchanged" in the summary |
| Different | 1 or 2                   | Review only the new diff (`git range-diff`); go to step 4                   |
| Different | 3, a must-fix still open | Stop writing; meet the author                                               |
| Different | 3, no must-fix open      | Review the new diff; go to step 4                                           |

Only the human approver that standard.md names for the changed paths approves and merges (Review Like a Referee); an AI approval never counts.

**Gate:** the summary names the reviewed head sha, and the round number is 3 or less.

## Answer a Review

### A1. Read each comment against the code

Read the code, config or data each comment points at ([answering-a-review.md](references/answering-a-review.md), section 1). Rate each comment:

| Rating                        | Then                                                           |
| ----------------------------- | -------------------------------------------------------------- |
| Real problem                  | Go to A2                                                       |
| Matter of taste or misreading | Reply with the reason and evidence (A5); change nothing        |
| Unclear                       | Ask one specific question (A5)                                 |
| Pre-existing problem          | Open a separate small PR or a ticket; reply with its link (A5) |

**Gate:** every comment, including each one from an AI reviewer, has a rating.

### A2. Reproduce the problem

Reproduce the reported bug, or run the reviewer's case.

- If it reproduces, go to A3.
- If it does not, reply with what you ran and its output (A5).

**Gate:** each "real problem" has a reproduced output or a "could not reproduce" reply.

### A3. Fix in the PR that introduced the code

Make one commit per comment, its message naming the comment. Bring the fix forward to each branch stacked on this PR.

**Gate:** `git log <base>..HEAD` shows one commit per fixed comment.

### A4. Put new results where readers look

Put any new result in the PR description or the doc, not only in a reply.

**Gate:** each new number in a reply also appears in the PR description or the doc.

### A5. Reply to every comment

Write the replies and the round summary ([format.md](references/format.md), Replies).

**Gate:** every comment has a reply, except a skipped nice-to-have, which is resolved.

### A6. Push once

Choose rebase or merge by [answering-a-review.md](references/answering-a-review.md), section 5. Push once for the round.

**Gate:** one push for the round, and CI has started on it.

### A7. Re-request review

**Gate:** every comment has an answer and CI has started; then re-request review.
