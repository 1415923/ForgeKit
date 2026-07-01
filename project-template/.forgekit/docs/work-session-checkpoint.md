# 工作会话 Checkpoint 协议

## Purpose

本协议规定工作会话中何时不写 ForgeKit managed docs、何时做最小写回、何时在交付前收口。目标是让 current docs 保留可恢复的当前事实，同时避免每次小改都产生文档噪音。

Checkpoint 由事件触发，不按消息数、命令数或固定时间触发。默认使用 `ManagedDocsWriteback: minimal`，只更新事实真正变化的负责文档。

## Writeback Levels

### Micro Update

不写 ForgeKit governance docs。适用于 typo、临时试错、单次失败命令、尚未形成结论的探索和纯格式调整。

Micro Update 只限制 `.forgekit` managed docs 的治理写回，不限制任务授权范围内修改业务代码、业务 README、注释、测试或配置。若小改最终形成任务状态、验证结论、风险或用户可见变化，则在闭环时升级为 Checkpoint Update。

### Checkpoint Update

只写回已确认且对恢复工作有用的最小事实。适用于：

- 完成一个可描述的小闭环；
- 任务状态、owner 或下一步变化；
- 关键结论或根因得到确认；
- 新风险、阻塞或 `TODO_REVIEW` 出现；
- 出现有意义的验证结果；
- 准备 compact、clear、换会话或中断工作；
- 子 agent 返回需要保留的关键结论。

### Ship Update

在 commit、tag、handoff、发布或 Archive Capsule 前执行。除 Checkpoint Update 外，还要确认用户可见变化、验证证据、开放风险、change 状态和后续入口已经收口。Ship Update 不授权自动 commit、tag、push、PR 或 archive apply。

## Write Targets

| 事实类型 | 写回位置 | 最小内容 |
| --- | --- | --- |
| 工作顺序、已确认进展、下一步 | `work-log.md` | 时间窗口、Task/Source、结果、下一步 |
| 任务状态变化 | `task-board.md` | 状态、owner、下一步、验证、Source ID |
| 当前验证方法、基线或缺口 | `testing.md` | 可复用命令、结论、缺口；不粘贴长日志 |
| 开放风险或阻塞 | `risk-register.md` | 风险、影响、缓解、状态 |
| 用户或版本可见变化 | `changelog.md` | 行为、兼容性、迁移提示 |
| 当前 medium/high change 证据 | `.forgekit/changes/<id>/` | 对应 verification/review/ship 工件 |
| 来源事实变化 | `task-intake.md` 或 scoped `source-links.md` | 原始来源或引用、人工确认状态 |

`task-intake.md`、`source-links.md` 和 `requirements.md` 不是一般进度写回目标。只有来源事实或已确认需求事实发生变化时才更新。

## Do Not Write Back

- typo 或纯格式调整；
- 临时试错和一次性失败命令；
- 未确认猜测、尚未形成结论的探索；
- 完整聊天、长命令输出、完整 diff 或测试流水；
- 为了“看起来同步”而重写没有变化的文档；
- 未经用户确认的需求或来源解释。

未知内容保留为 `TODO_REVIEW`，不得写成 current truth。

## Pre-Compact Checkpoint

当 compact、clear、换会话或中断可以预见时，先执行：

1. 确认当前目标、范围、已完成项和下一步。
2. 检查任务状态、验证结论、风险和关键根因是否已有最小落点。
3. 只更新命中的负责文档，不全量扫描或重写 `.forgekit/docs/**`。
4. 输出恢复入口：相关 Task/Source/Change ID、证据路径和下一条命令。

可复制提示词：

> 在 compact、clear 或换会话前做一次 pre-compact checkpoint。只把已确认的当前状态、验证、风险和下一步最小写回负责文档，不复制聊天或长日志；最后告诉我新会话应先读哪些文件。

## Post-Compact Recovery Check

auto compact 可能不可预见，不能假设用户总能提前 checkpoint。恢复后第一步：

1. 不立即继续写代码，先读取 `AGENTS.md` / `CLAUDE.md`、`workflow-router.md` 和最近命中的 task/change/work-log。
2. 对照当前工作区、验证证据和已落盘事实，识别可能丢失的结论。
3. 无证据内容标记 `TODO_REVIEW`，不得凭压缩摘要提升为事实。
4. 必要时执行一次 Checkpoint Update，再继续任务。

## Mode Rules

- `review-only`：不写 managed docs。
- `one-step`：结束前执行一次 writeback check；无新事实则不写。
- `bounded-auto`：每个授权 checkpoint 执行 writeback check；超范围或证据不足时停止。
- report-only 脚本：只写其声明的报告文件，不借本协议自动修复 current docs。

## Boundaries

- 不做后台定时写回或自动 compact 检测。
- 不扫描完整聊天补文档。
- 不自动拆分文档或创建 Project Capsule / Repo Lite。
- 不自动 commit、tag、push、PR 或 archive apply。
- business docs 是否更新仍由任务范围和用户授权决定。
