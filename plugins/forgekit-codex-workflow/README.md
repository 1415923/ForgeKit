# ForgeKit Codex Workflow

Chinese documentation: [README.zh-CN.md](README.zh-CN.md).

**A practical Codex workflow plugin for real software projects.**

ForgeKit turns a new or existing repository into a Codex-ready project: clear startup context, planning documents, review gates, release checks, safety rules, and stack-specific guidance. It is built for teams that want Codex to work like a careful project collaborator instead of jumping straight from a vague idea into code.

It is not a framework, scaffolded app, or deployment tool. It is a project workflow harness: skills, templates, checklists, and validation scripts that help Codex ask better questions, keep decisions traceable, and stop before risky actions.

## Why Use It

- Start new projects with product and architecture discussion before implementation.
- Hand over existing projects with audit-first review instead of blind refactoring.
- Keep project docs, task plans, tests, release notes, and safety checks in one repeatable structure.
- Load only the stack rules you need, avoiding irrelevant context.
- Share the same Codex workflow across a team through one plugin package.

## Quick Start

Run from this plugin directory:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\projects\my-app" -ProjectName "my-app" -Stacks java-springboot,vue
```

Then start Codex inside the generated project and ask:

```text
Read AGENTS.md and help me initialize this project with ForgeKit.
```

Not sure which stack to choose yet? Omit `-Stacks` first:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\projects\my-app" -ProjectName "my-app"
```

Codex can help you choose stacks during the planning phase.

## Common Stack Values

| Project type | Use |
| --- | --- |
| Java + Vue full stack | `java-springboot,vue` |
| Java backend | `java-springboot` |
| Python API | `python-fastapi` |
| Node API | `node-express` |
| C# / .NET API or Worker | `csharp-dotnet` |
| Go service or CLI | `go-service` |
| Laravel app or API | `php-laravel` |
| Rust CLI or service | `rust-cli-service` |
| Flutter app | `flutter-dart` |
| C++ CMake project | `cpp-cmake` |
| Kotlin backend | `kotlin-spring` |
| iOS app | `swift-ios` |
| Rails app or API | `ruby-rails` |
| R analysis / Shiny | `r-data-analysis` |
| FPGA / HLS | `fpga-vivado-vitis` |

Frontend-only projects can use `vue` or `react`.

## What You Get

Generated projects include:

- `AGENTS.md`: the first file Codex should read.
- `.codex/`: project facts, scope, commands, safety, testing, style, and selected stack guidance.
- `.agents/skills/`: project initialization, handover review, code review, release check, and security review skills.
- `docs/`: requirements, architecture, task board, roadmap, testing, deployment, risk, release, and traceability documents.
- `governance/`: lightweight SDLC, definition of ready/done, change control, release, incident, security, and agent-harness guidance.
- `scripts/`: read-only local toolchain and harness checks.

The plugin package also includes top-level `skills/` so Codex can discover ForgeKit skills before a project is generated.

## How ForgeKit Changes Codex Behavior

For new project ideas, Codex should not immediately write code. ForgeKit asks it to:

1. Clarify the product goal and user scenario.
2. Compare feasible product and architecture options.
3. Identify stack, environment, data, deployment, and validation constraints.
4. Produce an execution summary.
5. Wait for explicit confirmation before coding, installing dependencies, initializing Git, committing, pushing, deploying, or writing outside the project.

For existing projects, ForgeKit starts with audit, codebase mapping, toolchain checks, and P0/P1 risk review before large changes.

## Safety Boundary

ForgeKit does not enable hooks or MCP by default.

It does not include:

- user-specific `user-rules/`
- external development records under `document/`
- credentials, tokens, private service URLs, or deployment automation
- automatic issue, PR, deploy, tag, commit, or push actions

High-risk actions still require explicit user confirmation.

## Validate The Plugin

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-plugin-assets.ps1
```

Optional smoke test:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\tmp\forgekit-plugin-smoke" -ProjectName "forgekit-plugin-smoke" -Stacks java-springboot,vue -Force
```

Then run this inside the generated smoke project:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-harness-check.ps1
```

## When To Use Lite, Standard, Or Enterprise

| Mode | Best for |
| --- | --- |
| Lite | Small scripts, personal tools, quick prototypes |
| Standard | Normal apps, APIs, internal systems, data processing projects |
| Enterprise | Team delivery, production systems, high-risk changes, inherited projects |

Start with Standard unless the project is obviously tiny or clearly high-risk.

## Package Design

`assets/project-template/` keeps generated projects self-contained. The top-level `skills/` copy is intentional: it lets Codex discover ForgeKit skills from the plugin before any project exists.

This plugin is the recommended distribution form for ForgeKit.
