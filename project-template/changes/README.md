# Changes

In generated projects this material lives under `.forgekit/changes/`. Use it only when a change needs reviewable engineering artifacts.

Risk-based minimum:

| Risk | Required files |
| --- | --- |
| low | No change folder required unless the user asks for one. |
| medium | `proposal.md`, `tasks.md`, `verification.md`, `review.md` |
| high | `proposal.md`, `design.md`, `tasks.md`, `verification.md`, `review.md`, `ship.md` |

`retro.md` is recommended after high-risk or major changes, but it is not required for every change.

Change IDs should be short and stable, for example `20260608-add-payment-callback`.

Lifecycle status is recorded in `proposal.md`:

| Status | Meaning |
| --- | --- |
| `draft` | Being discussed; implementation is not confirmed. |
| `active` | Confirmed and being executed. |
| `done` | Implemented and verified; stable conclusions should already be synced to `.forgekit/docs/`. This status only warns that the change may be archived. |
| `archived` | Historical material; it is not an active change and is not checked as active work. |

Completed changes should sync stable conclusions back to current state docs. Do not keep current project truth only inside a change folder.
