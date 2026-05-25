# ForgeKit Codex Workflow Plugin

This plugin distributes the ForgeKit Codex workflow harness for team use.

Chinese documentation: [README.zh-CN.md](README.zh-CN.md).

## Included

- Skills for project initialization, bootstrap filling, handover review, code review, release checks, and security review.
- Read-only scripts for local toolchain detection and generated-project harness checks.
- Template assets copied from ForgeKit `project-template/`, `templates/`, and `questionnaires/`.
- Plugin docs under `assets/docs/` for install, upgrade, safety, and real-project trial feedback.
- Command, hook, and MCP examples as documentation assets only.

## Not Included

- `user-rules/`, because those files contain machine-specific preferences and paths.
- External development records under `document/`.
- Enabled hooks or MCP servers.
- Credentials, tokens, private service URLs, or deployment automation.

## Initialize A Project

Run the initializer from this plugin directory. The script copies ForgeKit template files into
your target project directory and optionally copies selected stack templates into
`.codex/stacks/<stack>/`.

General form:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 `
  -TargetPath "<absolute path to your project>" `
  -ProjectName "<project name>" `
  -Stacks <stack-1>,<stack-2>
```

Parameters:

- `-TargetPath`: Required. The project directory to initialize. Use an absolute path.
- `-ProjectName`: Optional but recommended. Written into `.codex/init.generated.md`.
- `-Stacks`: Optional. Comma-separated stack templates to add under `.codex/stacks/`.
- `-Force`: Optional. Overwrites existing template files. Omit it for normal first-time use.

Available stack values:

- `java-springboot`
- `vue`
- `react`
- `python-fastapi`
- `node-express`
- `csharp-dotnet`
- `go-service`
- `php-laravel`
- `fpga-vivado-vitis`

Examples:

Java + Vue full-stack project:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 `
  -TargetPath "D:\JAVA-code\my-business-app" `
  -ProjectName "my-business-app" `
  -Stacks java-springboot,vue
```

Python FastAPI project:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 `
  -TargetPath "D:\projects\my-api" `
  -ProjectName "my-api" `
  -Stacks python-fastapi
```

Smoke-test example:

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

## v0.9.1 Gate

The package keeps the full project template inside `assets/project-template/` so generated projects remain self-contained. The top-level `skills/` copy is intentionally separate so Codex can discover plugin skills before a project is generated.
