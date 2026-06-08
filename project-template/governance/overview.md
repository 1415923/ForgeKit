# 流程总览

本目录定义项目治理层。它借鉴成熟 SDLC、arc42、ADR、DORA、版本治理和既有项目接手流程，但做了 Codex 友好的裁剪。

## 四层结构

```text
1. SDLC 通用治理
   需求 -> 方案 -> 架构 -> 实现 -> 测试 -> 发布 -> 运营反馈

2. 架构治理
   arc42 轻量架构文档 + RFC + ADR 决策记录 + 质量属性 + 风险

3. 版本治理
   版本路线图 + Ready/Done + 发布检查 + review/refactor 中版本 + 推进闸门

4. 接手项目治理
   现状审计 + 兼容边界 + P0/P1 修复 + 风险登记 + 后续路线图
```

## 入口选择

| 场景 | 首选入口 | 核心产物 |
| --- | --- | --- |
| 新项目 | `project-init` | 项目开发方案、版本路线图、架构设计、ADR |
| 接手既有项目 | `handover-review` | 接手审计、缺陷修复计划、兼容边界、版本路线图 |
| 纯 Bug 修复 | `code-review` + `handover-review` | 缺陷修复计划、回归测试、版本记录 |
| 大功能开发 | `project-init` 或相关技术栈规则 | 需求、方案、ADR、测试计划 |
| 发布 | `release-check` | 发布检查、版本闸门、变更记录 |
| 安全敏感变更 | `security-review` | 安全 findings、修复项、用户确认项 |

## 通用闸门

无论什么入口，都必须遵守：

- 没有明确范围，不进入大规模编码。
- 没有技术栈和落地条件结论，不做关键架构实现。
- 影响架构的决策必须写 ADR。
- 决策前方案不清楚时先写 RFC。
- 需求、决策、任务、测试、缺陷要能追踪。
- 不满足 Definition of Ready 不进入开发。
- 不满足 Definition of Done 不宣称完成。
- 高影响变更必须做变更影响评估。
- 高风险必须进入风险登记册。
- 技术债必须进入技术债记录。
- 版本质量变化必须进入质量指标记录。
- 严重事故和重复缺陷必须复盘。
- 安全敏感变更必须进入安全治理。
- 发布、部署和环境变更必须进入 CI/CD 与环境治理。
- Critical 或 Unknown 代码区域变更必须进入代码所有权和评审责任治理。
- 大功能、缺陷和重构必须进入项目管理任务模型。
- 大版本结束后，必须做 review/refactor 中版本。
- 接手项目先审计和修 P0/P1，不默认改大架构。
- 跳过闸门必须人工明确确认。

## 推荐阅读顺序

新项目：

1. `governance/sdlc.md`
2. `docs/project-plan.md`
3. `docs/version-roadmap.md`
4. `governance/architecture-governance.md`
5. 相关 `templates/<stack>/`

接手既有项目：

1. `.codex/handover.md`
2. `docs/handover-audit.md`
3. `docs/defect-fix-plan.md`
4. `docs/version-roadmap.md`
5. `governance/version-governance.md`
