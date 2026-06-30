# ForgeKit

Chinese documentation: [README.md](README.md)

ForgeKit is a lightweight AI engineering delivery toolkit for keeping Codex, Claude Code, and adjacent coding agents inside a reviewable, verifiable, and handoff-friendly project workflow.

It does not generate business framework code or deploy your system. ForgeKit adds a local AI delivery workspace to a project: entry files, project boundaries, shared skills, risk-based change artifacts, governance docs, check scripts, and optional agent configuration templates.

## Why ForgeKit

AI coding tools can write code quickly. Delivery usually breaks for different reasons:

- The agent does not know the project boundary and edits the wrong repository or old docs.
- Requirements, tasks, implementation, verification, and handoff records are not traceable.
- Medium or high-risk changes skip proposal, tasks, verification, or review.
- Codex and Claude Code read different context and operate on different facts.
- The code is done, but reviewers cannot quickly see what changed, how it was verified, and what risks remain.

ForgeKit turns those delivery constraints into project-local files so AI work can move through one checkable workflow.

## When To Use It

Use ForgeKit when you want to:

- Start a new AI-assisted project after clarifying goals, boundaries, stack choices, and validation paths.
- Take over an existing project by extracting facts from README files, scripts, build files, and old docs before guessing the stack.
- Require proposal / tasks / verification / review before medium or high-risk changes, with design / ship / retro when needed.
- Let Codex and Claude Code share the same project facts, commands, skills, and delivery rules.

ForgeKit does not:

- Scaffold business framework code.
- Install dependencies, start services, deploy, or release.
- Enable hooks, MCP, memory, multi-agent runtimes, or external account integrations by default.
- Create issues or PRs automatically.
- Commit, tag, or push automatically.

## Quick Start

### 1. Generate a workspace

Use the unified entry by default. It detects whether the target needs initialization, is current, needs an upgrade plan, or requires legacy adoption:

```powershell
python .\scripts\forgekit-project.py --target "D:\projects\my-app-workspace"
```

The default confirmation is No. Non-interactive use only shows the plan; explicit `--yes` is required for initialization or `apply --safe`. An uninstalled but non-empty target also requires `--force-init`, while existing files remain preserved.

Use the lower-level init entry when you need explicit Mode, stack, or Native Agent Adapter selection:

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\projects\my-app-workspace" -ProjectName "my-app" -Mode Standard -NativeAgentAdapter all
```

Ubuntu / macOS:

```bash
./scripts/init-project-template.sh --target-path "$HOME/projects/my-app-workspace" --project-name "my-app" --mode Standard --native-agent-adapter all
```

The generated workspace has two layers:

```text
my-app-workspace/        # outer layer: ForgeKit governance, AI entry files, .forgekit, .codex, scripts
  my-app/                # inner layer: real business code and Git repository
