# Upgrade

Upgrade the plugin as a normal repository change:

1. Update source template files first.
2. Sync stable assets into `plugins/forgekit-codex-workflow/assets/`.
3. Update `.codex-plugin/plugin.json` version.
4. Run plugin asset validation.
5. Run the root template validation.
6. Run a plugin initialization smoke test into `D:\tmp`.
7. Record the result in the external ForgeKit project records.

Do not hand-edit user-local marketplace state as a substitute for updating the repo plugin package.

If a future release changes generated project behavior, keep the old generated projects compatible unless the version notes explicitly mark a breaking change.
