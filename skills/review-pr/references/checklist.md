# Review Checklist

Walk every section below and mark it pass, finding or not applicable. Reviewer conduct, including posture, severities and review rounds, is in [standard.md](standard.md), Review Like a Referee.

For the detailed rules, see [python-pipeline.md](../../coding/references/python-pipeline.md), [unit-tests.md](../../coding/references/unit-tests.md), [logging.md](../../coding/references/logging.md), and [write-docs](../../write-docs/SKILL.md).

## Design

- [ ] The change belongs in this code base and fits the pipeline it touches now.
- [ ] The approach is the simplest one that solves the stated problem.
- [ ] No speculative feature or abstraction exists with only one caller.
- [ ] Only the lines the change needs are modified.
- [ ] The PR states its assumptions and its success criteria.

## Functionality and Results

- [ ] The behavior matches the stated intent, including edge cases a user would reach.
- [ ] A change that can move outputs shows before-and-after results for `main` and the branch, with run ids a reviewer can open.
- [ ] Deleted config keys, catalog entries, fixtures, helpers and doc links leave no orphans behind.
- [ ] Nothing reads or writes a shared dataset in a way its other users would not expect.

## Complexity and Style

- [ ] Each function body stays near 30 lines, or the PR explains why it is longer.
- [ ] No function takes more than five arguments or a flag parameter that switches its behavior.
- [ ] Functions are pure: they change no input in place and use no mutable default arguments.
- [ ] Guard clauses handle invalid input before the main path runs.
- [ ] Every signature and every new local variable has a type hint.
- [ ] A call that passes more than two arguments uses keyword arguments.
- [ ] A value used by one function stays local to that function.

## Naming and Comments

- [ ] Names are clear enough to read without decoding abbreviations.
- [ ] Public functions have Google-style docstrings with `Args:` and `Returns:`, and a returned DataFrame lists its output columns.
- [ ] Comments explain why code exists, and the code itself shows what it does.
- [ ] No ticket ids or dates appear in code, comments, tests or doc headings.
- [ ] Every claim that a comment or doc makes about readers or behavior was checked in the code.

## Data Integrity

- [ ] Schema checks run at each step boundary.
- [ ] Every join names its keys, its join type and its expected cardinality, enforced with pandas `validate`.
- [ ] Empty input returns an empty frame that still has the output columns.
- [ ] Week numbers appear with their ISO year.
- [ ] Fills, shifts and "latest" picks run within each entity group.

## Tests

- [ ] Each test follows the Arrange, Act, Assert layout and uses realistic values, not placeholders such as `foo`.
- [ ] Edge cases are covered: empty input, one row, missing values and boundaries.
- [ ] Each new branch has its own test.
- [ ] No existing test is edited, deleted or skipped to match new output unless the commit message gives the reason.
- [ ] DataFrames are compared with `pd.testing.assert_frame_equal`, not mocked.

## Errors and Logging

- [ ] Each `except` clause names the specific exception types it handles.
- [ ] Error messages name the dataset and the bad input.
- [ ] No silent fallback exists, and a deliberate fallback logs the row count it touched.
- [ ] Code uses the project's shared logger with lazy `%` formatting, and warnings name the entity, the time window and the row count.
- [ ] No secrets or personal data appear in logs.

## Docs

- [ ] Model, dataset and config docs change when behavior, parameters or datasets change. A new config value says where it is set and how to update it.
- [ ] New terms reuse existing terms or get defined at first use.
- [ ] Results tables sit in the PR description or a dated changelog, not in stable docs.

## Before Merge

- [ ] `pre-commit run --all-files` passes.
- [ ] The test suite passes.
- [ ] The PR holds no unrelated refactor.
- [ ] Review replies go out as one round with one summary.
