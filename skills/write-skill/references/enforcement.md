# Enforcement Table

One row per rule that something other than the agent's memory should hold. `write-skill` asks for this table in section "Fix a Repeated Mistake at the Strongest Level". Read it when a mistake repeats, to see whether the rule has an enforcer. Add a row in the same change as a new check.

Enforcer values: **design** (the mistake cannot happen), **hook** (Claude Code runs it), **pre-commit** or **pre-push** (git runs it), **test** (pytest), **script** (a checker the agent runs by hand), **none: judgment** (no check can decide), **none: manual** (a check exists, but nobody runs it automatically).

| Rule                                                       | Where the rule lives                             | Enforcer                                                                                                  |
| ---------------------------------------------------------- | ------------------------------------------------ | --------------------------------------------------------------------------------------------------------- |
| A skill pointer names a skill that exists                  | all skills                                       | pre-commit: `scripts/check_skill_refs.py`                                                                 |
| Every PR adds a changelog line                             | `CONTRIBUTING.md`                                | pre-push: `scripts/check_changelog.py`                                                                    |
| No secret is committed                                     | none (no skill rule)                             | pre-commit: gitleaks                                                                                      |
| Chart series colors stay apart for every color-vision type | `make-chart`                                     | test: `skills/make-chart/test_chart_style.py`, `test_categorical_colors_stay_apart_for_every_vision_type` |
| A rebuilt `.pptx` has the same bytes                       | `make-deck`                                      | test: `test_same_deck_renders_to_identical_bytes`                                                         |
| A deck number comes from data and carries its source       | `make-deck`                                      | design: the kit fills every number from a `Num` with a source                                             |
| Push only once a unit of work is complete                  | `defaults`, Remote Writes                        | hook (optional): `hooks/ask_before_push.py` makes a person decide; completeness is none: judgment         |
| A skill file stays within 200 lines                        | `write-skill`, Sizing Guidelines                 | pre-commit: `scripts/check_skill_files.py`                                                                |
| No two tracked files are byte-identical                    | `write-skill`, Write Skill Files Like Clean Code | pre-commit: `scripts/check_skill_files.py`                                                                |
| Soundness before style in a review                         | `review-pr`, `references/standard.md`            | none: judgment                                                                                            |
| A report title states the answer with its key number       | `make-report`                                    | script: `scripts/check_report.py` warns on the title; the agent runs it by hand                           |

## Next candidates

A rule marked "none" has no enforcer yet. Harden one when it is broken a second time, and run the new check on that real case first.
