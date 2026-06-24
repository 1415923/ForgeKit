# 文档生命周期

ForgeKit 把项目文档分成当前事实、变更过程记录和历史归档，避免把“现在是什么”和“以前怎么讨论”混在一起。

核心规则：

```text
current docs say what is true now.
changes explain why and how one change happened.
archive preserves history without becoming current truth.
```

中文理解：

- 当前态文档只写现在仍然成立的事实。
- change 文档解释一次变更为什么发生、怎么执行、怎么验证。
- archive 保存历史，但默认不再作为当前事实来源。

## 文档层级

| 层级 | 默认路径 | 用途 | 默认读取 |
| --- | --- | --- | --- |
| current state docs | `.forgekit/docs/` | 当前项目事实、需求、架构、验证方式和发布状态 | 是，但只读任务相关文件 |
| change process docs | `.forgekit/changes/<change-id>/` | 单次中高风险变更的可审查工件 | 只在和当前任务相关时读取 |
| archive docs | `.forgekit/archive/` | 已关闭变更、旧发布材料、复盘和审计证据 | 默认不读，除非历史明确相关 |

## 当前态文档

当前态文档保留稳定事实，不保存长过程流水。

| 文档 | 写什么 | 不写什么 |
| --- | --- | --- |
| `project-plan.md` | 当前用户、产品形态、范围、非目标、落地条件和路线 | 讨论流水、已废弃方案细节、历史争论 |
| `architecture.md` | 当前架构、模块职责、数据流、API 边界和约束 | 每次架构变化过程或旧架构长历史 |
| `requirements.md` | 当前需求、验收标准、优先级和范围边界 | 已废弃需求的完整讨论过程 |
| `testing.md` | 当前验证命令、测试范围、测试策略和已知缺口 | 单次测试运行日志或临时失败流水 |
| `changelog.md` | 用户可见变化、兼容性、迁移提示、发布摘要 | 内部实现流水、所有任务细节、长 review 记录 |

短的稳定原因可以用 `Reason:` 留在当前态文档里。长过程历史应放到对应 change 或 archive。

## 变更过程

变更过程文档位于 `.forgekit/changes/<change-id>/`。

`proposal.md` 负责生命周期元信息：

```text
Status: draft | active | done | archived
Risk: low | medium | high
Created: YYYY-MM-DD
Owner: <name>
Reason: <short reason>
```

Status 含义：

| Status | 含义 |
| --- | --- |
| `draft` | 正在讨论，尚未确认实施。 |
| `active` | 已确认并正在执行。 |
| `done` | 已实现并验证，稳定结论已同步回当前态文档，但短期仍留在 active change 区方便复查。 |
| `archived` | 历史材料；默认 agent 不应把它当作活跃上下文。 |

中高风险变更完成后，应把稳定结论同步回当前态文档：

| 稳定结论 | 同步到 |
| --- | --- |
| 产品范围或非目标变化 | `.forgekit/docs/project-plan.md` |
| 架构、模块、接口或数据流变化 | `.forgekit/docs/architecture.md` |
| 需求和验收变化 | `.forgekit/docs/requirements.md` |
| 验证命令或测试策略变化 | `.forgekit/docs/testing.md` |
| 用户可见行为、兼容性或迁移变化 | `.forgekit/docs/changelog.md` |
| 风险、债务或事故 | 对应 risk、debt 或 incident 文档 |

## 归档

归档文档位于 `.forgekit/archive/`。

Archive 不是当前态事实来源。默认不要读取 archive；只有用户要求历史、审计、回归分析、事故复盘、历史决策解释或旧版本对比时才读取。

## 归档计划 dry-run

`scripts/archive-changes.py --dry-run` 可以为已完成 change 生成 `.forgekit/archive-plan.md`。

dry-run 只创建或覆盖 `.forgekit/archive-plan.md`。它不移动文件、不修改 proposal 状态、不重写链接、不更新当前态文档、不写业务文档、不更新 template-lock、不 commit、不 push。

归档计划会列出 candidates、blocked changes 和 skipped changes。`Status: archived` 的 change 会作为 skipped 列出，原因是 `already archived by status`。

`Current docs sync: not verified by script` 表示脚本没有确认稳定结论是否已经同步回当前态文档；未来执行 apply 前仍需人工确认。

v0.18 和 v0.19 不自动移动文件。旧材料如果重新变成当前事实，必须把稳定结论同步回当前态文档，而不是只链接 archive。

## 归档 apply

`scripts/archive-changes.py --apply --plan .forgekit/archive-plan.md --confirm` 可以把已审查的 candidates 从 `.forgekit/changes/<change-id>/` 移动到 `.forgekit/archive/changes/YYYY/<change-id>/`。

Apply 必须显式传入 `--confirm`，并要求 Git 工作区干净；唯一允许未提交的是指定的 `.forgekit/archive-plan.md`。它只读取 dry-run 计划里的 `Archive-Status: candidate` 条目。

Apply 不处理 blocked 或 skipped 条目，不重写链接，不更新当前态文档，不写业务文档，不更新 template-lock，不 commit、tag 或 push。

移动 candidate 后，apply 最多只把归档后副本里的 `proposal.md` 从 `Status: done` 改成 `Status: archived`。如果归档后 proposal 状态不是 `done`，apply report 只记录 warning，不猜测修改。

## 归档引用检查

`scripts/archive-changes.py --reference-check --plan .forgekit/archive-plan.md` 可以生成 `.forgekit/archive-reference-report.md`。

引用检查只读取 `.forgekit/archive-plan.md` 里的 `Archive-Status: candidate` 条目。它只做字符串匹配，不判断引用是否有害。

## 当前态文档同步检查

`scripts/archive-changes.py --sync-check --plan .forgekit/archive-plan.md` 可以生成 `.forgekit/current-docs-sync-report.md`。

同步检查只读取 `.forgekit/archive-plan.md` 里的 `Archive-Status: candidate` 条目，并检查每个 candidate 的 `review.md` 结构化元信息。它不做语义验证，不修改 `.forgekit/docs/**`，不写业务文档，不更新 template-lock，不重写 archive-plan，不移动文件。

核心字段是 `CurrentDocsSync: confirmed | not-needed | missing | unknown`。`ChangelogUpdated` 为 `no`、`unknown` 或缺失时产生 warning。`ArchitectureUpdated`、`TestingUpdated`、`RequirementsUpdated` 只是辅助证据。

## Smart Archive Advisor

`scripts/archive-changes.py --smart-check --plan .forgekit/archive-plan.md --reference-report .forgekit/archive-reference-report.md --sync-report .forgekit/current-docs-sync-report.md` 可以生成 `.forgekit/smart-archive-report.md`。

Smart check 只综合 archive plan、reference report 和 sync report 中的机器可读字段。它不把 archive 当当前事实，不做 AI 语义判断，不移动文件，不改 proposal 状态，不重写链接，不修改当前态文档，不写业务文档，不更新 template-lock，不 commit、不 push。

它检查 `.forgekit/docs/**`、draft/active/missing/unknown changes 和入口文档（`README.md`、`AGENTS.md`、`CLAUDE.md`）。它跳过 archive、upgrade-export、报告文件、模板和 candidate 自己的源目录。

报告每次运行都会重新生成。它不移动文件、不重写链接、不更新当前态文档、不写业务文档、不更新 template-lock、不 commit、tag 或 push。
