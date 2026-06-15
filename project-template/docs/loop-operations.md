# Loop Operations

Purpose: define explicitly triggered loop operation modes for reviewed loop blueprints.

Loop operations are off by default. This document is an operation protocol, not an automatic loop runner, daemon, cron job, scheduler, MCP connector, automatic PR flow, multi-agent dispatcher, worktree automation, or unattended continuous loop.

Before any loop operation, the project must have:

- reviewed `.forgekit/docs/loop-blueprint.md`
- explicit user request for the operation mode
- state file
- token or scope budget
- validation command
- stop condition
- human escalation path
- writeback target in `.forgekit/docs/work-log.md` or the loop state file

`loop-readiness.md` and `loop-blueprint.md` remain review documents. They are not automatic execution authorization.

## Loop Dry Run

Use when the user asks what one loop round would do.

Rules:

- read the loop blueprint and relevant state only
- explain the planned one-round action, inputs, write boundary, validation, stop condition, and escalation path
- do not modify files
- do not run dangerous commands
- do not commit, tag, push, create issues, or create PRs
- write nothing unless the user explicitly asks for a record

Output should state whether the blueprint is ready for `one-step`, blocked, or needs human clarification.

## Loop One Step

Use only after the user explicitly confirms one loop round.

Before execution, restate:

- Loop Name
- State File
- Allowed Paths
- Forbidden Paths
- Validation Command
- Stop Condition
- Human Escalation
- Token / Scope Budget
- whether this round will modify files

Rules:

- execute only one round
- stay inside the allowed paths and budget
- stop on unclear scope, budget exhaustion, validation failure, or forbidden path contact
- run the validation command when required and feasible
- write back the round result to `.forgekit/docs/work-log.md` or the loop state file

Default operation is one round only. Do not continue automatically.

## Loop Continue

Use only when the user explicitly asks to continue from a state file.

Rules:

- read the state file before acting
- continue exactly one next round unless the user explicitly confirms another round later
- do not infer permission for repeated or unattended execution
- write each round result to `.forgekit/docs/work-log.md` or the loop state file
- stop and escalate on unclear state, unclear scope, budget exhaustion, validation failure, forbidden path contact, or human-decision points

`continue` means resume from state once. It does not mean keep looping.

## Loop Stop / Handoff

Use when the user asks to stop, pause, hand off, or summarize loop state.

Write a handoff summary to `.forgekit/docs/work-log.md` or the loop state file with:

- completed work
- unfinished work
- blocking issues
- validation results
- files changed or intentionally left untouched
- risks and not-verified items
- recommended next step

Do not start another loop round during stop or handoff.

## Stop And Escalate

Stop and ask the user or owner when:

- scope is unclear
- budget is exhausted or missing
- validation fails or is missing
- state file is missing, stale, or contradictory
- allowed paths and forbidden paths conflict
- business docs, secrets, deploy, CI, `.forgekit/template-lock.json`, generated reports, Git writes, external writes, MCP, connector, automatic PR, sub-agent scheduling, or worktree automation would be needed

## Writeback

Every executed loop round must write back to one of:

- `.forgekit/docs/work-log.md`
- the explicit loop state file

Chat-only output is acceptable for dry-run unless the user asks for a written record. One-step, continue, stop, and handoff should not leave required state only in chat.
