# Codex Project Guide

This file is the first lightweight entry point for Codex in this project. Use it to avoid loading the entire governance set into context.

## Task Routing

| Task | Read First | Skill |
| --- | --- | --- |
| New project initialization | `governance/流程总览.md`, `.codex/init.generated.md`, `.codex/questionnaires/` | `project-init` |
| Fill docs from answers | `governance/project-bootstrap-fill.md`, `.codex/questionnaires/` | `project-init` or `project-bootstrap-fill` |
| Existing project handover | `.codex/handover.md`, `docs/既有项目接手审计.md` | `handover-review` |
| Feature implementation | `.codex/rules.md`, `.codex/scope.md`, `.codex/commands.md`, relevant `.codex/stacks/` only | relevant stack rules |
| Code review | `.codex/testing.md`, `.codex/security.md`, `docs/代码所有权.md`, `docs/项目任务看板.md` | `code-review` |
| Release or version gate | `.codex/version-gates.md`, `docs/版本路线图.md`, `docs/版本更新记录.md` | `release-check` |
| Security-sensitive change | `.codex/security.md`, `governance/security-governance.md` | `security-review` |

## Context Rules

- Do not read every file in `governance/` by default.
- Load only the selected stack folder under `.codex/stacks/`.
- For Lite projects, keep governance lightweight and ask before expanding to Enterprise-level documents.
- If project plan, technology choice, landing conditions, or version scope are unclear, interview the user before coding.

## Gates

- Do not start broad coding without a first-pass project plan and version scope.
- Do not start the next major version before the review/refactor gate is complete, unless the user explicitly accepts the risk.
- Do not deploy, push, tag, run migrations, or start long-running services without explicit user confirmation.
