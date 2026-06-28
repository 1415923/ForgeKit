# Claude Code Project Guide

This file is the first lightweight entry point for Claude Code in this project. Use it to avoid loading the entire governance set into context.

Keep this file short. Put stable workflows in skills, stack-specific rules in `.codex/stacks/`, and detailed governance in `governance/`.

When a task names a ForgeKit skill, read the project-local `.agents/skills/<skill>/SKILL.md` first. Do not assume a user-level or system-level skill path exists.

## Startup Order

1. Read this file first.
2. Read `.forgekit/project-boundary.yml` to identify ForgeKitRoot, ProjectRoot, managed docs root, change root, business docs roots, and write policy.
3. Read `.forgekit/docs/document-responsibility.md` to choose the right managed docs and avoid duplicate writes.
4. Read `.forgekit/docs/codebase-map.md` to find likely modules, entry files, and local validation commands.
5. Read `.forgekit/docs/workflow-router.md` when the user intent is unclear or the request is about tasks, sources, status, verification, reports, loop, review, worktree, or handoff.
6. Read `.forgekit/docs/local-toolchain.md` when lint, test, build, or local validation commands matter.
7. Read `.forgekit/docs/codex-next-work-order.md` after initialization or when project direction is unclear.
8. Read `.codex/project.md`, `.codex/scope.md`, and `.codex/commands.md` only as needed.
9. Read only the selected stack folder under `.codex/stacks/`.
10. Use `.claude/skills/` for ForgeKit workflow skills.
11. Read `governance/agent-harness.md` when the task involves context strategy, large code search, or unclear entry points.
12. Read `governance/large-change-execution.md` for large, cross-module, high-risk, migration, or refactor work.
13. Read `governance/ai-engineering-loop.md` when risk level, change artifacts, verification, review, ship, or retro expectations are unclear.
14. Read `.forgekit/docs/document-lifecycle.md` when deciding whether material belongs in current docs, change process docs, or archive.
15. Read `governance/team-agent-rollout.md` only when the task involves commands, hooks, plugins, MCP, CI, issue trackers, or team rollout.
16. Read `governance/agent-suitability.md` for initialization, existing project handover, or when project fit is unclear.
17. Read `.codex/automation-decision.md` before turning a repeated workflow into a skill, command, hook, script, plugin, or MCP.

## Task Routing

| Task | Read First | Local Skill |
| --- | --- | --- |
| New project initialization | `governance/overview.md`, `governance/agent-harness.md`, `.claude/init.generated.md`, `.codex/questionnaires/` | `project-init` |
| Post-init next step | `.forgekit/docs/codex-next-work-order.md`, `.forgekit/docs/project-suitability.md`, `.forgekit/docs/local-toolchain.md`, `.claude/init.generated.md` | `project-init` |
| Project suitability assessment | `governance/agent-suitability.md`, `.forgekit/docs/project-suitability.md`, `.forgekit/docs/project-trial-record.md` | `project-suitability` |
| Existing project handover | existing README/usage/setup/test/deploy docs first, then `.forgekit/docs/codebase-map.md`, `.codex/handover.md`, `.forgekit/docs/handover-audit.md` | `handover-review` |
| Backfill ForgeKit managed docs from business docs | source docs one at a time, then target files under `.forgekit/docs/` | `document-backfill` |
| Work source intake | `.forgekit/docs/task-intake.md`, then `.forgekit/docs/task-board.md` and `.forgekit/docs/requirements.md` | relevant existing skill |
| Document lifecycle or archive decision | `.forgekit/docs/document-lifecycle.md`, `.forgekit/docs/document-responsibility.md` | `release-check` |
| Feature implementation | `.codex/rules.md`, `.codex/scope.md`, `.codex/commands.md`, relevant `.codex/stacks/` only | relevant stack rules |
| Medium or high risk change | `governance/ai-engineering-loop.md`, `.forgekit/changes/README.md`, relevant `.forgekit/changes/<id>/` files | relevant existing skill |
| Large or cross-module change | `governance/large-change-execution.md`, `governance/ai-engineering-loop.md`, `.forgekit/docs/exploration-report.md`, `.forgekit/docs/implementation-plan.md`, relevant stack rules | `large-change-planning` |
| Automation boundary decision | `.codex/automation-decision.md`, `governance/team-agent-rollout.md` | relevant existing skill |
| Native agent adapter review | `.forgekit/docs/native-agent-adapter.md`, `.forgekit/docs/loop-operations.md`, `.forgekit/docs/maker-checker-protocol.md` | release-check or security-review |
| Document synchronization check | `.codex/hooks.md`, `.codex/commands.md`, `.forgekit/docs/changelog.md`, related docs | `release-check` |
| Archive dry-run plan | `.forgekit/docs/document-lifecycle.md`, `.forgekit/archive/README.md`, `.codex/commands.md` | `release-check` |
| Code review | `.codex/testing.md`, `.codex/security.md`, `.forgekit/docs/code-ownership.md`, `.forgekit/docs/task-board.md` | `code-review` |
| Release or version gate | `.codex/version-gates.md`, `.forgekit/docs/version-roadmap.md`, `.forgekit/docs/changelog.md` | `release-check` |
| Security-sensitive change | `.codex/security.md`, `governance/security-governance.md` | `security-review` |

