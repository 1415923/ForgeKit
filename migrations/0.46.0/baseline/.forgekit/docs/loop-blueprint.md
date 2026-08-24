# Loop 蓝图

用途：为某个具体项目工作流定义可审查的 loop 设计。

本文只是可审查的 loop 设计蓝图，不是自动执行授权。它不是 daemon、cron job、MCP 集成、connector、自动 PR 流程、sub-agent 调度器或 worktree 自动化配置。

Loop Name:
Owner:
Status: draft | reviewed | retired
Last Reviewed:
OperationMode: dry-run | one-step | continue | stop-handoff
LoopMode: one-step | bounded-auto | review-only
AuthorizationScope:
AgentModeRequired: native | fallback-allowed | any
RequiredAgents:
AllowedStages:
MaxRounds:
MaxStageCount:
MaxFixAttempts:
MaxFilesRead:
MaxFilesChanged:
MaxCommands:
ForbiddenActions:
StopConditions:
EscalationConditions:
CheckpointWriteback:
FinalHandoffRequired: yes
RequiresUserConfirmation: yes
WritebackTarget:
agent_mode: native | fallback | simulated
native_agent_status: available | unavailable | unverified
native_agent_lifecycle: generated | installed | registered | invoked
agent_runtime: claude-code | codex | unknown
agent_invocation_observed:
  planner: native | fallback | not-run
  reviewer: native | fallback | not-run
  verifier: native | fallback | not-run
fallback_reason:
StopOnUnclearScope: yes
StopOnValidationFailure: yes
WorktreeStrategy: none | optional | required
WorktreePath:
WorktreeBranch:
IsolationReason:
CleanupRule:

这些操作字段只是 `.forgekit/docs/loop-operations.md` 和 `.forgekit/docs/bounded-auto-loop-policy.md` 的审查字段，不是自动 runner 配置。

LoopMode 定义：

- `one-step`：每轮后停止，适合高风险或需要逐轮确认的任务。
- `bounded-auto`：只在用户授权 scope、stages、budget 和 stop conditions 内连续推进，适合中低风险。
- `review-only`：只审查或规划，不改文件，不运行写操作。

Agent 字段只记录父运行时在本轮 loop 中观察到的状态。`native_agent_status` 只允许 `available | unavailable | unverified`，不能写 `invoked`；`invoked` 只能写到 `native_agent_lifecycle` 或 `agent_invocation_observed`。子 agent 不能自行判断 `native_agent_status`。

`fallback` 和 `simulated` 都不能写成 native 成功；native 未验证时必须保持 `native_agent_status: unverified`。spawn 因 thread limit、`max_threads` 或已完成 agent 未关闭而失败时，记录为容量阻塞，不等于 native unavailable。

Worktree 字段只是 `.forgekit/docs/worktree-playbook.md` 的设计字段，不授权自动创建 worktree、启动 agent、merge、push、创建 PR、删除分支或清理目录。

## 触发方式

Default: manual only.

允许的触发：

- 用户明确要求按下方范围运行这个 loop。

默认不允许：

- daemon
- cron 或定时器
- connector 事件
- MCP 事件
- 自动 PR 或 issue 事件
- sub-agent 调度器
- worktree 自动化

Loop 默认关闭。只有用户明确要求 `dry-run`、`one-step`、`bounded-auto`、`review-only`、`continue` 或 `stop-handoff` 时，才进入对应操作模式。`bounded-auto` 必须有用户显式授权，不能由 AI 自行进入。

## 输入来源

| 来源 | 用途 | 是否必需 |
| --- | --- | --- |
| `AGENTS.md` 或 `CLAUDE.md` | 入口规则和任务路由 | yes |
| `.forgekit/project-boundary.yml` | 写入边界和 managed roots | yes |
| `.forgekit/docs/codebase-map.md` | 模块、入口文件、验证提示 | yes |
| `.forgekit/docs/local-toolchain.md` | 本地工具链和命令证据 | recommended |
| `.forgekit/docs/work-log.md` | 最近交接和中断恢复上下文 | recommended |
| `.forgekit/changes/<change-id>/` | loop 绑定到某个变更时的活跃 change 工件 | conditional |
| 生成报告 | 归档、同步、smart archive、升级、审查或验证证据 | conditional |

## 状态文件

