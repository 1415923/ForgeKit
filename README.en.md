# ForgeKit

Chinese documentation: [README.md](README.md).

**ForgeKit is a practical AI coding workflow plugin for real software projects.**

ForgeKit is not an app framework, code scaffold, or deployment tool. It turns a new or existing repository into an AI-ready project for Codex, Claude Code, and adjacent coding tools: clear entry points, discovery interviews, project documents, stack templates loaded on demand, review gates, release checks, and safety boundaries.

In short: ForgeKit helps the AI assistant clarify the goal, plan, risks, and validation path before it starts coding.

## Guides

If this is your first time here, read only these sections:

| Topic | What to read |
| --- | --- |
| Quick Start | Initialize a project and start the AI assistant in 3 steps |
| Discovery Interview | Let the AI clarify product shape and stack decisions through conversation |
| Safety Boundary | Understand what the plugin will not automate |

After generation, Codex starts from `AGENTS.md`; Claude Code starts from `CLAUDE.md`. Both share the same `.codex/`, `docs/`, and `governance/` project facts.

## Boundary With ECC

ForgeKit is not a smaller ECC and does not compete with ECC as an agent runtime. ECC is closer to an AI coding tool enhancement suite, covering commands, hooks, memory, MCP, multi-agent workflows, security tools, and cross-tool adapters.

ForgeKit has a narrower job: make a real project ready for stable AI handover. Its focus is project entry points, discovery interviews, existing-project scans, project documents, version roadmaps, task breakdown, review gates, release checks, and execution confirmation.

Default boundaries:

- Do not enable hooks, MCP, memory, session tracking, or multi-agent runtimes by default.
- Do not replicate ECC's command system, security tooling, cost controls, or automation runtime.
- Coexist with ECC: ECC enhances the AI tool; ForgeKit constrains the concrete project's delivery workflow.

## What's New

The current plugin includes:

- Skills for project initialization, handover review, code review, release check, and security review.
- One root-level plugin surface shared by Codex and Claude Code.
- Three project modes: Lite, Standard, and Enterprise, written during initialization with `-Mode`.
- Stack templates that can be loaded after the product and architecture direction is understood.
- Discovery states: `unclear`, `options-needed`, `research-needed`, `existing-project-scan`, and `ready-for-plan`.
- Read-only scripts for local toolchain checks and harness checks.
- Plugin validation to keep user paths, external records, and `.git/` out of the distribution.

## Quick Start

### Step 1: Generate a project from the ForgeKit directory

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\projects\my-app" -ProjectName "my-app" -Mode Standard
```

Do not rush stack selection here. For new projects, stack decisions should come after product shape, users, runtime constraints, validation needs, and deployment expectations are understood. For existing projects, the AI assistant should scan the current repository first and infer the stack from real files.

Mode is the only decision to make in Step 1:

| Mode | Best for | Command value |
| --- | --- | --- |
| Lite | Small scripts, personal tools, quick prototypes | `-Mode Lite` |
| Standard | Normal apps, APIs, internal systems, data projects | `-Mode Standard` |
| Enterprise | Team delivery, production, high-risk or inherited projects | `-Mode Enterprise` |

If unsure, use `Standard`. The selected mode is written into `.codex/init.generated.md` and `.claude/init.generated.md`.

### Step 2: Start from the generated project

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

If your startup command is different, use your normal command. The important part is that the working directory is the generated project root.

### Step 3: Send the startup message

Codex:

```text
Read AGENTS.md and help me initialize this project with ForgeKit.
```

Claude Code:

```text
Read CLAUDE.md and help me initialize this project with ForgeKit.
```

This starts the actual project planning conversation. The assistant will read the entry files and use your selected `-Mode` and project facts.

## Discovery Interview

For a new project, the AI assistant should not start with five fixed technical questions. It should first clarify:

1. Who the project serves, what pain it solves, and how success is measured.
2. Possible product shapes, including scope, cost, risks, and explicit non-goals.
3. Whether official docs, public repositories, product examples, or technical references should be researched.
4. The v0.1.0 minimum closed loop before architecture and stack decisions.
5. Options, defaults, and verification paths when the user cannot answer yet.

For an existing project, the assistant should not ask the user to restate the stack. It should scan the repository, README, build files, dependency files, scripts, and tests. New features, fixes, and refactors should default to the existing stack unless the user explicitly asks for migration or architectural change.

ForgeKit drives the interview toward a concrete state:

| State | What the assistant should do |
| --- | --- |
| `unclear` | Ask only about goal, users, pain, success evidence, and non-goals |
| `options-needed` | Provide 2 to 4 viable product-shape or scope options with tradeoffs and a recommended default |
| `research-needed` | Name the unknown, the blocked decision, and the official docs, GitHub examples, or prototype to inspect |
| `existing-project-scan` | Inspect local files first, then report inferred stack, commands, tests, integration points, and contradictions |
| `ready-for-plan` | Stop broad discovery and produce the project plan, roadmap, task split, and execution confirmation |

## Root-level plugin surface

Since ForgeKit 0.12.0, there are no separate Codex and Claude Code plugin subdirectories. The repository root is the unified plugin surface:

```text
ForgeKit/
├─ .codex-plugin/
│  └─ plugin.json                 # Codex plugin metadata
├─ .claude-plugin/
│  ├─ plugin.json                 # Claude Code plugin metadata
│  └─ marketplace.json            # Claude Code local marketplace example
├─ .agents/plugins/
│  └─ marketplace.json            # Codex local marketplace example
├─ skills/                        # Skills shared by Codex and Claude Code
├─ scripts/
│  ├─ init-project-template.ps1    # initialize a target project
│  └─ validate-plugin-assets.ps1   # validate the root plugin surface
├─ project-template/               # base generated-project template
├─ templates/                      # stack templates
└─ questionnaires/                 # initialization questions
```

Both `.codex-plugin/plugin.json` and `.claude-plugin/plugin.json` point to `./skills/`. Both marketplace examples point to the repository root `./`.

## Cross-Platform Support

ForgeKit is mostly Markdown, skills, and PowerShell scripts.

| Platform | Support |
| --- | --- |
| Windows | Primary supported platform; initializer and validation scripts are PowerShell |
| macOS / Linux | Generated Markdown, skills, and project rules are usable; initialization needs PowerShell 7 or manual copy |
| Codex CLI | Works through generated `AGENTS.md`, `.codex/`, and `.agents/skills/` |
| Claude Code | Works through generated `CLAUDE.md`, `.claude/skills/`, and shared project documents |

ForgeKit does not install JDK, Node, Python, Flutter, Xcode, Rust, CMake, or other toolchains. Missing tools are reported by detection scripts so the user can decide what to install.

## Checks And Tools

Validate the root plugin surface:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-plugin-assets.ps1
```

