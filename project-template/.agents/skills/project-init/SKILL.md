---
name: project-init
description: Initialize ForgeKit through its unified project entry when the user requests installation or initialization.
---

# Project Init

## Trigger Boundary

Use only when all of these are true:

- The user explicitly wants to initialize a new project or the current directory.
- The directory has not completed ForgeKit project initialization.
- The task is to establish the minimum project boundary and governance entry.

Do not use for an existing-project takeover audit, partial bootstrap placeholders, an implementation or bug fix, a read-only review, or a ForgeKit suitability assessment. Route those intents to `project-assessment`, `document-backfill`, the specific implementation or review Skill, or `project-assessment`. Do not run all of these Skills in sequence.

## Default Mode and Authorization

Status discovery and initialization assessment are read-only by default. When the user has explicitly asked to initialize this project, that request authorizes reversible local writes inside the named project and initialization scope; do not ask again for equivalent authorization.

That authorization does not include adjacent projects, dependency installation, remote repository operations, service creation, commit, push, publish, release, deploy, deletion, or irreversible conversion. Stop before any such action and obtain authorization for the specific target and impact.

## Workflow

1. Read the project boundary, startup entry, codebase map, and deterministic ForgeKit initialization state. Apply the root-resolution semantics in `governance/agent-entry-contract.md`. Use the unified `scripts/forgekit-project.py --target <ProjectRoot>` state result when that entry is available; do not reproduce its init/current/upgrade/adoption algorithm in this Skill.
2. Confirm the minimum project root, project purpose, task scope, and required validation from existing files and user facts.
3. Ask only for information that cannot be obtained from evidence and would change the initialization result. Do not use a fixed interview length, repeat facts already supplied, or block on non-critical preferences.
4. Mark unsupported fields `TODO_REVIEW` or `UNKNOWN`. Never invent architecture, technology stack, owners, commands, deployment, or external-system details.
5. Create only the minimum ForgeKit structure required for the selected initialization mode. Preserve existing files and user customization. Business/workspace `README.md` is user-owned: do not create, replace, or claim ownership of it as a ForgeKit bootstrap fact.
6. Run proportionate deterministic validation and report what is confirmed, unknown, changed, and still outside scope.

## Unified Layout Contract

At the semantic level, the high-level `--target` identifies the actual ProjectRoot unless the caller explicitly chooses `--layout legacy-nested`; fresh default planning is `--layout in-place`. Existing projects are discovered and reused, never moved or rewritten because a layout option is present. A legacy inner ProjectRoot must resolve only through the exact ancestor-boundary match defined by `agent-entry-contract.md`; do not choose the nearest unrelated ancestor or create a second `.forgekit` root.

Actual `--layout` CLI behavior, existing-root discovery code, manifest/install-lock README ownership, and init copy behavior are implementation concerns. Do not simulate them in this Skill or claim they exist without entry-path evidence.

## Risk Branch

Ordinary initialization is a bounded local write when it creates new, reversible project files inside the confirmed root. Escalate risk before overwriting existing content, moving across projects, deleting data, changing remote repositories or external systems, or performing an irreversible conversion. State the affected trust boundary, rollback, verification gap, and required authorization.

## Writeback and Stop Boundary

Write only confirmed initialization facts and the minimum current state to their owning project files. Do not create a complete governance system merely for completeness, copy the same fact into several owner documents, or write assumptions as current truth.

Initialization does not authorize business implementation. End with the initialization result, validation evidence, unresolved `TODO_REVIEW` or `UNKNOWN` items, and the single appropriate next route. Do not automatically enter bootstrap filling, handover repair, large-change implementation, or any external action.
