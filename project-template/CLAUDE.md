# Claude Code Project Guide

This file is the first lightweight entry point for Claude Code in this project. Use it to avoid loading the entire governance set into context.

Keep this file short. Put stable workflows in skills, stack-specific rules in `.codex/stacks/`, and detailed governance in `governance/`.

When a task names a ForgeKit skill, read the project-local `.agents/skills/<skill>/SKILL.md` first. Do not assume a user-level or system-level skill path exists.

## Startup Order

1. Read this file first.
2. Read `docs/codebase-map.md` to find likely modules, entry files, and local validation commands.
3. Read `docs/local-toolchain.md` when lint, test, build, or local validation commands matter.
4. Read `docs/codex-next-work-order.md` after initialization or when project direction is unclear.
5. Read `.codex/project.md`, `.codex/scope.md`, and `.codex/commands.md` only as needed.
6. Read only the selected stack folder under `.codex/stacks/`.
7. Use `.claude/skills/` for ForgeKit workflow skills.
8. Read `governance/agent-harness.md` when the task involves context strategy, large code search, or unclear entry points.
9. Read `governance/large-change-execution.md` for large, cross-module, high-risk, migration, or refactor work.
10. Read `governance/ai-engineering-loop.md` when risk level, change artifacts, verification, review, ship, or retro expectations are unclear.
11. Read `governance/team-agent-rollout.md` only when the task involves commands, hooks, plugins, MCP, CI, issue trackers, or team rollout.
12. Read `governance/agent-suitability.md` for initialization, existing project handover, or when project fit is unclear.
13. Read `.codex/automation-decision.md` before turning a repeated workflow into a skill, command, hook, script, plugin, or MCP.

## Task Routing

| Task | Read First | Local Skill |
| --- | --- | --- |
| New project initialization | `governance/overview.md`, `governance/agent-harness.md`, `.claude/init.generated.md`, `.codex/questionnaires/` | `project-init` |
| Post-init next step | `docs/codex-next-work-order.md`, `docs/project-suitability.md`, `docs/local-toolchain.md`, `.claude/init.generated.md` | `project-init` |
| Project suitability assessment | `governance/agent-suitability.md`, `docs/project-suitability.md`, `docs/project-trial-record.md` | `project-suitability` |
| Existing project handover | existing README/usage/setup/test/deploy docs first, then `docs/codebase-map.md`, `.codex/handover.md`, `docs/handover-audit.md` | `handover-review` |
| Backfill ForgeKit docs from existing docs | source docs one at a time, then target files under `docs/` | `document-backfill` |
| Feature implementation | `.codex/rules.md`, `.codex/scope.md`, `.codex/commands.md`, relevant `.codex/stacks/` only | relevant stack rules |
| Medium or high risk change | `governance/ai-engineering-loop.md`, `changes/README.md`, relevant `changes/<id>/` files | relevant existing skill |
| Large or cross-module change | `governance/large-change-execution.md`, `governance/ai-engineering-loop.md`, `docs/exploration-report.md`, `docs/implementation-plan.md`, relevant stack rules | `large-change-planning` |
| Automation boundary decision | `.codex/automation-decision.md`, `governance/team-agent-rollout.md` | relevant existing skill |
| Document synchronization check | `.codex/hooks.md`, `.codex/commands.md`, `docs/changelog.md`, related docs | `release-check` |
| Code review | `.codex/testing.md`, `.codex/security.md`, `docs/code-ownership.md`, `docs/task-board.md` | `code-review` |
| Release or version gate | `.codex/version-gates.md`, `docs/version-roadmap.md`, `docs/changelog.md` | `release-check` |
| Security-sensitive change | `.codex/security.md`, `governance/security-governance.md` | `security-review` |

## Context Rules

- Do not read every file in `governance/` by default.
- Do not read all `docs/` by default; use `docs/codebase-map.md` to choose what matters.
- Do not install tools or start services just because `docs/local-toolchain.md` has unknown values; ask first.
- `scripts/detect-local-toolchain.ps1` and `scripts/run-harness-check.ps1` are read-only helpers.
- For Lite projects, keep governance lightweight and ask before expanding to Enterprise-level documents.
- Use `.codex/automation-decision.md` to decide whether repeated work belongs in a skill, command, hook, script, plugin, MCP, or documentation.
- Load only the selected stack folder under `.codex/stacks/`.
- If suitability is Conditional or Custom, fill `docs/project-suitability.md` before broad coding.
- If the project plan, technology choice, landing conditions, or version scope are unclear, interview the user before coding.
- For existing projects, read existing docs and extract answers before asking broad handover questions.
- When backfilling `docs/` from existing project documents, process one source document at a time and update target docs before reading the next source document.
- After manual doc fixes or release-note changes, optionally run `scripts/check-doc-sync.ps1` to look for related docs, stale descriptions, and Changed entries without reasons.
- For implementation tasks, apply `.codex/rules.md`: think before coding, keep changes simple, edit surgically, and verify against explicit goals.
- Classify task risk before broad edits: low keeps a light flow; medium requires `proposal.md`, `tasks.md`, `verification.md`, and `review.md`; high also requires `design.md` and `ship.md`.
- For large or cross-module changes, search first, summarize findings, then propose a plan before editing.
- Do not enable hooks, plugins, MCP, issue tracker writes, or CI changes without explicit user confirmation.
- Treat installed plugins as distribution inputs; review their skills, scripts, permissions, and maintenance owner before relying on them for project decisions.

## Gates

- Do not start broad coding without a first-pass project plan and version scope.
- Do not start medium or high risk implementation until the required `changes/<id>/` artifacts exist and the plan is confirmed.
- For new projects, product and architecture discussion is a required phase. Do not treat a few engineering parameter answers as approval to implement.
- Before business code, dependency install, Git init, commit, push, deployment, or other external action, show an execution summary and wait for explicit user confirmation.
- Do not start large cross-module implementation before exploration and implementation plan are complete.
- Do not start the next major version before the review/refactor gate is complete, unless the user explicitly accepts the risk.
- Do not deploy, push, tag, run migrations, or start long-running services without explicit user confirmation.
