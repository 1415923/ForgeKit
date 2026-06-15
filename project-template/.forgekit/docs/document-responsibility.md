# Document Responsibility

Use this matrix with `document-lifecycle.md` to decide where facts belong before editing documents.

| Document | Responsible For | Not Responsible For | Update Trigger |
| --- | --- | --- | --- |
| `README.md` | Project purpose, quick start, user-visible run path | Long governance process, internal history | User entry, startup, or product positioning changes |
| `AGENTS.md` / `CLAUDE.md` | AI entry, boundary rules, task routing | Long checklists, template bodies, historical records | Startup order, write boundary, or gate changes |
| `.forgekit/project-boundary.yml` | ForgeKitRoot, ProjectRoot, managed docs root, change root, write policy | Product plan or architecture detail | Directory layout or write policy changes |
| `.forgekit/docs/*` | Current ForgeKit-managed project facts | One-off implementation logs, long history, archived evidence | Current facts, requirements, architecture, validation, or release state changes |
| `.forgekit/docs/work-log.md` | Personal work sequence, handoff context, interrupted session recovery, validation/commit/push/blocking/confirmation notes | Formal release notes, MR-ready changelog, task-board, testing report, risk register, traceability, sensitive information | Phase closure, validation complete, commit/push complete, blocking status change, leader/team lead confirmation, schedule or responsibility change, daily summary, interrupted session recovery, or explicit work-log sync request |
| `.forgekit/docs/loop-readiness.md` | Whether the project has the state, validation, boundary, stop, and escalation conditions needed for a safe loop | Automation runner configuration or execution approval | Before designing or running a repeated loop workflow |
| `.forgekit/docs/loop-blueprint.md` | Reviewable loop design: trigger, inputs, state file, paths, validation, stop condition, escalation, budget, comprehension check, and writeback | Daemon, cron, MCP, connector, automatic PR, sub-agent scheduling, or worktree automation | Before asking an agent to run a loop-like repeated workflow |
| `.forgekit/docs/maker-checker-protocol.md` | Maker and Checker responsibilities, evidence expectations, review outputs, and single-agent phase separation | Automatic checker runner, multi-agent scheduling, sub-agent configuration, or user final approval | Before medium/high risk code changes or independent review |
| `.forgekit/changes/<id>/*` | Medium/high risk change proposal, tasks, verification, review, and ship notes | Long-term current-state facts, unrelated history | Change start, implementation, verification, review, or release |
| `.forgekit/archive/*` | Historical changes, old release material, audit or retro evidence | Current project truth, active change artifacts | User asks for history/audit/regression/retro, or a completed change is manually archived |
| `docs/**` business docs | Existing business documentation and evidence source | ForgeKit governance templates by default | User explicitly asks to update business docs |

Business docs are read-mostly by default. Read and cite them as evidence, but do not write ForgeKit governance templates into them unless the user explicitly confirms the target files and reason.

Archive docs are not read by default. Read `.forgekit/archive/**` only for history, audit, regression analysis, retros, incident review, historical decision explanation, or old-version comparison.
