# Review Standard

A reviewer reaches this file from the `review-pr` skill. The rules cover pull requests (PRs) and experiment reports kept on a wiki. For the layout, see [format.md](format.md). For the checklist, see [checklist.md](checklist.md).

The posture follows the journal referee model and Google's code review standard. Under Google's standard, a reviewer approves a change once it clearly makes the code base better, even if the change is not flawless (Google, "The Standard of Code Review").

## Review Like a Referee

- Start with access problems: an unpushed branch, absent data, or missing permissions. State which parts you cannot judge as a result.
- Weigh value and soundness ahead of style. Look at the problem being solved, earlier work, the baseline, the comparison with the current method, whether the data backs the conclusions, the statistics behind each claim, and the limits the author admits (Nature Methods, "The good referee").
- Report design and logic issues before edge cases. Read the code, config and data that the change touches, not only the diff. Google recommends reading the full file for context.
- Rerun the author's evidence when it is missing or looks odd. If you skip the rerun, say your finding came from reading the code.
- Consult [verification.md](verification.md) before you publish a finding or carry forward an earlier conclusion.
- Confirm that someone can reproduce the work from the PR alone, using the pushed commit, the data date, the run ids, and the rerun command.
- Report what matters and stop: a short list the author must act on, not every idea you had.
- Number each finding and give it one severity.
- **must-fix**: a bug, a failing test, or a threat to data integrity or production.
- **should-fix**: a style, documentation, or over-engineering concern.
- **nice-to-have**: polish. The author replies only if they choose to act. Google suggests a "Nit:" prefix here.
- Call out over-engineering even when the code runs: an abstraction with a single caller, a new dependency, or code added on speculation.
- Label each finding "new in this PR" or "pre-existing". A pre-existing problem never holds up the PR. Request a small fix in a separate PR against main, or a follow-up ticket.
- Mention a recurring problem once, at its first occurrence, and ask for every instance to change.
- Address the work, not the author. Comment on grammar only when errors obscure the meaning (Google, "How to write code review comments").
- After three written rounds with a must-fix still open, switch to a live conversation with the author.
- Scale human review to the risk. Docs and notebooks need one human read. Production parameters, the data catalog, model config, and pipeline wiring need a named human approver. A model change also needs a before-and-after result against main. An AI approval never stands in for the human sign-off.

## Test a Finding on Data

- Run each data-sensitive must-fix and should-fix on real data before you post it.
- Use the PR head on the smallest data slice that exposes the issue, and name that slice in the comment.
- Run the PR head and your proposed fix on the same slice.
- Include both results in the comment.
- Treat production as read-only, and write outputs only to local storage.
- For pure logic, write a unit test in place of a data run.
- State in the comment anything you were unable to run.

## AI Reviewers

- Choose the model the tier table in [SKILL.md](../SKILL.md) assigns to the change.
- Write a brief that lists every file to read and each claim to verify. Request one verdict per claim, and findings ordered by severity, each with a `file:line` reference.
- Treat AI output as a rough first pass.
- Where you can, add a second reviewer built on a different model family, and keep it read-only.
- Before acting on any AI finding, check it against the code, and against data when the finding concerns data.

## Leave Mechanical Checks to Pre-commit

- The author runs the pre-commit hooks across the PR range and commits any fixes before the review starts.
- Reviewers do not repeat what automated tools already cover: formatting, linting, import order, whitespace, notebook outputs, large files, secrets, and YAML or TOML syntax.
- Human review time goes to what no tool catches: correctness, data handling, design, and documentation that matches the code.

## Post

- Submit inline comments in one batch at the close of the round. Unlike the web review button, API comments are not grouped automatically.
- After a network failure, fetch the PR's existing comments before retrying, so that nothing is posted twice.

## Answer a Review

Follow [answering-a-review.md](answering-a-review.md). Verify each comment before acting, fix the problem in the PR that introduced it, answer every comment, post one round summary, and push once.

## Sources

- "The good referee", _Nature Methods_ 15, 91 (2018). https://doi.org/10.1038/nmeth.4603
- "How to write a rebuttal letter", _Nature Methods_ 23, 1919 (2026).
- Google. "The Standard of Code Review" and "How to write code review comments", Google Engineering Practices Documentation. https://google.github.io/eng-practices/review/reviewer/standard.html and https://google.github.io/eng-practices/review/reviewer/comments.html (CC BY 3.0)
- Microsoft. "Reviewer Guidance", Code-With Engineering Playbook. https://microsoft.github.io/code-with-engineering-playbook/code-reviews/process-guidance/reviewer-guidance/ (CC BY 4.0)
