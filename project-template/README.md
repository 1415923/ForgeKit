# 项目模板

把本目录内容复制到具体项目根目录后使用。

## 初始化顺序

1. 读取 `governance/流程总览.md`，判断项目入口。
2. 填写 `.codex/project.md`，明确项目基本信息。
3. 填写 `.codex/scope.md`，明确当前版本范围。
4. 填写 `.codex/commands.md`，记录本项目常用命令。
5. 如果已有问答内容，优先使用 `project-bootstrap-fill` 根据 `.codex/questionnaires/项目初始化问答.md` 补齐第一版文档。
6. 新项目填写 `docs/项目开发方案.md` 和 `docs/版本路线图.md`。
7. 接手项目填写 `docs/既有项目接手审计.md` 和 `docs/缺陷修复计划.md`。
8. 重要方案讨论写入 `docs/rfc/`，重要架构决策写入 `docs/adr/`。
9. 需求、RFC、ADR、任务、测试、缺陷关系写入 `docs/追踪矩阵.md`。
10. 高风险写入 `docs/风险登记册.md`。
11. 高影响变更写入 `docs/变更影响评估.md`。
12. 严重事故或重复缺陷写入 `docs/事故复盘.md` 或 `docs/缺陷复盘.md`。
13. 安全敏感变更写入 `docs/安全威胁建模.md`，依赖变更写入 `docs/依赖安全审查.md`。
14. 环境和发布链路写入 `docs/环境矩阵.md` 和 `docs/发布流水线.md`。
15. 模块负责人和评审责任写入 `docs/代码所有权.md`。
16. Epic、Feature、Task、Bug 写入 `docs/项目任务看板.md`。
17. 技术债写入 `docs/技术债记录.md`，版本质量写入 `docs/质量指标记录.md`。
18. 开始编码前，确认 Definition of Ready；完成时确认 Definition of Done。

## 可选增强

- `.agents/skills/`：项目级 skills，内置项目初始化、代码审查、发布检查和安全审查。
- `.codex/agents/`：多 agent 角色设计，默认不启用。
- `.codex/config.example.toml`：Codex 配置示例，默认不覆盖用户配置。

## 项目级规则边界

这里的规则只描述当前项目，不记录用户电脑上的固定路径和个人权限偏好。

## 接手既有项目

如果不是新项目，而是接手已有项目，应先使用 `.agents/skills/handover-review/`：

1. 完成 `docs/既有项目接手审计.md`。
2. 完成 `docs/缺陷修复计划.md`。
3. 先修复 P0/P1 问题，不默认改变大架构。
4. 记录兼容边界。
5. 再基于当前技术栈、实际需求和版本闸门规划后续开发。

## 治理层

- `governance/sdlc.md`：通用 SDLC。
- `governance/architecture-governance.md`：arc42 轻量映射和 ADR 规则。
- `governance/rfc-process.md`：RFC / Design Proposal 流程。
- `governance/adr-process.md`：ADR 流程。
- `governance/traceability.md`：追踪编号体系。
- `governance/definition-of-ready.md`：进入开发前检查。
- `governance/definition-of-done.md`：完成标准。
- `governance/risk-management.md`：风险管理流程。
- `governance/change-management.md`：变更管理流程。
- `governance/incident-process.md`：事故 / 缺陷复盘流程。
- `governance/security-governance.md`：威胁建模、依赖审查和安全发布闸门。
- `governance/cicd-environment-governance.md`：环境矩阵、发布流水线和回滚治理。
- `governance/code-ownership-review-governance.md`：代码所有权、必要评审人和 Critical 区域规则。
- `governance/project-management-task-model.md`：Epic、Feature、Task、Bug 状态流和版本映射。
- `governance/project-bootstrap-fill.md`：初始化问答到第一版项目文档的填充映射。
- `governance/version-governance.md`：版本路线图和推进闸门。
- `governance/quality-metrics.md`：DORA 风格轻量质量指标。
- `governance/technical-debt-management.md`：技术债管理流程。
