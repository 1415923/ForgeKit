# Maker / Checker Protocol

Purpose: separate code-writing evidence from independent review evidence for medium and high risk changes.

This protocol is a review workflow. It is not a multi-agent scheduler, sub-agent configuration, automatic checker runner, daemon, MCP integration, worktree automation, or automatic PR flow.

## Roles

| Role | Responsible For | Not Responsible For |
| --- | --- | --- |
| Maker | Understand the task, edit code, run baseline validation, and record implementation evidence | Declaring the change finally passed |
| Checker | Review the diff, validation evidence, risks, document sync, and open issues from a clean review perspective | Expanding scope or implementing new features unless the user explicitly asks |
| User | Accept final product, business, release, and risk decisions | Supplying missing implementation evidence after the fact |

## Maker Phase

The Maker should:

- restate the requested scope and risk level
- modify only files needed for the confirmed scope
- run the agreed baseline validation command when feasible
- record changed files, implementation summary, validation run, known risks, and not-verified items
- mark the change `ready-for-check`, `blocked`, or `partial`

The Maker must not treat its own implementation as final approval. The strongest Maker outcome is `ready-for-check`.

## Checker Phase

The Checker should:

- start from the current diff and recorded Maker evidence
- review code behavior, validation results, risk notes, and document sync
- check whether sensitive information, business docs, secrets, deploy files, or CI were modified unexpectedly
- report findings with file and line references where possible
- recommend `pass`, `needs-fix`, or `manual-review`

The Checker should not broaden the requested scope, rewrite unrelated code, or add new features unless the user explicitly asks for that work.

## Single Agent Use

A single agent may follow this protocol by separating context and output:

1. Maker phase: implement and write Maker evidence.
2. Context reset or explicit phase switch.
3. Checker phase: review the diff and Maker evidence as if reviewing another contributor.

Single-agent use is still a process separation. It is not proof of independence, and high-risk decisions may still require human review.

## Multi Agent Use

Multiple agents, sub-agents, or human reviewers may use the same protocol, but they are optional implementation choices. ForgeKit v0.26 does not generate sub-agent configuration, runner code, worktree automation, or automatic review dispatch.

## Worktree Isolation

Maker and Checker may use Git worktrees for isolation when the user explicitly asks or confirms the plan. Worktrees can help separate parallel tasks, experiments, or clean review views.

ForgeKit v0.28 does not require worktrees and does not automatically create them. Before using a worktree, confirm a clean source working tree, base branch, worktree path, branch name, allowed paths, validation command, and cleanup plan. Record the outcome in the work log or change review.

## Evidence Location

For medium or high risk changes, record Maker and Checker evidence in:

- `.forgekit/changes/<change-id>/review.md`

Low risk changes may summarize Maker/Checker evidence in the final response when the user has not requested a change folder.

## Status Values

Maker status:

- `ready-for-check`: implementation and baseline validation evidence are ready for review
- `blocked`: implementation cannot continue without user input or external state
- `partial`: implementation is incomplete or validation is incomplete

Checker status:

- `pass`: no blocking finding found in the reviewed scope
- `needs-fix`: blocking issues should be fixed before final acceptance
- `manual-review`: user or domain owner judgment is required
- `not-run`: checker phase has not run yet

## Minimum Review Focus

The Checker should prioritize:

- diff behavior and unintended side effects
- validation command and result quality
- known risks and missing verification
- document sync for current facts and changelog needs
- accidental changes to business docs, sensitive information, secrets, deploy files, or CI
- whether the implementation stayed inside the requested scope

## Output

Maker output should end with a clear `ready for check`, `blocked`, or `partial` statement.

Checker output should end with exactly one recommendation:

- `pass`
- `needs-fix`
- `manual-review`
