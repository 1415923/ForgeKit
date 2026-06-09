# Document Lifecycle

ForgeKit separates project documents into current facts, change process records, and archived history.

Core rule:

```text
current docs say what is true now.
changes explain why and how one change happened.
archive preserves history without becoming current truth.
```

## Document Layers

| Layer | Default Path | Purpose | Default Read |
| --- | --- | --- | --- |
| current state docs | `.forgekit/docs/` | Current project facts, requirements, architecture, validation, and release state | Yes, read task-relevant files |
| change process docs | `.forgekit/changes/<change-id>/` | Reviewable artifacts for one medium/high risk change | Only when related to the current task |
| archive docs | `.forgekit/archive/` | Closed changes, old release material, retros, audit evidence | No, unless history is explicitly relevant |

## Current State Docs

Current docs keep stable facts, not long process logs.

| Document | Write | Do Not Write |
| --- | --- | --- |
| `project-plan.md` | Current users, product shape, scope, non-goals, landing conditions, and roadmap | Discussion logs, discarded option details, historical arguments |
| `architecture.md` | Current architecture, module responsibilities, data flow, API boundaries, and constraints | Every architecture change process or long old-architecture history |
| `requirements.md` | Current requirements, acceptance criteria, priority, and scope boundary | Full debate history for discarded requirements |
| `testing.md` | Current validation commands, test scope, test strategy, and known gaps | One-off test run logs or temporary failure streams |
| `changelog.md` | User-visible changes, compatibility notes, migration notes, release summaries | Internal implementation logs, task minutiae, long review records |

Short stable reasons may stay in current docs with `Reason:`. Long process history belongs in the related change or archive.

## Change Process

Change process docs live under `.forgekit/changes/<change-id>/`.

`proposal.md` owns the lifecycle metadata:

```text
Status: draft | active | done | archived
Risk: low | medium | high
Created: YYYY-MM-DD
Owner: <name>
Reason: <short reason>
```

Status meanings:

| Status | Meaning |
| --- | --- |
| `draft` | Being discussed; implementation is not confirmed. |
| `active` | Confirmed and being executed. |
| `done` | Implemented and verified; stable conclusions have been synced back to current docs, but the change still sits in the active change area for short-term review. |
| `archived` | Historical material; default agents should not treat it as active context. |

When a medium/high change is completed, sync stable conclusions back to current docs:

| Conclusion | Sync To |
| --- | --- |
| Product scope or non-goal changes | `.forgekit/docs/project-plan.md` |
| Architecture, module, interface, or data-flow changes | `.forgekit/docs/architecture.md` |
| Requirement and acceptance changes | `.forgekit/docs/requirements.md` |
| Validation command or test strategy changes | `.forgekit/docs/testing.md` |
| User-visible behavior, compatibility, or migration changes | `.forgekit/docs/changelog.md` |
| Risk, debt, or incidents | Matching risk, debt, or incident docs |

## Archive

Archive docs live under `.forgekit/archive/`.

Archive is not a current-state source. Do not read it by default. Read archive only when the user asks for history, audit, regression analysis, incident review, historical decision explanation, or old-version comparison.

## Archive Plan Dry Run

`scripts/archive-changes.py --dry-run` can generate `.forgekit/archive-plan.md` for completed changes.

The dry-run only creates or overwrites `.forgekit/archive-plan.md`. It does not move files, change proposal status, rewrite links, update current docs, write business docs, update template-lock, commit, or push.

The archive plan lists candidates, blocked changes, and skipped changes. `Status: archived` changes are listed as skipped with `already archived by status`.

`Current docs sync: not verified by script` means a human still needs to confirm that stable conclusions were copied back into current state docs before any future archive apply step.

v0.18 and v0.19 do not move files automatically. If old material becomes true again, sync the stable conclusion back into current docs instead of only linking to archive.

## Archive Apply

`scripts/archive-changes.py --apply --plan .forgekit/archive-plan.md --confirm` can move reviewed candidates from `.forgekit/changes/<change-id>/` to `.forgekit/archive/changes/YYYY/<change-id>/`.

Apply requires an explicit `--confirm` flag and a clean Git working tree except for the selected `.forgekit/archive-plan.md`. It only reads `Archive-Status: candidate` entries from the dry-run plan.

Apply does not move blocked or skipped entries. It does not rewrite links, update current docs, write business docs, update template-lock, commit, tag, or push.

After moving a candidate, apply may update only the archived copy of `proposal.md` from `Status: done` to `Status: archived`. If the archived proposal status is not `done`, the apply report records a warning instead of guessing.

## Archive Reference Check

`scripts/archive-changes.py --reference-check --plan .forgekit/archive-plan.md` can generate `.forgekit/archive-reference-report.md`.

The reference check reads only `Archive-Status: candidate` entries from `.forgekit/archive-plan.md`. It does string matching only and does not decide whether a reference is harmful.

It checks `.forgekit/docs/**`, draft/active/missing/unknown changes, and entry docs (`README.md`, `AGENTS.md`, `CLAUDE.md`). It skips archive, upgrade-export, report files, templates, and the candidate source directory itself.

The report is generated fresh on every run. It does not move files, rewrite links, update current docs, write business docs, update template-lock, commit, tag, or push.
