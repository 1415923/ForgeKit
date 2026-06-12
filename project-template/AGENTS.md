# Codex Project Guide

This file is the first lightweight entry point for Codex in this project. Use it to avoid loading the entire governance set into context.

Claude Code users should start from `CLAUDE.md`; both entry files route to the same project facts under `.codex/`, `.forgekit/docs/`, and `governance/`.

Keep this file short. Put stable workflows in skills, stack-specific rules in `.codex/stacks/`, and detailed governance in `governance/`.

When a task names a ForgeKit skill, read the project-local `.agents/skills/<skill>/SKILL.md` first. Do not assume a user-level or system-level skill path exists.

## Startup Order

1. Read this file first.
2. Read `.forgekit/project-boundary.yml` to identify ForgeKitRoot, ProjectRoot, managed docs root, change root, business docs roots, and write policy.
3. Read `.forgekit/docs/codebase-map.md` to find likely modules, entry files, and local validation commands.
4. Read `.forgekit/docs/local-toolchain.md` when LSP, lint, test, build, or local validation commands matter.
5. Read `.forgekit/docs/codex-next-work-order.md` after initialization or when project direction is unclear.
6. Read `.codex/project.md`, `.codex/scope.md`, and `.codex/commands.md` only as needed.
7. Read only the selected stack folder under `.codex/stacks/`.
8. Read `governance/agent-harness.md` when the task involves context strategy, large code search, AGENTS maintenance, or unclear entry points.
9. Read `governance/large-change-execution.md` for large, cross-module, high-risk, migration, or refactor work.
10. Read `governance/ai-engineering-loop.md` when risk level, change artifacts, verification, review, ship, or retro expectations are unclear.
11. Read `.forgekit/docs/document-lifecycle.md` when deciding whether material belongs in current docs, change process docs, or archive.
12. Read `governance/team-agent-rollout.md` only when the task involves commands, hooks, plugins, MCP, CI, issue trackers, or team rollout.
13. Read `governance/agent-suitability.md` for project initialization, existing project handover, or when the project may not fit an AI agent workflow.
14. Read `.codex/automation-decision.md` before turning a repeated workflow into a skill, command, hook, script, plugin, or MCP.

## Task Routing

| Task | Read First | Local Skill |
| --- | --- | --- |
| New project initialization | `governance/overview.md`, `governance/agent-harness.md`, `.codex/init.generated.md`, `.codex/questionnaires/` | `project-init` |
| Post-init next step | `.forgekit/docs/codex-next-work-order.md`, `.forgekit/docs/project-suitability.md`, `.forgekit/docs/local-toolchain.md`, `.codex/init.generated.md` | `project-init` |
| Project suitability assessment | `governance/agent-suitability.md`, `.forgekit/docs/project-suitability.md`, `.forgekit/docs/project-trial-record.md` | `project-suitability` |
| Fill docs from answers | `governance/project-bootstrap-fill.md`, `.codex/questionnaires/` | `project-init` or `project-bootstrap-fill` |
| Existing project handover | existing README/usage/setup/test/deploy docs first, then `.forgekit/docs/codebase-map.md`, `.codex/handover.md`, `.forgekit/docs/handover-audit.md` | `handover-review` |
| Backfill ForgeKit managed docs from business docs | source docs one at a time, then target files under `.forgekit/docs/` | `document-backfill` |
| Document lifecycle or archive decision | `.forgekit/docs/document-lifecycle.md`, `.forgekit/docs/document-responsibility.md` | `release-check` |
| Feature implementation | `.codex/rules.md`, `.codex/scope.md`, `.codex/commands.md`, relevant `.codex/stacks/` only | relevant stack rules |
| Medium or high risk change | `governance/ai-engineering-loop.md`, `.forgekit/changes/README.md`, relevant `.forgekit/changes/<id>/` files | relevant existing skill |
| Large or cross-module change | `governance/large-change-execution.md`, `governance/ai-engineering-loop.md`, `.forgekit/docs/exploration-report.md`, `.forgekit/docs/implementation-plan.md`, relevant stack rules | `large-change-planning` |
| Commands, hooks, plugin, MCP, CI integration | `governance/team-agent-rollout.md`, `.codex/commands-catalog.md`, `.codex/hooks.md`, `.codex/config.example.toml` | release-check or security-review |
| Automation boundary decision | `.codex/automation-decision.md`, `governance/team-agent-rollout.md` | relevant existing skill |
| Document synchronization check | `.codex/hooks.md`, `.codex/commands.md`, `.forgekit/docs/changelog.md`, related docs | `release-check` |
| Archive dry-run plan | `.forgekit/docs/document-lifecycle.md`, `.forgekit/archive/README.md`, `.codex/commands.md` | `release-check` |
| Code review | `.codex/testing.md`, `.codex/security.md`, `.forgekit/docs/code-ownership.md`, `.forgekit/docs/task-board.md` | `code-review` |
| Release or version gate | `.codex/version-gates.md`, `.forgekit/docs/version-roadmap.md`, `.forgekit/docs/changelog.md` | `release-check` |
| Security-sensitive change | `.codex/security.md`, `governance/security-governance.md` | `security-review` |

