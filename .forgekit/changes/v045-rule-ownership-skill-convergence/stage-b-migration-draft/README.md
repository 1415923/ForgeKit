# Stage B Entry Migration Draft

Status: development-fixture-only

This change-local package exercises the future v0.44.1 to v0.45.0 AGENTS/CLAUDE migration without registering a released `migrations/0.45.0` package. The release stage may promote the verified package through the normal migration distribution flow after later stages and release authorization.

- `baseline/` preserves the Stage A committed v0.44.1 entry bytes.
- `files/` contains the Stage B lightweight incoming entries.
- The fixture uses the existing `replace_file_if_baseline_matches` action and review packet system.
- Stock entries may update; custom and unknown-baseline entries stay local and become `REVIEW-NEEDED`; missing entries follow the existing missing-file contract.
- This draft does not change `VERSION`, plugin metadata, marketplace metadata, or the formal migration chain.
