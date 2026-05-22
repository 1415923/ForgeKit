---
name: release-check
description: Check release readiness and version-gate compliance for a project. Use when Codex is asked to prepare a release, verify changelog contents, inspect build/test status, review deployment notes, decide whether a project can be tagged, packaged, pushed, deployed, or whether the next major/minor version can start after required review/refactor gates.
---

# Release Check

## Workflow

1. Read `governance/version-governance.md`, `governance/quality-metrics.md`, `governance/technical-debt-management.md`, `governance/change-management.md`, `governance/incident-process.md`, `governance/security-governance.md`, `governance/cicd-environment-governance.md`, `governance/code-ownership-review-governance.md`, `governance/project-management-task-model.md`, `.codex/git.md`, `.codex/commands.md`, `.codex/testing.md`, `.codex/security.md`, `.codex/version-gates.md`, the version roadmap in `docs/`, quality metrics in `docs/`, technical debt records in `docs/`, change impact assessment in `docs/`, incident or defect reviews in `docs/`, security threat model and dependency review documents in `docs/`, environment matrix and release pipeline documents in `docs/`, code ownership and project task board documents in `docs/`, deployment docs in `docs/`, and the project changelog or version record in `docs/`.
2. Inspect `git status` and relevant diffs.
3. Verify that docs match visible behavior, APIs, database changes, config, and deployment changes.
4. Check whether the current release is a major feature version or a review/refactor gate version.
5. If the user wants to start the next major/minor version, verify that the previous review/refactor gate is complete.
6. Identify required commands from `.codex/commands.md`; do not invent release commands when the project defines them.
7. Do not commit, tag, push, publish, or deploy unless the user explicitly asks.

## Checklist

- Version number and branch are clear.
- Changelog is updated.
- Tests and build are run or explicitly waived.
- Security-sensitive changes are reviewed.
- API, database, config, and deployment docs are updated.
- Environment matrix, release pipeline, target environment, artifact, and rollback path are clear.
- Rollback or recovery path is known for risky releases.
- No secrets, local-only paths, or debug artifacts are included.
- Required review/refactor gate version is complete before the next major/minor version starts.
- Repeated code, excessive new files, unclear module boundaries, and documentation drift have been reviewed.
- Technical debt changes are recorded.
- Quality metrics are updated.
- High-impact changes have change impact assessments, validation, and rollback plans.
- Critical or Unknown ownership areas have owner or reviewer confirmation.
- Current version tasks, features, and bugs are closed, deferred, blocked, or explicitly dropped.
- SEV-1 / SEV-2 incidents and repeated defects have reviews and action items.
- S2/S3 security risks are closed or explicitly accepted.
- New or upgraded dependencies have dependency security review where needed.
- Production deploys, database migrations, Git tags, image pushes, and package publishes have explicit user approval.

## Refuse Unsafe Version Progression

If the previous major feature version does not have a completed review/refactor gate, do not approve starting the next major/minor version.

Respond with:

- which gate is missing
- what must be reviewed or refactored
- what documents must be updated
- that the user must explicitly confirm if they want to skip the gate

## Output

End with:

- Release summary.
- Pass/fail checklist.
- Blockers.
- Risk notes.
- Technical debt notes.
- Quality metric notes.
- Change impact notes.
- Incident or defect review notes.
- Security gate notes.
- CI/CD and environment gate notes.
- Ownership and review gate notes.
- Project task state notes.
- Suggested commands.
- Whether release is ready.
- Whether the next major/minor version may start.
