# 追踪编号体系

本文件定义需求、设计、决策、任务、测试、缺陷、版本之间的追踪关系。

## 编号类型

| 类型 | 前缀 | 示例 | 说明 |
| --- | --- | --- | --- |
| 需求 | `REQ` | `REQ-001` | 功能或非功能需求 |
| Epic | `EPIC` | `EPIC-001` | 阶段目标或业务主题 |
| Feature | `FEAT` | `FEAT-001` | 可验收能力 |
| RFC | `RFC` | `RFC-001` | 决策前的设计提案 |
| ADR | `ADR` | `ADR-001` | 最终架构或技术决策 |
| 任务 | `TASK` | `TASK-001` | 可执行开发任务 |
| 测试 | `TEST` | `TEST-001` | 测试用例或验证项 |
| 缺陷 | `BUG` | `BUG-001` | 缺陷修复项 |
| 风险 | `RISK` | `RISK-001` | 风险登记项 |
| 技术债 | `DEBT` | `DEBT-001` | 延后处理的质量或架构问题 |

## 关联规则

推荐链路：

```text
EPIC -> FEAT -> REQ -> RFC -> ADR -> TASK -> TEST -> VERSION
BUG -> TASK -> TEST -> VERSION
RISK -> RFC/ADR/TASK
DEBT -> review/refactor version
```

## 文档填写要求

- 新需求应有 `REQ-*`。
- 阶段目标应有 `EPIC-*`。
- 可验收能力应有 `FEAT-*`。
- 重要方案讨论应有 `RFC-*`。
- 重要技术决策应有 `ADR-*`。
- 开发任务应关联 Feature、需求、缺陷或技术债。
- Bug 修复应关联测试或验证方式。
- 版本记录应列出主要 REQ、BUG、ADR、DEBT。

## Codex 行为

- 新增需求、缺陷、ADR、RFC 时，建议分配编号。
- 无法确定编号时，先使用 `待编号`，并提醒用户整理。
- 做版本总结时，按编号汇总变更。
