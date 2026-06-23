# Managed Docs Responsibility Matrix v2

Use this file before editing `.forgekit/docs/**`. Its purpose is to reduce default reading, avoid duplicate writes, and keep human-facing documents short enough to review.

Document classes:

- `core`: usually relevant during onboarding or daily work.
- `current`: current project facts; update only when the stable fact changes.
- `working`: short operational state for current work.
- `triggered`: update only when the named event happens.
- `reference`: read only when the task needs that topic.
- `generated`: tool output; do not edit as current truth.
- `archive`: history; not read by default.

Default Read values:

- `yes`: normal startup or broad handover may read it.
- `as-needed`: read when the task points to that topic.
- `no`: do not read by default.

| Document | Document Class | Audience | Default Read | Write Here | Do Not Write Here | Update Trigger | Related Docs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `README.md` | core | users | yes | What this project is, quick start, basic usage | Internal process, long history, task logs | User entry or startup path changes | `AGENTS.md`, `CLAUDE.md` |
| `AGENTS.md` / `CLAUDE.md` | core | AI tools | yes | Short startup order, boundary rules, task routing | Long checklists, template bodies, stack manuals | Startup order, write boundary, routing change | `.codex/rules.md`, skills |
| `.forgekit/project-boundary.yml` | core | AI tools, maintainers | yes | ForgeKitRoot, ProjectRoot, managed docs root, change root, write policy | Product plan, architecture, task status | Directory layout or write policy changes | `AGENTS.md`, `CLAUDE.md` |
| `.forgekit/docs/document-responsibility.md` | core | users, AI tools | yes | Where facts belong and when docs should be updated | Project facts, task logs, release notes | Managed doc responsibility changes | `document-lifecycle.md` |
| `.forgekit/docs/codebase-map.md` | core | AI tools, maintainers | yes | Code search entry points, module map, key commands, cautious paths | Full architecture, API encyclopedia, long scan history | Module entry, command, or ownership changes | `architecture.md`, `api.md`, `local-toolchain.md` |
| `.forgekit/docs/task-intake.md` | working | users, AI tools | as-needed | Original task source, Source ID, responsibility split, time window, human review | Final requirements, task status, changelog, long analysis | Leader task, WeChat task, plan cell, meeting action, manual note | `requirements.md`, `task-board.md`, `work-log.md` |
| `.forgekit/docs/requirements.md` | current | users, product, AI tools | as-needed | Confirmed requirement facts, acceptance criteria, scope boundaries, Source ID reference | Original assignment text, long reasoning, execution status | Requirement confirmed, corrected, rejected, or scoped | `task-intake.md`, `traceability.md` |
| `.forgekit/docs/task-board.md` | working | users, AI tools | as-needed | Compact task status, owner, next action, validation method, Source ID | Original task text, changelog, test logs, long plans | Task is created, blocked, reviewed, done, or dropped | `task-intake.md`, `work-log.md`, `changes/<id>/tasks.md` |
| `.forgekit/docs/work-log.md` | working | users, AI tools | as-needed | Recent work window, handoff notes, validation/commit/push/blocker summaries | Full history warehouse, formal release notes, task board, secrets | Phase closure, validation, commit/push, blocker change, leader confirmation, daily summary, interrupted session recovery | `task-board.md`, `testing.md`, `changelog.md` |
| `.forgekit/docs/changelog.md` | current | users, release reviewers | as-needed | User-visible changes, compatibility, migration notes | Internal work sequence, every commit, raw validation logs | Completed user-visible change or release note update | `work-log.md`, `ship.md` |
| `.forgekit/docs/testing.md` | current | developers, QA, AI tools | as-needed | Current validation commands, test scope, manual verification checklist, known gaps | Every test run log, long failure history, screenshots | Test strategy or runnable validation command changes | `work-log.md`, `changes/<id>/verification.md` |
| `.forgekit/docs/risk-register.md` | current | users, maintainers | as-needed | Open risks that still affect delivery, safety, compatibility, cost, or schedule | Closed risk history, every bug, generic concerns | New risk, changed likelihood/impact, mitigation or closure | `technical-debt.md`, `incident-review.md` |
| `.forgekit/docs/project-plan.md` | current | users, maintainers | as-needed | Current project goal, non-goals, scope, landing conditions | Daily progress, version history, raw task source | Product direction or scope changes | `requirements.md`, `version-roadmap.md` |
| `.forgekit/docs/architecture.md` | current | developers, maintainers | as-needed | Current architecture, module responsibilities, data flow, boundaries | Old designs, implementation diary, API details | Architecture, boundary, or major dependency changes | `api.md`, `database-design.md`, ADR |
| `.forgekit/docs/local-toolchain.md` | reference | AI tools, developers | as-needed | Local build/test/lint/runtime facts | Install permission, credentials, unrelated environment notes | Toolchain detection or validation command changes | `.codex/commands.md` |
| `.forgekit/docs/codex-next-work-order.md` | working | users, AI tools | as-needed | Next useful AI work order after init or handoff | Long roadmap, work log, task board replacement | Init, handoff, or user direction changes | `project-plan.md`, `task-board.md` |
| `.forgekit/docs/implementation-plan.md` | triggered | developers, AI tools | no | Plan for large or cross-module work only | Small task status, current requirements | Large/cross-module/high-risk task is confirmed | `changes/<id>/tasks.md`, `exploration-report.md` |
| `.forgekit/docs/exploration-report.md` | triggered | developers, AI tools | no | Read-only findings before large work | Final architecture, task status, release notes | Large/cross-module/high-risk exploration | `implementation-plan.md` |
| `.forgekit/docs/defect-fix-plan.md` | triggered | developers, maintainers | no | Focused plan for a confirmed defect | General task board, unrelated risk history | Confirmed defect needs repair planning | `defect-review.md`, `task-board.md` |
| `.forgekit/docs/defect-review.md` | triggered | developers, maintainers | no | Root cause and prevention for repeated or serious defects | Ordinary bug status | Serious/repeated defect review | `incident-review.md`, `risk-register.md` |
| `.forgekit/docs/incident-review.md` | triggered | maintainers | no | Incident timeline, impact, root cause, follow-up | Normal bugs, daily logs | Incident or production-impacting failure | `risk-register.md`, `work-log.md` |
| `.forgekit/docs/dependency-review.md` | triggered | developers, security | no | Dependency change rationale, risk, license/security notes | All package versions, install logs | Dependency add/remove/major upgrade | `threat-model.md`, `.codex/security.md` |
| `.forgekit/docs/threat-model.md` | triggered | security, maintainers | no | Security-sensitive data flows, trust boundaries, threats, mitigations | Generic quality risks, credentials | Auth, permission, data exposure, secrets, external integration changes | `risk-register.md`, `.codex/security.md` |
| `.forgekit/docs/release-pipeline.md` | triggered | release owners | no | Current release path, rollback, deployment checks | Changelog, task history | Release process or deployment path changes | `changelog.md`, `environment-matrix.md` |
| `.forgekit/docs/quality-metrics.md` | triggered | maintainers | no | Selected quality indicators and review gates | Every test result, every defect | Quality metric or review gate changes | `testing.md`, `risk-register.md` |
| `.forgekit/docs/technical-debt.md` | triggered | maintainers | no | Accepted debt with owner and revisit condition | All TODOs, closed risks | Debt is accepted or retired | `risk-register.md`, `task-board.md` |
| `.forgekit/docs/traceability.md` | triggered | QA, maintainers | no | Requirement-task-test-defect mapping when needed | Original task text, long evidence | Regulated, high-risk, or user-requested traceability | `requirements.md`, `testing.md`, `task-board.md` |
| `.forgekit/docs/loop-readiness.md` | triggered | users, AI tools | no | Whether a loop is safe to run | Loop runner config, daemon setup | Before loop design or operation | `loop-blueprint.md`, `loop-operations.md` |
| `.forgekit/docs/loop-blueprint.md` | triggered | users, AI tools | no | Reviewable loop design | Automatic execution authorization | User asks for loop-like repeated work | `loop-readiness.md`, `work-log.md` |
| `.forgekit/docs/loop-operations.md` | triggered | users, AI tools | no | Explicit dry-run, one-step, continue, stop/handoff protocol | Background runner, scheduler, automation code | User explicitly operates a loop | `loop-blueprint.md` |
| `.forgekit/docs/maker-checker-protocol.md` | triggered | users, AI tools | no | Maker/Checker review protocol | Multi-agent scheduler or final human approval | Medium/high risk review separation | `changes/<id>/review.md` |
| `.forgekit/docs/worktree-playbook.md` | triggered | users, AI tools | no | Manual worktree isolation guidance | Automatic worktree orchestration | User asks for parallel isolated work | `work-log.md` |
| `.forgekit/changes/<id>/*` | triggered | developers, reviewers | no | One medium/high risk change process | Current-state truth, unrelated history | Medium/high risk change starts or closes | `document-lifecycle.md` |
| `.forgekit/archive/*` | archive | auditors, maintainers | no | Historical evidence and old change material | Current truth, active change context | User asks for history/audit/regression/retro | `document-lifecycle.md` |
| `.forgekit/*-report.md` | generated | users, AI tools | no | Tool output generated by scripts | Current facts or editable project docs | Script run creates/overwrites it | Relevant script docs |
| `docs/**` business docs | reference | users, AI tools | as-needed | Existing business evidence when user allows or requests | ForgeKit governance templates by default | User explicitly asks to update business docs | `.forgekit/project-boundary.yml` |

Before writing:

1. Decide the content type: source record, requirement fact, task status, validation method, work sequence, release change, risk, design decision, or history.
2. Write the fact once in the responsible document.
3. Add cross-references instead of copying the same paragraph into multiple docs.
4. Keep user-facing docs readable: short conclusion first, then only the evidence needed for review.
5. Do not read or update triggered docs unless the trigger actually happened.
