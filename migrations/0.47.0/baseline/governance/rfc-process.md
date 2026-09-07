# RFC / Design Proposal 流程

RFC 用于决策前的方案讨论。ADR 用于决策后的记录。

## 什么时候写 RFC

- 新项目核心方案还不明确。
- 大功能有多个实现路线。
- 技术栈选择存在争议。
- 接手项目需要决定保守修复还是重构。
- 变更会影响上下游、部署、数据库或权限。
- 需要人工评审后才能动手。

## RFC 与 ADR 的关系

```text
RFC: 讨论候选方案、风险、开放问题
ADR: 记录最终决策、后果、状态
```

一个 RFC 可以产生 0 个、1 个或多个 ADR。

## 编号规则

```text
.forgekit/docs/rfc/0001-project-architecture-options.md
.forgekit/docs/rfc/0002-auth-model-redesign.md
```

## 状态

| 状态 | 含义 |
| --- | --- |
| Draft | 草稿 |
| In Review | 正在评审 |
| Accepted | 已接受 |
| Rejected | 已拒绝 |
| Superseded | 被替代 |

## Codex 行为

- 遇到方向不清、方案不唯一的问题，先生成 RFC，而不是直接编码。
- RFC 中必须列备选方案和推荐方案。
- RFC 未确认前，不做不可逆实现。
- RFC 被接受后，如涉及重要架构决策，创建或更新 ADR。
