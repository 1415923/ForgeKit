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
- 用户、负责人或 review 规则要求人工确认。

## Checkpoint Writeback

每个阶段结束后必须写回 `.forgekit/docs/work-log.md` 或明确指定的 loop state，至少记录：

- 阶段名称。
- 已做事项。
- 修改文件。
- 验证结果。
- agent_mode / native_agent_status / native_agent_lifecycle。
- 阻塞、风险和下一步。

`review-only` 不改文件；除非用户要求记录，否则只在聊天中输出结论。

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
