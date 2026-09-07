# Bounded Auto Loop Policy

用途：定义用户一次授权 AI 在有限边界内连续推进多个阶段时必须遵守的规则。

本文是 policy，不是 readiness questionnaire、mandatory blueprint/state、runner、daemon、cron、scheduler、多 agent dispatcher、自动 PR 或 worktree orchestration。

<!-- forgekit:section s-6cdbac0f3763 -->
## Loop Mode

| LoopMode | 用途 | 写入权限 | 停止节奏 |
| --- | --- | --- | --- |
| `one-step` | 高风险、范围敏感或用户要逐轮确认的任务 | 只执行用户确认的一轮 | 每轮结束必须停止 |
| `bounded-auto` | 中低风险、边界清楚、验证命令明确的多阶段任务 | 只在授权 scope、stages、budget 内推进 | 命中 stop condition 必须停止 |
| `review-only` | 只审查、规划、对比或总结 | 不改文件，不运行写操作 | 输出结论后停止 |

默认不得自行进入 `bounded-auto`。用户必须明确授权，并给出实际需要的范围、允许/禁止路径、阶段、预算、停止条件与 handoff。普通实现授权、长任务或已有 agent 配置不自动触发 loop。

每轮执行应用 `governance/ai-engineering-loop.md`，明确 `ExecutionIntent: DIAGNOSTIC | SMOKE | FORMAL`；不存在 release intent。Effect Risk 与 Intent 正交，按 `governance/agent-entry-contract.md` 独立约束 external action、credential、budget、retry、destructive boundary 和 recovery。

<!-- forgekit:section s-75bb97eccdcd -->
## Scope 与 Managed Docs Writeback

执行前必须区分两层范围：

- `Implementation Scope`：业务代码、配置和测试允许修改的路径。
- `Governance Writeback Scope`：任务结束或 checkpoint 时允许最小写回的 ForgeKit managed docs。

使用以下字段声明写回策略：

```text
ManagedDocsWriteback: off | minimal | full-review
```

- 默认值是 `minimal`。
- `minimal` 只在 confirmed fact 变化时更新唯一负责 owner：近期恢复事实可写 `work-log.md`；任务状态确实变化时更新 `task-board.md`；出现用户或版本可见变化时更新 `changelog.md`；当前 change 流程需要时更新 `.forgekit/changes/<id>/*`。
- `full-review` 仍需逐项遵守 `usage-playbook.md` 和 `document-responsibility.md`，不表示可以全量改文档。
- `off` 只在用户明确说“不改文档”“不改 ForgeKit”“不写 managed docs”，或明确限定允许文件且同时禁止文档写入时使用。
- 用户说“只改这些业务文件”默认只限制 `Implementation Scope`，不等于关闭 `Governance Writeback Scope`。
- `task-intake.md` 原文、`requirements.md` 事实源和 business `docs/` 不属于默认最小写回；修改它们需要用户明确授权。
- report-only 脚本仍然只生成报告；本策略不能授权它们自动修复 doc-health、source-trace、handoff 或其他报告发现。

<!-- forgekit:section s-cfe9b04764d9 -->
## Bounded Execution Envelope

进入 `bounded-auto` 前，从用户请求、project boundary 与任务证据中确定本轮实际需要的字段：

```text
AuthorizationScope:
AllowedPaths:
ForbiddenPaths:
AllowedStages:
Budget: rounds / commands / files / time or cost, as applicable
Validation:
StopConditions:
EscalationConditions:
ExternalEffectEnvelope:
CheckpointEvents:
HandoffTarget:
```

不要为了“完整”创建 readiness、blueprint、state file 或固定 artifact chain。缺少会改变 target、write scope、external effect、budget 或 stop 行为的信息时，只停止受影响动作并请求确认；不阻止无关只读或可逆本地工作。

ExternalEffectEnvelope 按实际情况说明 target、credential scope、budget/rate limit、retry limit、destructive boundary、stop 与 recovery/rollback。commit、push、tag、release、deploy、生产变更、重要数据删除、不可逆 migration、permission/credential change 与 connector/MCP 写操作仍需用户针对具体目标和影响授权。

<!-- forgekit:section s-016fb441c3bd -->
## Agent Mode Gate

- 只有用户指定 native/fallback mode，或本轮实际依赖 native agent 时，才确认 `agent_mode`、`native_agent_status`、`native_agent_lifecycle` 和 `agent_runtime`；普通 bounded execution 不需要 native readiness check。
- `AgentModeRequired: native` 时，如果 `native_agent_status != available`，必须停止。
- `AgentModeRequired: fallback-allowed` 时可以降级，但必须记录 `agent_mode: fallback` 和 `fallback_reason`。
- 不得把 fallback、worker、explorer、general-purpose 或 simulated 执行说成 native。
- thread limit、`max_threads` 或已完成 agent 未关闭导致 spawn 失败时，记录为容量阻塞，不等于 native unavailable。

<!-- forgekit:section s-7d1c9e1572df -->
## Independent Review Gate

bounded-auto 本身不机械要求 independent review。只有用户或 frozen contract 明确设置 gate、objective impact 与 evidence 建立需要独立判断的 C1-C4 consequence，或适用 security/migration/release owner 明确要求时，才启用独立 review。

存在该 gate 时，Maker 只传最小 review packet，reviewer 保持 fresh read-only；self-review 不能满足它。Reviewer 不可用或证据不足时返回 `manual-review`，只停止该 gate 保护的 scoped action。Findings 按 `maker-checker-protocol.md` 独立表达 `impact_severity` 与 `blocking`；Severity、checker exit、strict warning 或 `TODO_REVIEW` 不自动产生 Blocking。

