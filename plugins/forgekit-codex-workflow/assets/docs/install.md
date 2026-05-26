# Install

Use the repo marketplace when testing ForgeKit as a team plugin:

```text
.agents/plugins/marketplace.json
plugins/forgekit-codex-workflow/
```

The marketplace entry points to `./plugins/forgekit-codex-workflow` and uses:

- `policy.installation`: `AVAILABLE`
- `policy.authentication`: `ON_INSTALL`

After installing or loading the plugin, verify the package from the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\plugins\forgekit-codex-workflow\scripts\validate-plugin-assets.ps1
```

Then run a smoke initialization:

```powershell
powershell -ExecutionPolicy Bypass -File .\plugins\forgekit-codex-workflow\scripts\init-project-template.ps1 `
  -TargetPath "D:\tmp\forgekit-plugin-smoke" `
  -ProjectName "forgekit-plugin-smoke" `
  -Mode Standard
```
