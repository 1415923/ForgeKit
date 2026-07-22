# Stage B/C/D Development Migration Draft

Status: development-fixture-only

This single change-local package exercises the future v0.44.1 to v0.45.0 AGENTS/CLAUDE plus Stage C and Stage D project-local Skill migration without registering a released `migrations/0.45.0` package. The release stage may promote the verified package through the normal migration distribution flow after later stages and release authorization.

- `baseline/` preserves the Stage A committed v0.44.1 entry bytes.
- `files/` contains the Stage B lightweight incoming entries.
- Skill-package baselines, including changed `agents/openai.yaml`, come from the committed Stage B production projection at `d02b496971db3773ac0c1435a423198189d6d8d8`; incoming package files are byte-identical to the current root/template Stage C projection.
- Stage D Skill-package baselines come from the committed Stage C projection at `868846da54634899141047951b0f4275ad378966`; incoming files are byte-identical to the current Stage D template projection.
- The fixture uses the existing `replace_file_if_baseline_matches` action and review packet system.
- Stock entries and Skills may update; custom and unknown-baseline files stay local and become `REVIEW-NEEDED`; missing files follow the existing missing-file contract.
- This draft does not change `VERSION`, plugin metadata, marketplace metadata, or the formal migration chain.
