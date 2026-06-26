---
name: forgekit-loop
description: Use ForgeKit loop, maker-checker, and verification protocols from Claude Code without enabling automatic execution.
---

# ForgeKit Loop Adapter

Use this skill when the user asks Claude Code to work with ForgeKit loop, planner, reviewer, or verifier behavior.

This skill is an adapter. It does not start a runner, daemon, scheduler, dispatcher, worktree automation, merge, commit, push, or PR.

Prefer native custom agents when the runtime shows that forgekit-planner, forgekit-reviewer, or forgekit-verifier are invoked. Generated config is not proof of runtime registration.

Native adapter lifecycle has four layers: generated, installed, registered, invoked. Only invoked can be called native available.

Keep native_agent_status limited to available, unavailable, or unverified. Do not write invoked into native_agent_status; record invoked in native_agent_lifecycle or agent_invocation_observed.

Native invocation evidence is recorded by the parent runtime. A child agent must not decide native_agent_status by itself.

If native custom agents are unavailable, you may fall back to a general-purpose or worker subagent with prompt injection only when the user did not request native-only mode and the workflow allows fallback. Record agent_mode=fallback and fallback_reason in the loop state or work log only when the user asked to record the run. If the user requested native-only mode, stop when native agents are unavailable.

If spawn fails because of a thread limit, max_threads, or completed agents that remain open, treat it as capacity blocked rather than native unavailable. Close completed agents or reduce concurrency before retrying.

Never describe fallback or simulated execution as native agent success. When native status has not been verified, record native_agent_status=unverified.

Native-only verification is read-only by default. Do not write task-intake.md, work-log.md, or loop state unless the user explicitly asks to record it.

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

Record whether planner execution was native, fallback, or not-run.

## Reviewer Mode

Reviewer mode is read-only. Review diff, validation evidence, risk, documentation sync, and scope control.

End with one recommendation: pass, needs-fix, or manual-review.

Record whether reviewer execution was native, fallback, or not-run.

## Verifier Mode

Verifier mode may run only user-confirmed low-risk validation commands.

Before running a command, state the command, reason, expected signal, and whether it may modify files.

Stop on failure, unclear scope, forbidden path contact, or any need for external access.

Record whether verifier execution was native, fallback, or not-run.

## Escalate

Escalate to the main session or user when the task needs implementation, external access, Git writes, worktree actions, deployment, secrets, CI changes, or automatic agent scheduling.
