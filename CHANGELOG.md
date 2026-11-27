# Changelog

What changed for a user of the `ds-lead` plugin, newest release first. A release is a Semantic Versioning tag `vMAJOR.MINOR.PATCH` on `main`; [CONTRIBUTING.md](CONTRIBUTING.md) says which number to bump. "Unreleased" lists what is merged to `main` but not yet tagged. Every pull request (PR) adds one line under Unreleased.

## Unreleased

- `make-deck`: new `Image` block puts a PNG, such as a `make-chart` histogram, in any chart region. The HTML embeds it, and the pptx centers it at its own aspect ratio, with its alt text and its source in the footer. `SKILL.md` gains a table of what a pptx reader can edit: "Edit Data" works only on the five chart kinds. ([#15](https://github.com/kamingfung/ds-lead/pull/15))
- New `docs/decisions.md` records repository-wide decisions with the options rejected and why. Its first entries explain why deck charts stay native PowerPoint charts and not `make-chart` pictures. `make-deck`: new tests fail when a chart kind lacks a label or a pptx builder. ([#14](https://github.com/kamingfung/ds-lead/pull/14))

## v1.1.0 (2026-11-27)

Docs, checks and fixes since the first release: no skill was removed or renamed.

- `workflows`: each workflow now opens with an arrow chain of its steps and a line for each branch, so an agent sees the path before the numbered steps.
- `make-chart`, `make-deck`: new `scripts/check_palette_sync.py`, run by pre-commit when `palette.css` or `theme.py` changes, fails when the 11 colors the deck and the charts share differ.
- `defaults` now covers only the challenge posture and reply style, so it loads less on every task. Parallel Work and Briefs moved into `defaults/references/delegation.md`; Remote Writes and Traceability moved into `write-pr` as "Push and Post" and "Tracker Issue" (its description now also triggers before a push or PR comment); the description is one case. `workflows` and `session` point to the new homes.
- New `hooks/` folder with an optional Claude Code hook, `ask_before_push.py`, that makes every `git push` and `gh pr` or `gh issue` write ask the user first; it backs the `defaults` rule "push only once a unit of work is complete" and does not turn on at install. `write-skill` now links `references/enforcement.md`, a table of which rule has which enforcer (hook, test, pre-commit, or judgment). New pre-commit check `scripts/check_skill_files.py` fails on a skill Markdown file over 200 lines or two tracked files with the same bytes. `coding` (Prove It Works) gains the rule "write a repeatable result as a script and run it". `write-skill` drops the section "Front Matter and Loading", which listed Claude and Kiro file formats, and the other Claude and Kiro wording and the section "Pointer files".
- `coding`: `python-pipeline.md` now points to the repository's English variant rule, matching `SKILL.md`.
- Removed every remaining mention of the deleted `check-backtest` skill: the README table, install line and workflow picture, `THIRD_PARTY_NOTICES.md`, and a broken link in `workflows` (step 5 now points to `write-pr`, Results). The README's "Customize colors and fonts" section no longer points to deleted deck files.
- `make-deck`: a waterfall now labels a decrease below its bar and an increase above it, in both the HTML and the `.pptx` renderer, as `make-chart` does; the example and gallery are regenerated.
- `coding`: the language rule now says to match the repository's English variant instead of requiring American English, and the logging examples say "step" for a pipeline unit. `plugin.json`: the author name is Ka Ming Fung.
- `plan-training`: the active lecture template sizes each phase as a share of the session, with minutes shown for a 50-minute class as an example.
- `plan-work`: step 1 now names the approver (the Accountable role in RACI) plus the people to consult and inform, and the plan template has `Consulted` and `Informed` lines.
- `make-chart`: removed `skills/make-chart/LICENSE`, a byte-identical copy of the root `LICENSE`.
- `write-skill`: new section "Write Skill Files Like Clean Code": name what a file does, keep one source of truth for values, avoid duplicate files, keep reference data with its owner, use a parameter for what varies, simplify, and check a claim before you write it.
- `coding`, `debrief`, `review-pr`, `solve`, `workflows`, `write-docs`, `write-pr`, `defaults`, `make-deck`: moved every citation out of the skill files into a `SOURCES.md` beside each skill, which lists which idea, number or quote comes from which source; the skill text no longer carries attributions, so the agent loads less. `write-skill` has the rule.
- `make-chart`: added `README.md` with the palette's provenance (Okabe-Ito hue roles, measured color distances) and the steps to change it; a test now fails when two series colors come too close under any color-vision simulation; the function list moved from `SKILL.md` into the `chart_style.py` docstring.
- `make-deck`: `render_pptx` writes the same bytes for the same deck, so a rebuild no longer shows `.pptx` files as changed.

## v1.0.0 (2026-11-27)

First release: 16 agent skills for data science work that ends in a decision.

- **Plan, frame and deliver:** `plan-work`, `plan-training`, `solve`, `debrief`, `make-report`, `make-chart` and `write-docs`. Each skill cites its public sources in a Sources section.
- **Decks:** `make-deck` builds a deck from one `Deck` spec with 24 layouts. An HTML renderer and a native, editable `.pptx` renderer (python-pptx) place the same boxes. Every number carries its source into the footer and the `Backup · Sources` slides.
- **Charts:** `make-chart` gives 15 matplotlib recipes on a colorblind-safe palette, with axis and gridline rules.
- **Build and review:** `coding`, `worktrees`, `review-pr` and `write-pr`.
- **How the agent works:** `defaults`, `workflows`, `session` and `write-skill`.
- Examples: `examples/global-food-supply` (a deck, a `.pptx` and a one-page report built from public Our World in Data CSVs), `examples/deck-gallery` (every layout) and `examples/make-chart` (every recipe).
- `scripts/check_skill_refs.py`: a pre-commit check that fails when a skill points to a skill that does not exist.
- pre-commit config: ruff, prettier and gitleaks. MIT license.
