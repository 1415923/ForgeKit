---
name: forgekit-code-review
description: Perform an independent read-only review of a supplied code diff and validation evidence. Use inside forgekit-code-reviewer or when explicitly asked to review code without fixing it.
---

# Independent Code Review

Stay read-only. Do not modify files or fix findings.

## Input gate

Require a task or requirement summary, a review range or staged diff, changed files, validation evidence, and known risks. If the range or evidence is missing, record it in `VerificationGaps` and use `manual-review` when the gap prevents a defensible decision.

Do not trust maker conclusions by default. Inspect the diff and evidence directly. Do not load the maker's full conversation history or all managed docs.

## Review order

For a high-risk change, use the Adversarial Review Pass from `.forgekit/docs/reasoning-review.md` when failure-path analysis is required. Keep this read-only and return fixes to the maker.

1. Read the task summary and review boundary.
   For medium/high risk changes, also read the frozen proposal boundary, acceptance IDs, authorized stage, and whether this is `initial` or `blocker-recheck`.
2. Inspect `git diff --stat`, the exact diff, and changed files.
3. Read [references/universal-review.md](references/universal-review.md).
4. Read [references/security-review.md](references/security-review.md) only for auth, permissions, input, secrets, external commands, data exposure, dependencies, or security-sensitive code.
5. Read [references/testing-review.md](references/testing-review.md) when behavior changed or validation evidence is part of the gate.
6. Report only issues introduced or exposed by the reviewed change unless a pre-existing issue directly blocks it.

## Decision rules

- `pass`: no blocking finding and evidence is sufficient for the reviewed range.
- `needs-fix`: at least one blocking finding exists.
- `manual-review`: scope, evidence, ownership, runtime behavior, or independent execution cannot be verified.
- `self-review` can inform the maker but cannot satisfy an independent-review gate.
- A blocking adversarial finding requires `needs-fix` or `manual-review`. Reviewer unavailability must not be reported as pass.
- In initial review, block frozen-contract violations. A matrix-external issue blocks only when it can cause data leakage/contamination, wrong execution/training/evaluation/checkpoint, artifact overwrite, unauthorized formal-entry execution, false success, or clearly untrustworthy conclusions. Keep other hardening and observability ideas as follow-ups and do not expand the frozen trust boundary.
- In `blocker-recheck`, default to the prior blocking findings and mark each Closed, Partially closed, or Still open. A regression introduced by the fix may block if it violates the frozen contract or causes a real Critical consequence. Keep unrelated new suggestions as follow-up; do not reopen architecture review or expand the trust boundary.
- Pass applies only to the supplied authorized stage.

## Output contract

```text
ReviewDecision: pass | needs-fix | manual-review
ReviewType: independent | self-review
ReviewerAgent:
ReviewMode: initial | blocker-recheck
ReviewedRange:
FrozenAcceptanceIDs:
AuthorizedStage:
Summary:
Findings:
- severity: blocking | important | nit | suggestion | praise
  file:
  line:
  issue:
  why_it_matters:
  suggested_fix:
  evidence:
VerificationGaps:
FollowUps:
TODO_REVIEW:
FinalVerdict:
```

Use file and line references when available. Keep nits and praise non-blocking. Never report pass solely because the maker says the change is complete or fixed.

