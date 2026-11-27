# Contributing: changelog and releases

These steps are for anyone who changes this repository, a person or an AI agent. `CHANGELOG.md` at the repo root tells a plugin user what changed. A release is a git tag on `main` with a GitHub release of the same name.

## Terms

- **Release tag:** `vMAJOR.MINOR.PATCH` (Semantic Versioning, semver.org), for example `v1.2.0`. Bump MAJOR when a skill is removed or renamed, or a trigger change stops a skill from loading; MINOR when a skill, reference or kit layout is added; PATCH when a rule is reworded or fixed.
- **Plugin version:** the `version` field of `plugin.json`. It takes the release tag without the `v`, for example `1.2.0`.
- **Changelog line:** one bullet under `## Unreleased`: what changed for a user, then the pull request (PR) link, e.g. `- \`review-pr\`: verdict phrases and one summary layout.`.

## Every PR

1. Branch from `origin/main`.
2. Make the change.
3. Add one changelog line at the top of `## Unreleased`. Write what a user notices, not the files you touched. Gate: the line names the change and the PR link (add it after you open the PR).
4. Run `python3 scripts/check_changelog.py --base origin/main`. Gate: it prints `OK`. The same check runs on `git push` once you ran `pre-commit install --hook-type pre-push` in your clone.
5. Open the PR against `main`. Gate: the PR diff shows `CHANGELOG.md`.

Decision: a PR with no user-visible effect (a typo, a test) still gets a line; keep it short. Never skip the check with `--no-verify`.

## Every release

The maintainer runs a release. Agents draft the steps and stop before the merge and the tag.

1. Pick the tag. Run `git fetch --tags` and `git tag -l 'v*' --sort=-v:refname | head -1` for the latest release. Read the Unreleased lines and bump by the rule under Terms. Gate: the new tag is not in the list.
2. Branch `release-<tag>` from `origin/main`.
3. In `CHANGELOG.md`, rename `## Unreleased` to `## <tag> (YYYY-MM-DD)` and add a new empty `## Unreleased` above it. Gate: `## Unreleased` is empty and every moved line sits under `## <tag>`.
4. Set `"version"` in `plugin.json` to the tag without the `v`. Gate: `git diff` shows only `CHANGELOG.md` and `plugin.json`.
5. Open a PR from `release-<tag>` to `main`, and merge it. (Maintainer.)
6. Tag the merge commit and publish the release: `gh release create <tag> --target main --title <tag> --notes "<the lines under ## <tag>>"`. (Maintainer.) Gate: `gh release view <tag>` shows it.
