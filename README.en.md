# ForgeKit

中文文档: [README.md](README.md)

ForgeKit is a lightweight AI engineering delivery toolkit for keeping Codex, Claude Code, and adjacent coding agents inside a **reviewable, verifiable, and handoff-friendly** project workflow.

It does not generate business framework code or deploy your system. ForgeKit adds a local AI delivery workspace to a project so agents know the project boundary, work sources, verification path, risks, handoff state, and when to stop for user confirmation.

---

## One-line summary

```text
ForgeKit = local delivery rules, docs, and checks for AI coding tools.
```

It helps answer:

```text
Where may the agent edit?
Where did this task come from?
What is the current status?
How was it verified?
What risks remain?
When should docs be updated?
How does the next session / reviewer / teammate resume?
```

---

## When to use ForgeKit

| Scenario | What ForgeKit helps with |
| --- | --- |
| New project startup | Clarify goals, boundaries, stack choices, and validation paths before coding |
| Existing project adoption | Inspect README files, scripts, build files, and old docs before guessing the stack |
| Medium / high-risk changes | Require proposal, tasks, verification, and review; add design / ship when needed |
| Long AI sessions | Checkpoint at phase boundaries, before compact, and before switching sessions |
| Multiple AI tools | Let Codex and Claude Code share the same project facts and delivery rules |
| Multi-repo workspaces | Separate workspace, project, repo, artifact, and archive boundaries |
| Delivery handoff | Produce handoff, archive capsule, and review-ready summaries |

Not a fit for:

| Not for | Why |
| --- | --- |
| Business framework scaffolding | ForgeKit does not generate Spring / React / FastAPI business templates |
| Deployment platform | It does not install dependencies, start services, deploy, or release |
| Background automation | It does not provide runners, daemons, or schedulers |
| Automatic Git operations | It does not auto commit, tag, push, or create PRs |
| External account integration | It does not enable GitHub issues, MCP, memory, or cloud accounts by default |

---

## 3-minute quick start

### 1. Initialize or sync a target project from the ForgeKit repo

Windows PowerShell:

```powershell
python .\scripts\forgekit-project.py --target "D:\path\to\project"
```

macOS / Linux:

```bash
python3 ./scripts/forgekit-project.py --target "/path/to/project"
```

The unified entry detects:

| Target state | ForgeKit behavior |
| --- | --- |
| Not installed | Shows an initialization plan |
| Already current | Prints up-to-date |
| Older supported version | Runs check + plan first; applies only after confirmation |
| Toolkit too old | Stops and asks you to update the outer ForgeKit |
| Legacy project | Gives adoption guidance; does not force an upgrade |

It does not write by default. Safe writes require interactive confirmation or explicit `--yes`.

Only projects initialized at v0.36.0 or later with `.forgekit/state.json` support safe migrations. Treat v0.35.x and earlier projects as existing-project adoption; do not auto-upgrade them.