First-Principles 或 Adversarial Review 由用户、真实高影响 failure path 或 frozen contract 按需触发，不组成 every-run 固定 chain。

<!-- forgekit:section s-5612ae8cfcd0 -->
## Stop Conditions

命中以下任一条件必须停止：

- 范围不清、目标变化或出现新需求。
- 超出 AuthorizationScope、AllowedPaths、AllowedStages、budget、retry limit 或其他已声明 envelope。
- 触及 ForbiddenActions。
- 验证失败、验证缺失或验证命令产生未确认副作用，且其 ValidationRelevance 使当前 claim/action 无法继续。
- 需要读取 secrets、`.env`、tokens、keys、证书或敏感配置。
- 需要修改 business docs、deploy、CI、release、migration、外部系统或 `.forgekit/template-lock.json`。
- 需要 commit、tag、push、issue、PR、MCP 写操作、connector 写操作、worktree orchestration 或自动调度。
- AgentModeRequired 不满足。
- 适用 independent gate 未满足、`ReviewDecision: needs-fix` 或 `manual-review`。
- `Blocking=YES` finding：只停止其 `BlockedScope`，不扩大为全项目 stop。
- native-only 要求下 native agent 不可用。
- 需要根据 `.forgekit/doc-health-report.md` 自动瘦身、归档、重写或合并 managed docs。
- 需要根据 `.forgekit/source-trace-report.md` 自动补 Source ID、改写任务状态、补验证记录或合并 changelog。
- 需要根据 `.forgekit/handoff-package.md` 自动修复文档、补证据、提交 Git、创建 PR 或编排 worktree。
- 用户、负责人或 review 规则要求人工确认。

Command nonzero、hygiene warning 或 non-blocking finding 只按真实 relevance 处理，不自动扩大成全项目 stop。Repeated governance-only blocking without new mainline evidence 时，先执行 `ai-engineering-loop.md` 的 simplification review；在新的受支持 C1-C4 consequence 或显式 user gate 出现前，不增加 readiness-of-readiness、checker-of-checker、counter、state 或 governance layer。

<!-- forgekit:section s-d1ac88c45cad -->
## Checkpoint Writeback

Checkpoint 由授权中声明的事件和真实事实变化触发，不按每个 stage 固定生成 work-log，也不要求 state file。按 `work-session-checkpoint.md` 与 `work-session-checkpoint.md` 执行 writeback check；无新事实时不写。关键结论不能只留在聊天里；长工具输出只保留摘要、证据路径和 `TODO_REVIEW`，不得写入全文。`minimal` 只在对应事实确实变化时更新唯一负责 owner，可包含：

- 阶段名称。
- 已做事项。
- 修改文件。
- 验证结果。
- agent_mode / native_agent_status / native_agent_lifecycle。
- 阻塞、风险和下一步。

`one-step` 在结束前执行一次最小 writeback check；`bounded-auto` 只在声明的 checkpoint 执行；`review-only` 绝不写文件，即使 `ManagedDocsWriteback` 不是 `off`，也只在聊天中输出结论。

Document ownership does not imply mandatory population。Active task 本身不产生 risk、testing、traceability 或 project-plan 内容。Active work 中 confirmed fact 可暂存在 active change/checkpoint；受影响 task/change/phase 被声明 closed、shipped 或 handed off 前才必须写回唯一 owner。用户禁止该写回时，只停止相关 closure/handover/ship declaration，不阻止无关工作。

ForgeKit 升级后，当前 `bounded-auto` 不得跨过版本边界继续新阶段。它必须在 Context Checkpoint 和 `ManagedDocsWriteback: minimal` 后停止；旧会话只可完成当前 handoff / commit / tag，新任务应新开会话或重启工具。

文档健康场景下，`bounded-auto` 最多生成 `.forgekit/doc-health-report.md` 并停止。报告只是 review 输入，不能自动触发文档瘦身、归档、链接重写或事实合并。

来源追溯场景下，`bounded-auto` 最多生成 `.forgekit/source-trace-report.md` 并停止。报告只是人工修链输入，不能自动补 Source ID、创建任务、改任务状态、补验证记录或重写 changelog。

阶段收口或交接场景下，`bounded-auto` 最多生成 `.forgekit/handoff-package.md` 或 scoped change `handoff.md` 并停止。handoff 只是人工 review 输入，不能自动修复 doc-health/source-trace 问题，不能自动提交 Git、创建 PR、改 current docs 或改 business docs。

项目维护场景下，`bounded-auto` 可以执行已授权的 maintenance plan。upgrade `apply --safe` 必须在明确授权范围内；Archive Capsule apply 即使在 bounded-auto 中也必须有针对该计划的明确确认。维护结束后必须输出 summary；不得自动整理旧 archive、修改 business docs 或提交 Git。

<!-- forgekit:section s-912945f19f58 -->
## Final Handoff

`bounded-auto` 结束时必须输出 handoff：

- 完成的阶段。
- 未完成的阶段。
- 停止原因。
- 验证结果。
- 已改文件。
- 风险和未验证项。
- 建议下一步。

<!-- forgekit:section s-a918e441c3d0 -->
## 不做事项

v0.31 不提供：

- 自动 runner。
- daemon、cron、scheduler。
- 多 agent dispatcher。
- worktree orchestration。
- 自动 merge、commit、tag、push、issue 或 PR。
- 自动安装依赖、启动服务、部署或迁移。
- 自动绕过用户确认。

<!-- forgekit:user begin -->
<!-- forgekit:user end -->
