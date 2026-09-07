# Security Review

Load this reference only when the diff touches a security-sensitive boundary.

## Trust boundaries

- Check authentication, authorization, tenant or ownership checks, and privilege changes.
- Check input validation, output encoding, path handling, and unsafe deserialization.
- Check SQL, shell, template, URL, header, and log injection paths.

## Sensitive data

- Do not expose secrets, tokens, keys, credentials, private data, or environment values.
- Check logs, errors, telemetry, caches, and generated artifacts for accidental disclosure.
- Check encryption, signature, randomness, and token validation assumptions when changed.

## External effects

- Check network calls, filesystem writes, process execution, dependency changes, and webhook handling.
- Check replay, timeout, retry, rate-limit, and failure behavior.
- Require manual review when security properties depend on unavailable deployment or identity context.

Do not run exploit commands, read secret files, or expand the review into an active penetration test.
