---
name: code-review
description: Review code changes for bugs, regressions, security risks, compatibility issues, and missing tests. Use when Codex is asked to review a diff, inspect current changes, prepare PR feedback, or check whether an implementation is safe to merge.
---

# Code Review

## Workflow

1. Read project rules: `.codex/rules.md`, `.codex/testing.md`, `.codex/security.md`, `governance/code-ownership-review-governance.md`, `governance/project-management-task-model.md`, code ownership and project task board documents in `.forgekit/docs/` if present, and relevant stack rules only.
2. Inspect `git status` and `git diff` unless the user provided a specific diff.
3. If changes touch API, database, configuration, deployment, permissions, security, external services, hardware interfaces, Critical ownership areas, or Unknown ownership areas, check whether change impact assessment and owner review exist.
4. If changes are large, cross-module, migration, refactor, or high-risk work, check whether the large-change protocol was followed:
   - `governance/ai-engineering-loop.md`
   - required `.forgekit/changes/<id>/` artifacts for the declared risk level
   - `governance/large-change-execution.md`
   - exploration report in `.forgekit/docs/`
   - implementation plan in `.forgekit/docs/`
   - staged validation and review notes
5. Prioritize findings in this order:
   - correctness bugs
   - behavioral regressions
   - security risks
   - missing change impact assessment
   - missing owner or reviewer confirmation
   - data loss or migration risks
   - compatibility issues
   - missing tests
6. Cite file paths and line numbers when possible.
7. Do not lead with style comments unless they cause real risk.

## Review Focus

- Inputs, validation, null/empty/error paths.
- Auth, permissions, secrets, external actions.
- Threat model and dependency review requirements for security-sensitive changes.
- Database queries, migrations, transactions.
- API compatibility and response shape changes.
- Change impact assessment for high-impact changes.
- Code ownership and required reviewer coverage for Critical or Unknown areas.
- Task, Feature, Bug, and version state consistency.
- Large-change exploration, implementation plan, staged validation, and session boundaries.
- Medium/high risk change artifacts: proposal, tasks, verification, review, and design/ship when high risk.
- Async, concurrency, lifecycle, resource cleanup.
- Tests that should exist for changed behavior.
- Repeated defects that should trigger defect review.
- Severe issues that should trigger incident review.

## Output

Use this order:

1. Findings
2. Open Questions
3. Test Gaps
4. Summary

If there are no findings, say so clearly and mention remaining validation risk.
