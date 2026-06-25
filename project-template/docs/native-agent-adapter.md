# Native Agent Adapter

用途：说明 ForgeKit 如何把现有 loop、Maker / Checker 和验证协议，映射为 Claude Code / Codex 可审查的原生 agent 配置。

本文是适配说明，不是自动执行授权。ForgeKit Core 仍然负责项目边界、任务澄清、风险分级、loop 操作协议、Maker / Checker 证据和验证记录；Claude Code / Codex native agents 只是可选执行后端。

## 为什么需要

有些 AI 工具已经支持原生 agent 或子任务配置。ForgeKit 不应该重做一个多 agent runtime，但可以把已有工程协议导出成这些工具能识别的轻量配置，让用户在需要时手动调用 planner、reviewer 或 verifier。

这个适配层解决的是“把协议翻译成工具配置”，不是“自动调度多个 agent”。

## 支持目标

v0.30.0 的目标：

- `claude-code`
- `codex`

Codex 相关文件只作为 example / reviewable template。不同 Codex 版本的原生配置格式可能变化，生成后需要用户按当前 Codex 版本审查。

## 默认角色

| Agent | 默认权限 | 适用场景 | 禁止事项 |
| --- | --- | --- | --- |
| planner | 只读 | 梳理需求、边界、风险、建议 change 工件 | 不改代码，不改文档，不运行危险命令 |
| reviewer | 只读 | 审查 diff、验证证据、文档同步和风险 | 不扩大范围，不实现新功能，不自动通过 |
| verifier | 低风险命令 | 运行用户确认的 lint/test/build/check 命令并报告 | 不改业务代码，不安装依赖，不启动服务 |

v0.30.0 不生成 implementer agent。实现仍默认由主会话完成，避免并发写代码、上下文分叉和责任不清。

## 与 ForgeKit Loop 的关系

`.forgekit/docs/loop-blueprint.md` 定义可审查蓝图。

`.forgekit/docs/loop-operations.md` 定义用户显式触发的 dry-run、one-step、continue 和 stop/handoff。

Native Agent Adapter 只提供原生工具配置模板。即使生成了 planner、reviewer 或 verifier，也不代表 loop 自动开启。进入 loop 仍需要用户明确要求，并且必须遵守 loop 蓝图、允许路径、禁止路径、验证命令、停止条件和人工升级规则。

## 与 Maker / Checker 的关系

Maker / Checker 协议仍以 `.forgekit/docs/maker-checker-protocol.md` 为准。

- Maker：主会话默认承担，实现并记录 ready-for-check 证据。
- Checker：reviewer agent 可以辅助做只读复核，但不能自动宣布最终通过。
- Verifier：verifier agent 可以运行已确认的验证命令，但不能替代人工判断验证是否充分。

## 生成方式

适配配置由 ForgeKit 仓库中的生成脚本按需写入目标项目。它是 opt-in 功能，不随项目初始化默认生成。

生成后建议先审查：

- Claude Code: `.claude/agents/`、`.claude/skills/`
- Codex: `.codex/agents/`、`.codex/config.example.toml`

不要直接把示例配置当成当前工具版本的最终配置。

## 不支持

v0.30.0 不提供：

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
