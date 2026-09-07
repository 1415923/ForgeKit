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

To apply reviewed candidates in v0.20:

```bash
python scripts/archive-changes.py --apply --plan .forgekit/archive-plan.md --confirm
```

Apply only moves candidates from the plan. It does not move blocked, skipped, draft, active, or business docs.

To apply only Smart Archive Advisor auto candidates:

```bash
python scripts/archive-changes.py --smart-apply --report .forgekit/smart-archive-report.md --confirm
```

Smart apply only moves `.forgekit/changes/<change-id>` to `.forgekit/archive/changes/YYYY/<change-id>` for `Smart-Status: auto_archive_candidate` entries.
