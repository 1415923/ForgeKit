# Codex 多 Agent 角色

本目录用于记录项目可选的多 agent 角色设计。

默认不自动运行多 agent。只有当项目复杂度较高，且任务可以安全拆分时，再按当前 Codex 版本显式调用。

## 推荐角色

| 角色 | 职责 | 权限边界 |
| --- | --- | --- |
| forgekit-planner | 只读澄清范围、风险、边界和验证建议 | 不修改文件 |
| forgekit-reviewer | 只读审查 diff、验证证据、文档同步和风险 | 不修改文件，输出 findings |
| forgekit-verifier | 运行用户确认的低风险验证命令并报告结果 | 不改业务代码，不读取敏感信息 |

## 使用原则

- 只有独立、可并行、边界清晰的任务才适合交给 agent。
- 不把紧急阻塞任务交给后台 agent。
- 多个 agent 的写入范围必须互不重叠。
- planner / reviewer 默认只读，避免边审查边改动导致责任不清。
- 生成配置不等于 runtime 已注册。先运行 `python scripts/check-codex-native-agents.py --repo-root .` 做静态检查，再观察 Codex 是否真的调用 `forgekit-*`。
- 如果 Codex 只显示 default、explorer 或 worker，记录 `native_agent_status: unavailable`，不得称为 native 成功。

## 角色模板

```toml
name = "forgekit-planner"
description = "Read-only ForgeKit planner."
developer_instructions = """
Act as a read-only planner. Do not edit files, start services, commit, push, or read secrets.
"""
sandbox_mode = "read-only"
```
