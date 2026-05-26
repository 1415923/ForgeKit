# Install

Use the Claude Code marketplace file when testing ForgeKit as a team plugin:

```text
.claude-plugin/marketplace.json
plugins/forgekit-claude-workflow/
```

The marketplace entry points to:

```text
./plugins/forgekit-claude-workflow
```

After installing or loading the plugin, verify the package from the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\plugins\forgekit-claude-workflow\scripts\validate-plugin-assets.ps1
```

Generate a Claude-ready project entry:

```powershell
powershell -ExecutionPolicy Bypass -File .\plugins\forgekit-claude-workflow\scripts\init-project-template.ps1 `
  -TargetPath "D:\tmp\forgekit-claude-smoke" `
  -ProjectName "forgekit-claude-smoke" `
  -Mode Standard
```

Version `0.11.1` generates `CLAUDE.md` and `.claude/skills/forgekit-project-workflow/` as a thin Claude Code entry while keeping shared project facts in `.codex/`, `docs/`, and `governance/`.
