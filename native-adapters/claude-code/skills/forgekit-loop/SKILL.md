---
name: forgekit-loop
description: Use ForgeKit loop, maker-checker, and verification protocols from Claude Code without enabling automatic execution.
---

# ForgeKit Loop Adapter

Use this skill when the user asks Claude Code to work with ForgeKit loop, planner, reviewer, or verifier behavior.

This skill is an adapter. It does not start a runner, daemon, scheduler, dispatcher, worktree automation, merge, commit, push, or PR.

## Read First

Read only the files needed for the task:

- AGENTS.md or CLAUDE.md
- .forgekit/project-boundary.yml
- .forgekit/docs/native-agent-adapter.md
- .forgekit/docs/loop-blueprint.md
- .forgekit/docs/loop-operations.md
- .forgekit/docs/maker-checker-protocol.md
- governance/ai-engineering-loop.md

Do not read secrets, .env files, tokens, keys, certificates, or credentials.

## Planner Mode

Planner mode is read-only. Clarify scope, risk, allowed paths, forbidden paths, required ForgeKit artifacts, validation command, stop condition, and escalation path.

Do not edit files or run implementation commands.

## Reviewer Mode

Reviewer mode is read-only. Review diff, validation evidence, risk, documentation sync, and scope control.

End with one recommendation: pass, needs-fix, or manual-review.

## Verifier Mode

Verifier mode may run only user-confirmed low-risk validation commands.

Before running a command, state the command, reason, expected signal, and whether it may modify files.

Stop on failure, unclear scope, forbidden path contact, or any need for external access.

## Escalate

Escalate to the main session or user when the task needs implementation, external access, Git writes, worktree actions, deployment, secrets, CI changes, or automatic agent scheduling.
