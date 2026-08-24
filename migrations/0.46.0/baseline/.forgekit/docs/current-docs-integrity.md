# 当前文档完整性

## Purpose

`.forgekit/docs/` 是当前工作状态数据库，必须足以支撑未完成任务继续推进。`.forgekit/archive/` 只保存历史证据，不能替代当前事实，也不能要求后续会话靠读取 archive 才能理解当前任务。

## Current Docs Invariants

- `task-board.md` 中真实 `Source ID` 必须能在 `task-intake.md` 找到真实 Source Record。
- 当前未完成任务必须留在 current docs，不能只存在于 archive。
- 当前仍有效风险必须留在 `risk-register.md`。
- 当前任务的最小验证基线必须留在 `testing.md`。
- 当前 Task、Source、Requirement、Test 等追踪关系必须留在 `traceability.md`。
- 示例 ID 和模板占位不是当前事实，不能用来满足完整性检查。

## Active Work Guard

只要 `task-board.md` 仍有 In Progress、Waiting、Review、Backend Ready、Needs Fix、Submitted、Mitigating、Open 或 Blocked 任务，本阶段就不是完整 phase close。归档只能标为 `legacy transition snapshot`、`provisional archive`、`evidence snapshot` 或 `active-work cleanup snapshot`，不能写成 completed phase archive。

## Archive Preflight Check

归档计划和 apply 前运行 `python scripts/check-current-docs-integrity.py --repo-root .`。检查 Source、Task、Risk、Traceability、Testing 和 work-log 状态。出现 blocking 时停止 apply，先执行 Current State Restoration Pass。普通 `--confirm` 不能绕过 blocking。

## Archive Postflight Check

移动计划内项目后再次执行同一检查，并验证 archive summary 没有把活跃工作写成 completed phase archive。postflight 失败时 capsule 必须标为 needs-fix，不能声明归档完成。

## Restoration Guidance

Current State Restoration Pass 从业务文档、当前代码、任务记录和必要的 archive 证据中逐项恢复仍有效事实：

1. 恢复真实 Source Record 和 Task 反链。
2. 恢复未完成任务及其最小 traceability。
3. 恢复仍开放风险或人工确认的“当前无开放风险”。
4. 恢复当前验证命令、范围、通过标准或 `TODO_REVIEW`。
5. 在 work-log 中说明旧 handed-off 结论已 superseded/corrected。

只恢复当前事实，不把 archive 全文复制回 current docs。修复后重新运行检查，并记录 `.forgekit/docs/` 是恢复后的当前事实入口。

## Template Placeholder Rules

`SRC-EXAMPLE-001`、`SRC-YYYYMMDD-001`、`TASK-EXAMPLE-001`、只出现在模板区的 `TASK-001`，以及 `EPIC-001`、`FEAT-001`、`RISK-001` 等占位不参与真实任务检查。真实活跃任务存在时，`task-intake.md`、`risk-register.md`、`traceability.md`、`testing.md` 不能只剩这些占位或“待补充”。

## Boundaries

- 检查器默认只读，不恢复、不覆盖、不移动文件。
- 不自动读取或复制全量 archive。
- 不修改 business docs、业务代码、Git、commit、push 或 PR。
- 完整性通过只说明 current docs 链路达到最小要求，不证明所有业务事实都正确。
- 本检查器负责单作用域 current docs 的 Source / Task / Risk / Traceability / Testing 完整性。启用 multi-project scoped docs 后，跨 Workspace / Project / Repo / Artifact / Archive 的关系由 `check-workspace-integrity.py` 检查；两者不能互相替代。
