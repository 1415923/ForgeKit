---
name: forgekit-maintenance
description: Route ForgeKit project bootstrap and maintenance requests such as install, init, upgrade sync, phase archive, context checkpoint, handoff, doc health, and source trace. Use when the user asks to install, initialize, sync, tidy, archive, close a phase, preserve context, prepare a handoff, or inspect governance documents.
---

# ForgeKit Maintenance

Identify one `MaintenanceIntent` before running tools:

- `project-bootstrap`
- `upgrade-sync`
- `archive-capsule`
- `context-checkpoint`
- `handoff`
- `doc-health`
- `source-trace`

Read `.forgekit/docs/project-maintenance.md` for the selected workflow. Do not load all managed docs or the full archive.

## Route

- Install, initialize, update, or sync ForgeKit: prefer the ForgeKitRoot `forgekit-project.py` unified entry and use `project-bootstrap`.
- Outer ForgeKit updated, sync, or upgrade cleanup: `upgrade-sync`.
- Phase complete, archive, or put history away: `archive-capsule`.
- Preserve conclusions or prepare for compaction: `context-checkpoint`.
- Prepare material for a leader, reviewer, or tester: `handoff`.
- Documents are too long, duplicated, or misplaced: `doc-health`.
- Ask where a task came from or whether completion has evidence: `source-trace`.

If the intent or scope is ambiguous, ask one focused question before planning.

## Plan Before Apply

1. State the intent, project root, ForgeKit root when relevant, scope, files that may change, and forbidden actions.
2. Run or produce a report-only plan.
3. Show the plan and unresolved questions.
4. Apply only after explicit user confirmation or an existing bounded-auto authorization that covers the exact action.
5. Produce an operation summary and perform the required minimal checkpoint/writeback.

For project bootstrap, run the ForgeKitRoot `forgekit-project.py --target <project-root>`. Let it detect init, up-to-date, versioned upgrade, toolkit-too-old, or legacy adoption. Non-interactive use is plan-only unless `--yes` is explicit.

For advanced upgrade sync, run `forgekit-upgrade.py check`, then `plan`, then confirmed `apply --safe`. Remind the user to refresh the session after rules, skills, or agents change.

For archive capsule, run `archive-capsule.py plan` with explicit items. Never treat archive as deletion. `apply --confirm` may move only planned items and must create the capsule summary, item log, and archive index entry.

## Boundaries

- Do not modify business docs.
- Do not use `--force-init` on an installed or legacy ForgeKit project. It only authorizes preserve-existing initialization in an uninstalled non-empty directory.
- Do not scan or rearrange legacy archive content.
- Do not apply an archive plan without explicit confirmation.
- Do not commit, push, create a PR, start a runner, daemon, or scheduler.
- Do not invent archive evidence. Use `TODO_REVIEW` when the plan does not prove a fact.
