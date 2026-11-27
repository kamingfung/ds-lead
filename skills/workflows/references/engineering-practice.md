# Engineering Practice

Four habits apply to any code change: plan before a multi-step change, test first, debug from the cause, and verify before you call the work done. Each rule names, after "so that" or "because", the failure it prevents, and each piece of work ends at a _pass test_: the exact command that shows the work is done.

## 1. Plan Before a Multi-Step Change

- Read the commit log and other active work before you touch shared state, so that a push does not carry someone else's commits along.
- Edit only in a workspace you created, so that you never overwrite changes that another person or session has in progress.
- Search past experiments by config key and by name before you rerun one, so that you do not repeat work or miss a result that already answers the question.
- Write the output contract into the plan: grain, index, columns and units, so that every reader agrees on what a table means before anyone builds it.
- Put every input, the branch and the forbidden actions in a task brief, and ask for the input row counts back, so that a delegate cannot run against the wrong data or branch.
- Split work that needs different evidence into separate changes, so that a review of one kind of evidence does not hide a problem in another.
- Find who owns a failure before you fix it, so that you do not patch a symptom in code that its owner is still changing.
- Take any change to ground truth, a metric or an approved decision to its owner, so that no one alters a number that others already rely on without agreement.
- Wait until the system of record shows an operational change before you rerun on it, so that you do not compute results on a state the data does not yet reflect.

## 2. Test First

- Run each new test on the unchanged code and see it fail, so that you know the test can catch the bug it targets.
- Use non-default values in fixtures, so that a default that happens to match the expected result cannot hide a wrong calculation.
- Give every new branch a test that reaches it, so that untested code paths do not ship unchecked.
- Test boundaries and malformed input, including empty input, one row, missing values and cutoff dates, so that edge cases fail in the test and not in production.
- Run the project's full CI recipe, not a subset, so that a failure in a check you skipped does not reach the shared branch.
- Run once on a real data slice before review, so that rounding and name collisions appear, because unit tests on small fixtures usually miss them.
- Test a metric on a known-bad case before you trust it, so that a metric that always reports success cannot pass unnoticed.
- Read [unit-tests.md](../../coding/references/unit-tests.md) for the test structure, fixtures and mocking rules.

## 3. Debug From the Cause

- Read the code from where a value is made to where it is used, before you name a cause, so that you trace the real path and not the path you expect.
- Call a cause a hypothesis until code, a measurement or the data owner confirms it, so that a guess does not turn into a fix.
- Name the strongest rival explanation and run the check that separates the two, so that you do not confirm your first idea by default.
- Fix bad input at its source rather than clipping it downstream, so that every reader gets the same corrected value.
- Reproduce the failure on the smallest real data slice and trace one entity end to end, so that the fault shows without noise from the rest of the data.
- Rule out the comparison itself, including row order, forecast horizon and units, before you call a difference a bug, so that a mismatched setup does not look like a defect.

## 4. Verify Before You Say It Is Done

- Rerun the pass test yourself before you accept "done", so that you rely on a result you saw rather than a report.
- Rerun the tests in a fresh detached checkout of `HEAD` before merge, so that uncommitted or ignored files cannot hide a break.
- Make a check fail when its success signal is missing, so that an empty result does not pass as a clean one.
- Run the real pipeline end to end, including the downstream readers, so that a change that passes unit tests but breaks a consumer is found.
- Diff a merge, a sync or a generated config against what you intended, so that an unnoticed side effect is caught before it ships.
- Scan every commit, not only the final tree, before a public push, so that a secret removed in a later commit does not stay in the history.
- Recheck statuses and recompute numbers when you write them, so that the text does not repeat a stale value.
- State each gain with its baseline, metric, period and run ids, so that a reader can reproduce the claim and see what it compares against.
- Reread the change description against the final diff, so that the description does not promise work the diff does not contain.

## 5. When Two Rules Conflict

| Conflict                | Rule A                                                        | Rule B                                                                  | Resolution                                                                             |
| ----------------------- | ------------------------------------------------------------- | ----------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Decide or ask           | Decide design choices inside the brief and record the sources | Ask before changing an approved decision, model, metric or ground truth | Decide within the brief; ask first when a change touches an approved input or a metric |
| Fail loudly or tolerate | Raise an error on any unexpected input                        | Count and log a normal gap                                              | Raise on the unexpected; count and log expected gaps, and name them in config          |
| Test or assert          | Write tests for production code                               | Use inline asserts in experiments                                       | Tests for production code and inline asserts for experiments; see each fail once       |
| Wait for CI or move on  | Never claim a green build before it finishes                  | Keep working while checks run                                           | Report the check as running, then continue                                             |
| Verify or delegate      | Look up evidence by default                                   | Hand reruns to a delegate                                               | Look up evidence first; rerun only when it is missing or surprising, in a fresh agent  |

## Sources

- Winters, T., Manshreck, T. and Wright, H. (2020). _Software Engineering at Google_, chapter "Unit Testing". O'Reilly. https://abseil.io/resources/swe-book
- Beyer, B. et al. (2016). _Site Reliability Engineering_, chapter "Postmortem Culture". O'Reilly. https://sre.google/sre-book/postmortem-culture/
