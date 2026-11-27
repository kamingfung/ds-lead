---
name: workflows
description: Use when you start a bug fix, an investigation or analysis, a ticket pickup, a feature, or opening a pull request, to get the order of steps and the skill each step needs.
---

# Workflows

Each workflow gives the order of steps for one kind of task, and the guide each step needs. Pick the workflow that matches the task, and put its steps in your task list before the first tool call.

| Task                                                            | Workflow                             |
| --------------------------------------------------------------- | ------------------------------------ |
| Something that worked now fails, or gives a wrong number        | [1. Bug fix](#1-bug-fix)             |
| A question about data, code or a model, with no code change yet | [2. Investigation](#2-investigation) |
| New behavior: a pipeline step, a parameter, a model change      | [3. Feature](#3-feature)             |
| The change is done and needs a pull request (PR)                | [4. Opening a PR](#4-opening-a-pr)   |

- When a task spans two workflows, run them one after the other. An investigation that finds a bug goes on in Bug fix; every workflow that changes code ends in Opening a PR.
- When no workflow fits, say which one was nearest and plan the task ([engineering-practice.md](references/engineering-practice.md), section 1).
- End with the reply that the workflow's last line describes.

## Contribution handoff

- Break a story into tasks that can finish in a focused day or less.
- Keep the owner responsible for checking each result against evidence before handoff.
- Record the branch, commit, checks and open questions in the handoff so another person can reproduce the work.
- Treat review feedback as an input to the owning agent; do not merge or publish without the named human approval.

## 1. Bug fix

```
blame → reproduce → failing test → fix → prove → Opening a PR
```

- blame finds the break in someone else's open work → send its owner the diagnosis, not a fix; stop.

1. Find the commit or PR that broke it (`git log -S`, `git blame`). If it is in someone else's open work, send its owner the diagnosis, not a fix ([engineering-practice.md](references/engineering-practice.md), section 1).
2. Reproduce the bug and find its cause ([engineering-practice.md](references/engineering-practice.md), section 3).
3. Write a test that fails on the bug, before the fix ([unit-tests.md](../coding/references/unit-tests.md)).
4. Fix the cause at its source ([python-pipeline.md](../coding/references/python-pipeline.md), Fail Loud).
5. Show that the fix works, and compare main with the branch when outputs can move ([engineering-practice.md](references/engineering-practice.md), section 4).
6. Go on with Opening a PR.

Reply: what broke, the cause, the fix, and the command output before and after the fix.

## 2. Investigation

```
question → search → evidence → write up
```

- The answer needs a code change → go on with Bug fix or Feature.

1. State the question, the key hypothesis, its strongest rival and the subset of data that tells them apart (skill `solve`).
2. Search earlier work (tickets, pages, changelogs) for the same question or config key.
3. Collect the evidence with read-only queries and code reads, and test the rival on that subset ([engineering-practice.md](references/engineering-practice.md), section 3).
4. Write the findings top-down ([`write-docs`](../write-docs/SKILL.md)).
5. If the answer needs a code change, go on with Bug fix or Feature.

Reply: the answer, the evidence for and against it, the rival you ruled out, and the asks.

## 3. Feature

```
plan → tests → brief → verify → numbers → Opening a PR
```

- The change cannot move model outputs → skip numbers.

1. Plan the change, with its output contract and one check per step ([engineering-practice.md](references/engineering-practice.md), section 1; [`coding`](../coding/SKILL.md)).
2. Write the tests first ([engineering-practice.md](references/engineering-practice.md), section 2).
3. Brief each sub-agent, one brief per piece ([`defaults`](../defaults/SKILL.md), Briefs).
4. Verify each result ([engineering-practice.md](references/engineering-practice.md), section 4).
5. If the change can move model outputs, check the numbers ([`check-backtest`](../check-backtest/SKILL.md)).
6. Go on with Opening a PR.

Reply: what you built, each choice with the options you rejected, the run ids, and the open decisions.

## 4. Opening a PR

```
check scope → pre-commit → self-review → description → draft PR → ready
```

1. Check the branch and the scope of the change ([`session`](../session/SKILL.md), Pull requests).
2. Run pre-commit and commit its fixes (skill `review-pr`, Leave Mechanical Checks to Pre-commit).
3. Self-review with an AI reviewer (skill `review-pr`, AI Reviewers).
4. Write the description (skill `write-pr`).
5. Open the PR as a draft, then mark it ready when CI has started.

Reply: the PR link, its CI state, and what the reviewer must look at first.
