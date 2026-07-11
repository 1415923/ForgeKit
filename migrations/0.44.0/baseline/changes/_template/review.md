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
ReviewedRange:
DiffReviewed: yes | no
ValidationReviewed: yes | no
DocsReviewed: yes | no
RisksReviewed: yes | no
Findings:
RequiredFixes:
VerificationGaps:
TODO_REVIEW:
FinalRecommendation:

`self-review` 不能满足 mandatory independent review。reviewer agent 不可用或独立执行无法确认时，使用 `manual-review`，不得写 `pass`。

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
