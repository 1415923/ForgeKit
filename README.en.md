# ForgeKit

中文文档: [README.md](README.md)

ForgeKit is a **local project-governance scaffold** for AI coding tools such as Codex and Claude Code.

It does not generate your business framework, deploy your system, or operate Git on your behalf. Instead, it puts project boundaries, task sources, current state, verification evidence, risks, and handoff rules inside the repository so an AI agent can work in a **reviewable, verifiable, and recoverable** process.

```text
ForgeKit = project entry + on-demand Skills + current project facts + safe checks and migrations
```

## What it solves

AI coding usually fails because context and authority drift, not because the model cannot write code:

- the agent edits the wrong directory or crosses a project boundary;
- task sources, previous decisions, and unfinished work are forgotten;
- implementation is claimed complete without reliable verification;
- context compaction, tool switching, or handoff breaks continuity;
- review, repair, commit, push, and release permissions get mixed together;
- upgrades overwrite project-specific customization.

ForgeKit anchors those facts in local files and checks. It is a workflow scaffold, not an agent runtime or background automation platform.

## Quick start

### 1. Initialize or sync a target project

Run from the ForgeKit repository.

Windows PowerShell:

```powershell
python .\scripts\forgekit-project.py --target "D:\path\to\project"
```

macOS / Linux:

```bash
python3 ./scripts/forgekit-project.py --target "/path/to/project"
```

The unified entry inspects the target before choosing an action:

| Target state | ForgeKit behavior |
| --- | --- |
| ForgeKit is not installed | Show an initialization plan |
| Already current | Report `up-to-date` |
| Supported older version | Show checks and an upgrade plan before applying |
| Outer ForgeKit is too old | Stop and ask you to update ForgeKit first |
| Legacy or unsafe-to-migrate project | Treat it as existing-project adoption instead of forcing an upgrade |

ForgeKit is plan-first. Safe writes require interactive confirmation or explicit `--yes`.

Formal safe migrations are supported for projects initialized with v0.36.0 or later and containing `.forgekit/state.json`. Earlier projects should start with a read-only handover review.

### 2. Start the AI tool from the project root

Codex:

```powershell
cd D:\path\to\project
codex
```

Claude Code:

```powershell
cd D:\path\to\project
claude
```

### 3. Recover project context before editing

Codex:

```text
Read AGENTS.md and follow the project-local ForgeKit rules. First summarize the project boundary, current task, available evidence, risks, and recommended next step. Do not edit files yet.
```

Claude Code:

```text
Read CLAUDE.md and follow the project-local ForgeKit rules. First summarize the project boundary, current task, available evidence, risks, and recommended next step. Do not edit files yet.
```

## How v0.45.0 works

v0.45.0 separates always-on boundaries from conditional workflows:

- `AGENTS.md` / `CLAUDE.md` keep only always-on boundaries, authorization, and routing rules;
- root `skills/` is the semantic authority for nine shared Skills;
- generated `.agents/skills/` is synchronized deterministically;
- `.claude/skills/` remains a Claude-specific adapter, not a mechanical copy.

### Nine on-demand Skills

| Skill | Use it for |
| --- | --- |
| `project-init` | Initialize a new project that does not use ForgeKit yet |
| `project-bootstrap-fill` | Fill evidence-backed placeholders in an initialized project |
| `handover-review` | Inspect an existing project read-only before deciding what to change |
| `document-backfill` | Backfill factual documentation from implementation and evidence |
| `large-change-planning` | Freeze scope, authorization, acceptance, non-goals, and rollback for high-impact work |
| `code-review` | Review existing implementation, diff, tests, and evidence read-only |
| `security-review` | Review a real security surface without turning every code change into a security review |
| `release-check` | Inspect an explicit release candidate without treating every commit as a release |
| `project-suitability` | Assess whether ForgeKit fits a project without initializing it automatically |

These Skills are not a mandatory pipeline. Invoke only what the task and its actual impact require.

Review, assessment, and planning are read-only by default. A finding does not grant repair permission. Local writes, commit, push, tag, publish, release, and deploy require separate authorization.

Risk follows impact, not file or line counts. Consider:

- trust-boundary changes;
- external or irreversible actions;
- data, permission, or public-interface impact;
- rollback difficulty;
- evidence uncertainty.

## Common prompts

More examples are available in the generated project:

```text
.forgekit/docs/usage-playbook.md
```

Useful short prompts:

| Goal | Copyable prompt |
| --- | --- |
| Start today’s work | `Read the current task, recent progress, risks, and verification entry points. Recommend the next step before editing files.` |
| Adopt an existing project | `Use $handover-review to inspect <project-root> read-only. Report boundaries, current state, risks, and adoption advice without initializing or repairing automatically.` |
| Fill an initialized project | `Explicitly invoke $project-bootstrap-fill. Fill only evidence-backed placeholders and preserve customization.` |
| Backfill factual docs | `Explicitly invoke $document-backfill and make the smallest evidence-backed update from implementation and verification evidence.` |
| Plan a high-impact change | `Explicitly invoke $large-change-planning and freeze scope, authorization, acceptance, non-goals, and rollback.` |
| Review code | `Use $code-review to inspect the current diff, tests, and evidence read-only. Do not auto-fix.` |
| Review security | `Use $security-review for the explicit security surface. Report evidence, risk, and repair ownership without auto-fixing.` |
| Check a release candidate | `Use $release-check to inspect versions, migrations, artifacts, and gates. Do not publish.` |
| Assess suitability | `Use $project-suitability to assess ForgeKit fit read-only. Do not initialize automatically.` |
| Save progress | `Write back only confirmed status, verification, risks, and next steps to the responsible documents.` |
| Before compaction or handoff | `Create a minimal checkpoint and list the files the next session should read first.` |
| Before commit | `Check the diff, verification, independent review, risks, and required writeback. Do not commit automatically.` |