## Context Rules

- Do not read every file in `governance/` by default.
- 默认不要读取全部 `.forgekit/docs/**`。先读 `.forgekit/docs/document-responsibility.md`、`.forgekit/docs/codebase-map.md` 和必要的 `.forgekit/docs/workflow-router.md`，再按默认读取策略和任务触发条件读取相关文档。
- 用户请求不明确时，先做 intent routing：判断 Read Targets、Write Targets、Do Not Write 和 Required Output。
- 没有写入触发条件时，不要修改 managed docs；不要把同一事实写进多个文档。
- Separate Implementation Scope from Governance Writeback Scope. A business-file-only implementation scope does not disable ForgeKit managed docs writeback unless the user explicitly forbids docs or ForgeKit writes.
- Default to `ManagedDocsWriteback: minimal`: update work-log for actual progress, task-board only for real status changes, changelog only for user/version-visible changes, and current change artifacts only when required.
- Do not use minimal writeback to edit task-intake source text, requirements facts, or business docs without explicit authorization. Review-only writes nothing, and report-only outputs never trigger automatic fixes.
- 文档混乱、过长、重复或职责错位时，先建议或运行 `scripts/doc-health-report.py`。它只生成 `.forgekit/doc-health-report.md`，不得自动按报告修改 managed docs。
- 任务来源、完成证据或追溯链路不清时，先建议或运行 `scripts/source-trace-report.py`。它只生成 `.forgekit/source-trace-report.md`，不得自动补 Source ID、改任务状态或补验证记录。
- 阶段收口、领导汇报、reviewer 审查或测试交接时，可以建议或运行 `scripts/handoff-package.py`。它只生成 `.forgekit/handoff-package.md` 或 `.forgekit/changes/<id>/handoff.md`，不得编造 commit、验证、风险或文件列表，缺证据必须写 `TODO_REVIEW`。
- Boundary first: ForgeKitRoot is the toolkit source and is read-only unless this task is maintaining ForgeKit itself; ProjectRoot is the business repository and Git commit location.
- Use `.forgekit/docs` as the default ForgeKit-managed docs root and `.forgekit/changes` as the default change root.
- Treat business `docs/` as read-mostly evidence. Read and cite it, but do not write ForgeKit governance templates there unless the user confirms target files and reasons.
- Do not read all business `docs/` by default; use `.forgekit/docs/codebase-map.md` to choose what matters.
- Treat `.forgekit/state.json` as the v0.36+ versioned migration state. For upgrades, use `scripts/forgekit-upgrade.py check`, then `plan`, then explicit `apply --safe`.
- Projects without state or below v0.36 are existing-project adoption cases. Do not create state or claim an automatic upgrade without explicit user confirmation.
- Treat `upgrade-forgekit.*`, `.forgekit/upgrade-export/**`, and `.forgekit/upgrade/**` as legacy compatibility. Do not read or export all candidates by default, and never treat them as current truth.
- Treat `.forgekit/template-lock.json` as a legacy installation baseline; the v0.36 migration model does not update it.
- Treat `.forgekit/docs/**` as current state docs: keep stable facts, not long process history.
- Before updating managed docs, classify the content type: source record, requirement fact, task status, validation method, work sequence, release change, risk, design decision, or history.
- 不要把同一事实重复写进多个文档。只写到负责文档，相关文档用链接或 Source ID 交叉引用。
- 触发式文档只有对应事件发生时才更新；不要把缺陷、事故、依赖、安全、发布、追踪、loop、maker-checker 或 worktree 文档当成日常噪音填充。
- 给用户看的文档要短、自然、可确认：先写结论，再写必要证据，不写模板腔和长篇 AI 过程自述。
- Treat `.forgekit/changes/<change-id>/**` as one-change process records: proposal, design, tasks, verification, review, ship, and retro.
- Treat `.forgekit/archive/**` as historical material, not current truth. Do not read archive by default; read it only when the user asks for history, audit, regression analysis, retro, incident review, historical decision explanation, or old-version comparison.
- Treat `.forgekit/archive-plan.md` as generated dry-run output. It is not current-state docs or an active change, and each dry-run may overwrite it.
- Treat `.forgekit/archive-apply-report.md` as generated apply output. It is not current-state docs, an active change, or release evidence.
- Treat `.forgekit/archive-reference-report.md` as generated report-only output. It is not current-state docs, an active change, or release evidence.
- Treat `.forgekit/current-docs-sync-report.md` as generated report-only output. It is not current-state docs, an active change, or proof that current docs are semantically correct.
- Treat `.forgekit/smart-archive-report.md` as generated report-only advice. It is not permission to archive, does not replace user confirmation, and is not current-state truth.
- Treat `.forgekit/doc-health-report.md` as generated report-only advice. It is not a long-term managed doc and must not trigger automatic doc slimming, archive, rewrite, or merge without explicit user authorization.
- Treat `.forgekit/source-trace-report.md` as generated report-only advice. It is not a long-term managed doc and must not trigger automatic Source ID creation, status changes, verification edits, or changelog rewrites without explicit user authorization.
- Treat `.forgekit/handoff-package.md` and `.forgekit/changes/<id>/handoff.md` as generated report-only handoff packages. They are not fact sources and must not trigger automatic fixes, commits, PRs, runner execution, daemon execution, or worktree automation.
- `.forgekit/docs/task-intake.md` 是工作来源台账。领导任务、微信任务、计划表格子、会议任务、文档任务、个人规划、用户反馈、bug、技术债、测试失败和调研发现都先归并来源，再生成任务；补充、确认、改期或责任修正默认写入已有 Source 的 `Update Notes`，不要默认创建新任务。
- `.forgekit/docs/task-board.md` 只接收可执行任务：必须有动作、owner 或待确认 owner、下一步、`Source ID`、完成标准或验证方式。过时任务必须标为 `Superseded` / `Dropped`，不要继续出现在当前重点。
- `.forgekit/docs/work-log.md` 只记录推进过程、验证、提交/推送、阻塞和确认，并引用 `Task ID` / `Source ID`。工作日志里的后续跟进不自动成为任务；先回到 task-intake 做 Task Decision。
- 拆解任务必须引用 Source ID；未人工确认的派发内容保持 `Human Review: pending`；不要把密钥或未脱敏敏感信息写入管理文档。
- `.forgekit/docs/work-log.md` 是个人工作顺序记录，用于交接和中断会话恢复。用户要求更新 ForgeKit 文档且本轮包含阶段收口、验证、提交/推送、阻塞或领导/组长确认时，应同步它；用户明确要求同步工作日志时必须更新；仅稳定技术事实变化不强制更新。
- Treat `.forgekit/docs/loop-readiness.md` and `.forgekit/docs/loop-blueprint.md` as reviewable loop design docs, not automatic execution authorization.
- Treat `.forgekit/docs/loop-operations.md` as an explicit operation protocol, not an automatic runner or unattended loop authorization.
- Treat `.forgekit/docs/bounded-auto-loop-policy.md` as bounded-auto policy only. Do not enter bounded-auto unless the user explicitly authorizes it.
- Treat `.forgekit/docs/maker-checker-protocol.md` as a review protocol, not multi-agent scheduling or automatic checker authorization.
- Treat `.forgekit/docs/worktree-playbook.md` as a manual isolation guide, not automatic worktree scheduling or agent orchestration.
- Treat `.forgekit/docs/native-agent-adapter.md` as an opt-in configuration adapter guide, not automatic agent execution, scheduling, merge, commit, push, or PR authorization.
- Generated native agent config is not proof of runtime registration. Do not call fallback or simulated execution native success.
- Native lifecycle has four layers: generated, installed, registered, invoked. Keep `native_agent_status` limited to available/unavailable/unverified; record invoked in `native_agent_lifecycle` or `agent_invocation_observed`.
- Parent runtime records native invocation evidence. Child agents must not decide `native_agent_status` themselves.
- If Codex only exposes default, explorer, or worker, record `native_agent_status: unavailable`; do not call that native success.
- If spawn fails because of thread limit, `max_threads`, or open completed agents, record capacity blocked rather than native unavailable.
- Native-only verification is read-only by default. Do not write task-intake, work-log, or loop state unless the user explicitly asks to record it.
- Fallback requires explicit user permission or a workflow rule that allows fallback.
- A loop must have a state file, validation command, stop condition, and human escalation path before it runs.
- A loop must not modify business docs, secrets, deploy files, or CI by default.
- Do not enter loop mode unless the user explicitly asks for loop dry-run, one-step, bounded-auto, review-only, continue, or stop/handoff.
- Before one-step or bounded-auto, restate scope, stages, budget, forbidden actions, stop conditions, agent mode, and whether files will change.
- Bounded-auto must stop on unclear scope, budget overrun, validation failure, forbidden action contact, or unmet agent mode.
- One-step must stop after one round. Review-only must not modify files or run write operations.
- Loop continue must not run continuously; each round requires an explicit user trigger.
- Stop and escalate on unclear scope, budget overrun, validation failure, or forbidden path contact.
- Loop output must write back to `.forgekit/docs/work-log.md` or the specified state file; bounded-auto must checkpoint each stage and end with handoff.
- Bounded-auto or loop execution must record `agent_mode`; native custom agents start as `native_agent_status: unverified` until observed.
- Do not modify business docs, secrets, deploy files, CI, or `.forgekit/template-lock.json` by default.
- Medium or high risk code changes should separate Maker phase and Checker phase.
- Maker phase may say `ready for check`, but must not declare final pass.
- Checker phase should review diff, validation, risks, and document sync; it should output `pass`, `needs-fix`, or `manual-review`.
- Checker should not expand scope or implement new features unless the user explicitly asks.
- For company or business projects, Checker must check for accidental writes to sensitive information, business docs, secrets, deploy files, and CI.
- Do not create a worktree unless the user explicitly asks.
- Before creating a worktree, confirm `git status --short` is clean and state base branch, worktree path, branch name, allowed paths, validation command, and cleanup plan.
- Do not automatically merge, push, delete branches, remove worktrees, create PRs, start agents, or schedule worktree tasks.
- Worktree results must be written to `.forgekit/docs/work-log.md` or the scoped change review.
- Do not install tools or start services just because `.forgekit/docs/local-toolchain.md` has unknown values; ask first.
- `scripts/detect-local-toolchain.ps1` and `scripts/run-harness-check.ps1` are read-only helpers.
- For Lite projects, keep governance lightweight and ask before expanding to Enterprise-level documents.
- Use `.codex/automation-decision.md` to decide whether repeated work belongs in a skill, command, hook, script, plugin, MCP, or documentation.
- Load only the selected stack folder under `.codex/stacks/`.
- If suitability is Conditional or Custom, fill `.forgekit/docs/project-suitability.md` before broad coding.
- If the project plan, technology choice, landing conditions, or version scope are unclear, interview the user before coding.
- For existing projects, read existing docs and extract answers before asking broad handover questions.
- When backfilling `.forgekit/docs/` from existing project documents, process one source document at a time and update target docs before reading the next source document.
- After manual doc fixes or release-note changes, optionally run `scripts/check-doc-sync.ps1` to look for related docs, stale descriptions, and Changed entries without reasons.
- For implementation tasks, apply `.codex/rules.md`: think before coding, keep changes simple, edit surgically, and verify against explicit goals.
- Classify task risk before broad edits: low keeps a light flow; medium requires `proposal.md`, `tasks.md`, `verification.md`, and `review.md`; high also requires `design.md` and `ship.md`.
- For large or cross-module changes, search first, summarize findings, then propose a plan before editing.
- Do not enable hooks, plugins, MCP, issue tracker writes, or CI changes without explicit user confirmation.
- Treat installed plugins as distribution inputs; review their skills, scripts, permissions, and maintenance owner before relying on them for project decisions.

## Gates

- Do not start broad coding without a first-pass project plan and version scope.
- Do not start medium or high risk implementation until the required `.forgekit/changes/<id>/` artifacts exist and the plan is confirmed.
- For new projects, product and architecture discussion is a required phase. Do not treat a few engineering parameter answers as approval to implement.
- Before business code, dependency install, Git init, commit, push, deployment, or other external action, show an execution summary and wait for explicit user confirmation.
- Do not start large cross-module implementation before exploration and implementation plan are complete.
- Do not start the next major version before the review/refactor gate is complete, unless the user explicitly accepts the risk.
- Do not deploy, push, tag, run migrations, or start long-running services without explicit user confirmation.