## Context Rules

- Do not read every file in `governance/` by default.
- Boundary first: ForgeKitRoot is the toolkit source and is read-only unless this task is maintaining ForgeKit itself; ProjectRoot is the business repository and Git commit location.
- Use `.forgekit/docs` as the default ForgeKit-managed docs root and `.forgekit/changes` as the default change root.
- Treat business `docs/` as read-mostly evidence. Read and cite it, but do not write ForgeKit governance templates there unless the user confirms target files and reasons.
- Do not read all business `docs/` by default; use `.forgekit/docs/codebase-map.md` to choose what matters.
- Treat `.forgekit/template-lock.json` as an installation baseline. Do not edit it during report-only upgrade checks.
- Treat `.forgekit/upgrade-export/**` as candidate comparison material, not current-state docs, active changes, release evidence, or changelog content.
- Treat `.forgekit/docs/**` as current state docs: keep stable facts, not long process history.
- Treat `.forgekit/changes/<change-id>/**` as one-change process records: proposal, design, tasks, verification, review, ship, and retro.
- Treat `.forgekit/archive/**` as historical material, not current truth. Do not read archive by default; read it only when the user asks for history, audit, regression analysis, retro, incident review, historical decision explanation, or old-version comparison.
- Treat `.forgekit/archive-plan.md` as generated dry-run output. It is not current-state docs or an active change, and each dry-run may overwrite it.
- Treat `.forgekit/archive-apply-report.md` as generated apply output. It is not current-state docs, an active change, or release evidence.
- Treat `.forgekit/archive-reference-report.md` as generated report-only output. It is not current-state docs, an active change, or release evidence.
- Treat `.forgekit/docs/work-log.md` as a personal work sequence log for handoff and interrupted session recovery. If the user asks to update ForgeKit docs and this turn includes phase closure, validation, commit/push, blocking, or leader/team lead confirmation, update it; if the user explicitly asks to sync the work log, update it; stable technical fact updates alone do not force it.
- Do not install tools or start services just because `.forgekit/docs/local-toolchain.md` has unknown values; ask first.
- `scripts/detect-local-toolchain.ps1` and `scripts/run-harness-check.ps1` are read-only helpers; do not treat their output as permission to install or change anything.
- Use `.codex/automation-decision.md` to decide whether repeated work belongs in a skill, command, hook, script, plugin, MCP, or documentation.
- Load only the selected stack folder under `.codex/stacks/`.
- For Lite projects, keep governance lightweight and ask before expanding to Enterprise-level documents.
- If suitability is Conditional or Custom, fill `.forgekit/docs/project-suitability.md` before broad coding.
- If project plan, technology choice, landing conditions, or version scope are unclear, interview the user before coding.
- For existing projects, read existing docs and extract answers before asking broad handover questions.
- When backfilling `.forgekit/docs/` from existing project documents, process one source document at a time and update target docs before reading the next source document.
- After manual doc fixes or release-note changes, optionally run `scripts/check-doc-sync.ps1` to look for related docs, stale descriptions, and Changed entries without reasons.
- For implementation tasks, apply `.codex/rules.md`: think before coding, keep changes simple, edit surgically, and verify against explicit goals.
- Classify task risk before broad edits: low keeps a light flow; medium requires `proposal.md`, `tasks.md`, `verification.md`, and `review.md`; high also requires `design.md` and `ship.md`.
- For large or cross-module changes, search first, summarize findings, then propose a plan before editing.
- For large changes, create or update `.forgekit/docs/exploration-report.md` and `.forgekit/docs/implementation-plan.md` before broad implementation.
- Do not enable hooks, plugins, MCP, issue tracker writes, or CI changes without explicit user confirmation.
- Treat installed plugins as distribution inputs; review their skills, scripts, permissions, and maintenance owner before relying on them for project decisions.

## AGENTS Layering

- Root `AGENTS.md` should stay under 200 lines.
- Add subdirectory `AGENTS.md` only for local rules that differ from root rules.
- Review this file every 3 to 6 months or during a review/refactor gate.
- Do not paste long prompts, long checklists, environment-specific paths, or stack manuals here.

## Gates

- Do not start broad coding without a first-pass project plan and version scope.
- Do not start medium or high risk implementation until the required `.forgekit/changes/<id>/` artifacts exist and the plan is confirmed.
- For new projects, product and architecture discussion is a required phase. Do not treat a few engineering parameter answers as approval to implement.
- Before business code, dependency install, Git init, commit, push, deployment, or other external action, show an execution summary and wait for explicit user confirmation.
- Do not start large cross-module implementation before exploration and implementation plan are complete.
- Do not start the next major version before the review/refactor gate is complete, unless the user explicitly accepts the risk.
- Do not deploy, push, tag, run migrations, or start long-running services without explicit user confirmation.