Validate the template:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-template.ps1
```

Generate a smoke-test project:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\tmp\forgekit-plugin-smoke" -ProjectName "forgekit-plugin-smoke" -Mode Standard -Force
```

Run the harness check inside a generated project:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-harness-check.ps1
```

Run the local toolchain detector inside a generated project:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\detect-local-toolchain.ps1
```

These scripts check and copy templates only. They do not install tools, start services, or deploy projects.

## What's In The Generated Project

```text
AGENTS.md                         # Codex entry
CLAUDE.md                         # Claude Code entry
.codex/                           # Codex project context, commands, rules, initialization record
.claude/                          # Claude Code thin entry and initialization record
.agents/skills/                   # self-contained generated-project skills
docs/代码库地图.md                # codebase entry and module map
docs/本地工具链检查.md            # toolchain and validation capability record
docs/Codex下一步工作单.md         # next work order
docs/
governance/
scripts/
```

## Stack Templates Are Loaded On Demand

Global rules keep only cross-project behavior. Java, Vue, React, Python, Node, C#/.NET, Go, Laravel, Rust, Flutter, C++, Kotlin, Swift, Rails, R, FPGA, and other stack-specific rules live under `templates/`, but they are not selected during initialization.

For new projects, load stack templates after the discovery interview. For existing projects, infer the stack from local files first.

Do not load FPGA rules for a Java project, and do not load C# rules for a Laravel project. Load only what the current project needs to avoid context rot.

## Safety Boundary

This plugin is a distribution package, not an automation switch.

It does not enable by default:

- hooks
- MCP
- external account integrations
- automatic deployment
- automatic issue or PR creation
- automatic commit, tag, or push

It also does not include:

- `user-rules/`, which usually contains machine-specific paths and personal preferences
- external development records under `document/`
- credentials, tokens, private service URLs, or deployment automation

High-risk actions still require explicit user confirmation.

## How ForgeKit Changes AI Behavior

For new project ideas, the assistant should:

1. Clarify the product goal, user scenario, and real problem.
2. Compare feasible product and architecture options.
3. Confirm environment, data, deployment, testing, and acceptance constraints, then confirm the stack when the plan is clear enough.
4. Produce an execution confirmation summary.
5. Wait for explicit confirmation before coding, installing dependencies, initializing Git, committing, pushing, deploying, or writing outside the project.

For existing projects, ForgeKit starts with audit, codebase mapping, toolchain checks, and P0/P1 risk review before large changes.
