---
name: worktrees
description: Use when working on more than one branch at a time and each branch needs an isolated folder. Not for a single branch where changing branches in place is simpler.
---

# Worktrees

Give each branch its own folder with `git worktree`, so several branches stay open at once with no stashing and no cross-branch edits. Use it when you work on more than one branch at a time, for example while a pull request (PR) waits for review. For one branch at a time, plain `git switch` is simpler.

## 1. Rules

- **One worktree, one branch, one PR, one ticket:** never reuse a worktree for a second branch.
- **Keep `main` as a clean reference:** never commit in the `main` worktree; use it to run the stable code and produce baseline outputs.
- **Fetch before you branch:** start every new worktree from the latest `origin/main` or from its parent branch.
- **Start agents inside the worktree:** an AI agent launched in a worktree folder stays scoped to that branch.
- **Leave other people's worktrees alone:** never check out, reset or pull in a worktree you did not create; read another branch by ref (`git show <branch>:<path>`) or in your own detached worktree.

## 1a. Create safely

- Confirm the base branch and target branch before changing files.
- Create the worktree and branch together with `git worktree add -b <branch> <path> <base>`.
- Install dependencies and hooks required by the repository after creating the worktree.

## 2. Layout

Default: a normal clone stays on `main`, and every other branch lives in a sibling folder `<repo>.worktrees/<branch>`. The worktree folder sits beside the repo, never inside it, so recursive tools (`grep`, `ruff`, `pytest`, `git clean`) never scan another branch.

```
~/repos/
├── <repo>/                  # main checkout: stays on main, never edited
└── <repo>.worktrees/
    ├── <ticket>-short-description/
    └── <ticket>-other-task/
```

- **Exception, app-managed worktrees:** the Claude desktop app creates its own worktrees in `<repo>/.claude/worktrees/` and may recycle them. Leave those to the app; do not move them.
- **Folder name:** use the `<ticket>-short-description` slug, not a branch name with slashes (`claude/foo` would nest folders).

Variant, bare clone: keep the git database in `~/repos/<repo>.git` and add `main` as a worktree. Use it only if you want no main checkout at all.

```bash
git clone --bare <remote-url> ~/repos/<repo>.git
# A bare clone tracks no remote branches; without this line `origin/main` does not exist.
git -C ~/repos/<repo>.git config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"
git -C ~/repos/<repo>.git fetch origin
git -C ~/repos/<repo>.git worktree add ~/repos/<repo>.worktrees/main main
```

## 3. Create a Worktree

Name the branch and the folder alike, starting with the ticket id: `<ticket>-short-description`.

```bash
git -C ~/repos/<repo> fetch origin

# Branch whose PR targets main
git -C ~/repos/<repo> worktree add ~/repos/<repo>.worktrees/<branch> -b <branch> origin/main

# Stacked branch whose PR targets a parent branch
git -C ~/repos/<repo> worktree add ~/repos/<repo>.worktrees/<branch> -b <branch> <parent-branch>

# Read-only look at another branch, with no new branch
git -C ~/repos/<repo> worktree add --detach ~/repos/<repo>.worktrees/<name> origin/<other-branch>
```

## 4. Work in a Worktree

- **Install dependencies once per worktree:** each folder has its own virtual environment and build outputs.
- **Switch tasks with `cd`:** never `git switch` inside a worktree to reach another task.
- **Push with upstream on the first push:** `git push -u origin <branch>`, then open the PR against the branch the worktree was cut from.
- **Rebase a stacked branch when its parent merges:** `git rebase --onto origin/main <old parent tip> <branch>`, then retarget the PR to `main`.

## 5. Clean Up

Remove a worktree once its PR is merged or its work is abandoned and pushed. This deletes the local folder only; the branch history stays in git.

```bash
git -C ~/repos/<repo> worktree list
git -C ~/repos/<repo> worktree remove ~/repos/<repo>.worktrees/<branch>
git -C ~/repos/<repo> worktree prune   # drop records of folders deleted by hand
```

- **Run removal from outside the worktree:** a shell whose current folder is the worktree breaks, and git refuses to remove the branch it has checked out.
- **Check before you remove:** `git status` in the worktree must be clean, and `git log origin/<branch>..<branch>` must be empty; `worktree remove` refuses a dirty folder, and `--force` discards the changes.
- **Save outputs first:** copy any run output you still need out of the folder before removing it.
