# ForgeKit

Chinese documentation: [README.md](README.md).

**ForgeKit is a lightweight AI engineering delivery toolkit.**

ForgeKit is not an app framework, code scaffold, or deployment tool. It helps Codex, Claude Code, and adjacent coding agents move from ad-hoc prompting to reviewable engineering delivery: clarify the goal and risk, create just enough artifacts by risk level, then verify, review, ship, and record what changed.

In short: ForgeKit provides a lightweight AI Engineering Loop so the assistant clarifies the goal, plan, risks, and validation path before it starts coding and shipping.

## Quick Start

### 1. Generate the project template

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\projects\my-app" -ProjectName "my-app" -Mode Standard
```

Ubuntu / macOS:

```bash
./scripts/init-project-template.sh --target-path "$HOME/projects/my-app" --project-name "my-app" --mode Standard
```

Modes:

| Mode | Best for |
| --- | --- |
| `Lite` | Small scripts, personal tools, quick prototypes |
| `Standard` | Normal apps, APIs, internal systems, data projects |
| `Enterprise` | Team delivery, production, high-risk or inherited projects |

If unsure, use `Standard`. `Mode` is written to initialization metadata for later AI filling priority and governance-strength discussion; the current version does not crop copied files by mode. Do not rush stack selection here. New projects should choose a stack after discovery; existing projects should infer the stack from real files first.

### 2. Start your AI tool from the generated project

Codex:

```powershell
cd D:\projects\my-app
codex
```

Claude Code:

```powershell
cd D:\projects\my-app
claude
```

### 3. Send the startup message

Codex:

```text
Read AGENTS.md, prefer the project-local .agents/skills/project-init/SKILL.md, and help me initialize this project with ForgeKit. Do not read a user-level or system-level project-init path.
```

Claude Code:

```text
Read CLAUDE.md, prefer the project-local .agents/skills/project-init/SKILL.md, and help me initialize this project with ForgeKit. Do not read a user-level or system-level project-init path.
```

## Core Capabilities

- `project-init`: discovery interview and project entry setup.
- `project-suitability`: decide whether Lite, Standard, Enterprise, or Custom flow fits.
- `document-backfill`: read existing docs one by one and migrate facts into ForgeKit `docs/`.
- `handover-review`: audit inherited projects and identify risks.
- `large-change-planning`: explore and plan broad, cross-module, migration, or refactor work before implementation.
- `code-review`, `release-check`, `security-review`: code review, release gate, and security review.
- AI Engineering Loop: low risk keeps a light flow; medium risk needs proposal / tasks / verification / review; high risk adds design / ship; retro is recommended only after major changes.
- Optional document-sync checks and Git hooks for related-doc drift, stale descriptions, and version-record reasons.

After generation, Codex starts from `AGENTS.md`; Claude Code starts from `CLAUDE.md`. Both share `.codex/`, `docs/`, `governance/`, and `.agents/skills/`.

Key generated files:

- `docs/codebase-map.md`: code entry points, module map, and local validation commands.
- `docs/local-toolchain.md`: local lint, test, build, LSP, and toolchain capability.
- `governance/ai-engineering-loop.md`: risk levels, change artifacts, and delivery loop.
- `changes/_template/`: proposal, design, tasks, verification, review, ship, and retro templates.
- `.codex/commands.md`: project-specific commands.
- `.agents/skills/`: self-contained project skills.

## Upgrade An Existing Project

When upgrading from an older ForgeKit version, use upgrade mode and do not use `-Force` / `--force`:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\projects\my-app" -ProjectName "my-app" -Mode Standard -Upgrade -ExportUpgradeTemplates
```

```bash
./scripts/init-project-template.sh --target-path "$HOME/projects/my-app" --project-name "my-app" --mode Standard --upgrade --export-upgrade-templates
```

Upgrade mode:

- Copies missing files from the newer template.
- Preserves existing project facts and docs instead of overwriting `docs/`, `.codex/`, `AGENTS.md`, or `CLAUDE.md`.
- Writes changed existing files to `.codex/upgrade-report.md`.
- Optionally exports newer template copies to `.codex/upgrade-templates/` for human or AI-assisted diff and merge.

After upgrading, ask the assistant:

```text
Review .codex/upgrade-report.md and compare .codex/upgrade-templates/. Merge useful new ForgeKit template sections into existing project files without overwriting project facts.
```

## Existing Projects And Old Docs

For inherited projects, the assistant should not ask for the stack first. It should read README files, setup notes, startup scripts, test docs, deployment docs, API docs, build files, and dependency files, then extract answers from evidence. Ask only when docs are missing, contradictory, or stale.

If there are many old docs, use:

```text
Use document-backfill to read documents under <old-docs-dir> one source document at a time and complete ForgeKit docs as you go. Do not read every document into one large summary.
```

## Optional Hooks

ForgeKit does not enable hooks by default. To enable document-sync reminders, install the opt-in Git hook.

Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-hooks.ps1 -Profile docs-warn -Target git
```

Ubuntu / macOS:

```bash
./scripts/install-hooks.sh --profile docs-warn --target git
```

`docs-warn` warns only. Use `docs-strict` only after the team accepts the noise level.

## Checks

Validate the template:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-template.ps1
```

Validate plugin distribution:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-plugin-assets.ps1
```

Run inside a generated project:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-harness-check.ps1
```

Check document synchronization:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check-doc-sync.ps1
```

```bash
./scripts/check-doc-sync.sh
```

These scripts only check, copy templates, or install local opt-in hooks. They do not install dependencies, start services, deploy, commit, tag, or push.

## Plugin Distribution

ForgeKit uses one root-level plugin surface:

```text
.codex-plugin/plugin.json
.claude-plugin/plugin.json
.agents/plugins/marketplace.json
.claude-plugin/marketplace.json
skills/
project-template/
templates/
questionnaires/
scripts/
```

Both `.codex-plugin/plugin.json` and `.claude-plugin/plugin.json` point to the shared `./skills/` directory.

## Boundary With ECC

ECC is closer to an AI coding tool enhancement suite: commands, hooks, memory, MCP, multi-agent workflows, security tools, and cross-tool adapters. ForgeKit has a narrower job: constrain the concrete project's delivery workflow so AI tools can take over more reliably.

ForgeKit does not enable by default:

- hooks
- MCP
- memory or session tracking
- multi-agent runtimes
- external account integrations
- automatic deployment
- automatic issue or PR creation
- automatic commit, tag, or push

ForgeKit can coexist with ECC: ECC enhances the AI tool; ForgeKit constrains the project workspace.

## Recent Releases

| Version | User-facing change |
| --- | --- |
| `0.15.0` | Repositioned ForgeKit as a lightweight AI engineering delivery toolkit with an AI Engineering Loop and risk-based change templates. |
| `0.14.0` | Release-usability fixes: English template file names, mode semantics, upgrade misuse guard, cross-platform smoke test, and generic template path isolation. |
| `0.13.0` | Project suitability, large-change planning, document-sync checks, optional Git hooks, upgrade reports, and template diff support. |
| `0.12.x` | Unified root-level plugin distribution for Codex and Claude Code, with both `AGENTS.md` and `CLAUDE.md` generated. |
| `0.11.x` | Improved Claude Code entry and shared project facts across tools. |
