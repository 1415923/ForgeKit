# Native Agent Adapter

用途：说明 ForgeKit 如何把现有 loop、Maker / Checker 和验证协议，映射为 Claude Code / Codex 可审查的原生 agent 配置，并区分 native agent 与 fallback 执行。

本文是适配说明，不是自动执行授权。ForgeKit Core 仍然负责项目边界、任务澄清、风险分级、loop 操作协议、Maker / Checker 证据和验证记录；Claude Code / Codex native agents 只是可选执行后端。

生成配置不等于运行时已经注册。Claude Code / Codex 是否真正加载 custom agents，取决于路径、格式、工具版本、session 启动方式，以及是否重启或按官方方式重新加载。没有观察到 `forgekit-planner`、`forgekit-reviewer` 或 `forgekit-verifier` 被实际调用前，不能把结果称为 native agent 成功。

native_agent_lifecycle: generated | installed | registered | invoked
agent_mode: native | fallback | simulated
FallbackPolicy: fallback is downgrade mode, not native success

## 为什么需要

有些 AI 工具已经支持原生 agent 或子任务配置。ForgeKit 不应该重做一个多 agent runtime，但可以把已有工程协议导出成这些工具能识别的轻量配置，让用户在需要时手动调用 planner、reviewer 或 verifier。

这个适配层解决的是“把协议翻译成工具配置”，不是“自动调度多个 agent”。

## 支持目标

v0.30.x 的目标：

- `claude-code`
- `codex`

Codex 相关文件只作为 example / reviewable template。不同 Codex 版本的原生配置格式可能变化，生成后需要用户按当前 Codex 版本审查。

## 默认角色

| Agent | 默认权限 | 适用场景 | 禁止事项 |
| --- | --- | --- | --- |
| planner | 只读 | 梳理需求、边界、风险、建议 change 工件 | 不改代码，不改文档，不运行危险命令 |
| reviewer | 只读 | 审查 diff、验证证据、文档同步和风险 | 不扩大范围，不实现新功能，不自动通过 |
| verifier | 低风险命令 | 运行用户确认的 lint/test/build/check 命令并报告 | 不改业务代码，不安装依赖，不启动服务 |

v0.30.x 不生成 implementer agent。实现仍默认由主会话完成，避免并发写代码、上下文分叉和责任不清。

## 四层状态

Native Agent Adapter 必须区分四层状态：

| 状态 | 含义 | 对应字段 |
| --- | --- | --- |
| `generated` | ForgeKit 已生成配置文件 | `native_agent_lifecycle: generated` |
| `installed` | 配置文件位于目标项目预期路径且 schema 通过 | `native_agent_lifecycle: installed` |
| `registered` | 工具 runtime 的 agent 列表能看到 `forgekit-*` | `native_agent_lifecycle: registered` |
| `invoked` | 父运行时明确观察到 `forgekit-*` 被调用 | `native_agent_lifecycle: invoked` 或 `agent_invocation_observed.<role>: native` |

只有 `invoked` 才能写成 native 真正可用。`generated`、`installed` 和 `registered` 都不能替代真实调用证据。

## Runtime 状态

Native Agent Adapter 有三种运行状态：

| 状态 | 含义 | 记录要求 |
| --- | --- | --- |
| `native` | 已观察到工具实际调用 `forgekit-*` custom agent | 写明 runtime、角色和调用证据 |
| `fallback` | native agent 不可用，改用 general-purpose / worker 加 prompt injection | 写明 fallback_reason，不能称为 native 成功 |
| `simulated` | 仅由主会话按 planner / reviewer / verifier 角色模拟执行 | 写明没有调用 native agent |

`native_agent_status` 合法值只允许 `available | unavailable | unverified`。它不记录 `invoked`；`invoked` 只能写入 `native_agent_lifecycle` 或 `agent_invocation_observed`。

原生调用证据由父运行时记录。子 agent 可以报告“我看到的角色、命令、输出和限制”，但不能自行判断或改写 `native_agent_status`。

`native_agent_status` 默认为 `unverified`。只有父运行时明确观察到 `forgekit-*` 被调用，才可记录为 `available`；确认 runtime 只暴露 default / explorer / worker 时记录为 `unavailable`。

如果 spawn 因 thread limit、`max_threads`、agent 数量上限或未关闭已完成 agent 而失败，这不是 native unavailable，应记录为容量阻塞。关闭已完成 agent 或降低并发后可以重试。

## 与 ForgeKit Loop 的关系

`.forgekit/docs/loop-blueprint.md` 定义可审查蓝图。

`.forgekit/docs/loop-operations.md` 定义用户显式触发的 dry-run、one-step、continue 和 stop/handoff。

