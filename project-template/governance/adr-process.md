# ADR 流程

ADR 用于记录重要架构和技术决策。它回答：为什么当时这样选，替代方案是什么，代价是什么。

## 什么时候必须写 ADR

- 选择或更换技术栈。
- 引入新数据库、中间件、模型服务、硬件接口。
- 改变模块边界或核心架构。
- 改变 API 协议、鉴权方式、部署方式。
- 改变数据结构或数据语义。
- 进行大规模重构。
- 接手项目时决定保留或替换旧架构。
- 跳过版本闸门或接受明显技术债。

## 编号规则

```text
.forgekit/docs/adr/0001-use-spring-boot.md
.forgekit/docs/adr/0002-use-ollama-for-local-deepseek.md
.forgekit/docs/adr/0003-keep-legacy-api-compatible.md
```

规则：

- 四位递增编号。
- 文件名使用英文小写和连字符。
- 一个 ADR 只记录一个重要决策。
- 不删除历史 ADR；被替代时标记为 `Superseded`。

## 状态流转

```text
Proposed -> Accepted -> Superseded
                  \-> Deprecated
```

| 状态 | 含义 |
| --- | --- |
| Proposed | 正在讨论 |
| Accepted | 已采纳 |
| Superseded | 被后续 ADR 替代 |
| Deprecated | 不再推荐，但没有明确替代 |

## Codex 行为

- 遇到重要技术选择时，先建议创建 ADR。
- ADR 未确认前，不应直接执行不可逆架构改动。
- 修改已被 ADR 约束的实现时，先读取相关 ADR。
- 如果实现和 ADR 冲突，提醒用户确认是否新增 ADR 或更新状态。

## 关联关系

ADR 应尽量关联：

- 需求编号：`REQ-001`
- 版本：`v0.1.0`
- RFC：`RFC-001`
- 任务：`TASK-001`
- 测试：`TEST-001`
