---
name: write-skill
description: Use when creating, editing or reviewing a skill, steering file or agent rule file - its size, structure, triggers and overlap - or when a mistake an agent repeats needs a fix.
---

# Skill Standards

## Purpose

A skill is a scoped instruction set that shapes agent behavior. Every matching interaction loads it as context tokens, so every line has a cost.

"Skill" here means any scoped instruction file an agent loads: a Claude skill, a Claude rule file, or a Kiro steering file ("steering file" is Kiro's name for a skill).

## When to Create a New Skill

Create one when the agent repeats a mistake or misses a convention. First rule out a design change, check or test (section Fix a Repeated Mistake at the Strongest Level). A skill is a fix for a recurring pattern, not a preemptive rulebook.

Use these instead of a new skill:

- Chat, for a one-off instruction.
- Nothing, for facts the model already knows (Python syntax, the pandas API).
- The existing skill, for a rule it already holds.

## Fix a Repeated Mistake at the Strongest Level

When the same mistake happens a second time, use the first fix in this list that works:

1. **Change the design.** Make the mistake impossible: keep one supported way to do each task and one source for each value. Delete the old way, so no agent copies it.
2. **Add a check.** A lint rule, hook, schema check or CI step that fails on the mistake. Its error message says what to do instead.
3. **Add a test.** A test that fails when the behavior breaks, and still passes when only the internals change.
4. **Write a rule.** A skill line, only for a judgment call that no check can make.

- Run a new check on a real earlier case of the mistake, and show that it fails.
- Keep one table per repository, in a skill that loads only on request, with one row per rule and what enforces it: a hook, a test, a CI step, or "none: judgment".
- When a rule marked "none" is broken again, move it to a stronger fix in the same change.
- Delete a rule when its mistake can no longer happen.

## Structure

Every skill must have:

1. **Front matter** in the form of the tool that loads it (table below)
2. **Exactly one `#` heading** that identifies the domain
3. **Sections** that gather related rules, each no more than 15 lines
4. **Examples** only where a rule stays unclear without them (a good and a bad pattern)

````markdown
---
paths:
  - "src/**/*.py"
---

# [Domain] Standards

## Rule Group

- Rule as imperative sentence
- Rule as imperative sentence

## Code Pattern (only if needed)

\```python

# Good

...

# Bad

...
\```
````

## Front Matter and Loading

Each tool names and loads a skill in its own way. The rules in this file apply to all of them.

| Tool               | File                                                                    | Loads when                                                                                                 |
| ------------------ | ----------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Claude skill       | `skills/<name>/SKILL.md` with `name` and `description`                  | The description matches the task. The description is always in context; the body loads only after a match. |
| Claude rule        | `.claude/rules/*.md` with a `paths:` glob list                          | A matching file is in context. With no `paths:`, always.                                                   |
| Kiro steering file | `.kiro/steering/*.md` with `inclusion: always`, `fileMatch` or `manual` | By that mode; `manual` loads only when the user names it with `#name`.                                     |

- Prefer scoped loading: a specific description, a `paths:` glob, or `fileMatch`. Always-on text costs tokens on every interaction; keep it to one or two files.

## Sizing Guidelines

- **Target: 50–120 lines.** Long enough to help, short enough to fit in context beside the user's own code.
- **Hard ceiling: 200 lines.** A file over this limit gets split by sub-domain, or its examples move to a reference file beside it.

## Writing Rules

- **Imperative voice.** Write "Format logs with lazy % arguments," not "You may want to format logs lazily."
- **Cite in `SOURCES.md`, not in the skill.** Put each source in `skills/<name>/SOURCES.md` beside the skill, with the idea, number or quote it supports. Leave attributions out of the skill text, because the agent never needs them.
- **One rule per bullet.** Split any bullet that joins two rules with "and".
- **Grep before you add.** Search the existing skills for the rule; if one holds it, point to that file by name.
- **Examples must justify their length.** Add a good/bad pair only when the rule is truly unclear. Leave examples out of obvious rules, such as "add type hints."
- **Domain-specific over generic.** "Log customer, region, and period in WARNING messages" beats "Include context in log messages."

## Review Pass

Run this pass on every new or changed skill before you push it, one sentence at a time. Each point ends on a check you can answer yes or no. It follows Matt Pocock's [writing-for-agents](https://github.com/mattpocock/skills/tree/main/skills/productivity/writing-for-agents) skill; the wording here is our own.

1. **The description is a pointer.** It is always in context, so prune it hardest. It names the skill and lists each distinct case that should trigger it, with the key word first. Give one trigger per case: two words for the same case are one trigger written twice. Check: every word in the description either names the skill or adds a case.
2. **Choose who invokes it.** Keep a model-facing trigger (a description, a `fileMatch` pattern) only when an agent must reach the skill by itself. A skill people only call by hand loads by name and costs no context. Check: the skill loads the same way in every AI tool the repo supports, or the repo changelog says why not.
3. **Rank the content.** Steps come first, in order. Reference that the agent reads on demand comes next. What only some cases need moves to a sibling file behind a pointer. A fact sits in the step that uses it. Check: no reference section comes before the first step.
4. **End every step on a pass condition** that is checkable and exhaustive: "every changed function is listed", not "list the changes". Check: each stage ends with a `Pass:` line or a step whose result can be counted.
5. **Use a leading word.** Where a phrase is spelled out in several places, use one word the model already knows, and repeat that word. Coin a word only when you also define it. Check: every coined word has a definition at first use.
6. **State the target, not the ban.** Write what to do. Keep a prohibition only as a hard guardrail, next to the positive target. Check: each "never" or "not" has the target beside it, or guards secrets, data or prod.
7. **One source of truth.** Each meaning lives in one place. Do not copy what one lookup answers: a script name, a config value, a schedule, the output of `--help`. Point to the file that holds it. Check: no environment name, region, job size or schedule time is typed out when a config file holds it.
8. **Hunt no-ops.** For each sentence, ask whether deleting it changes what the agent does. If not, delete it; history goes in the changelog. Two people who disagree settle it by running the skill, not by debate. Check: every sentence changes an action.
9. **Cut sprawl.** A file over the size limit moves reference behind pointers or splits by case. Split a run of steps only where the later steps make the agent rush the current one. Check: the file and each section are within the size limits in this file.

### Pointer files

- A pointer skill points straight at the file that holds the rules: the guide, or the steering or agent file. It never points at a file whose only content is an include of another file, and it never teaches one tool's include syntax to another tool.
- When one guide serves several AI tools, give each tool its own trigger for the same cases, for example a description for one and a `fileMatch` pattern for the other.

## Anti-Patterns

- **The always-on firehose.** Several `always` files that add up to 800+ lines. Scope most rules to the files they touch.
- **The aspirational rulebook.** Rules the team does not follow in practice. A skill records what the team does now, not what it hopes for.

## Maintenance

- Revisit a skill once it no longer prevents mistakes, either because the agent learned the rule or because the rule is out of date.
- Rerun the Review Pass on a skill each time you change it.
