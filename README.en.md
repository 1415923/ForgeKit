# ForgeKit

Chinese documentation: [README.md](README.md).

ForgeKit is a lightweight AI engineering delivery toolkit for keeping Codex, Claude Code, and adjacent coding agents inside a reviewable, verifiable, and handoff-friendly project workflow.

It is not an application framework scaffold and not a deployment platform. ForgeKit generates project-local workflow structure: entry files, project boundaries, AI skills, risk-based change artifacts, governance docs, check scripts, and optional hooks.

## When To Use It

ForgeKit is useful when you want to:

- Start a new project with AI after clarifying goals, boundaries, stack choices, and validation paths.
- Take over an existing project by extracting facts from README files, build files, scripts, and old docs before asking stack questions.
- Require proposal / tasks / verification / review before medium or high-risk changes, with design / ship / retro when needed.
- Let Codex and Claude Code share one project-local set of facts, commands, skills, and delivery rules.

ForgeKit does not:

- Generate business framework code.
- Install dependencies, start services, or deploy.
- Enable hooks, MCP, memory, multi-agent runtimes, or external account integrations by default.
- Create issues or PRs automatically.
- Commit, tag, or push automatically.

## Quick Start

### 1. Generate The Project Template

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\projects\my-app" -ProjectName "my-app" -Mode Standard
```

Ubuntu / macOS:

```bash
./scripts/init-project-template.sh --target-path "$HOME/projects/my-app" --project-name "my-app" --mode Standard
```

Modes are written to initialization metadata only; they do not crop copied files:

| Mode | Best for |
| --- | --- |
| `Lite` | Small scripts, personal tools, quick prototypes |
| `Standard` | Normal apps, APIs, internal systems, data projects |
| `Enterprise` | Team delivery, production systems, high-risk or inherited projects |

If unsure, use `Standard`. Do not rush stack selection during template generation. New projects should choose a stack after goals and constraints are clear; existing projects should infer the stack from real files first.

### 2. Start Your AI Tool From The Generated Project

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

### 3. Send The Startup Message

Codex:

```text
Read AGENTS.md, prefer the project-local .agents/skills/project-init/SKILL.md, and help me initialize this project with ForgeKit. Do not read a user-level or system-level project-init path.
```

Claude Code:

```text
Read CLAUDE.md, prefer the project-local .agents/skills/project-init/SKILL.md, and help me initialize this project with ForgeKit. Do not read a user-level or system-level project-init path.
```

## What Gets Generated

After generation, Codex starts from `AGENTS.md`; Claude Code starts from `CLAUDE.md`. Both share `.codex/`, `.forgekit/`, `governance/`, and `.agents/skills/`.

Key files:

| Path | Purpose |
| --- | --- |
| `.forgekit/project-boundary.yml` | ForgeKitRoot, ProjectRoot, managed docs root, change root, and write policy |
| `.forgekit/docs/codebase-map.md` | Code entry points, module map, and local validation commands |
| `.forgekit/docs/local-toolchain.md` | Local lint, test, build, LSP, and toolchain capability |
| `.forgekit/docs/changelog.md` | Current version update record |
| `.forgekit/docs/version-roadmap.md` | Version roadmap and delivery gates |
| `.forgekit/docs/loop-readiness.md` | Whether the project has the state, validation, boundary, stop, and escalation conditions needed for a safe loop |
| `.forgekit/docs/loop-blueprint.md` | Reviewable loop design blueprint, not automatic execution authorization |
| `.forgekit/docs/loop-operations.md` | Explicitly triggered loop dry-run, one-step, continue, and stop/handoff operation protocol, not an automatic runner |
| `.forgekit/docs/maker-checker-protocol.md` | Evidence protocol for Maker implementation and Checker review, not an automatic multi-agent system |
| `.forgekit/docs/worktree-playbook.md` | Manual worktree isolation guide; no automatic creation, scheduling, merge, push, or PR |
| `.forgekit/changes/_template/` | proposal, design, tasks, verification, review, ship, and retro templates |
| `.codex/commands.md` | Project-specific commands |
| `.agents/skills/` | Self-contained project skills |
| `governance/ai-engineering-loop.md` | Risk levels, change artifacts, and delivery loop |

By default, ForgeKit governance docs are written under `.forgekit/docs/`, and medium/high-risk change artifacts are written under `.forgekit/changes/`. Existing business `docs/` is read-mostly evidence: AI may read and cite it, but should not write ForgeKit governance templates there by default.

## Core Capabilities

| Capability | Purpose |
| --- | --- |
| `project-init` | Discovery interview, project entry setup, and first project facts |
| `project-suitability` | Decide whether Lite, Standard, Enterprise, or Custom flow fits |
| `document-backfill` | Read existing business docs one by one and backfill the ForgeKit managed docs root |
| `handover-review` | Audit inherited projects and identify risks |
| `large-change-planning` | Explore and plan broad, cross-module, migration, or refactor work before implementation |
| `code-review` | Review for bugs, regression risks, and missing tests |
| `release-check` | Check release gates, validation, rollback, and delivery records |
| `security-review` | Review security risks |

Loop Readiness / Loop Blueprint provides managed docs templates and short entry rules only. It helps assess whether a project can safely run a loop; ForgeKit does not provide an automatic loop runner, daemon, cron, MCP, connector, automatic PR flow, sub-agent scheduler, or worktree automation.

Optional Loop Operation Mode defines only explicitly triggered dry-run, one-step, continue, and stop/handoff protocols. Loop operation is off by default; ForgeKit does not provide background automation, unattended runners, or continuous looping.

Maker / Checker Protocol defines evidence separation for medium/high-risk code changes: Maker implements and marks ready for check; Checker reviews diff, validation, risks, and document sync, then recommends pass / needs-fix / manual-review. It is not an automatic multi-agent system.

Worktree Playbook provides only manual worktree isolation guidance for parallel tasks, experiment branches, and AI multi-session collaboration. ForgeKit does not automatically create worktrees, start agents, merge, push, or create PRs.

The AI Engineering Loop scales artifacts by risk:

| Risk | Suggested artifacts |
| --- | --- |
| low | proposal / verification / review |
| medium | proposal / tasks / verification / review |
| high | proposal / design / tasks / verification / review / ship |

`retro` is recommended only after major changes, incidents, failed deliveries, or explicit team requests.

## Common Commands

### Template Repository Checks

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-template.ps1
```

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-plugin-assets.ps1
```

```bash
bash scripts/smoke-test.sh
python3 scripts/update-template-manifest.py --check --repo-root .
```

### Checks Inside A Generated Project

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-harness-check.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\check-doc-sync.ps1
```

