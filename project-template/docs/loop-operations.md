# Loop 操作协议

用途：为已审查的 loop 蓝图定义需要用户明确触发的操作模式。

Loop 默认关闭。本文只是操作协议，不是自动 loop runner、daemon、cron job、scheduler、MCP connector、自动 PR 流程、多 agent dispatcher、worktree 自动化或无人值守连续循环。

任何 loop 操作开始前，项目必须已经具备：

- 已审查的 `.forgekit/docs/loop-blueprint.md`
- 用户明确要求本次操作模式
- 状态文件
- token 或范围预算
- 验证命令
- 停止条件
- 人工升级路径
- `.forgekit/docs/work-log.md` 或 loop 状态文件中的回写位置
- agent_mode、native_agent_status、agent_runtime 和 fallback_reason 记录位置

`loop-readiness.md` 和 `loop-blueprint.md` 仍然只是审查文档，不是自动执行授权。

## Loop Dry Run

用户询问“一轮 loop 会做什么”时使用。

规则：

- 只读取 loop 蓝图和相关状态
- 说明计划执行的一轮动作、输入、写入边界、验证、停止条件和升级路径
- 不修改文件
- 不运行危险命令
- 不 commit、tag、push、创建 issue 或创建 PR
- 除非用户明确要求记录，否则不写任何文件

输出应说明蓝图是否可以进入 `one-step`，还是被阻塞或需要人工澄清。

## Loop One Step

只在用户明确确认执行一轮 loop 后使用。

执行前先复述：

- Loop Name
- State File
- Allowed Paths
- Forbidden Paths
- Validation Command
- Stop Condition
- Human Escalation
- Token / Scope Budget
- 本轮是否会修改文件
- agent_mode: native | fallback | simulated
- native_agent_status: available | unavailable | unverified
- fallback_reason

规则：

- 只执行一轮
- 原生 custom agent 优先；如果未验证或不可用，只能在用户允许降级时使用 fallback，并在状态文件记录 `agent_mode: fallback`
- 用户要求 native-only 时，native 不可用必须停止，不得 fallback
- 保持在允许路径和预算内
- 范围不清、预算耗尽、验证失败或触碰禁止路径时停止
- 需要且可行时运行验证命令
- 将本轮结果回写到 `.forgekit/docs/work-log.md` 或 loop 状态文件

默认操作只是一轮，不自动继续。

## Loop Continue

只在用户明确要求从状态文件继续时使用。

规则：

- 行动前先读状态文件
- 只继续下一轮；如果还要再继续，必须等用户之后再次明确确认
- 不推断用户允许重复或无人值守执行
- 每轮结果都写入 `.forgekit/docs/work-log.md` 或 loop 状态文件
- 每轮都记录 `agent_invocation_observed`，不得把 fallback 或 simulated 结果写成 native 成功
- 状态不清、范围不清、预算耗尽、验证失败、触碰禁止路径或遇到需要人判断的节点时停止并升级

`continue` 的含义是从状态恢复一次，不是一直循环。

## Loop Stop / Handoff

用户要求停止、暂停、交接或总结 loop 状态时使用。

把交接摘要写入 `.forgekit/docs/work-log.md` 或 loop 状态文件，包含：

- 已完成工作
- 未完成工作
- 阻塞问题
- 验证结果
- 已改文件或有意未改的文件
- 风险和未验证项
- agent_mode、native_agent_status、agent_runtime、agent_invocation_observed 和 fallback_reason
- 建议下一步

停止或交接期间不要启动另一轮 loop。

## 停止并升级

出现以下情况时停止并询问用户或负责人：

- 范围不清
- 预算耗尽或缺失
- 验证失败或缺失
- 状态文件缺失、过期或矛盾
- 允许路径和禁止路径冲突
- 需要触碰 business docs、secrets、deploy、CI、`.forgekit/template-lock.json`、生成报告、Git 写入、外部写入、MCP、connector、自动 PR、sub-agent 调度或 worktree 自动化

## 回写

每一轮实际执行过的 loop 都必须回写到以下位置之一：

- `.forgekit/docs/work-log.md`
- 明确指定的 loop 状态文件

dry-run 只输出到聊天是可以的，除非用户要求写记录。one-step、continue、stop 和 handoff 不应把必要状态只留在聊天里。只要涉及 planner、reviewer 或 verifier，就必须写明 `agent_mode`；未观察到 native custom agent 时，`native_agent_status` 必须是 `unverified` 或 `unavailable`。
