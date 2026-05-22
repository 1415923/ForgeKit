# Codex Template Repository Guide

This repository maintains a reusable Codex CLI workflow template.

## Start Here

- Read `README.md` for the user-facing workflow.
- Read `project-template/AGENTS.md` when changing the generated project template.
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
  - `project-template/.codex/skills.md`
  - `project-template/.agents/skills/README.md`
  - `scripts/validate-template.ps1`

## Validation

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-template.ps1
```

For generated project smoke tests, run `scripts/init-project-template.ps1` into `D:\tmp`.
