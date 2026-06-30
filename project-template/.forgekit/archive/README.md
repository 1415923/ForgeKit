# Archive

This folder preserves historical ForgeKit material without making it current truth.

Default agents should not read archive content unless the task is about history, audit, regression analysis, incident review, historical decision explanation, or old-version comparison.

Archive material is read-only historical context by default. If an archived conclusion becomes current again, copy the stable conclusion into `.forgekit/docs/` and cite the archive as background.

v0.39 adds Archive Capsules for phase-level maintenance. Use `.forgekit/archive/index.md` as the search entry, and read a capsule summary before opening its items. Capsule apply requires an explicit plan and confirmation; it does not delete or reorganize legacy archive content. See `.forgekit/docs/archive-capsule.md`.

v0.19 adds an archive dry-run plan at `.forgekit/archive-plan.md`.

The plan is a candidate report, not an archive result. Each run recreates the plan instead of appending old content.

The dry-run only creates or overwrites `.forgekit/archive-plan.md`. It does not move files, change proposal status, rewrite links, update current docs, write business docs, update template-lock, commit, or push.

Archive apply is opt-in:

```bash
python scripts/archive-changes.py --apply --plan .forgekit/archive-plan.md --confirm
```

Apply requires a reviewed dry-run plan, explicit confirmation, and a clean Git working tree except for the plan file itself. It writes `.forgekit/archive-apply-report.md` after moving candidates.

Before applying, run the reference check when you need to know whether candidates are still mentioned by current docs, active changes, or entry docs:

```bash
python scripts/archive-changes.py --reference-check --plan .forgekit/archive-plan.md
```

The reference report is report-only and uses string matching. It does not rewrite links or decide whether a reference is harmful.

Before applying, run the sync check when you need structured evidence that stable conclusions were synchronized back into current state docs:

```bash
python scripts/archive-changes.py --sync-check --plan .forgekit/archive-plan.md
```

The sync report is report-only. It reads `review.md` metadata for candidates and does not change current docs, business docs, archive-plan, template-lock, links, or files.

Smart Archive Advisor:

```bash
python scripts/archive-changes.py --smart-check --plan .forgekit/archive-plan.md --reference-report .forgekit/archive-reference-report.md --sync-report .forgekit/current-docs-sync-report.md
```

Smart check combines machine-readable fields from the archive plan, reference report, and sync report. It writes `.forgekit/smart-archive-report.md` and remains report-only.

Smart Archive Apply:

```bash
python scripts/archive-changes.py --smart-apply --report .forgekit/smart-archive-report.md --confirm
```

Smart apply requires explicit confirmation and a clean Git working tree except for the smart report itself. It only moves entries with `Smart-Status: auto_archive_candidate`, writes `.forgekit/smart-archive-apply-report.md`, and does not modify current docs, business docs, README, AGENTS, CLAUDE, template-lock, reports, commits, or links.