```bash
./scripts/check-doc-sync.sh
```

These scripts only check, copy templates, or install local opt-in hooks. They do not install dependencies, start services, deploy, commit, tag, or push.

## Change Archiving

ForgeKit separates current truth from historical process:

- Current facts live in `.forgekit/docs/`.
- Active or recently completed changes live in `.forgekit/changes/`.
- Historical changes live in `.forgekit/archive/changes/YYYY/`.

Archive flow:

```bash
python3 scripts/archive-changes.py --dry-run
python3 scripts/archive-changes.py --reference-check --plan .forgekit/archive-plan.md
python3 scripts/archive-changes.py --sync-check --plan .forgekit/archive-plan.md
python3 scripts/archive-changes.py --smart-check --plan .forgekit/archive-plan.md --reference-report .forgekit/archive-reference-report.md --sync-report .forgekit/current-docs-sync-report.md
python3 scripts/archive-changes.py --smart-apply --report .forgekit/smart-archive-report.md --confirm
```

`--smart-apply` requires clean Git status and explicit `--confirm`. It moves only entries marked `Smart-Status: auto_archive_candidate` in `.forgekit/smart-archive-report.md` and writes `.forgekit/smart-archive-apply-report.md`.

## Upgrade An Existing Project

When upgrading from an older ForgeKit version, use upgrade mode and do not use `-Force` / `--force`:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\projects\my-app" -ProjectName "my-app" -Mode Standard -Upgrade -ExportUpgradeTemplates
```

```bash
./scripts/init-project-template.sh --target-path "$HOME/projects/my-app" --project-name "my-app" --mode Standard --upgrade --export-upgrade-templates
```

Upgrade mode generates reports and candidate templates only; it does not overwrite project files:

- Preserves project facts, `.forgekit/template-lock.json`, business `docs/`, `.codex/`, `AGENTS.md`, and `CLAUDE.md`.
- Writes skip / can_replace / needs_merge_report / can_restore / ask / readonly classifications to `.forgekit/upgrade-report.md`.
- Exports newer candidate templates by expanded target path under `.forgekit/upgrade-export/<version>/`.
- If an old project has no `.forgekit/template-lock.json`, ForgeKit writes a `legacy_no_lock` report and does not create a lock automatically.

After upgrading, ask the assistant:

```text
Review .forgekit/upgrade-report.md and compare .forgekit/upgrade-export/. Merge useful new ForgeKit template sections into existing project files without overwriting project facts, and do not treat upgrade-export as current-state docs.
```

## Inherited Projects

For inherited projects, the assistant should not ask for the stack first. It should read README files, setup notes, startup scripts, test docs, deployment docs, API docs, build files, and dependency files, then extract answers from evidence. Ask only when docs are missing, contradictory, or stale.

If there are many old docs, use:

```text
Use document-backfill to read documents under <old-docs-dir> one source document at a time and complete the ForgeKit managed docs root as you go. Do not read every document into one large summary.
```

## Optional Hooks

ForgeKit does not enable hooks by default. To enable document-sync reminders, install the opt-in Git hook:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-hooks.ps1 -Profile docs-warn -Target git
```

