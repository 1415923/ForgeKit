# Bounded Auto Loop Policy

用途：定义用户一次授权 AI 在有限边界内连续推进多个阶段时必须遵守的规则。

本文是 policy 和检查清单，不是 runner、daemon、cron、scheduler、多 agent dispatcher、自动 PR 或 worktree orchestration。

## Loop Mode

| LoopMode | 用途 | 写入权限 | 停止节奏 |
| --- | --- | --- | --- |
| `one-step` | 高风险、范围敏感或用户要逐轮确认的任务 | 只执行用户确认的一轮 | 每轮结束必须停止 |
| `bounded-auto` | 中低风险、边界清楚、验证命令明确的多阶段任务 | 只在授权 scope、stages、budget 内推进 | 命中 stop condition 必须停止 |
| `review-only` | 只审查、规划、对比或总结 | 不改文件，不运行写操作 | 输出结论后停止 |

默认不得自行进入 `bounded-auto`。用户必须明确授权，并给出范围、阶段、预算、禁止动作、停止条件和 agent mode 要求。

## Scope 与 Managed Docs Writeback

执行前必须区分两层范围：

- `Implementation Scope`：业务代码、配置和测试允许修改的路径。
- `Governance Writeback Scope`：任务结束或 checkpoint 时允许最小写回的 ForgeKit managed docs。

使用以下字段声明写回策略：

```text
ManagedDocsWriteback: off | minimal | full-review
```

- 默认值是 `minimal`。
- `minimal` 只允许按实际事件更新 `work-log.md`；任务状态确实变化时更新 `task-board.md`；出现用户或版本可见变化时更新 `changelog.md`；当前 change 流程需要时更新 `.forgekit/changes/<id>/*`。
- `full-review` 仍需逐项遵守 `workflow-router.md` 和 `document-responsibility.md`，不表示可以全量改文档。
- `off` 只在用户明确说“不改文档”“不改 ForgeKit”“不写 managed docs”，或明确限定允许文件且同时禁止文档写入时使用。
- 用户说“只改这些业务文件”默认只限制 `Implementation Scope`，不等于关闭 `Governance Writeback Scope`。
- `task-intake.md` 原文、`requirements.md` 事实源和 business `docs/` 不属于默认最小写回；修改它们需要用户明确授权。
- report-only 脚本仍然只生成报告；本策略不能授权它们自动修复 doc-health、source-trace、handoff 或其他报告发现。

## 启动前复述

进入 `bounded-auto` 前必须复述并等待用户确认：

- AuthorizationScope
- AllowedStages
- MaxRounds
- MaxStageCount
- MaxFixAttempts
- MaxFilesChanged
- MaxCommands
- ForbiddenActions
- StopConditions
- EscalationConditions
- AgentModeRequired
- RequiredAgents
- CheckpointWriteback
- ManagedDocsWriteback
- Implementation Scope
- Governance Writeback Scope
- FinalHandoffRequired

## Agent Mode Gate

- 开始前必须确认 `agent_mode`、`native_agent_status`、`native_agent_lifecycle` 和 `agent_runtime`。
- `AgentModeRequired: native` 时，如果 `native_agent_status != available`，必须停止。
- `AgentModeRequired: fallback-allowed` 时可以降级，但必须记录 `agent_mode: fallback` 和 `fallback_reason`。
- 不得把 fallback、worker、explorer、general-purpose 或 simulated 执行说成 native。
- thread limit、`max_threads` 或已完成 agent 未关闭导致 spawn 失败时，记录为容量阻塞，不等于 native unavailable。

## Stop Conditions

命中以下任一条件必须停止：

- 范围不清、目标变化或出现新需求。
- 超出 AuthorizationScope、AllowedStages、MaxRounds、MaxStageCount、MaxFixAttempts、MaxFilesChanged 或 MaxCommands。
- 触及 ForbiddenActions。
- 验证失败、验证缺失或验证命令产生未确认副作用。
- 需要读取 secrets、`.env`、tokens、keys、证书或敏感配置。
- 需要修改 business docs、deploy、CI、release、migration、外部系统或 `.forgekit/template-lock.json`。
- 需要 commit、tag、push、issue、PR、MCP 写操作、connector 写操作、worktree orchestration 或自动调度。
- AgentModeRequired 不满足。
- native-only 要求下 native agent 不可用。
- 需要根据 `.forgekit/doc-health-report.md` 自动瘦身、归档、重写或合并 managed docs。
- 需要根据 `.forgekit/source-trace-report.md` 自动补 Source ID、改写任务状态、补验证记录或合并 changelog。
- 需要根据 `.forgekit/handoff-package.md` 自动修复文档、补证据、提交 Git、创建 PR 或编排 worktree。
- 用户、负责人或 review 规则要求人工确认。

## Checkpoint Writeback

每个阶段结束后先执行 writeback check，按 `ManagedDocsWriteback` 决定是否写回。`minimal` 模式至少把实际完成进展写入 `.forgekit/docs/work-log.md` 或明确指定的 loop state，并只在状态或用户可见事实确实变化时更新其他允许目标：

- 阶段名称。
- 已做事项。
- 修改文件。
- 验证结果。
- agent_mode / native_agent_status / native_agent_lifecycle。
- 阻塞、风险和下一步。

`one-step` 在结束前执行一次最小 writeback check；`bounded-auto` 每个 checkpoint 都执行；`review-only` 绝不写文件，即使 `ManagedDocsWriteback` 不是 `off`，也只在聊天中输出结论。

文档健康场景下，`bounded-auto` 最多生成 `.forgekit/doc-health-report.md` 并停止。报告只是 review 输入，不能自动触发文档瘦身、归档、链接重写或事实合并。

来源追溯场景下，`bounded-auto` 最多生成 `.forgekit/source-trace-report.md` 并停止。报告只是人工修链输入，不能自动补 Source ID、创建任务、改任务状态、补验证记录或重写 changelog。

阶段收口或交接场景下，`bounded-auto` 最多生成 `.forgekit/handoff-package.md` 或 scoped change `handoff.md` 并停止。handoff 只是人工 review 输入，不能自动修复 doc-health/source-trace 问题，不能自动提交 Git、创建 PR、改 current docs 或改 business docs。

## Final Handoff

`bounded-auto` 结束时必须输出 handoff：

- 完成的阶段。
- 未完成的阶段。
- 停止原因。
- 验证结果。
- 已改文件。
- 风险和未验证项。
- 建议下一步。

## 不做事项

v0.31 不提供：

- 自动 runner。
- daemon、cron、scheduler。
- 多 agent dispatcher。
- worktree orchestration。
- 自动 merge、commit、tag、push、issue 或 PR。
- 自动安装依赖、启动服务、部署或迁移。
- 自动绕过用户确认。
