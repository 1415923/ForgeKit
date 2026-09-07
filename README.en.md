# ForgeKit

[中文说明](README.md)

ForgeKit **v0.47.0** is a local project governance scaffold for Codex and Claude Code. It provides project instructions, on-demand Skills, source traceability, managed documents, and versioned migrations.

This version simplifies instructions for GPT-6 Astra while retaining both platforms and the user's model configuration. Actual Astra behavior and performance still require client evaluation.

## Initialize or update

Run from the ForgeKit repository:

```powershell
python .\scripts\forgekit-project.py --target "D:\path\to\project"
```

On macOS or Linux:

```bash
python3 ./scripts/forgekit-project.py --target "/path/to/project"
```

The unified entry detects initialization, an existing installation, an available upgrade, a newer project version, or legacy adoption. It previews the plan and writes after confirmation or explicit `--yes`. Use `--dry-run` to inspect without applying. A completed upgrade returns `up-to-date` with zero migration actions on the next run.

Fresh unattended initialization requires an explicit layout:

```powershell
python .\scripts\forgekit-project.py --target "D:\path\to\project" --yes --layout in-place
```

`--layout legacy-nested` remains available. Existing layouts stay in place; the business root README is user-owned and is not created, overwritten, or removed by installation or migration.

Projects with valid state from v0.36.0 onward follow the exact available migration chain. Earlier or missing-state projects require legacy adoption. The tool displays the full chain, evaluates each step in memory, and applies only after the entire plan is conflict-free. It does not skip required steps and overwrite everything with the latest template.

The installed version comes from `.forgekit/state.json`. The version in the boundary file identifies the template used when that file was created.

## Seven on-demand Skills

| Skill | Use |
| --- | --- |
| project-init | Initialize or install through the unified entry |
| document-backfill | Explicitly requested initial filling or factual backfill |
| project-assessment | Adoption suitability or takeover assessment |
| large-change-planning | Scope, acceptance, and recovery planning for high-impact work |
| code-review | Read-only code review and focused re-review |
| security-review | Review actual security boundaries |
| release-check | Check readiness of an explicitly identified release candidate |

Three previous names remain explicit aliases in 0.47.x: `project-bootstrap-fill` maps to document-backfill/bootstrap, `handover-review` to project-assessment/takeover, and `project-suitability` to project-assessment/adoption. Skills are selected by task, not run as a mandatory pipeline.

Root `skills/` owns their content; `.agents/skills/` is a deterministic projection, while `.claude/skills/` retains platform adapters. Load only the relevant Skill branch and stack material.

## Preserve customizations during upgrades

The 0.46.0 to 0.47.0 migration compares the previous template, local content, and incoming template. It preserves resolvable additions and edits, moves content through explicit mappings, and does not call a model to infer project facts.

An explicit allowlist of project fact documents, including requirements, API, tasks, testing, and the codebase map, may use a completely different section structure. Filled documents are retained, with mapped old references updated. This policy does not apply to governance rules, Skills, or entry rules. Historical ancestry covers release snapshots, published migration payloads, and equivalent LF, CRLF, and UTF-8 BOM representations.

| Situation | Result |
| --- | --- |
| Unmodified template or template-only change | Update automatically |
| User regions and resolvable non-overlapping edits | Preserve or relocate |
| Overlapping rules, unknown ancestry, or ambiguous identifiers | Stop the entire apply; keep the installed version unchanged |
| Inputs change after planning | Require a new plan |
| A write fails | Attempt recovery of changed files; retain backups and report paths if recovery is incomplete |

Results record actual actions and recovery material. Legacy manual-merge policies cannot bypass structured conflicts or label a partial upgrade successful. The low-level `forgekit-upgrade.py` supports check/plan and `apply --safe`, JSON output, and apply-time `--plan-hash` verification.

## Separate template rules, project constraints, and current facts

| Content | Owner | Upgrade behavior |
| --- | --- | --- |
| ForgeKit rules | Managed entry regions, governance, and Skills | Updated through the version chain |
| Additional project boundaries and routing | Entry user regions, with details in maps and project documents | Preserved independently of the template |
| Current versions, runtime state, and acceptance | Corresponding evidence sources and factual owners | Verified from evidence; migration does not infer new business state |

Put project additions between the existing `<!-- forgekit:user begin -->` and `<!-- forgekit:user end -->` markers. Do not nest or duplicate these regions. Reference changing release, commit, scheduler, and source state instead of caching them in several entry files. A disk manifest, process health, and user acceptance establish different facts. Keep historical acceptance evidence dated and distinguish it from current state.

If an old AGENTS or CLAUDE entry was completely rewritten, a conflict line number identifies only the first baseline difference. A maintainer should compare the exact installed template with project rules, review stale facts, and, with authorization, restore managed template content plus a project user region. The ordinary upgrade command can then update the template. Migration does not automatically rewrite nested business-repository AGENTS files.

For an explicitly reviewed full-preservation candidate, `--entry-resolutions <resolution.json>` binds the project, version, input, and output hashes. It must be passed explicitly and does not replace semantic review or factual maintenance. See the [entry resolution format](project-template/docs/project-maintenance.md#整份定制入口的显式合并). Normal upgrades do not need this option.

## Everyday use and boundaries

Start Codex or Claude Code at the project entry and describe the desired outcome, scope, and acceptance. Use `testing.md` for relevant commands and `codebase-map.md` when the implementation location is unclear. Authorized implementation includes necessary validation and repairs within scope; passing required checks does not automatically require broader testing.

Audits, reviews, and planning are read-only unless modification is authorized. Commits, pushes, releases, deployment, important-data deletion, and permission or credential changes require their corresponding authorization. Self-review cannot satisfy an independent-review gate.

Record only confirmed facts in their responsible documents: task-intake owns sources, task-board owns execution state, and work-log owns progress. A document's existence does not require filling it. Multi-project scoped documents are opt-in. Maintenance and archive work retain planning, confirmation, current-document checks, and result indexes; archive is not deletion.

The HTML entry is retired. Generated projects use `.forgekit/docs/usage-playbook.md` for examples, `testing.md` for validation, and `work-session-checkpoint.md` for continuity. After an upgrade changes entries, Skills, or agents, start a fresh AI session; use the old session only for minimal checkpoint and closure.

## Validation

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-template.ps1
python .\scripts\check-current-docs-integrity.py --repo-root "D:\path\to\project"
```

See [CHANGELOG.md](CHANGELOG.md) for release changes. Static checks and generated-project smoke tests do not establish actual client loading, model success rates, or token and latency improvements.