```bash
./scripts/install-hooks.sh --profile docs-warn --target git
```

`docs-warn` warns only. Use `docs-strict` only after the team accepts the noise level.

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

ForgeKit can coexist with ECC: ECC enhances the AI tool; ForgeKit constrains the project workspace.

## Recent Releases

| Version | User-facing change |
| --- | --- |
| `0.28.0` | Worktree Playbook: adds manual worktree isolation guidance and short entry rules without automatic worktree scheduling. |
| `0.27.0` | Optional Loop Operation Mode: adds explicit loop dry-run / one-step / continue / stop-handoff protocols without an automatic runner. |
| `0.26.0` | Maker / Checker Protocol: adds a managed docs template and review evidence fields to separate implementation and review without automatic multi-agent scheduling. |
| `0.25.0` | Loop Readiness / Loop Blueprint: adds managed docs templates and short entry rules for reviewing loop suitability and design, without an automatic runner. |
| `0.24.0` | Smart Archive Apply: with clean Git status and explicit confirmation, archives only changes marked `auto_archive_candidate` by Smart Archive Advisor and writes an apply report. |
| `0.23.0` | Smart Archive Advisor: combines archive plan, reference report, and sync report into a report-only archive advice report. |
| `0.22.0` | Current Docs Sync Check: generates a report-only current-docs sync evidence report from archive plan candidates without modifying project fact files. |
| `0.21.1` | Work Log Managed Doc Template: adds `.forgekit/docs/work-log.md` for personal work sequence, handoff context, and interrupted session recovery. |
| `0.21.0` | Archive Reference Check: generates a reference report from archive plan candidates and checks string references in current docs, active changes, and entry docs. |
| `0.20.0` | Archive Apply: moves candidate changes from a reviewed dry-run plan only after Git is clean and the user passes `--confirm`, then writes an apply report. |
| `0.19.0` | Archive Plan: adds a dry-run archive plan that only creates or overwrites `.forgekit/archive-plan.md` without moving files. |
| `0.18.0` | Document Lifecycle: adds current docs / changes / archive layers, keeps archive out of default context, and warns when done changes may be archived. |
| `0.17.0` | Template Versioning: adds template manifest / lock and report-only upgrade classifications with candidate template export, without automatic overwrites. |
| `0.16.0` | Boundary First: adds `.forgekit/project-boundary.yml`, writes ForgeKit managed docs to `.forgekit/docs`, and writes change artifacts to `.forgekit/changes` by default. |
| `0.15.0` | Repositioned ForgeKit as a lightweight AI engineering delivery toolkit with an AI Engineering Loop and risk-based change templates. |
