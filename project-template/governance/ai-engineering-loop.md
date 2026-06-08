# AI Engineering Loop

ForgeKit turns AI coding into a lightweight engineering loop:

1. Clarify the work.
2. Size the risk.
3. Create just enough reviewable change artifacts.
4. Implement with small, scoped edits.
5. Verify, review, ship, and record what changed.

ForgeKit does not replace the framework, CI, issue tracker, or architecture process. It provides project-local prompts, skills, templates, and checks so AI agents work inside visible engineering boundaries.

## Risk Levels

| Risk | Typical work | Required workflow |
| --- | --- | --- |
| low | Single-file fix, copy edit, local test adjustment, no public behavior or data impact | Clarify if needed, edit surgically, run relevant validation, summarize result. A `.forgekit/changes/<id>/` folder is optional. |
| medium | Multi-file change, small feature, template/script change, user-visible flow, documentation structure change | Create `.forgekit/changes/<id>/proposal.md`, `tasks.md`, `verification.md`, and `review.md`; confirm the plan before implementation. |
| high | Architecture change, migration, security/permission change, cross-platform script, public template contract, deployment or compatibility risk | Create `proposal.md`, `design.md`, `tasks.md`, `verification.md`, `review.md`, and `ship.md`; confirm the design before implementation. `retro.md` is recommended after completion. |

## Change Metadata

Each `.forgekit/changes/<id>/proposal.md` should start with ASCII metadata:

```text
Status: draft
Risk: medium
Created: YYYY-MM-DD
Owner: <name>
Reason: <short reason>
```

If `Risk:` is missing, treat the change as needing review before coding.

## Completion

- Do not stop at "tests passed" for medium or high risk changes.
- Record verification results in `verification.md`.
- Record review notes and residual risk in `review.md`.
- For high risk changes, record release and rollback notes in `ship.md`.
- Use `retro.md` only when the change was high risk, major, surprising, or explicitly requested.

