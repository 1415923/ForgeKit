# 质量指标

本文件借鉴 DORA 和工程质量治理思想，定义轻量质量指标。

## 交付指标

| 指标 | 含义 | 记录方式 |
| --- | --- | --- |
| 变更前置时间 | 从开始开发到可交付的时间 | 版本记录或任务记录 |
| 变更失败率 | 发布后导致回滚、热修、严重 bug 的比例 | 版本记录 |
| 恢复时间 | 从故障发现到恢复的时间 | 事故或缺陷记录 |
| 发布频率 | 多久能稳定发布一次 | 版本记录 |
| 严重事故数量 | SEV-1 / SEV-2 数量 | 事故复盘 |
| 缺陷复发率 | 同类缺陷重复出现情况 | 缺陷复盘 |

## 代码质量指标

| 指标 | 检查方式 |
| --- | --- |
| 重复逻辑 | review/refactor 中版本检查 |
| 文件增长 | 版本 diff 和目录审查 |
| 测试覆盖核心路径 | 测试文档和验证记录 |
| 架构决策可追溯 | ADR |
| 文档同步 | 发布检查 |

## 使用原则

- 指标用于发现问题，不用于形式主义打分。
- 小项目可以只记录结论。
- 接手项目先记录基线，再逐步改善。
- 指标异常时，优先安排 review/refactor 中版本。

## 记录位置

- 质量指标记录在 `.forgekit/docs/quality-metrics.md`。
- 技术债记录在 `.forgekit/docs/technical-debt.md`。
- 高风险技术债应同步到 `.forgekit/docs/risk-register.md`。
- 版本 review/refactor 结论应同步到 `.forgekit/docs/version-roadmap.md`。
- 严重事故和重复缺陷应同步到 `.forgekit/docs/incident-review.md` 或 `.forgekit/docs/defect-review.md`。
