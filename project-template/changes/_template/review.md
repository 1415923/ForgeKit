# 复查

## Maker 摘要

MakerStatus: ready-for-check | blocked | partial
FilesChanged:
ImplementationSummary:
ValidationRun:
KnownRisks:
NotVerified:

## Checker 复查

CheckerStatus: pass | needs-fix | manual-review | not-run
ReviewDecision: pass | needs-fix | manual-review
ReviewType: independent | self-review
ReviewerAgent:
ReviewMode: initial | blocker-recheck
ReviewedRange:
FrozenAcceptanceIDs:
AuthorizedStage:
DiffReviewed: yes | no
ValidationReviewed: yes | no
DocsReviewed: yes | no
RisksReviewed: yes | no
Findings:

```text
- impact_severity: CRITICAL | MAJOR | MINOR | NOTE
  blocking: YES | NO
  primary_consequence: C1 | C2 | C3 | C4
  secondary_consequences:
  failure_path:
  blocked_scope:
  validation_relevance:
  evidence:
```

`primary_consequence`、`failure_path`、`blocked_scope` 仅在 `blocking: YES` 时必填；每个 Blocking finding 只有一个 PrimaryConsequence。Impact Severity 不推导 Blocking。

BlockingFindings:
FollowUps:
RequiredFixes:
VerificationGaps:
TODO_REVIEW:
FinalRecommendation:

`initial` 首审可发现冻结合同违例及会造成真实错误的 Critical consequence。`blocker-recheck` 默认只复核上一轮 blocking findings，并逐项标记 `Closed`、`Partially closed` 或 `Still open`。本轮修复新引入且违反冻结合同或会造成真实错误的回归可以继续阻塞；与修复无关的新建议只能记为 follow-up。不得重新进行开放式架构审查或扩大 trust boundary。

`pass` 只授权 `AuthorizedStage` 对应的下一步，不自动授权 commit、真实 smoke 或完整执行。

当用户、frozen contract 或真实 C1-C4 consequence 已要求 independent review 时，`self-review` 不能满足该 gate。reviewer agent 不可用或独立执行无法确认时，使用 `manual-review`，不得写 `pass`。

## 自查

- 改了什么？
- 为什么本次变更仍限制在预期范围内？

## 剩余风险

- 已知取舍、边界情况或后续工作。

## 文档同步

- 当前态文档、changelog、任务看板或 change 工件是否已更新。
- 属于 `.forgekit/docs/` 的稳定结论，不应只留在本 change folder 中。

## 当前态文档同步元信息

CurrentDocsSync: confirmed | not-needed | missing | unknown
ChangelogUpdated: yes | no | not-needed | unknown
ArchitectureUpdated: yes | no | not-needed | unknown
TestingUpdated: yes | no | not-needed | unknown
RequirementsUpdated: yes | no | not-needed | unknown
