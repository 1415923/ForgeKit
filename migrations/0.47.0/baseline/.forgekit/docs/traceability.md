# 追踪矩阵

用于记录需求、设计、决策、任务、测试、缺陷、版本之间的关系。

## 总表

| ID | 类型 | 标题 | 关联 ID | 版本 | 状态 |
| --- | --- | --- | --- | --- | --- |
| EPIC-001 | Epic | 待补充 | FEAT-001 | v0.1.x | Backlog |
| FEAT-001 | Feature | 待补充 | EPIC-001, REQ-001, TASK-001 | v0.1.0 | Backlog |
| REQ-001 | 需求 | 待补充 | RFC-001, TEST-001 | v0.1.0 | Draft |
| RFC-001 | RFC | 待补充 | ADR-001, REQ-001 | v0.1.0 | Draft |
| ADR-001 | ADR | 待补充 | RFC-001 | v0.1.0 | Proposed |
| TASK-001 | 任务 | 待补充 | REQ-001 | v0.1.0 | Todo |
| TEST-001 | 测试 | 待补充 | REQ-001, BUG-001 | v0.1.0 | Todo |
| BUG-001 | 缺陷 | 待补充 | TEST-001 | v0.1.0 | Open |

## 状态建议

| 类型 | 状态 |
| --- | --- |
| Epic | Backlog / Ready / In Progress / Done / Dropped |
| Feature | Backlog / Ready / In Progress / Review / Done / Dropped |
| 需求 | Draft / Ready / In Progress / Done / Dropped |
| RFC | Draft / In Review / Accepted / Rejected / Superseded |
| ADR | Proposed / Accepted / Superseded / Deprecated |
| 任务 | Todo / In Progress / Review / Done |
| 测试 | Todo / Passing / Failing / Waived |
| 缺陷 | Open / Fixing / Fixed / Won't Fix |
