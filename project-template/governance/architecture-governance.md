# 架构治理

本文件借鉴 arc42 和 ADR 思路，但保持轻量。

## 架构治理产物

| 产物 | 作用 |
| --- | --- |
| `docs/项目开发方案.md` | 定义问题、约束、落地条件、技术路线 |
| `docs/架构设计.md` | 定义模块、数据流、接口边界、风险 |
| `docs/技术选型.md` | 定义技术栈选择和替代方案 |
| `docs/rfc/` | 记录决策前的方案讨论 |
| `docs/adr/` | 记录重要架构决策 |

## 什么时候必须写 ADR

- 选择或更换技术栈。
- 改变模块边界。
- 改变数据库结构或数据语义。
- 改变接口协议。
- 引入新中间件、模型服务、硬件接口。
- 改变部署方式。
- 做大规模重构。
- 接手项目时决定是否保留旧架构。

## 轻量 arc42 映射

| arc42 关注点 | 本模板落点 |
| --- | --- |
| Introduction and Goals | `docs/项目开发方案.md` |
| Constraints | `docs/项目开发方案.md`、`.codex/scope.md` |
| Context and Scope | `docs/架构设计.md` |
| Solution Strategy | `docs/项目开发方案.md` |
| Building Block View | `docs/架构设计.md` |
| Runtime View | `docs/架构设计.md` |
| Deployment View | `docs/部署文档.md` |
| Architecture Decisions | `docs/adr/` |
| Quality Requirements | `governance/quality-metrics.md` |
| Risks and Technical Debt | `docs/项目开发方案.md`、`docs/版本路线图.md` |

## 架构 Review 问题

- 当前结构是否服务长期目标？
- 是否需要先写 RFC？
- 新文件和新模块是否真的必要？
- 相似逻辑是否可以复用？
- 上下游接口是否保持兼容？
- 是否有无法回滚的设计？
- 是否需要 ADR？
- 是否需要更新风险登记册？
- 是否应该推迟到 review/refactor 中版本？
