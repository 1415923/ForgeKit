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

Version `0.11.0` distributes Claude Code skills and shared ForgeKit assets only. Native generated-project support for `CLAUDE.md` and `.claude/skills/` is planned for a later version.