Path:
Owner:
Write rule:
LoopMode: one-step | bounded-auto | review-only
AuthorizationScope:
AgentModeRequired: native | fallback-allowed | any
RequiredAgents:
AllowedStages:
MaxStageCount:
MaxFixAttempts:
ForbiddenActions:
StopConditions:
EscalationConditions:
CheckpointWriteback:
FinalHandoffRequired: yes
agent_mode: native | fallback | simulated
native_agent_status: available | unavailable | unverified
native_agent_lifecycle: generated | installed | registered | invoked
agent_runtime: claude-code | codex | unknown
agent_invocation_observed:
  planner: native | fallback | not-run
  reviewer: native | fallback | not-run
  verifier: native | fallback | not-run
fallback_reason:

没有明确状态文件时不能运行 loop。状态文件必须记录当前步骤、上次验证结果、阻塞条件、下一步允许动作、LoopMode、AuthorizationScope、预算、agent_mode、native_agent_status、native_agent_lifecycle 和 fallback_reason。

## 允许路径

列出精确路径或窄前缀：

- 

## 禁止路径

默认禁止路径和动作：

- business `docs/**`，除非明确纳入范围并确认
- secrets、credentials、private keys、tokens、本机专用环境文件
- deploy、release、migration 和生产操作文件，除非明确纳入范围并确认
- CI 配置，除非明确纳入范围并确认
- `.forgekit/template-lock.json`
- 生成报告，除非 loop 范围明确允许重新生成
- `README.md`、`AGENTS.md`、`CLAUDE.md`，除非 loop 范围明确包含入口文档变更
- Git commit、tag、push、issue 创建、PR 创建或外部写入

## 验证命令

Command:
Expected result:
Failure handling:

没有验证命令时不能运行 loop。验证失败时，按下面的停止和升级规则停止或升级给用户。

## 停止条件

满足以下条件时停止：

- 

Loop 启动前必须有可观察的停止条件。

## 人工升级

出现以下情况时升级给用户或负责人：

- 状态文件缺失、含糊或前后不一致
- 允许路径和禁止路径冲突
- 验证缺失、失败或超出预算
- 必需项目事实缺失或互相矛盾
- 需要触碰 secrets、deploy、CI、外部服务、Git push、自动 PR、MCP、connector、sub-agent 调度或 worktree 自动化
- `AgentModeRequired` 不满足
- `bounded-auto` 超出阶段、修复次数、文件数、命令数或授权范围

Decision owner:
Question format:

## Token 预算

Budget:
Stop or escalate when:

Scope budget:
Max files read:
Max files changed:
Max commands:

## 理解复述

修改文件前先复述：

- 目标
- 状态文件
- 允许路径
- 禁止路径
- 验证命令
- 停止条件
- 人工升级路径
- token 预算
- LoopMode、AuthorizationScope、AllowedStages、MaxRounds、MaxStageCount、MaxFixAttempts、MaxFilesChanged、MaxCommands
- ForbiddenActions、StopConditions、EscalationConditions
- 输出和回写位置
- agent_mode、native_agent_status、native_agent_lifecycle、agent_runtime 和 fallback_reason

## 输出 / 回写

结果写入：

- `.forgekit/docs/work-log.md` 或 loop 状态文件
- 如果 loop 属于中高风险变更，写入对应 `.forgekit/changes/<change-id>/` 工件

需要用于交接、验证或中断恢复的 loop 结果，不要只留在聊天里。

`bounded-auto` 每个阶段结束都必须 checkpoint writeback；最终必须输出 handoff。

## Maker / Checker 策略

如果 loop 涉及代码变更，需要定义 Maker 阶段和 Checker 阶段如何分离。职责、证据字段和审查输出见 `.forgekit/docs/maker-checker-protocol.md`。

本节不是自动 sub-agent 配置，不授权多 agent 调度、worktree 自动化或自动 checker 执行。

## Worktree 策略

只有并行任务、实验或 Maker / Checker 分离确实需要隔离时，才使用 worktree。

WorktreeStrategy: none | optional | required
WorktreePath:
WorktreeBranch:
IsolationReason:
CleanupRule:

这些字段只描述可审查的隔离意图，不授权自动创建 worktree、调度器、agent 编排、merge、push、PR、删除分支或清理目录。
