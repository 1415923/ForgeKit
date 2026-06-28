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
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\projects\my-app-workspace" -ProjectName "my-app" -Mode Standard -NativeAgentAdapter all
```

Ubuntu / macOS:

```bash
./scripts/init-project-template.sh --target-path "$HOME/projects/my-app-workspace" --project-name "my-app" --mode Standard --native-agent-adapter all
```

This single command initializes the project template and generates reviewable Native Agent Adapter configuration templates for Claude Code and Codex. Generated config is not runtime registration; verify the first real invocation with `.forgekit/docs/native-agent-adapter.md`.

The generated workspace has two layers:

```text
my-app-workspace/        # outer layer: ForgeKit governance, AI entry files, .forgekit, .codex, scripts
  my-app/                # inner layer: real business code and Git repository
```

If you already have code, put the whole business project inside `my-app/`. For a new project, create source code, tests, business README, and build files inside the inner directory. Initialize Git, commit, and push from `my-app/` only, so ForgeKit governance files in the outer layer are not pushed to the business repository.

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
cd D:\projects\my-app-workspace
codex
```

Claude Code:

```powershell
cd D:\projects\my-app-workspace
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

## What To Read By Scenario

New users do not need to read every file. Start with the scenario-specific entry points:

| Scenario | Main files |
| --- | --- |
| Personal greenfield project | `AGENTS.md` / `CLAUDE.md`, `.forgekit/docs/document-responsibility.md`, `.forgekit/docs/codebase-map.md`, `.forgekit/docs/workflow-router.md`, `.forgekit/docs/task-intake.md`, `.forgekit/docs/task-board.md`, `.forgekit/docs/work-log.md` |
| Company project takeover | `AGENTS.md` / `CLAUDE.md`, `.forgekit/docs/document-responsibility.md`, `.forgekit/docs/codebase-map.md`, `.forgekit/docs/workflow-router.md`, `.forgekit/docs/local-toolchain.md`, `.forgekit/docs/handover-audit.md`, business `README` / `docs/` |
| Daily task development | `.forgekit/docs/task-intake.md`, `.forgekit/docs/task-board.md`, `.forgekit/docs/work-log.md`; read `testing.md` / `requirements.md` / `architecture.md` as needed |
| Medium/high-risk change | `.forgekit/changes/<change-id>/`, `.forgekit/docs/testing.md`, `.forgekit/docs/changelog.md`, and `architecture.md` when needed |
| Release check | `.forgekit/docs/changelog.md`, `.forgekit/docs/testing.md`, `.forgekit/docs/task-board.md`, `.codex/version-gates.md` |
| ForgeKit upgrade | `.forgekit/upgrade/upgrade-plan.md`, `.forgekit/upgrade/upgrade-actions.md`, `.forgekit/upgrade/candidates/<version>/` |

Takeover audit docs are not the daily task entry point. Once a project is stable, daily work usually follows `task-intake -> task-board -> work-log`, with requirements, testing, architecture, and changelog updated only when their facts change.

Business code lives under the inner `ProjectName/` directory by default. When AI needs code context, point it to the inner directory; keep ForgeKit managed docs, AGENTS, CLAUDE, and adapter config in the outer governance workspace.

## What Gets Generated

After generation, Codex starts from `AGENTS.md`; Claude Code starts from `CLAUDE.md`. Both share `.codex/`, `.forgekit/`, `governance/`, and `.agents/skills/`.

Key files:

| Path | Purpose |
| --- | --- |
| `.forgekit/project-boundary.yml` | ForgeKitRoot, ProjectRoot, managed docs root, change root, and write policy |
| `.forgekit/docs/document-responsibility.md` | Managed docs responsibility matrix: audience, triggers, write/do-not-write boundaries, and default-read policy |
| `.forgekit/docs/codebase-map.md` | Code search entry points, module entry map, and local validation commands; not a project encyclopedia |
| `.forgekit/docs/workflow-router.md` | User intent router: decide what to read, what to write, and what not to touch |
| `.forgekit/doc-health-report.md` | Doc health report: checks long docs, duplicated facts, misplaced content, and workflow-router boundary risks; report-only |
| `.forgekit/source-trace-report.md` | Source trace report: checks Source ID, requirement, task, change, verification, work-log, and changelog trace breaks; report-only |
| `.forgekit/handoff-package.md` | Review-ready handoff package: summarizes source, tasks, changes, verification, risks, and TODO_REVIEW; report-only |
| `.forgekit/docs/local-toolchain.md` | Local lint, test, build, LSP, and toolchain capability |
| `.forgekit/docs/changelog.md` | Current version update record |
| `.forgekit/docs/version-roadmap.md` | Version roadmap and delivery gates |
| `.forgekit/docs/task-intake.md` | Work source ledger: record assigned work, self-planned work, user feedback, bugs, and technical debt before deciding whether to create executable tasks |
| `.forgekit/docs/loop-readiness.md` | Whether the project has the state, validation, boundary, stop, and escalation conditions needed for a safe loop |
| `.forgekit/docs/loop-blueprint.md` | Reviewable loop design blueprint, not automatic execution authorization |
| `.forgekit/docs/loop-operations.md` | Explicitly triggered loop dry-run, one-step, bounded-auto, review-only, continue, and stop/handoff operation protocol, not an automatic runner |
| `.forgekit/docs/bounded-auto-loop-policy.md` | Scope, stages, budget, stop conditions, agent mode, and handoff rules for bounded user-authorized progress |
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
| `workflow-router` doc | Routes requests such as source text, current tasks, validation results, daily progress, handoff, loop continuation, or release closure to the right docs |
| `doc-health-report.py` | Generates `.forgekit/doc-health-report.md` for long docs, duplicate facts, role drift, and workflow-router boundary risks without automatic fixes |
| `source-trace-report.py` | Generates `.forgekit/source-trace-report.md` to check trace links from source to task, implementation, verification, and status records without automatic fixes |
| `handoff-package.py` | Generates `.forgekit/handoff-package.md` or change-scoped `handoff.md` for leader / reviewer / tester handoff without inventing missing evidence |
| `project-suitability` | Decide whether Lite, Standard, Enterprise, or Custom flow fits |
| `document-backfill` | Read existing business docs one by one and backfill the ForgeKit managed docs root |
| `handover-review` | Audit inherited projects and identify risks |
| `large-change-planning` | Explore and plan broad, cross-module, migration, or refactor work before implementation |
| `code-review` | Review for bugs, regression risks, and missing tests |
| `release-check` | Check release gates, validation, rollback, and delivery records |
| `security-review` | Review security risks |

Loop Readiness / Loop Blueprint provides managed docs templates and short entry rules only. It helps assess whether a project can safely run a loop; ForgeKit does not provide an automatic loop runner, daemon, cron, MCP, connector, automatic PR flow, sub-agent scheduler, or worktree automation.

Bounded Auto Loop Policy defines three explicitly authorized modes only: `one-step` stops after each round, `bounded-auto` proceeds only within scope / stages / budget / stop conditions, and `review-only` plans or reviews without file edits. It does not provide a runner, daemon, cron, scheduler, automatic PR, or worktree orchestration.

Optional Loop Operation Mode defines only explicitly triggered dry-run, one-step, bounded-auto, review-only, continue, and stop/handoff protocols. Loop operation is off by default; ForgeKit does not provide background automation, unattended runners, or continuous looping.

Maker / Checker Protocol defines evidence separation for medium/high-risk code changes: Maker implements and marks ready for check; Checker reviews diff, validation, risks, and document sync, then recommends pass / needs-fix / manual-review. It is not an automatic multi-agent system.

Worktree Playbook provides only manual worktree isolation guidance for parallel tasks, experiment branches, and AI multi-session collaboration. ForgeKit does not automatically create worktrees, start agents, merge, push, or create PRs.

Work Source Intake requires assigned work, self-planned work, user feedback, bugs, technical debt, test failures, or research findings to be recorded in `.forgekit/docs/task-intake.md` first: redacted original text or original idea, Update Notes, Task Decision, Derived Task IDs, and Human Review status. Small confirmations and schedule/responsibility updates should update the existing Source by default, not create new tasks. `task-board.md` only accepts executable tasks with action, owner, next step, Source ID, and verification method; `work-log.md` records progress and references Task ID / Source ID.

Managed Docs Responsibility Matrix v2 classifies `.forgekit/docs/**` as core, current, working, triggered, reference, generated, or archive. AI should start with `document-responsibility.md` and `codebase-map.md`, then read only docs triggered by the task; do not read all docs by default or duplicate the same fact across documents.

Managed Docs Writeback Policy defaults to `minimal` and separates business Implementation Scope from ForgeKit Governance Writeback Scope. A request to edit only named business files still permits factual updates to `work-log.md`, status changes in `task-board.md`, user/version-visible changes in `changelog.md`, and the current change artifacts. Writeback is disabled only when the user explicitly forbids documentation writes. Review-only and report-only tools remain non-writing and non-fixing.

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
## Native Agent Adapter

Native Agent Adapter is an opt-in feature that exports ForgeKit loop / maker-checker / verification protocols into reviewable native agent configuration templates for Claude Code and Codex. It only generates configuration; it does not run loops, start agents, provide a runner or dispatcher, automate worktrees, merge, commit, push, or create PRs.

Generated config is not proof that the runtime registered a native agent. Record native mode only after observing `forgekit-planner`, `forgekit-reviewer`, or `forgekit-verifier` being invoked. If execution uses a general-purpose / worker fallback with prompt injection, record fallback instead of calling it native success.

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\projects\my-app-workspace" -ProjectName "my-app" -Mode Standard -NativeAgentAdapter all
```

Bash:

```bash
./scripts/init-project-template.sh --target-path "$HOME/projects/my-app-workspace" --project-name "my-app" --mode Standard --native-agent-adapter all
```

The old standalone `generate-native-agent-adapter.*` scripts remain for compatibility and maintenance, but they are no longer the recommended path for new users. Prefer the one-step initialization command.

The Codex adapter generates `.codex/agents/*.toml` plus a minimal project-scoped `.codex/config.toml`. Run `python scripts/check-codex-native-agents.py --repo-root .` for schema checks; `SchemaStatus: pass` still does not mean runtime registration. Record native mode only after observing a `forgekit-*` agent invocation. If Codex only shows default / explorer / worker, record `native_agent_status=unavailable`.

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

When upgrading from an older ForgeKit version, prefer guided upgrade and do not use `-Force` / `--force`:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\upgrade-forgekit.ps1 -ProjectPath "D:\projects\my-app"
```

```bash
./scripts/upgrade-forgekit.sh --project-path "$HOME/projects/my-app"
```

Guided upgrade generates plans and candidate templates only; it does not overwrite project files:

- Preserves project facts, `.forgekit/template-lock.json`, business `docs/`, source code, `.codex/`, `AGENTS.md`, and `CLAUDE.md`.
- Writes `.forgekit/upgrade/upgrade-plan.md` with must_review / merge_carefully / can_add / can_ignore / template_only classifications.
- Writes `.forgekit/upgrade/upgrade-actions.md` as a short AI merge work order.
- Exports newer candidate templates by expanded target path under `.forgekit/upgrade/candidates/<version>/`.
- If an old project has no `.forgekit/template-lock.json`, ForgeKit writes `.forgekit/upgrade/legacy-inventory.md` and does not create a lock automatically.

After upgrading, ask the assistant:

```text
Read .forgekit/upgrade/upgrade-actions.md and merge ForgeKit upgrade content according to .forgekit/upgrade/upgrade-plan.md. Inspect only must_review, merge_carefully, and needed can_add files; do not overwrite project facts, business docs, source code, or template-lock, and do not treat candidates as current-state docs.
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
| `0.35.2` | Managed Docs Writeback Policy: separates implementation scope from governance writeback and restores minimal work-log / task-board / changelog / change updates while preserving review-only and report-only boundaries. |
| `0.35.1` | Codex Custom Agent Schema Hotfix: fixes and validates Codex custom agent TOML so `name`, `description`, and `developer_instructions` are strings, avoiding table/map schema errors. |
| `0.35.0` | Review-Ready Handoff Package: adds a report-only handoff package for source, requirement, task, change, verification, risk, and TODO_REVIEW summaries without automatic fixes, commits, or PRs. |
| `0.34.0` | Source Trace Report v2: adds a report-only source trace report for Source ID -> requirement -> task -> change -> verification -> work-log/changelog breaks without automatic fixes. |
| `0.33.0` | Doc Health Report v2: adds a report-only managed-docs health summary for long docs, duplicated facts, misplaced content, and workflow-router boundary risks without automatic fixes. |
| `0.32.0` | Workflow Router: adds `.forgekit/docs/workflow-router.md` to route user intent to the right Read / Write / Do Not Write docs, reducing full-doc scans and duplicate writes. |
| `0.31.0` | Bounded Auto Loop Policy: adds one-step / bounded-auto / review-only authorization boundaries, budgets, stop conditions, agent mode gates, and handoff rules without a runner. |
| `0.30.1` | Native Agent Adapter Verification: clarifies that generated config is not runtime registration, and adds native / fallback / simulated state fields and verification checklists. |
| `0.30.0` | Native Agent Adapter: adds opt-in native agent configuration generation, exporting ForgeKit loop / maker-checker / verification protocols as reviewable Claude Code / Codex templates without automatic execution. |
| `0.29.0` | Guided Upgrade Workflow: adds standalone upgrade scripts that generate upgrade-plan, upgrade-actions, and candidate templates to reduce manual judgment and token cost. |
| `0.28.5` | Work Source Unification: brings assigned work, self-planned work, user feedback, bugs, and technical debt into one Source ID -> Task ID -> Work Log chain. |
| `0.28.4` | Source-to-Task Alignment: tightens task-intake, task-board, and work-log linkage so updates merge into existing Sources and task-board only accepts executable tasks. |
| `0.28.3` | Localized triggered managed docs: loop, maker-checker, worktree, and change templates are Chinese-readable while keeping machine fields stable. |
| `0.28.2` | Managed Docs Responsibility Matrix v2: tightens managed doc ownership, default-read policy, and duplicate-write boundaries so human-facing docs stay shorter and easier to confirm. |
| `0.28.1` | Source-First Task Intake: adds `.forgekit/docs/task-intake.md` for source assignment text, AI interpretation, task backlinks, and human review status. |
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