Native Agent Adapter 只提供原生工具配置模板。即使生成了 planner、reviewer 或 verifier，也不代表 loop 自动开启，也不代表 runtime 已加载这些 agent。进入 loop 仍需要用户明确要求，并且必须遵守 loop 蓝图、允许路径、禁止路径、验证命令、停止条件和人工升级规则。

如果 loop 使用 `bounded-auto`，必须先读取 `.forgekit/docs/bounded-auto-loop-policy.md`。`AgentModeRequired: native` 时，`native_agent_status != available` 必须停止；`fallback-allowed` 时可以降级，但必须记录 `agent_mode: fallback` 和 `fallback_reason`，不得把 fallback 称为 native。

## 与 Maker / Checker 的关系

Maker / Checker 协议仍以 `.forgekit/docs/maker-checker-protocol.md` 为准。

- Maker：主会话默认承担，实现并记录 ready-for-check 证据。
- Checker：reviewer agent 可以辅助做只读复核，但不能自动宣布最终通过。
- Verifier：verifier agent 可以运行已确认的验证命令，但不能替代人工判断验证是否充分。

## 生成方式

适配配置由 ForgeKit 初始化参数或单独生成脚本按需写入目标项目。它仍是 opt-in 功能，不代表 loop 自动启动。

生成后建议先审查：

- Claude Code: `.claude/agents/`、`.claude/skills/`
- Codex: `.codex/agents/`、`.codex/config.toml`、`.codex/config.example.toml`

不要直接把示例配置当成当前工具版本的最终配置。

## Native Agent 验证清单 / Native Agent Verification Checklist

Claude Code：

- `.claude/agents/forgekit-planner.md` 存在。
- frontmatter `name` 与 `forgekit-planner` / `forgekit-reviewer` / `forgekit-verifier` 一致。
- session 已重启，或已按当前 Claude Code 官方方式重新加载 agent。
- `/agents` 能看到 `forgekit-*` agent。
- 显式调用时能观察到 `forgekit-*`，而不是 `general-purpose` fallback。

Codex：

- `.codex/agents/forgekit-planner.toml` 存在。
- `name`、`description`、`developer_instructions` 齐全。
- `.codex/config.toml` 存在，且只包含项目级 agents 安全设置。
- 当前 Codex 版本支持 custom agents。
- 可先运行 `python scripts/check-codex-native-agents.py --repo-root .` 做静态检查；报告中的 `SchemaStatus: pass` 不等于 runtime 已注册。
- 如果 Codex 只显示 default / explorer / worker，应记录 `native_agent_status: unavailable`。
- 如果 Codex 因 thread limit / `max_threads` 拒绝 spawn，应记录容量阻塞，不要写成 native unavailable。
- 显式 spawn 时能观察到 `forgekit-*` 被调用，而不是 default / worker / explorer fallback。

## Fallback 规则

原生优先，fallback 可用，但必须可检测、可记录、不可混淆。

- fallback 是降级模式，不是 native 成功。
- native agent 未验证时，`native_agent_status: unverified`。
- native agent 不可用但用户允许降级时，可以使用 general-purpose / worker 加 prompt injection。
- fallback 结果必须记录 `agent_mode: fallback` 和 `fallback_reason`。
- 如果用户要求 native-only，native agent 不可用时必须停止，不得降级。
- native-only verification 默认只读；除非用户明确要求“记录到文档”，不得自动写 `task-intake.md`、`work-log.md` 或 loop state。
- 不得把 fallback 或 simulated 结果描述为 native agent 成功。

## 不支持

v0.30.x 不提供：

- 自动 loop runner
- daemon、scheduler、cron
- 多 agent dispatcher
- 自动 worktree 创建或清理
- 自动 merge、commit、tag、push、PR
- 自动安装依赖或启动服务
- 默认启用网络、MCP、外部账号或 connector
- 默认读取 secrets、`.env`、tokens、keys、证书

## 人工升级规则

出现以下情况时停止并交给主会话或用户：

- 任务范围不清
- 需要改代码或业务文档
- 需要读取敏感文件
- 需要安装依赖、启动服务、访问网络或外部系统
- 验证命令缺失、失败或会产生副作用
- 需要 Git 写入、merge、commit、push 或 PR
- planner、reviewer、verifier 的结论互相矛盾

## 适用场景

- 中高风险变更前，让 planner 做只读计划草案。
- Maker 完成后，让 reviewer 做只读复核。
- 发布或归档前，让 verifier 运行已确认的检查命令并输出证据。
- 团队想逐步试用工具原生 agent，但仍保留 ForgeKit 的项目边界和交付规则。

## 不适用场景

- 希望无人值守连续开发。
- 希望多个 agent 同时修改代码。
- 希望自动创建分支、worktree、PR 或发布。
- 项目没有明确验证命令、停止条件和人工升级路径。