To generate reviewable Claude Code / Codex agent configuration during first initialization, use the lower-level advanced entry:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\path\to\workspace" -ProjectName "my-app" -Mode Standard -NativeAgentAdapter all
```

This option only generates configuration; it does not prove runtime agent registration.

---

### 2. Start your AI tool from the project root

Codex:

```powershell
cd D:\path\to\project
codex
```

Claude Code:

```powershell
cd D:\path\to\project
claude
```

---

### 3. Send the startup prompt

Codex:

```text
Read AGENTS.md, prefer the project-local .agents/skills/project-init/SKILL.md, and follow the ForgeKit workflow. First tell me the project boundary, current task, risks, and suggested next step. Do not edit files yet.
```

Claude Code:

```text
Read CLAUDE.md and follow the ForgeKit workflow. First tell me the project boundary, current task, risks, and suggested next step. Do not edit files yet.
```

---

## Copyable prompts for common situations

Detailed variants live in the generated project at:

```text
.forgekit/docs/usage-playbook.md
```

Use these short prompts for daily work.

| Goal | Prompt to send to Claude / Codex |
| --- | --- |
| Initialize a new project | `Use the ForgeKitRoot unified entry to initialize <project-root>. Show the plan first; do not commit automatically.` |
| Adopt an existing project | `Inspect <project-root> read-only and propose an existing-project adoption plan before changes.` |
| Upgrade ForgeKit in a project | `The outer ForgeKit is updated. Run check and plan for <project-root>; do not apply without confirmation.` |
| Start today’s work | `Use the workflow router to read current tasks, recent progress, risks, and verification entry points; give me today’s next step.` |
| Execute a task | `Execute <Task ID>. Confirm scope and verification first, then make a minimal checkpoint.` |
| Save current progress | `Write back only confirmed status, verification, risks, and next steps to their responsible docs.` |
| Before compact / clear | `Create a pre-compact checkpoint and list the files the next session should read first.` |
| Recover after compact | `A compact / session switch just happened. Read current docs to recover the current goal, latest conclusions, risks, verification, and next step. Do not edit files.` |
| Before commit | `Check diff, verification, independent review, risks, and minimal writeback. Do not commit automatically.` |
| End a phase / archive | `Check current docs integrity, then generate an Archive Capsule plan. Do not apply yet.` |
| Generate handoff | `Generate a review-ready handoff; mark missing evidence TODO_REVIEW and do not invent facts.` |
| Multi-project read-only analysis | `Analyze only mapped project/repo scopes; do not enable the map or create capsules.` |
| Before enabling multi-project map | `Run workspace integrity checks and provide adoption guidance only.` |
| First-principles analysis | `Analyze this from first principles: separate facts, assumptions, constraints, and the smallest correct mechanism.` |
| Adversarial review | `Run an adversarial review and focus on failure paths, edge cases, and verification gaps.` |

---

## When to update ForgeKit docs

Since v0.42, doc writeback is event-triggered, not “write after every edit”.

| Level | Write ForgeKit managed docs? | Typical cases |
| --- | --- | --- |
| Micro Update | No | typo, small parameter change, temporary experiment, one failed command, unconfirmed exploration |
| Checkpoint Update | Minimal writeback | small closed loop, task status change, root cause confirmed, new risk, useful verification, before interruption / session switch |
| Ship Update | Closure writeback | commit, tag, handoff, archive, release preparation |

Writeback targets:

| Information | Target |
| --- | --- |
| Progress and next step | `.forgekit/docs/work-log.md` |
| Task status change | `.forgekit/docs/task-board.md` |
| Verification result and gap | `.forgekit/docs/testing.md` |
| Risk or blocker | `.forgekit/docs/risk-register.md` |
| User-visible / version-visible change | `CHANGELOG.md` |
| Source fact change | `task-intake.md` or project `source-links.md` |

Important:

```text
Micro Update only skips ForgeKit governance-doc writeback.
It does not prohibit authorized edits to business code, business README files, comments, tests, or configuration.
```

Before predictable compact, clear, or session switch, run a pre-compact checkpoint.
After unexpected auto compact, start with a post-compact recovery check.

---

## Common commands

### Upgrade / sync ForgeKit in a project

Windows:

```powershell
python .\scripts\forgekit-project.py --target "D:\path\to\project"
powershell -ExecutionPolicy Bypass -File .\scripts\forgekit-project.ps1 --target "D:\path\to\project"
```

macOS / Linux:

```bash
python3 ./scripts/forgekit-project.py --target "/path/to/project"
bash ./scripts/forgekit-project.sh --target "/path/to/project"
```

### Lower-level upgrade commands

```bash
python scripts/forgekit-upgrade.py check --repo-root <project>
python scripts/forgekit-upgrade.py plan --repo-root <project>
python scripts/forgekit-upgrade.py apply --safe --repo-root <project>
```

| Command | Purpose |
| --- | --- |
| `check` | Check version and migration eligibility without writing |
| `plan` | Print a migration plan without writing |
| `apply --safe` | Run only migration actions explicitly marked safe |

### Check current docs integrity

Windows:

```powershell
python .\scripts\check-current-docs-integrity.py --repo-root "D:\path\to\project"
```

macOS / Linux:

```bash
python3 ./scripts/check-current-docs-integrity.py --repo-root "/path/to/project"
```

### Check multi-project workspace integrity

Windows:

```powershell
python .\scripts\check-workspace-integrity.py --repo-root "D:\path\to\workspace"
```

macOS / Linux:

```bash
python3 ./scripts/check-workspace-integrity.py --repo-root "/path/to/workspace"
```

---

## Generated content overview

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | Codex project entry |
| `CLAUDE.md` | Claude Code project entry |
| `.agents/skills/` | Self-contained project skills |
| `.codex/` | Codex rules, commands, and optional agent config |
| `.forgekit/state.json` | ForgeKit project version and feature state |
| `.forgekit/project-boundary.yml` | Project boundary and write policy |
| `.forgekit/workspace-map.json` | Machine-readable multi-project workspace map, disabled by default |
| `.forgekit/docs/` | Current project facts, tasks, verification, risks, handoff, and local toolchain docs |
| `.forgekit/projects/_template/` | Minimal Project Capsule template |
| `.forgekit/changes/` | Proposal / design / tasks / verification / review artifacts |
| `.forgekit/archive/` | Historical evidence and archive capsules |
| `scripts/` | Initialization, upgrade, check, and archive scripts |

Existing business `docs/` is read-mostly evidence by default. AI may read and cite it, but should not write ForgeKit governance templates there by default.

---

## Core capabilities

| Capability | Problem solved |
| --- | --- |
| Boundary-first workspace | Prevents agents from confusing ForgeKitRoot, ProjectRoot, business repo, and artifact paths |
| Source-first task intake | Records work sources before creating executable tasks |
| Risk-based change artifacts | Scales proposal / tasks / verification / review / design / ship by risk |
| Managed docs responsibility | Defines which docs own which facts and reduces duplicate writeback |
| Work session checkpoint | Avoids both over-writing docs and losing daily progress |
| Context Continuity Protocol | Preserves critical facts before compact, handoff, or session switch |
| Active current docs integrity | Prevents archive from breaking active task continuity |
| Project maintenance operations | Routes init, upgrade, archive, handoff, and reports through plan-first flows |
| Native Agent Adapter | Optionally generates Claude Code / Codex agent config; runtime registration and invocation still require verification |
| Independent Code Review Protocol | Separates maker from read-only reviewer |
| First-principles pass | Derives the smallest correct mechanism from facts, assumptions, and constraints |
| Adversarial review | Looks for failure paths before high-risk closure |
| Multi-project scoped docs | Separates workspace, project, repo, artifact, and archive boundaries |
| Safe migration | Uses plan-first safe upgrades without overwriting user content |

---

## Multi-project workspace model

Since v0.41, ForgeKit supports opt-in multi-project workspaces.

| Layer | Purpose |
| --- | --- |
| Workspace Docs | Cross-project facts, overall tasks, integration state, cross-project risks |
| Project Capsule | Local project tasks, tests, risks, and source links |
| Repo Lite | Thin code-repository pointer, not a third fact source |
| Artifact | Report samples, runtime logs, build outputs, test evidence |
| Archive | Historical evidence, not current truth |

New projects install a disabled `.forgekit/workspace-map.json` and `_template`. ForgeKit does not enable multi-project mode or split existing docs automatically.

Common path:

```text
Register a project as workspace-only first.
Switch only long-running independent projects to project-capsule later.
```

---

## Risk-based artifacts

| Risk | Suggested artifacts |
| --- | --- |
| low | proposal / verification / review |
| medium | proposal / tasks / verification / review |
| high | proposal / design / tasks / verification / review / ship |

Use `retro` only after major changes, incidents, failed deliveries, or explicit team requests.

---

## Common misunderstandings

| Misunderstanding | Reality |
| --- | --- |
| ForgeKit generates business project code | It does not; it generates an AI delivery workspace |
| ForgeKit deploys or releases my system | It does not |
| ForgeKit automatically commits or pushes | It does not |
| Every small edit needs a doc update | No; Micro Update skips ForgeKit governance docs |
| I can work all day without doc writeback | Risky; do a minimal checkpoint |
| Archive means deleting old files | No; archive is searchable historical evidence |
| Multi-project mode automatically splits docs | It does not; it only adds map, templates, and checks |
| Project Capsule is a full ForgeKit copy | No; it is a minimal local fact set |
| Codex / Claude automatically reloads new rules | Not guaranteed; after upgrade, start a new session for new work |

---

## Documentation map

| Need | File |
| --- | --- |
| Daily AI prompts | `.forgekit/docs/usage-playbook.md` |
| When to update docs | `.forgekit/docs/work-session-checkpoint.md` |
| Which doc owns which fact | `.forgekit/docs/document-responsibility.md` |
| Current tasks | `.forgekit/docs/task-board.md` |
| Work sources | `.forgekit/docs/task-intake.md` |
| Verification | `.forgekit/docs/testing.md` |
| Risks and blockers | `.forgekit/docs/risk-register.md` |
| Project boundary | `.forgekit/project-boundary.yml` |
| Multi-project boundary | `.forgekit/workspace-map.json` |
| Version history | `CHANGELOG.md` |

---

## Version history

For full version history, design tradeoffs, and the real pain points solved by each release, see:

```text
CHANGELOG.md
```

README intentionally keeps only the current positioning, quick start, common entries, and daily usage.