## Upgrade an existing project

Most users should continue using the unified entry:

Windows:

```powershell
python .\scripts\forgekit-project.py --target "D:\path\to\project"
```

macOS / Linux:

```bash
python3 ./scripts/forgekit-project.py --target "/path/to/project"
```

For migration troubleshooting, use the lower-level commands:

```bash
python scripts/forgekit-upgrade.py check --repo-root <project>
python scripts/forgekit-upgrade.py plan --repo-root <project>
python scripts/forgekit-upgrade.py apply --safe --repo-root <project>
```

| Command | Purpose |
| --- | --- |
| `check` | Check version and migration eligibility without writing |
| `plan` | Print the migration plan without writing |
| `apply --safe` | Execute only migration actions marked safe |

### Upgrade from v0.44.1 to v0.45.0

The formal migration classifies every managed target:

| State | Behavior |
| --- | --- |
| `stock` | Matches the previous baseline and can be updated safely |
| `custom` | Locally modified; preserve it and require manual merge |
| `unknown` | Cannot be identified reliably; do not overwrite |
| `missing` | Handle according to the action contract |
| rollback | Restore the state from the beginning of this upgrade |

After upgrading, start a new AI session or ask the current session to reload the entry and current-task documents before continuing.

## Multi-project workspaces

Multi-project support is optional. ForgeKit does not enable it or split existing documentation automatically.

| Layer | Purpose |
| --- | --- |
| Workspace Docs | Cross-project tasks, integration state, and overall risks |
| Project Capsule | Local tasks, tests, and risks for one long-running subproject |
| Repo | Business code; not a third task-fact source |
| Artifact | Reports, logs, build outputs, and test evidence |
| Archive | Historical material; not current truth |

A common adoption path is:

```text
Register a project as workspace-only first.
Move only long-running independent projects to project-capsule.
```

Create a minimal Project Capsule:

```powershell
python .\scripts\bootstrap-project-capsule.py plan --repo-root "D:\path\to\workspace" --project backend
python .\scripts\bootstrap-project-capsule.py apply --repo-root "D:\path\to\workspace" --project backend --confirm
```

This does not split workspace docs, migrate tasks, or move business repositories.

## Generated content

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | Codex project entry |
| `CLAUDE.md` | Claude Code project entry |
| `.agents/skills/` | Project-local on-demand Skills |
| `.codex/` | Codex rules, commands, and optional configuration |
| `.forgekit/state.json` | Current ForgeKit version and feature state |
| `.forgekit/project-boundary.yml` | Project boundary and write policy |
| `.forgekit/workspace-map.json` | Optional multi-project boundary map |
| `.forgekit/docs/` | Current tasks, sources, verification, risks, handoff, and toolchain facts |
| `.forgekit/projects/` | Optional Project Capsules |
| `.forgekit/changes/` | Proposals, tasks, verification, and review for medium/high-impact changes |
| `.forgekit/archive/` | Searchable historical evidence |
| `scripts/` | Initialization, upgrade, integrity-check, and archive tools |

Existing business `docs/` is treated as read-mostly evidence by default. ForgeKit does not place governance templates there automatically.

## When to write back documentation

Writeback is event-triggered, not “after every edit”.

| Situation | Recommendation |
| --- | --- |
| Typo, temporary experiment, unconfirmed exploration | Do not update ForgeKit governance docs |
| Task-state change, confirmed root cause, new risk, useful verification | Create a minimal checkpoint |
| Commit, handoff, archive, release preparation | Perform closure writeback |
| Predictable compaction or session switch | Save the current goal, conclusions, risks, verification, and next step first |

Skipping governance-doc writeback for a micro change does not prohibit authorized edits to business code, README files, comments, tests, or configuration.

## Safety boundaries

ForgeKit does not automatically:

- generate Spring, React, FastAPI, or other business-project templates;
- install dependencies, start services, or deploy your application;
- run agents, daemons, or schedulers in the background;
- commit, push, tag, create pull requests, or publish releases;
- enable multi-project mode or split existing documentation;
- overwrite customized managed files;
- convert a review finding into repair authorization.

Agent-specific Skill loading, selection behavior, and context benefits can vary by client and version. These real-runtime items remain `NEEDS_TEST`; verify the first use in your target environment.

## Common checks

Check whether current docs can still support unfinished work:

```powershell
python .\scripts\check-current-docs-integrity.py --repo-root "D:\path\to\project"
```

Check multi-project boundaries:

```powershell
python .\scripts\check-workspace-integrity.py --repo-root "D:\path\to\workspace"
```

## Documentation map

| Need | File |
| --- | --- |
| Daily AI prompts | `.forgekit/docs/usage-playbook.md` |
| Writeback timing | `.forgekit/docs/work-session-checkpoint.md` |
| Document ownership | `.forgekit/docs/document-responsibility.md` |
| Current tasks | `.forgekit/docs/task-board.md` |
| Task sources | `.forgekit/docs/task-intake.md` |
| Verification | `.forgekit/docs/testing.md` |
| Risks and blockers | `.forgekit/docs/risk-register.md` |
| Project boundary | `.forgekit/project-boundary.yml` |
| Multi-project boundary | `.forgekit/workspace-map.json` |
| Version changes | `CHANGELOG.md` |

## Version history

See [CHANGELOG.md](CHANGELOG.md) for release history and upgrade notes.
