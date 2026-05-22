# Codex 多 Agent 角色

本目录用于记录项目可选的多 agent 角色设计。

默认不启用多 agent。只有当项目复杂度较高，且任务可以安全拆分时，再在 `.codex/config.example.toml` 的基础上启用。

## 推荐角色

| 角色 | 职责 | 权限边界 |
| --- | --- | --- |
| explorer | 只读分析代码、文档、配置 | 不修改文件 |
| reviewer | 审查改动、查找 bug、安全风险、测试缺口 | 不修改文件，输出 findings |
| docs-researcher | 查询官方文档、版本变化、API 行为 | 网络只读 |
| build-resolver | 分析构建、测试、类型错误 | 修改范围限于错误相关文件 |

## 使用原则

- 只有独立、可并行、边界清晰的任务才适合交给 agent。
- 不把紧急阻塞任务交给后台 agent。
- 多个 agent 的写入范围必须互不重叠。
- reviewer 默认只读，避免边审查边改动导致责任不清。

## 角色模板

```toml
[agent]
name = "explorer"
description = "Read-only codebase analysis"
model = "gpt-5.4"

[permissions]
read = true
write = false
network = false
```