```

If you already have code, put the whole business project inside `my-app/`. For a new project, put source code, tests, the business README, and build files inside the inner directory.

Initialize Git, commit, and push from `my-app/` only, so ForgeKit governance files in the outer layer are not pushed to the business repository.

### 2. Start your AI tool from the outer layer

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

### 3. Send the startup message

Codex:

```text
Read AGENTS.md, prefer the project-local .agents/skills/project-init/SKILL.md, and help me initialize this project with ForgeKit. Do not read a user-level or system-level project-init path.
```

Claude Code:

```text
Read CLAUDE.md, prefer the project-local .agents/skills/project-init/SKILL.md, and help me initialize this project with ForgeKit. Do not read a user-level or system-level project-init path.
```

`-NativeAgentAdapter all` only generates reviewable native agent configuration templates for Claude Code and Codex. It does not prove runtime registration. Verify the first real invocation with `.forgekit/docs/native-agent-adapter.md` before recording native mode.

## Upgrade Existing ForgeKit Projects

The entry semantics are unified; shell syntax remains platform-specific.

Windows PowerShell:

```powershell
python .\scripts\forgekit-project.py --target "D:\path\to\project"
powershell -ExecutionPolicy Bypass -File .\scripts\forgekit-project.ps1 --target "D:\path\to\project"
```

macOS / Linux:

```bash
python3 ./scripts/forgekit-project.py --target "/path/to/project"
bash ./scripts/forgekit-project.sh --target "/path/to/project"
```

It shows ProjectRoot, installed version, toolkit version, and the detected action. For an older supported project it runs check + plan first, then calls `apply --safe` only after interactive `y/yes` or explicit `--yes`.

Starting with v0.36.0, new projects use the Versioned Migration Upgrade Model. These commands remain available as advanced entries:

```bash
python scripts/forgekit-upgrade.py check --repo-root <project>
python scripts/forgekit-upgrade.py plan --repo-root <project>
python scripts/forgekit-upgrade.py apply --safe --repo-root <project>
```

- `check` verifies `.forgekit/state.json` and migration eligibility without writing files.
- `plan` prints a one-screen migration plan without writing files.
- `apply --safe` runs only actions explicitly marked safe; it does not perform three-way merge, edit business docs, or create commits.

If an upgrade changes AGENTS / CLAUDE / rules, skills, or agents, use the current session only for checkpoint and closure. Start a new session or restart the tool before new work; updated files on disk do not prove that the old session reloaded them.

Only projects initialized at v0.36.0 or later with `.forgekit/state.json` use this model. v0.35.x and earlier projects should be treated as existing-project adoption: inventory current facts first, then create new v0.36+ state only after explicit user confirmation.

## Project Maintenance

v0.39.0 adds Project Maintenance Operations and Unified Project Bootstrap. Install, init, update, and sync requests prefer `forgekit-project.py` for automatic routing; other maintenance follows `intent -> plan -> confirm/apply -> summary/index`.

## First-Principles and Adversarial Review

v0.40.0 adds two risk-triggered protocols. Complex problems derive the smallest correct mechanism from facts, assumptions, and constraints; high-risk closure actively searches for failure paths. They are not mandatory for typos or low-risk edits and do not replace independent code review.

```text
Analyze this bug root cause from first principles.
Run an adversarial review of this feature and focus on failure paths.
```

```text
I updated the outer ForgeKit; sync this project.
This phase is complete; archive it as a capsule.
Generate a maintenance plan, but do not apply it.
```

Upgrade sync reuses `forgekit-upgrade.py check / plan / apply --safe`. Phase archive uses `scripts/archive-capsule.py plan` and requires explicit `apply --confirm`. Archive is not deletion: apply creates a capsule summary, item log, and `.forgekit/archive/index.md` without reorganizing legacy archive or modifying business docs.

## Workflow

ForgeKit recommends one traceable delivery chain:

```text
source -> task -> change -> verification -> review -> work-log / changelog / handoff
```

Typical daily use:

1. Record assigned work, feedback, bugs, technical debt, or research findings in `.forgekit/docs/task-intake.md`.
2. Move only executable work into `.forgekit/docs/task-board.md`.
3. Create change artifacts under `.forgekit/changes/<change-id>/` based on risk.
4. Implement and record verification results.
5. Review code changes with the Independent Code Review Protocol, separating the maker from an independent read-only reviewer.
6. Create a minimal Context Checkpoint at phase boundaries, before context compact/clear, and after critical subagent findings.
7. Update work-log, changelog, or handoff records for resumption and transfer.

Suggested artifacts by risk:

| Risk | Suggested artifacts |
| --- | --- |
| low | proposal / verification / review |
| medium | proposal / tasks / verification / review |
| high | proposal / design / tasks / verification / review / ship |

Use `retro` only after major changes, incidents, failed deliveries, or explicit team requests.

## Generated Files

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | Codex project entry |
| `CLAUDE.md` | Claude Code project entry |
| `.agents/skills/` | Self-contained project skills |
| `.forgekit/project-boundary.yml` | ForgeKitRoot, ProjectRoot, managed docs root, change root, and write policy |
| `.forgekit/docs/` | Managed docs for project facts, tasks, verification, handoff, and local toolchain |
| `.forgekit/changes/` | Proposal / design / tasks / verification / review artifacts for risky changes |
| `.codex/` | Codex commands, version gates, and optional agent config |
| `governance/` | AI Engineering Loop and governance notes |
| `scripts/` | Initialization, checks, upgrades, archiving, and opt-in hook scripts |

Existing business `docs/` is read-mostly evidence by default. AI may read and cite it, but should not write ForgeKit governance templates there by default.

## Core Capabilities

| Capability | Purpose |
| --- | --- |
| Boundary-first workspace | Separates the outer governance workspace from the inner business repository |
| Source-first task intake | Records work sources before deciding whether to create executable tasks |
| Risk-based change artifacts | Scales proposal, tasks, verification, review, design, and ship artifacts by risk |
| Managed docs responsibility | Defines when docs should be read, what should be written, and what should not be duplicated |
| Report-only checks | Produces doc-health, source-trace, and handoff reports without automatic fixes or commits |
| Native Agent Adapter | Optionally exports Codex / Claude Code native agent configuration templates |
| Independent Code Review Protocol | Uses an independent read-only reviewer, a minimal context packet, and pass / needs-fix / manual-review gates |
| Context Continuity Protocol | Checkpoints critical facts to responsible docs so long sessions, compaction, clearing, and delegation do not erase engineering state |
| Project Maintenance Operations | Routes upgrade sync, Archive Capsule, checkpoint, handoff, and reports through plan, confirmation, and summary/index steps |

## Common Commands

Template repository checks:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-template.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\validate-plugin-assets.ps1
```

