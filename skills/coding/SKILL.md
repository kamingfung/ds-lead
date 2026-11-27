---
name: coding
description: Use when writing, changing or reviewing code, tests, log calls, parameters or schemas, or sizing a change; for prose, use skill `write-docs`.
---

# Coding

These rules apply to every coding task. Language-specific detail lives in [references/python-pipeline.md](references/python-pipeline.md), [references/unit-tests.md](references/unit-tests.md) and [references/logging.md](references/logging.md).

## Agree the Goal First

Turn the request into a goal that a test or command can check. Write your assumptions down. When a request can mean two things, name both and ask. Do not choose silently. When you cannot tell what is wanted, stop, say which part confuses you, and ask before you write code. When a simpler approach than the one requested exists, say so.

| Request                                   | Checkable goal                                                                                  |
| ----------------------------------------- | ----------------------------------------------------------------------------------------------- |
| The weekly total for one region is wrong. | A test that loads that region's orders fails now and passes after the fix.                      |
| Make the regional rollup faster.          | The benchmark runs under 60 seconds and the output matches the saved hash.                      |
| Clean up this module.                     | Name the cleanup, such as one duplicate helper. `git grep` finds one definition and tests pass. |
| Accept a new input format.                | A test reads a semicolon sample and returns the same rows as the comma sample.                  |

For multi-step work, write a short plan with one check per step.

## Build Only What Was Asked

- Do not add a feature, option, abstraction or single-implementation interface that nobody asked for.
- Skip a factory that builds one kind of object, a config key whose value never changes, a setting that serves one case, and a parameter no caller passes.
- Share code at the second caller when both use it unchanged. Wait for a third caller when sharing needs a new parameter or flag.
- Handle errors that can happen. Skip handling for states that cannot happen.
- When a much shorter version works, write the shorter version.
- PEP 20 says that "simple is better than complex" (Peters, 2004).
- Google's review guidance asks reviewers to flag code more generic than the task needs (Google, "What to look for in a code review").

## Change Only What the Task Needs

- Trace every changed line back to the request. Match the style of the file you edit, and follow PEP 8 (van Rossum, Warsaw and Coghlan, 2001) where the file is silent.
- Leave unrelated code alone, including its comments and formatting. Mention dead code, but do not delete it.
- Do not refactor working code that the task does not need changed.
- Remove imports, variables and functions that your change leaves unused.
- After a deletion, `git grep` each name, config key, fixture and doc link it used. Delete what nothing reads any more.
- Delete code your change turns into a no-op, such as a fallback that can no longer run.
- Aim for one self-contained change. Google treats about 100 changed lines as reasonable and about 1000 as usually too many (Google, "Small CLs").

## Put Each Explanation in the Right Place

Use the first that carries the point.

1. A clear name.
2. A short inline comment on a line a reader cannot follow.
3. A docstring that states why the code exists and how to call it.
4. A doc, for stable, reproducible facts. Branch-specific notes go in the PR description or the changelog.

The detail sits in [python-pipeline.md, Where explanation belongs](references/python-pipeline.md#where-explanation-belongs).

- Keep ticket ids and dates out of code, comments, docstrings, test names and YAML. Put them in the commit message and the changelog.
- Before a comment, docstring, doc or PR description says what code does, read the code path and `git grep` the name. Never describe behavior the code lacks.
- When text says who reads a column, dataset or parameter, name the reader you found in the code.

## Prove It Works

- A bug fix starts with a test that fails on the current code, then passes after the fix.
- A refactor passes the same tests before and after.
- Check that each test fails when the code it covers is broken (Google, "What to look for in a code review").
- Put new tests in the same change as the logic they cover (Google, "Small CLs").
- Compare outputs on `main` and on the branch before review when a change can move them.
- A pure refactor or deletion shows that outputs are unchanged.

## American English

Write American English in code, comments, commit messages and new names.

- Use -ize and -ization, as in "normalize".
- Use -or, as in "behavior".
- Use one l before a suffix, as in "modeled" and "labeled".
- Use -er, as in "center".
- Words such as analysis, basis, exercise and surprise are spelled the same in both. Do not change them.
- Keep an existing identifier's spelling, even when British. A rename is a separate change.

## Sources

- Peters, T. PEP 20, "The Zen of Python" (2004). https://peps.python.org/pep-0020/
- van Rossum, G., Warsaw, B. and Coghlan, N. PEP 8, "Style Guide for Python Code" (2001). https://peps.python.org/pep-0008/
- Google. "Small CLs", Google Engineering Practices Documentation. https://google.github.io/eng-practices/review/developer/small-cls.html (CC BY 3.0)
- Google. "What to look for in a code review", Google Engineering Practices Documentation. https://google.github.io/eng-practices/review/reviewer/looking-for.html (CC BY 3.0)
