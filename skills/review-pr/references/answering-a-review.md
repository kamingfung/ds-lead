# Answering a review

Applies to comments on a pull request or a report. The reply rules follow "How to write a rebuttal letter", Nat. Methods 23, 1919 (2026), doi:10.1038/s41592-026-03261-0.

A review round ends when every comment has a verified answer and the reviewer can check each fix on its own. Make each answer cheap to confirm.

## 1. Check before you act

- Before accepting a comment, inspect the code, config or data it refers to, since a comment can sound right and still misstate behavior.
- Reproduce a reported bug, or run the reviewer's case, before you fix it; a fix for a bug you never saw may fix nothing.
- Sort each comment into one of three groups: a real problem, a matter of taste, or a misreading. Accept only real problems, and state your position openly on the other two.
- Ask one specific question when a comment is unclear, and state how you read it meanwhile, so the round does not stall.
- Treat a comment from an AI reviewer like any other: confirm it against the code before you change anything.

## 2. Fix in the right place

- Correct the problem in the pull request that brought in the code, then carry that correction onto every branch stacked above it.
- Make one commit per comment, with a message that names the comment, so the reviewer reads each fix on its own.
- Put a new result (a rerun, a table, a figure) in the pull request description or the document, not only in a reply, so it survives the thread.
- Answer "why not X" in the reply, not in a code comment; code comments explain the code, not the review.
- Move a pre-existing defect the reviewer flagged into its own small change or ticket, keeping this pull request narrow.

## 3. Reply to every comment

- Reply to every comment, including nice-to-haves you act on. Resolve skipped nice-to-haves with no reply needed.
- Point to the fix (commit, file and line, section) instead of pasting it.
- Disagree politely, with a reason and evidence; if you cannot make a change, say why.
- Keep replies short and skip per-comment thanks.
- Reply once to a point raised twice, then link that reply from the other thread.

## 4. Close the round

- Push once per round, after every comment is answered, because each push reruns CI and notifies every reviewer.
- Post one summary per round as a reply under the reviewer's own review-summary comment. With no such comment, post it top-level. With two or more reviewers who each posted a summary, reply under each, or under one and link it from the others.
- Shape the summary: the head sha first, one bullet per finding with its fix commit, then whether outputs change (with the evidence), the test count and the CI state. Example: "Review round answered, head [sha](link). \* finding → fix ([sha](link)). Outputs do not change (evidence). Tests: N passed. CI is running." Then any open question.
- Request a fresh review once each comment has a response and CI is running.
- After three written rounds with a blocking comment still open, stop writing and meet the reviewer to rethink the approach.

## 5. Update the branch

- Refresh a pull request branch with `git rebase origin/main` only if the pull request holds all its commits and no other branch depends on it; if not, merge instead.
- Use `--force-with-lease` when you push a rebased branch.
- Rebase ahead of a review or between rounds, never during a round.
- Before you rebase, check that no doc, changelog or ticket comment cites a commit the rebase would orphan.
