# Archived Changes

Store completed historical change folders here after they no longer need to stay in `.forgekit/changes/`.

Suggested layout:

```text
.forgekit/archive/changes/
  YYYY/
    YYYYMMDD-short-change-id/
```

Archived changes are not active change process docs. They are not checked as active changes and should not be used as the source of current facts unless the user explicitly asks for historical context.

Before manually archiving a completed change, run:

```bash
python scripts/archive-changes.py --dry-run
```

Review `.forgekit/archive-plan.md` first. The script does not move files in v0.19.
