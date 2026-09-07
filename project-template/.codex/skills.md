# ForgeKit Skills

七个主要能力按任务选用，不组成固定流水线。

| Skill | 用途 |
| --- | --- |
| project-init | 通过统一入口初始化 |
| document-backfill | 初始化填充或既有事实回填，按显式请求使用 |
| project-assessment | 采用适用性评估或接手审计，选择一个分支 |
| large-change-planning | 按真实影响规划高影响变更 |
| code-review | 只读代码审查和定向复查 |
| security-review | 只读安全边界审查 |
| release-check | 明确发布候选的就绪检查 |

旧名称 project-bootstrap-fill、handover-review、project-suitability 在 0.47.x 保留为显式兼容入口。
Skills 正文和 references 由根级 skills/ 维护，project-template/.agents/skills/ 是确定性投影；Claude 适配保留平台调用方式。
用户授权和系统约束优先于 Skill 指导。只加载选中分支，不扫描整个文档集。
