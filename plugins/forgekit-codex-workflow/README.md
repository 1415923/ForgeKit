# ForgeKit Codex Workflow Plugin

This plugin distributes the ForgeKit Codex workflow harness for team use.

## Included

- Skills for project initialization, bootstrap filling, handover review, code review, release checks, and security review.
- Read-only scripts for local toolchain detection and generated-project harness checks.
- Template assets copied from ForgeKit `project-template/`, `templates/`, and `questionnaires/`.
- Command, hook, and MCP examples as documentation assets only.

## Not Included

- `user-rules/`, because those files contain machine-specific preferences and paths.
- External development records under `document/`.
- Enabled hooks or MCP servers.
- Credentials, tokens, private service URLs, or deployment automation.

## Initialize A Project

From this plugin directory:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 `
  -TargetPath "D:\tmp\forgekit-plugin-smoke" `
  -ProjectName "forgekit-plugin-smoke" `
  -Stacks java-springboot,vue
```

Then start Codex from the generated project `AGENTS.md`.

## Validate The Plugin Package

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-plugin-assets.ps1
```

This check verifies the plugin manifest, required skills, template assets, and forbidden package paths.

## Safety

The plugin does not enable hooks or MCP by default. External writes such as issue updates, pull requests, deploys, tags, or pushes still require explicit user confirmation.
