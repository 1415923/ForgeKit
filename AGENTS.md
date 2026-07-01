# Codex Template Repository Guide

This repository maintains a reusable Codex CLI workflow template.

## Start Here

- Read `README.md` for the user-facing workflow.
- Read `project-template/AGENTS.md` when changing the generated project template.
- Read `project-template/governance/ai-engineering-loop.md` when changing risk-based workflow, change artifacts, verification, review, ship, or retro behavior.
- Read `project-template/governance/agent-harness.md` when changing context strategy, AGENTS routing, codebase-map behavior, or Codex startup flow.
- Read `project-template/docs/codebase-map.md` when changing generated project onboarding or startup guidance.
- Read only the governance file related to the task. Do not load all governance docs by default.
- Use `scripts/validate-template.ps1` after changing template structure, skills, prompts, scripts, or HTML.

## Editing Rules

- Keep project skill `SKILL.md` files ASCII-only.
- Keep user-facing docs in Chinese unless the file is a Codex skill instruction that must remain ASCII.
- Do not put machine-specific local paths into `project-template/`; keep them in `user-rules/`.
- When adding a new template capability, update all relevant entry points:
  - `README.md`
  - `usage.html`
  - `project-template/README.md`
  - `project-template/AGENTS.md`
  - `project-template/.codex/skills.md`
  - `project-template/.agents/skills/README.md`
  - `scripts/validate-template.ps1`
- Plugin distribution is root-level like ECC: `.codex-plugin/plugin.json`, `.claude-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `.claude-plugin/marketplace.json`, and shared `skills/`. Do not reintroduce per-tool plugin subdirectories under `plugins/`; do not package `user-rules/` or external development records.

## Harness Rules

- Keep root and generated `AGENTS.md` short; details belong in skills, stack templates, docs, or governance files.
- Do not duplicate the same long instruction in HTML, prompts, skills, and AGENTS.
- When adding startup behavior, make sure Codex can answer: first file to read, search starting point, stack-specific files, and validation command.
- When adding managed docs, update `project-template/.forgekit/docs/document-responsibility.md`, `project-template/docs/codebase-map.md`, manifest checks, and smoke tests.
- Source-first task intake belongs in `project-template/docs/task-intake.md`; do not let `requirements.md`, `task-board.md`, or `changelog.md` replace the original assignment ledger.
- Managed docs should stay lean: define audience, trigger, and "do not write here" boundaries before adding or expanding a document.
- Critical engineering conclusions must survive chat compaction, clearing, and delegation through narrow managed-doc or change-artifact checkpoints; never copy full chats or long tool output into project docs.
- After a ForgeKit upgrade changes entry rules, skills, or agents, use the current session only for checkpoint, minimal writeback, and closure; start a new session or restart the tool before new work.
- Route install/init/update/sync through the ForgeKitRoot `forgekit-project.py` unified entry; it detects init, current, upgrade, toolkit-too-old, or legacy adoption. Other maintenance still uses `project-maintenance.md`: plan before apply, require confirmation, and produce summary/index. Archive is not deletion.
- Before and after archive or maintenance, check current docs integrity. Real task-board Source IDs must resolve to task-intake; active work must not exist only in archive. If current docs are placeholder-only or broken, run a Current State Restoration Pass before more archive work; ignore example IDs.
- Multi-project scoped docs are opt-in. Keep the machine entry at `.forgekit/workspace-map.json`, templates under `.forgekit/projects/_template/`, and the protocol at `.forgekit/docs/scoped-docs.md`; do not create a second managed-doc source under `project-template/docs/` or auto-split user docs.
- Keep independent code review split into maker request, fresh read-only reviewer context, structured gate result, and explicit human escalation; self-review must not satisfy an independent-review gate.
- When the user requests first-principles analysis, derive from confirmed facts, assumptions, constraints, and the smallest verifiable mechanism. For high-risk completion, use adversarial failure-path review before declaring done.
- Checkpoint critical derivations and blocking findings as summaries with evidence paths and `TODO_REVIEW`; never write unverified reasoning as fact or copy full review logs into persistent docs.

## Validation

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-template.ps1
```

For generated project smoke tests, run `scripts/init-project-template.ps1` into `D:\tmp`.
