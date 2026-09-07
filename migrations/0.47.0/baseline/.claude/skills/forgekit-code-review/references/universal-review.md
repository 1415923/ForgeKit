# Universal Review

Apply this reference to every code review.

## Correctness

- Compare behavior with the task and acceptance boundary.
- Check null, empty, error, retry, timeout, and partial-failure paths.
- Look for state corruption, data loss, ordering, concurrency, and cleanup defects.
- Check whether changed defaults or control flow alter existing behavior.

## Scope and compatibility

- Identify unrelated edits or missing required changes.
- Check API, schema, configuration, CLI, file-format, and backward-compatibility impact.
- Verify callers and consumers still match changed contracts.
- Do not request preference-only refactors as blocking findings.

## Maintainability

- Flag hidden coupling, duplicated policy, unclear ownership, or error handling that obscures failure.
- Prefer evidence-backed findings over speculative style advice.
- Treat lint and formatting as tool concerns unless they cause behavior or maintenance risk.

## Finding contract

Use the canonical contract from `.forgekit/docs/maker-checker-protocol.md`:

- `impact_severity: CRITICAL | MAJOR | MINOR | NOTE` describes consequence magnitude.
- `blocking: YES | NO` independently decides whether the current scoped action must stop.
- Every Blocking finding needs one primary C1-C4 consequence, evidence, a failure path, and a blocked scope.
- Optional hardening, clarity improvements, and praise remain `Blocking=NO`.

Do not derive Blocking from severity, checker exit, or strict mode.
