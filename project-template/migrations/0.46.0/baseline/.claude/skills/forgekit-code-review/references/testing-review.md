# Testing Review

Load this reference when behavior changed or validation evidence is required.

## Evidence quality

- Distinguish tests actually run from tests merely suggested.
- Match validation commands and output to the changed behavior.
- Check whether failures, skipped tests, warnings, and untested branches were disclosed.
- Do not treat a successful build as proof of behavioral correctness.

## Coverage of the change

- Check normal, boundary, error, authorization, compatibility, and rollback paths as relevant.
- Check whether tests would fail before the fix and detect a regression afterward.
- Check test isolation, deterministic setup, and meaningful assertions.

## Decision impact

- Missing non-critical coverage can be an `important` finding or verification gap.
- Missing evidence for core behavior, security, data migration, or release gates requires `manual-review` or `needs-fix`.
- Never invent test output or infer that unreported tests passed.
