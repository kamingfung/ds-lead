# Hooks (Claude Code only, optional)

A skill is a rule the agent can skip. A hook is a check Claude Code runs itself, so it holds even when the agent forgets the rule. These hooks work in Claude Code only. The skills do not need them, and nothing here turns on at install.

## ask_before_push.py

Makes every `git push` and every `gh pr` or `gh issue` write (create, comment, review, merge, edit, close, ready, reopen, lock, unlock, delete, transfer, pin, unpin) ask the user first. It checks each command in a chain (`a && git push`) and skips env assignments and wrappers such as `sudo` in front of it. It answers `ask`, not `deny`, so one click approves a push you want. A dry run (`git push -n`) passes.

It backs the rule "push only once a unit of work is complete" in skill `write-pr`, section Push and Post. The hook cannot judge whether the work is complete. It makes sure a person decides.

Turn it on by adding this to `~/.claude/settings.json` (all projects) or `.claude/settings.json` (one project), with the path to your clone of this repository:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /path/to/ds-lead/hooks/ask_before_push.py",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

Check it: `python3 hooks/ask_before_push.py --selftest` prints `selftest ok`.

Limits: the hook reads the command text. A push hidden in a script (`./release.sh`) or behind `xargs` passes. Text in quotes that looks like a push (`git commit -m "x; git push"`) also asks, which errs on the safe side. Pair it with a branch protection rule for a branch that must never take a direct push.
