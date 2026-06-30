# 上下文连续性协议

## Purpose

聊天上下文不是可靠的工程状态。本文规定在长会话、上下文压缩、清空会话、子 agent 委派和多阶段推进中，哪些关键事实需要以最小摘要写回 ForgeKit，保证后续会话可以从项目事实继续，而不是重新猜测。

本文不是聊天日志、token 监控器或自动执行器，也不要求全量读取 managed docs。

## Why Chat Context Is Not Durable State

- 会话可能被压缩、清空、中断或切换工具。
- 子 agent 的关键发现不会天然成为父会话或下一会话的事实。
- 大型命令输出会挤占上下文，但原始输出本身通常不适合长期保存。
- 只存在聊天里的决定无法被 review、handoff 或后续任务稳定引用。

因此，关键事实应 checkpoint 到职责最窄的 current doc 或 change artifact；临时推理和长输出不应落盘。

## Critical Facts

First-Principles Pass 的关键机制推导，以及 Adversarial Review 的 blocking finding、失败路径和验证要求，都属于 Critical Facts。checkpoint 只记录结论摘要、证据路径、决策和 `TODO_REVIEW`，不复制完整推理或审查长日志。

以下内容不能只留在聊天里：

- 用户确认过的需求、范围和非目标。
- 重要技术决策及其稳定原因。
- 关键 bug 根因。
- 已验证的修复结论。
- 不应重复尝试的失败路线及失败证据摘要。
- 风险、阻塞和 `TODO_REVIEW`。
- 任务状态变化。
- 用户或版本可见变化。
- reviewer / verifier 的阻断结论和验证缺口。

## Context Checkpoint Triggers

在以下时机执行一次 Context Checkpoint 检查：

- 长会话进入阶段边界。
- 用户准备 compact / clear，或明确要求保存当前关键结论。
- `bounded-auto` 的每个 checkpoint。
- 子 agent 返回关键结论后。
- 处理大工具输出、长日志或大型报告后。
- 任务状态发生变化后。
- review / verification 出现 blocking、失败或 `TODO_REVIEW` 后。
- handoff、commit 或 tag 前。

Checkpoint 只写发生变化且有证据的关键事实；无新事实时不为“同步”而改文档。

## Context Survival Map

| 需要存活的内容 | 目标 | 边界 |
| --- | --- | --- |
| 长期行为规则 | `AGENTS.md` / `CLAUDE.md` | 只放短规则，不放项目流水 |
| 项目结构和搜索入口 | `codebase-map.md` | 不做项目百科 |
| 用户原始任务 | `task-intake.md` | 保留脱敏原文和 Source ID，不写 AI 推理 |
| 已确认需求事实 | `requirements.md` | 需用户确认，不复制任务原文 |
| 当前任务状态 | `task-board.md` | 只写状态、owner、下一步、验证和 Source ID |
| 近期工作过程摘要 | `work-log.md` | 只保留恢复工作所需摘要 |
| 技术决策 | `.forgekit/changes/<id>/design.md` 或 `tech-decisions.md` | 保留决定、原因和影响，不写长讨论 |
| 验证方法 | `testing.md` | 只保留可复用方法 |
| 验证证据 | `.forgekit/changes/<id>/verification.md` 或 `work-log.md` | 摘要命令、结果和证据路径 |
| 风险和阻塞 | `risk-register.md` | 只保留仍有效的开放风险 |
| 阶段交付总结 | `.forgekit/handoff-package.md` 或 scoped `handoff.md` | report-only，不作为事实源 |
| 长工具输出 | 外部日志、临时文件或生成报告 | 常驻 docs 只保留结论、路径和必要片段 |

## Compact / Clear Readiness

准备压缩或清空上下文前，确认：

1. 当前目标、范围和非目标已有稳定落点。
2. 当前 Task / Change 状态和下一步已更新。
3. 已完成验证、失败路线、风险和 `TODO_REVIEW` 有可追溯摘要。
4. 子 agent 的 blocking 结论已经写入当前 change review/verification 或 work-log。
5. 后续会话能从 `codebase-map.md`、`workflow-router.md` 和相关任务文档恢复，不需要全量读取 docs。

ForgeKit 不自动执行 compact 或 clear；这只是执行前的人工可审查检查。

## Post-Upgrade Session Refresh

ForgeKit upgrade 后旧会话只用于收口，不继续承担新版本后的新任务。

1. 当前会话先执行 Context Checkpoint，并按 `ManagedDocsWriteback: minimal` 写回已确认的进度、验证、风险和下一步。
2. 旧会话可以完成当前 commit、tag 或 handoff，但不启动新版本后的新任务。
3. 如果升级更新了 `AGENTS.md`、`CLAUDE.md`、`.codex/rules.md`、`.claude/skills/**`、`.claude/agents/**` 或 `.codex/agents/**`，新任务应新开会话或重启对应工具。
4. 新会话开始时先读取新版 `AGENTS.md` / `CLAUDE.md`、`.codex/rules.md`、`workflow-router.md` 和本文。
5. 不假设当前会话自动加载新规则；磁盘文件已更新不等于当前运行时已重新加载。

如果无法确认当前工具是否已重新加载，将会话状态视为 stale，停止新任务并要求刷新会话。

## Maintenance Checkpoint

upgrade sync、Archive Capsule、handoff 或其他维护动作前，先记录当前范围、状态、未完成项和计划路径；操作后记录实际动作、验证、summary/index 路径和下一步。Archive Capsule 的 `archive-summary.md` 是恢复历史上下文的入口，但不是 current truth；默认先通过 `.forgekit/archive/index.md` 定位，不读取全量 archive。升级完成后继续遵守 Post-Upgrade Session Refresh。

## Subagent Output Handling

- 父运行时负责判断和记录子 agent 输出，不要求子 agent自行修改 managed docs。
- planner 的稳定方案进入 proposal/design/tasks；reviewer 的 gate 进入 review；verifier 的证据进入 verification。
- 子 agent 的长解释不原样复制，只保留结论、证据、阻断原因和 `TODO_REVIEW`。
- 无法确认来源、范围或证据时标记 `TODO_REVIEW`，不得提升为稳定事实。

## Large Output Handling

- 不把完整构建日志、测试日志、diff、trace 或工具输出写入常驻 managed docs。
- 保留命令、结果摘要、关键错误、时间、文件路径或 report 路径。
- 临时输出应放在项目允许的临时位置，并遵守敏感信息和清理规则。
- 输出中包含 secrets、token、账号、证书或环境地址时必须脱敏。

## Writeback Boundaries

- 默认使用 `ManagedDocsWriteback: minimal`。
- 不记录完整聊天、临时推理或未经确认的猜测。
- 不自动改 `task-intake.md` 原文。
- 不自动改 `requirements.md` 事实源；需求变化需用户确认。
- 不把所有事实或项目状态塞进 `CLAUDE.md` / `AGENTS.md`。
- business docs 仍为 read-mostly，除非用户明确授权。
- report-only、review-only 流程仍保持不写或仅写其声明的报告目标。
- 不确定项统一标记 `TODO_REVIEW`。

## Examples

**子 agent 找到 bug 根因**：把根因、证据文件和影响写入当前 change review/design；把修复验证写入 verification；不复制完整子 agent 对话。

**测试输出很长**：`work-log.md` 只写执行命令、通过/失败、关键错误摘要和日志路径；不粘贴几千行输出。

**准备清空会话**：检查 task-board 的状态和下一步、work-log 的近期摘要、当前 change 的 verification/review；缺失证据写 `TODO_REVIEW` 后再 handoff。
