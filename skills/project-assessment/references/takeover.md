# Handover Review

## Trigger Boundary

Use for taking over an existing project, auditing its current state, checking historical documents against the repository, identifying compatibility and risk boundaries, or deciding whether work can safely continue.

Do not use to initialize a new project, fill bootstrap placeholders, implement a known fix, backfill documents, or perform release review. Findings may recommend another Skill, but must not automatically invoke repair or writeback.

## Read-Only Default

Handover review is read-only by default. A request to audit, assess, diagnose, or review authorizes inspection and reporting only. It does not authorize code fixes, document backfill, dependency changes, service startup, or project-state updates.

If the user explicitly authorizes recording the handover result, update only the handover owner document in the stated scope without asking again for equivalent authorization. That write does not authorize fixing code or implementing findings. Commit, push, release, deploy, production checks, credential or permission changes, deletion, and other external or irreversible actions still need specific authorization.

## Evidence Priority

Resolve conclusions in this order, while reporting material conflicts rather than hiding them:

1. Current code, configuration, and files.
2. Repeatable commands, tests, builds, and runtime evidence.
3. Current machine-readable or maintained state files.
4. Work records, verification records, and recent change artifacts.
5. Historical plans, proposals, roadmaps, and narrative documents.

Documentation that claims success is not a substitute for current code and repeatable evidence. Historical plans describe intent unless current evidence confirms completion.

## Audit Workflow

1. Confirm the project and read boundary, then use the codebase map to choose a focused search start.
2. Inspect the smallest evidence set needed to establish entry points, stack, commands, tests, dependencies, deployment assumptions, compatibility boundaries, and current work state.
3. Run safe read-only checks when available. Do not install missing tools or start services merely to complete the audit.
4. Classify each material conclusion as confirmed, unconfirmed, conflicting, or historical, and include the evidence path or command.
5. Identify risks, verification gaps, and the safest next step. High-impact findings may route to `large-change-planning`; an explicitly requested factual migration may route to `document-backfill`. Neither route runs automatically.
6. Check recoverability and closure writeback: confirmed facts may be temporarily carried by an active change/checkpoint, but a declared closure, ship, or handoff must not leave the responsible current owner stale. Document ownership alone does not require risk, testing, traceability, or project-plan population when no such fact exists.
7. Decide whether the project is safe to continue, safe only within a bounded area, or blocked pending evidence or authorization. Apply the universal finding contract in `.forgekit/docs/maker-checker-protocol.md`; severity does not imply Blocking, and any scoped stop needs a supported C1-C4 failure path and blocked scope.

## Output and Minimum Writeback

Organize the result around the evidence actually found rather than a fixed section template or fixed question count. Clearly distinguish confirmed facts, unconfirmed claims, conflicts, risks, suggested next steps, and the safe-to-continue decision.

Without explicit writeback authorization, return the audit in chat and leave the repository byte-identical. With explicit handover-state authorization, write only confirmed conclusions and unresolved `TODO_REVIEW` items to the handover owner document. Never write speculation as fact or combine the reviewer and maker roles in the same audit.

If a required confirmed-fact owner remains stale, block only the affected handover/closure declaration and only when evidence establishes the actual failure path. Do not block unrelated read-only work, and do not fabricate a fact to satisfy a checker.
