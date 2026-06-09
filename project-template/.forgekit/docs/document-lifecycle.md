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

v0.18 does not move files automatically. If old material becomes true again, sync the stable conclusion back into current docs instead of only linking to archive.
