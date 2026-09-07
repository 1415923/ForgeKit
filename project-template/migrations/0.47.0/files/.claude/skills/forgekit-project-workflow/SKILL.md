---
name: forgekit-project-workflow
description: Route an unclear ForgeKit workflow request in Claude Code to the relevant project capability. Skip this router when the task and target are already clear.
---

# ForgeKit Project Workflow

Use this skill as the Claude Code bridge into a ForgeKit-generated project.

## Start Here

Use `CLAUDE.md` and the declared project boundary. When the implementation location is unclear, consult `.forgekit/docs/codebase-map.md`; otherwise read the relevant implementation directly. Load `.forgekit/docs/testing.md` for validation commands and only the selected stack under `.codex/stacks/`.

## Discovery State

When the goal or scope is unclear, identify the missing decision from existing evidence. Ask only questions that change the outcome or authorization, and continue independent authorized work.

Load one relevant capability from `.agents/skills/`: `project-init`, `document-backfill`, `project-assessment`, `large-change-planning`, `code-review`, `security-review`, or `release-check`. These are alternatives or risk-based combinations, not a required pipeline. For independent review, use the Claude request/reviewer adapters and the maker-checker protocol.

## Boundaries

Use `governance/agent-entry-contract.md` for authorization, evidence and completion. An approved implementation includes necessary bounded local changes, verification and relevant repairs; do not ask again for equivalent authorization. Review and assessment stay read-only. External, destructive or irreversible effects still require authorization for the actual target and effect.

## Output

Report the requested result, evidence, actual unresolved limits and next necessary step. Do not impose a fixed questionnaire or output template. Persist only confirmed critical facts in the responsible owner or narrow checkpoint.
