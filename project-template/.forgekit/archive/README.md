# Archive

This folder preserves historical ForgeKit material without making it current truth.

Default agents should not read archive content unless the task is about history, audit, regression analysis, incident review, historical decision explanation, or old-version comparison.

Archive material is read-only historical context by default. If an archived conclusion becomes current again, copy the stable conclusion into `.forgekit/docs/` and cite the archive as background.

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
