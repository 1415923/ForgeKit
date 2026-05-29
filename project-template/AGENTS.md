# Codex Project Guide

This file is the first lightweight entry point for Codex in this project. Use it to avoid loading the entire governance set into context.

Claude Code users should start from `CLAUDE.md`; both entry files route to the same project facts under `.codex/`, `docs/`, and `governance/`.

Keep this file short. Put stable workflows in skills, stack-specific rules in `.codex/stacks/`, and detailed governance in `governance/`.

## Startup Order

1. Read this file first.
2. Read `docs/代码库地图.md` to find likely modules, entry files, and local validation commands.
3. Read `docs/本地工具链检查.md` when LSP, lint, test, build, or local validation commands matter.
4. Read `docs/Codex下一步工作单.md` after initialization or when project direction is unclear.
5. Read `.codex/project.md`, `.codex/scope.md`, and `.codex/commands.md` only as needed.
6. Read only the selected stack folder under `.codex/stacks/`.
7. Read `governance/agent-harness.md` when the task involves context strategy, large code search, AGENTS maintenance, or unclear entry points.
8. Read `governance/large-change-execution.md` for large, cross-module, high-risk, migration, or refactor work.
9. Read `governance/team-agent-rollout.md` only when the task involves commands, hooks, plugins, MCP, CI, issue trackers, or team rollout.
10. Read `governance/agent-suitability.md` for project initialization, existing project handover, or when the project may not fit an AI agent workflow.
11. Read `.codex/automation-decision.md` before turning a repeated workflow into a skill, command, hook, script, plugin, or MCP.

## Task Routing

| Task | Read First | Skill |
| --- | --- | --- |
| New project initialization | `governance/流程总览.md`, `governance/agent-harness.md`, `.codex/init.generated.md`, `.codex/questionnaires/` | `project-init` |
| Post-init next step | `docs/Codex下一步工作单.md`, `docs/项目适用性评估.md`, `docs/本地工具链检查.md`, `.codex/init.generated.md` | `project-init` |
| Project suitability assessment | `governance/agent-suitability.md`, `docs/项目适用性评估.md`, `docs/真实项目试用记录.md` | `project-suitability` |
| Fill docs from answers | `governance/project-bootstrap-fill.md`, `.codex/questionnaires/` | `project-init` or `project-bootstrap-fill` |
| Existing project handover | existing README/usage/setup/test/deploy docs first, then `docs/代码库地图.md`, `.codex/handover.md`, `docs/既有项目接手审计.md` | `handover-review` |
| Backfill ForgeKit docs from existing docs | source docs one at a time, then target files under `docs/` | `document-backfill` |
| Feature implementation | `.codex/rules.md`, `.codex/scope.md`, `.codex/commands.md`, relevant `.codex/stacks/` only | relevant stack rules |
| Large or cross-module change | `governance/large-change-execution.md`, `docs/探索报告.md`, `docs/实施计划.md`, relevant stack rules | `large-change-planning` |
| Commands, hooks, plugin, MCP, CI integration | `governance/team-agent-rollout.md`, `.codex/commands-catalog.md`, `.codex/hooks.md`, `.codex/config.example.toml` | release-check or security-review |
| Automation boundary decision | `.codex/automation-decision.md`, `governance/team-agent-rollout.md` | relevant existing skill |
| Document synchronization check | `.codex/hooks.md`, `.codex/commands.md`, `docs/版本更新记录.md`, related docs | `release-check` |
| Code review | `.codex/testing.md`, `.codex/security.md`, `docs/代码所有权.md`, `docs/项目任务看板.md` | `code-review` |
| Release or version gate | `.codex/version-gates.md`, `docs/版本路线图.md`, `docs/版本更新记录.md` | `release-check` |
| Security-sensitive change | `.codex/security.md`, `governance/security-governance.md` | `security-review` |

## Context Rules

- Do not read every file in `governance/` by default.
- Do not read all `docs/` by default; use `docs/代码库地图.md` to choose what matters.
- Do not install tools or start services just because `docs/本地工具链检查.md` has unknown values; ask first.
- `scripts/detect-local-toolchain.ps1` and `scripts/run-harness-check.ps1` are read-only helpers; do not treat their output as permission to install or change anything.
- Use `.codex/automation-decision.md` to decide whether repeated work belongs in a skill, command, hook, script, plugin, MCP, or documentation.
- Load only the selected stack folder under `.codex/stacks/`.
- For Lite projects, keep governance lightweight and ask before expanding to Enterprise-level documents.
- If suitability is Conditional or Custom, fill `docs/项目适用性评估.md` before broad coding.
- If project plan, technology choice, landing conditions, or version scope are unclear, interview the user before coding.
- For existing projects, read existing docs and extract answers before asking broad handover questions.
- When backfilling `docs/` from existing project documents, process one source document at a time and update target docs before reading the next source document.
- After manual doc fixes or release-note changes, optionally run `scripts/check-doc-sync.ps1` to look for related docs, stale descriptions, and Changed entries without reasons.
- For large or cross-module changes, search first, summarize findings, then propose a plan before editing.
- For large changes, create or update `docs/探索报告.md` and `docs/实施计划.md` before broad implementation.
- Do not enable hooks, plugins, MCP, issue tracker writes, or CI changes without explicit user confirmation.
- Treat installed plugins as distribution inputs; review their skills, scripts, permissions, and maintenance owner before relying on them for project decisions.

## AGENTS Layering

- Root `AGENTS.md` should stay under 200 lines.
- Add subdirectory `AGENTS.md` only for local rules that differ from root rules.
- Review this file every 3 to 6 months or during a review/refactor gate.
- Do not paste long prompts, long checklists, environment-specific paths, or stack manuals here.

## Gates

- Do not start broad coding without a first-pass project plan and version scope.
- For new projects, product and architecture discussion is a required phase. Do not treat a few engineering parameter answers as approval to implement.
- Before business code, dependency install, Git init, commit, push, deployment, or other external action, show an execution summary and wait for explicit user confirmation.
- Do not start large cross-module implementation before exploration and implementation plan are complete.
- Do not start the next major version before the review/refactor gate is complete, unless the user explicitly accepts the risk.
- Do not deploy, push, tag, run migrations, or start long-running services without explicit user confirmation.
