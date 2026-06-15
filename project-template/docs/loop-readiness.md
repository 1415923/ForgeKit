# Loop Readiness

Purpose: decide whether this project has enough evidence, boundaries, validation, and escalation paths to run a loop safely.

This document is not automation approval. A loop still requires an explicit user request and a reviewed `loop-blueprint.md`.

Readiness Status: not-ready | partial | ready
Last Reviewed:
Reviewer:
Scope:

## Required Conditions

| Condition | Status | Evidence | Gap |
| --- | --- | --- | --- |
| Explicit loop objective exists | unknown |  |  |
| State file exists | unknown |  |  |
| Validation command exists | unknown |  |  |
| Allowed paths are defined | unknown |  |  |
| Forbidden paths are defined | unknown |  |  |
| Stop condition is defined | unknown |  |  |
| Human escalation path is defined | unknown |  |  |
| Token budget is defined | unknown |  |  |
| Comprehension check is defined | unknown |  |  |
| Work-log or loop state writeback is defined | unknown |  |  |

## Safety Gates

| Area | Default | Project Decision | Evidence |
| --- | --- | --- | --- |
| Business docs | read-mostly |  |  |
| Secrets and credentials | forbidden |  |  |
| Deploy and release actions | forbidden without explicit confirmation |  |  |
| CI configuration | forbidden unless explicitly scoped |  |  |
| External services | forbidden without explicit confirmation |  |  |
| Git commit, tag, push | forbidden without explicit confirmation |  |  |

## ForgeKit Loop Five

| Loop capability | ForgeKit evidence | Ready? |
| --- | --- | --- |
| skill | `.agents/skills/`, `.codex/skills.md`, project-local skill instructions | unknown |
| memory | `.forgekit/docs/work-log.md`, `.forgekit/docs/*`, `.forgekit/changes/*` | unknown |
| validation | `.codex/commands.md`, `scripts/check-doc-sync.*`, `scripts/run-harness-check.ps1`, project validation commands | unknown |
| boundary | `.forgekit/project-boundary.yml`, `AGENTS.md`, `CLAUDE.md`, `.codex/rules.md` | unknown |
| reports | archive, sync, smart archive, upgrade, review, and verification reports | unknown |

## Known Gaps

Automation runners, worktree orchestration, connectors, MCP integration, sub-agent scheduling, and automatic PR or issue flows are future roadmap items only. They are not provided by this project template.

## Decision

Loop suitability: not-ready | partial | ready
Reason:
Required fixes before loop:

