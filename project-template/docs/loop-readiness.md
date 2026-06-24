# Loop 准备度

用途：判断当前项目是否具备足够的证据、边界、验证命令和人工升级路径，可以安全运行一次明确范围的 loop。

本文不是自动化授权。真正运行 loop 仍需要用户明确请求，并且需要先审查 `loop-blueprint.md`。

Readiness Status: not-ready | partial | ready
Last Reviewed:
Reviewer:
Scope:

## 必备条件

| 条件 | 状态 | 证据 | 缺口 |
| --- | --- | --- | --- |
| 有明确的 loop 目标 | unknown |  |  |
| 有状态文件 | unknown |  |  |
| 有验证命令 | unknown |  |  |
| 已定义允许修改路径 | unknown |  |  |
| 已定义禁止触碰路径 | unknown |  |  |
| 已定义停止条件 | unknown |  |  |
| 已定义人工升级路径 | unknown |  |  |
| 已定义 token 或范围预算 | unknown |  |  |
| 已定义理解复述检查 | unknown |  |  |
| 已定义工作日志或状态文件回写位置 | unknown |  |  |

## 安全门禁

| 区域 | 默认策略 | 项目决定 | 证据 |
| --- | --- | --- | --- |
| 业务文档 | 默认只读 |  |  |
| 密钥和凭据 | 禁止触碰 |  |  |
| 部署和发布动作 | 未明确确认前禁止 |  |  |
| CI 配置 | 未明确纳入范围前禁止 |  |  |
| 外部服务 | 未明确确认前禁止 |  |  |
| Git commit、tag、push | 未明确确认前禁止 |  |  |

## ForgeKit Loop 五要素

| loop 能力 | ForgeKit 证据 | 是否就绪 |
| --- | --- | --- |
| skill | `.agents/skills/`、`.codex/skills.md`、项目内 skill 说明 | unknown |
| memory | `.forgekit/docs/work-log.md`、`.forgekit/docs/*`、`.forgekit/changes/*` | unknown |
| validation | `.codex/commands.md`、`scripts/check-doc-sync.*`、`scripts/run-harness-check.ps1`、项目验证命令 | unknown |
| boundary | `.forgekit/project-boundary.yml`、`AGENTS.md`、`CLAUDE.md`、`.codex/rules.md` | unknown |
| reports | 归档、同步、smart archive、升级、审查和验证报告 | unknown |

## 已知缺口

自动 runner、worktree 编排、connector、MCP 集成、sub-agent 调度、自动 PR 或 issue 流程都只是未来路线图内容。当前项目模板不提供这些能力。

## 决定

Loop suitability: not-ready | partial | ready
Reason:
Required fixes before loop:
