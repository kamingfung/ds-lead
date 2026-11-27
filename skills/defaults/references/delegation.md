# Subagent delegation and briefs

Use this guide when handing off a code change, test run, investigation, or draft to a subagent or worker session.

## 1. Split the work

- Split large tasks into independent pieces (one module, one review comment, one report section), each with its own pass test.
- Give parallel workers disjoint file scopes or separate git worktrees (skill [`worktrees`](../../worktrees/SKILL.md)). Never let two writers share one working tree.

## 2. Write a self-contained brief

Include every detail the worker needs in the brief itself. A subagent does not see your earlier conversation.

- **Goal and inputs:** State the exact file paths, queries, or counts. Never write "see earlier" or "the list above."
- **Write scope:** Name the only paths the worker may create or edit.
- **Pass test:** Give the exact command that proves the work is done.
- **Forbidden actions:** State what the worker must not do (for example: pushing, merging, editing `main`, or writing to external systems).
- **For analyses:** Ask for the strongest rival explanation of the main finding and the check that separates the two.
- **For large tasks:** Ask the worker to list the weak points of its plan before starting.

## 3. Worker contract

- **Input echo first:** Before heavy work, echo the received counts and scope (for example, "12 files, window 2026-01..2026-06") so a missing input surfaces immediately.
- **Stop at done-criteria:** Stop once the pass test and brief requirements pass. Do not invent extra gates, review rounds, or unrequested refactors.
- **Ask before irreversible choices:** Make reversible design choices inside the brief and log them. Stop and ask before altering an approved decision, ground truth, or a shared interface.
- **Typed report:** End with `STATUS`, `RESULT`, `EVIDENCE` (commands, row counts, query or run ids), `CHANGED`, `DECISIONS` (what, why, and rejected alternatives), `OPEN`, and `NOT CHECKED`.

## 4. Verify and hand off to review

- **Pre-commit before review:** Run `pre-commit` (formatting, lint, whitespace, secrets) and commit fixes before sending a branch to a reviewer. Reviews then focus on logic instead of style.
- **Verify by lookup:** Confirm evidence lines against the diff and logs rather than redoing the work. Rerun the pass test yourself—or in a fresh agent—whenever evidence is missing or surprising.
