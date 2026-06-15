# Loop Blueprint

Purpose: define a reviewable loop design for a specific project workflow.

This is a reviewable loop design blueprint, not authorization to execute automatically. It is not a daemon, cron job, MCP integration, connector, automatic PR flow, sub-agent scheduler, or worktree automation configuration.

Loop Name:
Owner:
Status: draft | reviewed | retired
Last Reviewed:
OperationMode: dry-run | one-step | continue | stop-handoff
MaxRounds:
MaxFilesRead:
MaxFilesChanged:
MaxCommands:
RequiresUserConfirmation: yes
WritebackTarget:
StopOnUnclearScope: yes
StopOnValidationFailure: yes

These operation fields are review fields for `.forgekit/docs/loop-operations.md`. They are not automatic runner configuration.

## Trigger

Default: manual only.

Allowed trigger:

- User explicitly asks to run this loop for the scope below.

Not allowed by default:

- daemon
- cron or timer
- connector event
- MCP event
- automatic PR or issue event
- sub-agent scheduler
- worktree automation

Loop operation is off by default. Only enter `dry-run`, `one-step`, `continue`, or `stop-handoff` when the user explicitly asks for that operation.

## Input Sources

| Source | Purpose | Required? |
| --- | --- | --- |
| `AGENTS.md` or `CLAUDE.md` | entry rules and task routing | yes |
| `.forgekit/project-boundary.yml` | write boundary and managed roots | yes |
| `.forgekit/docs/codebase-map.md` | modules, entry files, validation hints | yes |
| `.forgekit/docs/local-toolchain.md` | local toolchain and command evidence | recommended |
| `.forgekit/docs/work-log.md` | recent handoff and interruption context | recommended |
| `.forgekit/changes/<change-id>/` | active change artifacts when loop is scoped to a change | conditional |
| generated reports | archive, sync, smart archive, upgrade, review, or verification evidence | conditional |

## State File

Path:
Owner:
Write rule:

The loop must not run without a clear state file. The state file must record the current step, last validation result, blocking condition, and next allowed action.

## Allowed Paths

List exact paths or narrow prefixes:

- 

## Forbidden Paths

Default forbidden paths and actions:

- business `docs/**` unless explicitly scoped and confirmed
- secrets, credentials, private keys, tokens, and local-only environment files
- deploy, release, migration, and production operation files unless explicitly scoped and confirmed
- CI configuration unless explicitly scoped and confirmed
- `.forgekit/template-lock.json`
- generated reports unless the loop scope explicitly says they may be regenerated
- `README.md`, `AGENTS.md`, and `CLAUDE.md` unless the loop scope explicitly includes entry documentation changes
- Git commit, tag, push, issue creation, PR creation, or external writes

## Validation Command

Command:
Expected result:
Failure handling:

The loop must not run without a validation command. If validation fails, stop or escalate according to the section below.

## Stop Condition

Stop when:

- 

The loop must have an observable stop condition before it starts.

## Human Escalation

Escalate when:

- the state file is missing, ambiguous, or inconsistent
- allowed and forbidden paths conflict
- validation is missing, failing, or too expensive for the budget
- required project facts are missing or contradictory
- secrets, deploy, CI, external services, Git push, automatic PR, MCP, connector, sub-agent scheduling, or worktree automation would be needed

Decision owner:
Question format:

## Token Budget

Budget:
Stop or escalate when:

Scope budget:
Max files read:
Max files changed:
Max commands:

## Comprehension Check

Before modifying files, restate:

- objective
- state file
- allowed paths
- forbidden paths
- validation command
- stop condition
- human escalation path
- token budget
- output and writeback target

## Output / Writeback

Write results to:

- `.forgekit/docs/work-log.md` or the loop state file
- the scoped `.forgekit/changes/<change-id>/` artifact when the loop belongs to a medium or high risk change

Do not leave loop results only in chat when they are needed for handoff, validation, or interruption recovery.

## Maker / Checker Strategy

If the loop involves code changes, define how Maker phase and Checker phase are separated. Use `.forgekit/docs/maker-checker-protocol.md` for responsibilities, evidence fields, and review outputs.

This section is not automatic sub-agent configuration. It does not authorize multi-agent scheduling, worktree automation, or automatic checker execution.