```bash
bash scripts/smoke-test.sh
python3 scripts/update-template-manifest.py --check --repo-root .
```

Checks inside a generated project:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-harness-check.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\check-doc-sync.ps1
```

```bash
./scripts/check-doc-sync.sh
```

These scripts only check, copy templates, or install local opt-in hooks. They do not install dependencies, start services, deploy, commit, tag, or push.


## Optional Features

### Native Agent Adapter

Native Agent Adapter exports ForgeKit loop, maker-checker, and verification protocols as reviewable native agent configuration templates for Codex and Claude Code.

It only generates config. It does not run loops, start agents, provide a runner or dispatcher, automate worktrees, merge, commit, push, or create PRs.

### Hooks

ForgeKit does not enable hooks by default. To enable document-sync reminders, install the opt-in Git hook:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-hooks.ps1 -Profile docs-warn -Target git
```

```bash
./scripts/install-hooks.sh --profile docs-warn --target git
```

`docs-warn` warns only. Use `docs-strict` only after the team accepts the noise level.

### Change Archiving

ForgeKit separates current truth from historical process:

- Current facts: `.forgekit/docs/`
- Active or recently completed changes: `.forgekit/changes/`
- Historical changes: `.forgekit/archive/changes/YYYY/`

Common archive entry points:

```bash
python3 scripts/archive-changes.py --dry-run
python3 scripts/archive-changes.py --smart-check --plan .forgekit/archive-plan.md --reference-report .forgekit/archive-reference-report.md --sync-report .forgekit/current-docs-sync-report.md
python3 scripts/archive-changes.py --smart-apply --report .forgekit/smart-archive-report.md --confirm
```

`--smart-apply` requires clean Git status and explicit `--confirm`. It moves only changes marked `auto_archive_candidate` in the report.

## Boundary With ECC

ECC is closer to an AI coding tool enhancement suite: commands, hooks, memory, MCP, multi-agent workflows, security tools, and cross-tool adapters.

ForgeKit has a narrower job: constrain the concrete project's delivery workflow so AI tools can take over more reliably.

They can coexist: ECC enhances the AI tool; ForgeKit constrains the project workspace.

## Version Note

See [CHANGELOG.md](CHANGELOG.md) for the full release history.
