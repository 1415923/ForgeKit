# 第一性原理与对抗式审查协议

## Purpose

本协议用于复杂问题的根因推导和高风险变更的失败路径审查。第一性原理回答“为什么这样做”，对抗式审查回答“这样做会怎么坏”。它们按风险触发，不替代独立代码审查，也不要求每个小改动执行。

## First-Principles Pass

先区分已确认事实和假设，再从目标与约束推导最小正确机制。不要因为现有代码或常见模式存在，就默认它们是正确起点。

固定输出：

1. **Problem / Goal**：真正要解决的问题和可观察目标。
2. **Known Facts**：已有证据支持的事实及证据路径。
3. **Assumptions**：尚未验证的推测。
4. **Constraints**：工程、时间、兼容、安全和组织约束。
5. **First-Principles Derivation**：不照搬现有实现时，最小正确机制如何成立。
6. **Surface Fix vs Root Fix**：候选方案是表层修补还是根因修复，依据是什么。
7. **Minimal Verifiable Outcome**：最小可验证结果及验证方式。
8. **Recommended Next Step**：下一步动作和理由。

### Trigger Rules

必须触发：

- 用户明确要求“从第一性原理出发”；
- Bug 根因不清、同一问题反复修补，或用户质疑是否治标不治本；
- 架构、数据流、权限、安全、迁移、升级或性能瓶颈设计。

建议在高风险 proposal/design 前、reviewer 发现系统性风险后、bounded-auto 进入高风险阶段前触发。拼写、格式、小文档修正和明确的低风险局部修改不触发。

## Adversarial Review Pass

从恶意用户、异常数据、未来维护者和生产事故视角寻找失败路径。每条 finding 必须包含：

- **Failure Scenario**
- **Entry Point**
- **Trigger Condition**
- **Expected Failure**
- **Evidence / Reproduction**
- **Severity**
- **Fix Recommendation**
- **Verification Needed**
- **TODO_REVIEW**（不确定时）

覆盖维度按任务选择，不做机械全量清单：correctness、edge cases、reliability、security、performance、data integrity、operations、documentation drift。

归档或维护场景额外检查：active task source loss、task-board 与 task-intake 断链、风险只留在 archive、traceability 退化为占位、testing baseline 丢失，以及 archive 被误写成 completed phase close。

### Trigger Rules

必须触发：

- 用户明确要求“对抗式审查”；
- 高风险 change 在 handoff、commit 或 tag 前；
- 权限、安全、数据迁移、导出、支付、队列、定时任务、部署、批处理或清理脚本发生变化；
- independent reviewer 给出 `needs-fix`、`manual-review` 或 blocking finding；
- 生产事故或重大 Bug 修复后。

建议在 bounded-auto 收口、release-check 前，以及包含高风险变更的 archive capsule 前触发。低风险文案、注释和 typo 不触发。

## Output Contracts

- 推导必须标记事实、假设和证据，未经验证的结论不能写成事实。
- 高严重级别 finding 默认进入 `needs-fix` 或 `manual-review`，不得静默通过。
- reviewer 不直接修代码；修复交回 maker，随后重新验证和审查。

## Writeback Rules

常驻 managed docs 只写稳定结论、证据路径和 `TODO_REVIEW`。完整过程放入当前 change 的 design/review/verification、handoff 或临时报告；开放风险写入 risk-register。不要把长推理或完整审查日志复制到多个文档。

## Relationship to Independent Code Review

v0.37 independent review 负责上下文隔离和 gate。First-Principles Pass 补充根因与机制推导，Adversarial Review Pass 补充失败路径。自审仍不能替代 independent review；reviewer 不可用时必须 `manual-review`。

## Relationship to Context Continuity

关键设计推导、blocking finding、失败路径和验证要求属于 Critical Facts。checkpoint 只保存摘要、证据位置、决策和待确认项，不保存完整会话或长日志。

## Examples

- “从第一性原理出发，重新分析这个 Bug 的根因。”先执行 First-Principles Pass，再决定是否修改。
- “从第一性原理检查归档是否合理。”先检查 `current-docs-integrity.md` 的 current docs invariants，再判断归档是历史移出还是破坏当前工作状态。
- “对这个导出功能做一次对抗式审查。”按输入、权限、资源、数据完整性和运维失败路径输出 findings，不自动修复。

## Boundaries

本协议不是哲学说明、自动 runner、无限 agent 授权或自动修复器。它不修改 business docs，不自动 commit/push/PR，也不把未经验证的推导升级为项目事实。
