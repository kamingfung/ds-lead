---
name: session
description: Use when starting, handing off or resuming a session, or tracking progress in a changelog. Not for the order of a task's steps (workflows).
---

# Session workflow

Rules for starting a session, tracking progress, and handing work between agents or machines. A _progress file_ is one markdown file per ticket, committed with the branch, that holds the brief, the current state and the decisions.

## 1. Session start

When you start a session or pick up work from another machine or agent:

1. Read the ticket's progress file: `## Brief` for intent and pass criteria, `## Progress` for the current state and next steps, `## Decisions` for earlier technical choices.
2. Run `git log --oneline -10` to see recent commits.
3. Run `git status` to see uncommitted work.

## 2. Several agents at once

- Give each agent its own branch, tied to one ticket.
- Give each ticket its own progress file, for example `changelogs/<TICKET>-short-title.md`.
- Commit the progress file to the branch before another agent takes over.
- Hands off any worktree you did not create for this task, such as the main checkout or a peer's worktree. Inside those, never run `checkout`, `switch`, `reset`, `pull`, `rebase`, `merge` or a bare `stash`.
- Read a file from another branch by naming its ref, never by switching: `git show <ref>:<path>`, `git diff <a>..<b>`, `git grep <pattern> <ref>`.
- For code on another branch that needs running or editing, open a detached worktree in a temp folder: `git worktree add --detach <temp folder> origin/<branch>`. Then `git push origin HEAD:<branch>`, followed by `git worktree remove` (skill [`worktrees`](../worktrees/SKILL.md)).
- Treat a branch checked out in another worktree as someone else's: do not write there, and tell its owner when you push to it.
- If you alter a shared worktree by accident, put it back right away and report it.

## 3. Another machine

1. Commit and push the work, the progress file included.
2. Pull on the other machine.
3. Read the progress file and resume where it says.

## 4. Progress file

Keep the sections in this order: Brief, Progress, Decisions.

- **Brief** (written before implementation, never edited): the goal, the pass criteria, and links to the ticket, the spec and the PR.
- **Progress** (updated every session): status (on track, at risk, blocked, done), the last items completed, the next steps with file paths, the blockers.
- **Decisions** (append-only): each entry gives the date, what was chosen, what was rejected, why, and one evidence line (a commit sha, PR, `file:line`, run id or query id).

Decision entries:

- Add an entry when the approach changes (a choice between options, a switch to another approach, a revert), at the time it happens, not only for the final choice.
- Before you hand off or close the session, check each entry: it is a real decision, and its evidence line opens and shows what it says.
- Check that each change of approach that shaped the work has an entry.

Rules:

- Keep one file per ticket, named `<TICKET>-short-title.md`.
- Never edit a past decision; append a new entry that replaces it and names the date of the old one.
- Keep the file after merge as the historical record.
- Write no placeholder links.
- Record the why, not the what; the diff shows the what.
- Put repository-wide decisions (architecture, platform, data contracts) in one shared decisions file, in the same format.

## 5. Pull requests

- Each PR serves one purpose; leave out unrelated refactors.
- Keep a PR small enough to review in about 30 minutes; split bigger work into stacked PRs.
- Put the ticket key in the PR title ([`write-pr`](../write-pr/SKILL.md), Tracker Issue).
- Cover the change itself, its motive and the test steps in the description (skill `write-pr`).
- Note each simplification made on purpose, and say why it is acceptable.
- Cite both run ids (main and branch) for a change that can move model outputs.

## Branch naming and review handoff

- Name branches with a short hyphen-separated description that identifies the work.
- Break work into reviewable commits and keep the changelog with the feature branch.
- Before opening a pull request, check the diff, run repository checks, and explain what changed, why and how to test it.
- Keep one purpose per pull request and request reviewers who understand the affected area.
