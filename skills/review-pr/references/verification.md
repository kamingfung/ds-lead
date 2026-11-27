# Verification: how a finding was checked, and when a verdict still holds

Read this before you post a finding, and before you reuse a verdict from an earlier review round.

## Say how each finding was checked

Give every finding one of these four labels. They go from weakest to strongest:

| How it was checked | What you did                                                                                                                                                   |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| read in code       | You cite the `file:line` in the change, or in the library source, that shows the problem.                                                                      |
| traced             | You followed one failing input through the code, call by call, to the wrong result.                                                                            |
| ran                | A test, script or query on the head of the change shows the wrong result. Paste the command and its output.                                                    |
| ran on data        | A pipeline run on the head of the change shows the wrong result on real data. Name the slice and the run id ([SKILL.md](../SKILL.md), Test a Finding on Data). |

- Use the cheapest check that settles the finding.
- A claim with none of these labels is an opinion. Post it as a question.
- A must-fix needs "ran" or "ran on data". A data-sensitive must-fix needs "ran on data".
- Post a finding that is only "read in code" or "traced" as a question, not as a must-fix.
- Put the label after the severity: "❌ must-fix (new in this change; ran): ...".
- When a change looks risky, first name the condition that keeps it safe (for example, "the column has no nulls after `clean_orders`"). Check that condition with "ran" before you list other risks.
- Treat a finding from an AI reviewer as unchecked until you check it yourself.

## A verdict holds for a diff, not for a commit

A verdict judges the diff you reviewed. A rebase gives every commit a new sha but can leave the diff the same. One more small push can change the diff under the same title.

- Write the head sha you reviewed next to the verdict in the summary comment.
- Before you reuse an earlier verdict, compare the patch ids of the reviewed sha and the current head. A patch id is the hash that `git patch-id --stable` gives a diff: two equal diffs give the same id, whatever their commit shas.

```bash
git diff origin/main...<reviewed sha> | git patch-id --stable
git diff origin/main...<head sha> | git patch-id --stable
```

- Same patch id: keep the verdict, and write "verdict from <reviewed sha>; diff unchanged" in the summary.
- Different patch id: review what changed since the verdict (`git range-diff`) before you give a verdict again.
- When only tests or docs changed, review those files. The verdict on the rest still holds.
- A green CI build or an AI approval is not a verdict: neither judges the change as a reviewer does.
