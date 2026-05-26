# ForgeKit Claude Workflow

Chinese documentation: [README.zh-CN.md](README.zh-CN.md).

**A ForgeKit workflow plugin for Claude Code.**

This package adapts the ForgeKit project workflow skills for Claude Code. It is a sibling distribution to `forgekit-codex-workflow`, not a replacement for it.

ForgeKit is not an app framework, code scaffold, or deployment tool. It helps Claude Code clarify project goals, discovery state, risks, validation evidence, and execution boundaries before implementation.

## What This Version Does

`v0.11.1` provides the Claude Code plugin package and generated-project entry:

- `.claude-plugin/plugin.json` for Claude Code plugin discovery.
- ForgeKit workflow skills under `skills/`.
- Shared template assets under `assets/`.
- Initialization, read-only validation, and inspection scripts under `scripts/`.
- Separate package validation with `scripts/validate-plugin-assets.ps1`.
- `CLAUDE.md` and `.claude/skills/forgekit-project-workflow/` for the generated project's Claude Code entry.

This version does not enable hooks, MCP, subagents, slash commands, deployment, issue writes, Git writes, or external automation by default.

The Claude entry follows an ECC-style "shared core assets plus thin tool entry" approach. `.claude/skills/forgekit-project-workflow/` only routes and gates work; project facts still live in `.codex/`, `docs/`, and `governance/`.

## Boundary With ECC

ForgeKit Claude Workflow is not a smaller ECC and does not compete with the Claude Code runtime. ECC is closer to an AI coding tool enhancement suite, covering commands, hooks, memory, MCP, multi-agent workflows, security tools, and cross-tool adapters.

ForgeKit has a narrower job: make a real project ready for stable Claude Code handover. Its focus is project entry points, discovery interviews, existing-project scans, project documents, version roadmaps, task breakdown, review gates, release checks, and execution confirmation.

Default boundaries:

- Do not enable hooks, MCP, memory, session tracking, subagents, or slash commands by default.
- Do not replicate ECC's command system, security tooling, cost controls, or automation runtime.
- Coexist with ECC: ECC enhances the AI tool; ForgeKit constrains the concrete project's delivery workflow.

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

### Step 2: Generate the project entry

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\projects\my-app" -ProjectName "my-app" -Mode Standard
```

This generates `CLAUDE.md` and `.claude/skills/forgekit-project-workflow/`, while keeping shared project facts in `.codex/`, `docs/`, and `governance/`.

### Step 3: Start Claude Code in your project

```powershell
cd D:\projects\my-app
claude
```

If your Claude Code command is different, use your normal command. The important part is that the working directory is the project root.

### Step 4: Ask Claude Code to use ForgeKit

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

This is the Claude Code project-entry adapter, not an ECC-style runtime enhancement layer. ForgeKit does not enable hooks, MCP, subagents, or slash commands by default.
