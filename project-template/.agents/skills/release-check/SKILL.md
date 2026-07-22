---
name: release-check
description: Assess release readiness for an explicit release, version bump, migration, packaging, tag, release-candidate, or publication task. Use to verify version and artifact consistency, migrations, manifests, tests, smoke evidence, rollback, and release gates. Do not trigger for an ordinary commit or daily implementation task.
---

# Release Check

## Trigger Boundary

Use this Skill only when the user intends a release, version bump, migration, package, tag, release candidate, publication, or release-readiness decision.

An ordinary commit, code change, or code review is not a release. Route implementation correctness to `code-review`, an actual security boundary to `security-review`, and ForgeKit adoption fit to `project-suitability`. Do not run all Stage D Skills for every release or project task.

## Default Mode: Read-Only

Release check is a read-only gate by default. Inspect status, relevant diffs, release type, authoritative version fields, artifacts, migrations, manifests, tests, smoke results, required reviews, and rollback evidence. Do not modify release inputs merely because a blocker is found.

If the user separately and explicitly authorizes a named local release-metadata repair, hand it to a bounded maker workflow. That bounded maker may change only non-empty explicit writable paths, must record changed-path evidence and validation evidence, and must not expand to another finding, path, project, or external action. That authorization does not permit a version bump, formal migration change, tag, push, publish, release, or deploy unless the user names that action.

## Progressive Evidence

First identify the release type and changed surfaces. Load only evidence relevant to those surfaces:

- version and branch consistency
- template state and manifest or lock identity
- plugin or marketplace metadata when packaged
- migration baselines, incoming files, stock/custom/unknown/missing behavior, and rollback when upgraded
- build, tests, smoke, validation, and independent review required by objective impact
- changelog, release notes, deployment entry, artifacts, and recovery evidence when applicable

Do not require database, deployment, security, ownership, or high-risk change material for a release that does not touch those boundaries. Do not invent commands when the project defines its own.

## Decision

Return exactly one readiness state:

- `ready`: required deterministic and review evidence is complete for the named release action.
- `blocked`: a known unmet gate prevents release.
- `not-verified`: evidence is unavailable or insufficient to decide.

List blockers, evidence gaps, applicable risk, rollback or recovery, required commands, and the exact next authorization. A document that claims a test passed is not a substitute for reproducible evidence.

## Version and Migration Boundary

Keep current version, template version, schema version, and historical version fields separate. Do not mechanically rewrite all version-like values. Do not create or edit a formal migration unless a maker task explicitly authorizes that path and stage.

## External Actions

Never bump `VERSION`, commit, push, tag, publish, release, deploy, run an irreversible migration, or change an external system from a read-only release check. Commit, push, tag, publish, release, deploy, and other external actions each require explicit user authorization.
