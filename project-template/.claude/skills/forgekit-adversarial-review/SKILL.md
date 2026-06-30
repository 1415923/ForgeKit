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
- Severity
- Fix Recommendation
- Verification Needed
- TODO_REVIEW when uncertain

Blocking findings require needs-fix or manual-review. Return fixes to the maker. Do not claim pass when evidence or an independent reviewer is unavailable.
