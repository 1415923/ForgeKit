# Worktree Playbook

Purpose: define safe, reviewable use of Git worktrees for parallel tasks, experiment branches, and AI multi-session collaboration.

This playbook is guidance only. It is not a worktree runner, scheduler, agent orchestration system, automatic merge flow, automatic PR flow, or unattended automation.

## When to Use

Use a worktree when:

- two tasks must proceed in parallel without sharing a dirty working tree
- an experiment needs an isolated branch and directory
- Maker and Checker need separate views of the same repository
- a risky refactor needs an easy way to compare against the base branch
- multiple AI or human sessions must avoid overwriting each other's files

## When Not to Use

Do not use a worktree when:

- the current task is small and can be completed safely in the main working tree
- the repository has unresolved dirty changes that have not been reviewed
- the base branch is unclear
- branch naming, cleanup, or validation ownership is unclear
- secrets, deploy, CI, migrations, or production operations are involved without explicit user confirmation
- the user has not explicitly asked to create or use a worktree

## Naming Convention

Recommended pattern:

- Worktree path: `../<repo-name>-wt/<change-id-or-topic>`
- Branch name: `work/<change-id-or-topic>`

Examples:

- `../my-app-wt/20260616-search-refactor`
- `work/20260616-search-refactor`

Use short, scoped names. Avoid user names, secrets, ticket text with private data, or machine-specific absolute paths in template documentation.

## Worktree Creation Checklist

Before creating a worktree, confirm and state:

- user explicitly requested worktree use
- `git status --short` is clean in the source working tree
- base branch
- worktree path
- branch name
- allowed paths
- forbidden paths
- validation command
- cleanup plan
- whether Maker, Checker, or both will use the worktree

If any item is unclear, stop and ask.

## Recommended Commands

Inspect state:

```bash
git status --short
git branch --show-current
git worktree list
```

Create an isolated worktree after explicit confirmation:

```bash
git worktree add -b work/<topic> ../<repo-name>-wt/<topic> <base-branch>
```

Check the isolated worktree:

```bash
cd ../<repo-name>-wt/<topic>
git status --short
```

Remove a completed worktree only after explicit confirmation:

```bash
git worktree remove ../<repo-name>-wt/<topic>
```

Delete a branch only after explicit confirmation:

```bash
git branch -d work/<topic>
```

Do not automatically merge, push, delete branches, remove worktrees, create PRs, or start agents.

## Maker / Checker Usage

Maker may use a worktree to implement a scoped change without disturbing the main working tree.

Checker may use a separate worktree or the main working tree to review a clean diff, validation evidence, risks, and document sync.

Worktree use does not replace Maker / Checker evidence. Record the worktree path, branch, validation command, and findings in `.forgekit/changes/<change-id>/review.md` or `.forgekit/docs/work-log.md`.

## Cleanup

Before cleanup, record:

- final status
- validation result
- files changed
- whether changes were merged, abandoned, or still pending
- remaining branch and worktree paths
- next owner or next step

Cleanup must be explicit. Do not automatically remove a worktree, delete a branch, merge, push, or create a PR.

## Safety Rules

- Do not create a worktree unless the user explicitly asks.
- Confirm the source working tree is clean before creation.
- State base branch, worktree path, branch name, allowed paths, validation command, and cleanup plan before creation.
- Do not use worktrees to bypass forbidden paths.
- Do not write secrets or private local paths into managed docs.
- Do not automatically merge, push, delete branches, remove worktrees, create PRs, or start agents.
- Write results to `.forgekit/docs/work-log.md` or the scoped change review.
