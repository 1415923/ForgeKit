# ForgeKit Claude Workflow

Chinese documentation: [README.zh-CN.md](README.zh-CN.md).

**A ForgeKit workflow plugin for Claude Code.**

This package adapts the ForgeKit project workflow skills for Claude Code. It is a sibling distribution to `forgekit-codex-workflow`, not a replacement for it.

ForgeKit is not an app framework, code scaffold, or deployment tool. It helps Claude Code clarify project goals, discovery state, risks, validation evidence, and execution boundaries before implementation.

## What This Version Does

`v0.11.0` provides the Claude Code plugin package:

- `.claude-plugin/plugin.json` for Claude Code plugin discovery.
- ForgeKit workflow skills under `skills/`.
- Shared template assets under `assets/`.
- Read-only validation and inspection scripts under `scripts/`.
- Separate package validation with `scripts/validate-plugin-assets.ps1`.

This version does not enable hooks, MCP, subagents, slash commands, deployment, issue writes, Git writes, or external automation by default.

## Quick Start

### Step 1: Add the local plugin marketplace or plugin path

Use your team's Claude Code plugin installation flow for a local or repository plugin. The plugin directory is:

```text
plugins/forgekit-claude-workflow/
```

The manifest is:

```text
plugins/forgekit-claude-workflow/.claude-plugin/plugin.json
```

### Step 2: Start Claude Code in your project

```powershell
cd D:\projects\my-app
claude
```

If your Claude Code command is different, use your normal command. The important part is that the working directory is the project root.

### Step 3: Ask Claude Code to use ForgeKit

```text
Use ForgeKit to initialize or review this project. Start by clarifying discovery state before implementation.
```

Claude Code should discover the bundled skills and apply the relevant workflow.

## Discovery Interview

ForgeKit uses the same discovery states as the Codex package:

| State | What Claude Code should do |
| --- | --- |
| `unclear` | Ask only about goal, users, pain, success evidence, and non-goals |
| `options-needed` | Provide 2 to 4 viable product-shape or scope options with tradeoffs and a recommended default |
| `research-needed` | Name the unknown, blocked decision, and official docs, GitHub examples, or prototype to inspect |
| `existing-project-scan` | Inspect local files first, then report inferred stack, commands, tests, integration points, and contradictions |
| `ready-for-plan` | Stop broad discovery and produce the project plan, roadmap, task split, and execution confirmation |

## Checks

Validate the Claude plugin package:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-plugin-assets.ps1
```

From the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\plugins\forgekit-claude-workflow\scripts\validate-plugin-assets.ps1
```

## Package Layout

```text
forgekit-claude-workflow/
├─ .claude-plugin/
│  └─ plugin.json
├─ skills/
├─ scripts/
└─ assets/
   ├─ project-template/
   ├─ templates/
   ├─ questionnaires/
   └─ docs/
```

## Roadmap Boundary

This is the first Claude Code distribution layer. Native generated-project support for `CLAUDE.md` and `.claude/skills/` is planned as a later step.
