# Codex Template Repository Guide

This repository maintains a reusable Codex CLI workflow template.

## Start Here

- Read `README.md` for the user-facing workflow.
- Read `project-template/AGENTS.md` when changing the generated project template.
- Read `project-template/governance/agent-harness.md` when changing context strategy, AGENTS routing, codebase-map behavior, or Codex startup flow.
- Read `project-template/docs/代码库地图.md` when changing generated project onboarding or startup guidance.
- Read only the governance file related to the task. Do not load all governance docs by default.
- Use `scripts/validate-template.ps1` after changing template structure, skills, prompts, scripts, or HTML.

## Editing Rules

- Keep project skill `SKILL.md` files ASCII-only.
- Keep user-facing docs in Chinese unless the file is a Codex skill instruction that must remain ASCII.
- Do not put machine-specific local paths into `project-template/`; keep them in `user-rules/`.
- When adding a new template capability, update all relevant entry points:
  - `README.md`
  - `使用说明.html`
  - `project-template/README.md`
  - `project-template/AGENTS.md`
  - `project-template/.codex/skills.md`
  - `project-template/.agents/skills/README.md`
  - `scripts/validate-template.ps1`

## Harness Rules

- Keep root and generated `AGENTS.md` short; details belong in skills, stack templates, docs, or governance files.
- Do not duplicate the same long instruction in HTML, prompts, skills, and AGENTS.
- When adding startup behavior, make sure Codex can answer: first file to read, search starting point, stack-specific files, and validation command.

## Validation

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-template.ps1
```

For generated project smoke tests, run `scripts/init-project-template.ps1` into `D:\tmp`.
