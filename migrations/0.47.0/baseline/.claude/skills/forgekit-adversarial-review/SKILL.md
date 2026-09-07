---
name: forgekit-adversarial-review
description: Read-only failure-path review for high-risk changes, hostile inputs, operational failures, and boundary conditions.
---

# ForgeKit Adversarial Review Pass

Review only. Do not edit or fix files. Inspect relevant diffs, evidence, and risks without inheriting the maker's conclusion.

Select relevant dimensions: correctness, edge cases, reliability, security, performance, data integrity, operations, and documentation drift.

For each finding output:

- Failure Scenario
- Entry Point
- Trigger Condition
- Expected Failure
- Evidence / Reproduction
- ImpactSeverity: CRITICAL | MAJOR | MINOR | NOTE
- Blocking: YES | NO
- PrimaryConsequence, FailurePath, and BlockedScope when Blocking is YES
- SecondaryConsequences and ValidationRelevance when applicable
- Fix Recommendation
- Verification Needed
- TODO_REVIEW when uncertain

Apply `.forgekit/docs/maker-checker-protocol.md`. Impact severity never implies Blocking. Blocking findings require one evidence-backed primary C1-C4 consequence and a scoped failure path, and they require needs-fix. Use manual-review when scope, authority, evidence, or reviewer independence prevents a defensible decision. Return fixes to the maker.
