Status: done
Risk: high
Created: 2026-07-11
Owner: ForgeKit maintainers
Reason: Make independent review converge around a frozen change contract.

# 变更提案

## 问题与目标

中高风险 change 虽已有 Maker/Checker 分离和范围约束，但缺少可复用的验收冻结、blocker 分类、限定复审和阶段授权语义。本变更扩展现有工件与协议，使实现前冻结、首审可发现真实错误、复审默认只闭合既有 blocker。

## 冻结范围

- 扩展现有 proposal、verification、review 模板。
- 扩展现有 Maker/Checker 协议、工程循环和 usage playbook。
- 在生成项目入口加入简短稳定规则，并保持相关入口可发现。
- 通过 ForgeKit 版本迁移安全下发到已有项目。

## 信任边界

- 防止正式入口违反冻结合同、执行未授权阶段、产生错误数据/训练/评估/checkpoint/artifact 状态或虚假成功。
- Reviewer 可审查真实正式路径与关键拒绝反例。
- 不要求抵抗有代码写权限的开发者主动 import 内部 helper，也不把本地科研/开发程序默认提升为多租户安全系统。

## 非目标

- 不新增权限、安全 token、Agent 框架、review runner 或并行协议。
- 不新增独立长期治理文档或强制 low-risk change 使用完整矩阵。
- 不禁止 Reviewer 报告新问题；只限制新问题自动成为 blocker 的条件。
- 不修改归档、capsule 或业务功能。

## 阶段授权

当前授权：implementation ready for review。

本 change 可准备代码、模板、迁移和验证证据；不自动授权 commit、push、向真实项目 apply 升级或任何项目的真实 smoke/full execution。

## 需要确认的决定

- 版本定为 0.44.0，表示生成项目治理合同和安全迁移能力发生功能变化。
- 已由用户明确要求在审查和冻结后实施；本提案按该授权进入 active。

## 0.44.0 发布前一致性审计

- 保持原 `forgekit-project.py --target <project-root>` 单命令交互入口；不新增入口或必填参数。
- 复审允许阻塞本轮修复新引入的冻结合同/真实错误回归；无关新建议仍为 follow-up。
- v0.43.2 AGENTS 已能路由到受管 Maker/Checker 协议；0.44.0 结果界面另提供精确人工合并片段，不自动覆盖根 AGENTS。
- cancel/abort 必须不修改 state、target、业务文件、真实 change 或 review report。
