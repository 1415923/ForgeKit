# Claude Code Project Guide

This is the lightweight Claude Code entry for the generated project. The unique shared safety, evidence, authorization, writeback, and routing contract is [`governance/agent-entry-contract.md`](governance/agent-entry-contract.md); this file applies that contract and adds only Claude Code routing details.

## Always-On Boundaries

- [Project and Write Boundary](governance/agent-entry-contract.md#project-and-write-boundary): read `.forgekit/project-boundary.yml` first. Stay inside the user-named project and task scope; do not absorb adjacent projects, repositories, evidence roots, or user files. Local writes are limited to the authorized scope.
- [Evidence and No Fabrication](governance/agent-entry-contract.md#evidence-and-no-fabrication): base conclusions on locatable files, commands, and user facts. Mark insufficient evidence as unknown, assumption, or `TODO_REVIEW`.
- [Audit Default](governance/agent-entry-contract.md#audit-default): audit, review, assessment, diagnosis, and planning are read-only unless the user explicitly requests a write.
- [Bounded Local Authorization](governance/agent-entry-contract.md#bounded-local-authorization): an explicit fix, implementation, or update request authorizes reversible local edits and necessary validation within its stated scope. Do not repeat the same authorization question or expand it beyond that scope.
- [External and Irreversible Actions](governance/agent-entry-contract.md#external-and-irreversible-actions): commit, push, tag, release, deploy, important-data deletion, irreversible migration, permission or credential change, and other external or destructive actions need specific authorization. Authorization does not reduce objective risk.
- [Minimum Evidence-Based Writeback](governance/agent-entry-contract.md#minimum-evidence-based-writeback): persist only confirmed facts needed for the authorized task, in the document that owns them. Do not copy full chats or long tool output, and do not write project business facts into governance templates.

## Startup and Routing

1. Read `.forgekit/project-boundary.yml`, then `.forgekit/docs/codebase-map.md` for the search start and validation commands.
2. Read `.forgekit/docs/workflow-router.md` only when intent or managed-document ownership is unclear. Do not load all of `.forgekit/docs/**` or `governance/` by default.
3. Under the [Skill Routing](governance/agent-entry-contract.md#skill-routing) contract, use `.claude/skills/` for Claude platform adapters and `.agents/skills/<skill>/SKILL.md` for portable project workflows; load only direct references and the selected `.codex/stacks/<stack>/` material.
4. Run validation proportionate to objective impact and the evidence available. File count alone does not determine risk: low-risk deterministic work stays light; public contracts, data migrations, authentication, permissions, release rules, and hard-to-verify changes route to `governance/ai-engineering-loop.md` and the active change artifacts.

| Intent | Route |
| --- | --- |
| Initialize, fill confirmed setup facts, or assess fit | `project-init`, `project-bootstrap-fill`, `project-suitability`; Claude orchestration may use `forgekit-project-workflow` |
| Audit an existing project or backfill managed facts | `handover-review`, `document-backfill` |
| Plan a high-impact change or review correctness/security | `large-change-planning`, `code-review`, `security-review` |
| Request or perform independent review | `forgekit-request-code-review`, `forgekit-code-review` |
| Check release readiness or perform project maintenance | `release-check`, `forgekit-maintenance` |
| First-principles or adversarial analysis | `forgekit-first-principles`, `forgekit-adversarial-review` |

Claude Skill metadata, agent wiring, and permission mode affect invocation mechanics only; they do not expand the shared authorization contract. Specific triggers and execution contracts belong to the corresponding Skill, and this entry does not copy their workflow bodies.

## Continuity, Validation, and Upgrades

- Critical conclusions must not live only in chat. Before compact, handoff, or session closure, preserve only confirmed decisions, blockers, validation, and evidence paths through `.forgekit/docs/context-continuity.md`; mark uncertainty `TODO_REVIEW`.
- Use project validation commands from `.forgekit/docs/codebase-map.md` and `.forgekit/docs/local-toolchain.md`; do not install tools or start services merely because availability is unknown.
- Route ForgeKit install/init/update/sync through the ForgeKitRoot `scripts/forgekit-project.py --target <ProjectRoot>` entry. Low-level diagnosis may use project-local `scripts/forgekit-upgrade.py check` and `plan`; `apply --safe` still requires its defined confirmation.
- After a ForgeKit upgrade changes entries, rules, Skills, or agents, use the current session only for minimal checkpoint and closure. Start a fresh session before new work; updated disk files do not prove the current session reloaded them.
