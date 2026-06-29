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

## Severity

- `blocking`: correctness, security, data loss, incompatible behavior, or release gate failure.
- `important`: material maintainability, observability, or non-blocking regression risk.
- `nit`: small clarity issue with no delivery impact.
- `suggestion`: optional improvement outside the required fix.
- `praise`: concise evidence-backed strength.
