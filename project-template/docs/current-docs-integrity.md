# 当前文档完整性

## Purpose

`.forgekit/docs/` 保存当前工作需要的事实。`.forgekit/archive/` 只保存历史证据，不能替代已经存在的 current fact，也不能要求后续会话靠读取 archive 才能理解当前任务。

Document ownership does not imply mandatory population。Active task 只要求其 Source/Task 链路可恢复；它本身不产生 risk、testing、traceability 或 project-plan 事实。

## Current Docs Invariants

- `task-board.md` 中真实 `Source ID` 必须能在 `task-intake.md` 找到真实 Source Record。
- 当前未完成任务必须留在 current docs，不能只存在于 archive。
- 已确认且仍影响当前工作的风险事实由 `risk-register.md` 负责；没有风险事实时可保持 lean/template。
- 已确认的可复用验证方法、基线或缺口由 `testing.md` 负责；尚无 testing fact 时，active task alone cannot block。
- 真实需要的 Task、Source、Requirement、Test 映射由 `traceability.md` 负责；不存在该事实时不强制创建。
- 当前方向或范围事实变化时才更新 `project-plan.md`；active task 不自动产生 project-plan 内容。
- 示例 ID 和模板占位不是当前事实，不能用来满足完整性检查。
- 不得为了 checker 编造“无风险”、测试命令、traceability 或计划事实。

## Fact-Triggered Population Cases

1. Active task 存在，但没有实际 risk fact，`risk-register.md` 为 lean/template：`Blocking=NO`。
2. Active task 存在，但尚无 testing fact，`testing.md` 为 lean/template：active task alone cannot block。
3. Confirmed fact 已存在，且正在声明 closure/handover/ship，但负责 owner 仍 stale：只有按 `maker-checker-protocol.md` 建立真实 C1-C4 FailurePath 后，才对受影响的 closure/handover/ship scoped Blocking。

Active work 中 confirmed fact 可暂存在 active change/checkpoint。该临时承载不能在受影响 closure 之后继续成为唯一事实来源。

## Active Work Guard

只要 `task-board.md` 仍有 In Progress、Waiting、Review、Backend Ready、Needs Fix、Submitted、Mitigating、Open 或 Blocked 任务，本阶段就不是完整 phase close。归档只能标为 `legacy transition snapshot`、`provisional archive`、`evidence snapshot` 或 `active-work cleanup snapshot`，不能写成 completed phase archive。

## Archive Preflight Check

归档计划和 apply 前运行 `python scripts/check-current-docs-integrity.py --repo-root .`。当前 v0.45 checker 输出仍按其既有 machine contract 解释；本指南不得把 legacy command nonzero、strict warning 或 template owner 自动提升为 project Blocking。证据支持的 scoped Blocking 才停止 apply 并进入 Current State Restoration Pass；普通 `--confirm` 不能绕过真实 Blocking。

## Archive Postflight Check

移动计划内项目后再次执行同一检查，并验证 archive summary 没有把活跃工作写成 completed phase archive。postflight 失败时 capsule 必须标为 needs-fix，不能声明归档完成。

## Restoration Guidance

Current State Restoration Pass 从业务文档、当前代码、任务记录和必要的 archive 证据中逐项恢复仍有效事实：

1. 恢复真实 Source Record 和 Task 反链。
2. 恢复未完成任务及其最小 traceability。
3. 仅在证据确认仍有开放风险事实时恢复 risk owner；不编造“当前无开放风险”。
4. 仅在证据确认验证方法、范围、通过标准或缺口时恢复 testing owner；无事实时保持 lean。
5. 在 work-log 中说明旧 handed-off 结论已 superseded/corrected。

只恢复当前事实，不把 archive 全文复制回 current docs。修复后重新运行检查，并记录 `.forgekit/docs/` 是恢复后的当前事实入口。

## Template Placeholder Rules

`SRC-EXAMPLE-001`、`SRC-YYYYMMDD-001`、`TASK-EXAMPLE-001`、只出现在模板区的 `TASK-001`，以及 `EPIC-001`、`FEAT-001`、`RISK-001` 等占位不参与真实任务检查。真实 active task 要求真实 Source/Task 链路；risk/testing/traceability/project-plan owner 是否需要非模板内容，只由已确认事实和 closure writeback deadline 决定。

## Boundaries

- 检查器默认只读，不恢复、不覆盖、不移动文件。
- 不自动读取或复制全量 archive。
- 不修改 business docs、业务代码、Git、commit、push 或 PR。
- 完整性通过只说明 current docs 链路达到最小要求，不证明所有业务事实都正确。
- 本检查器负责单作用域 current docs 的 Source / Task / Risk / Traceability / Testing 完整性。启用 multi-project scoped docs 后，跨 Workspace / Project / Repo / Artifact / Archive 的关系由 `check-workspace-integrity.py` 检查；两者不能互相替代。
