# Claude Code Project Guide

This file is the first lightweight entry point for Claude Code in this project. Use it to avoid loading the entire governance set into context.

Keep this file short. Put stable workflows in skills, stack-specific rules in `.codex/stacks/`, and detailed governance in `governance/`.

## Startup Order

1. Read this file first.
2. Read `docs/代码库地图.md` to find likely modules, entry files, and local validation commands.
3. Read `docs/本地工具链检查.md` when lint, test, build, or local validation commands matter.
4. Read `docs/Codex下一步工作单.md` after initialization or when project direction is unclear.
5. Read `.codex/project.md`, `.codex/scope.md`, and `.codex/commands.md` only as needed.
6. Read only the selected stack folder under `.codex/stacks/`.
7. Use `.claude/skills/` for ForgeKit workflow skills.
8. Read `governance/agent-harness.md` when the task involves context strategy, large code search, or unclear entry points.
9. Read `governance/large-change-execution.md` for large, cross-module, high-risk, migration, or refactor work.
10. Read `governance/team-agent-rollout.md` only when the task involves commands, hooks, plugins, MCP, CI, issue trackers, or team rollout.

## Task Routing

| Task | Read First | Skill |
| --- | --- | --- |
| New project initialization | `governance/流程总览.md`, `governance/agent-harness.md`, `.claude/init.generated.md`, `.codex/questionnaires/` | `project-init` |
| Post-init next step | `docs/Codex下一步工作单.md`, `docs/项目适用性评估.md`, `docs/本地工具链检查.md`, `.claude/init.generated.md` | `project-init` |
| Existing project handover | existing README/usage/setup/test/deploy docs first, then `docs/代码库地图.md`, `.codex/handover.md`, `docs/既有项目接手审计.md` | `handover-review` |
| Backfill ForgeKit docs from existing docs | source docs one at a time, then target files under `docs/` | `document-backfill` |
| Feature implementation | `.codex/rules.md`, `.codex/scope.md`, `.codex/commands.md`, relevant `.codex/stacks/` only | relevant stack rules |
| Large or cross-module change | `governance/large-change-execution.md`, `docs/探索报告.md`, `docs/实施计划.md`, relevant stack rules | project-init or code-review |
| Code review | `.codex/testing.md`, `.codex/security.md`, `docs/代码所有权.md`, `docs/项目任务看板.md` | `code-review` |
| Release or version gate | `.codex/version-gates.md`, `docs/版本路线图.md`, `docs/版本更新记录.md` | `release-check` |
| Security-sensitive change | `.codex/security.md`, `governance/security-governance.md` | `security-review` |

## Context Rules

- Do not read every file in `governance/` by default.
- Do not read all `docs/` by default; use `docs/代码库地图.md` to choose what matters.
- Do not install tools or start services just because `docs/本地工具链检查.md` has unknown values; ask first.
- `scripts/detect-local-toolchain.ps1` and `scripts/run-harness-check.ps1` are read-only helpers.
- Load only the selected stack folder under `.codex/stacks/`.
- If the project plan, technology choice, landing conditions, or version scope are unclear, interview the user before coding.
- For existing projects, read existing docs and extract answers before asking broad handover questions.
- When backfilling `docs/` from existing project documents, process one source document at a time and update target docs before reading the next source document.
- For large or cross-module changes, search first, summarize findings, then propose a plan before editing.
- Do not enable hooks, plugins, MCP, issue tracker writes, or CI changes without explicit user confirmation.

## Gates

- Do not start broad coding without a first-pass project plan and version scope.
- For new projects, product and architecture discussion is a required phase. Do not treat a few engineering parameter answers as approval to implement.
- Before business code, dependency install, Git init, commit, push, deployment, or other external action, show an execution summary and wait for explicit user confirmation.
- Do not deploy, push, tag, run migrations, or start long-running services without explicit user confirmation.
