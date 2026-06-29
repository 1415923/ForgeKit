# Changelog

本文件记录 ForgeKit 的用户可感知变化。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)；版本号遵循语义化版本风格。README 只保留当前定位、快速开始和常用入口，完整版本历史放在这里维护。

## [Unreleased]

### Added

- 暂无。

### Changed

- 暂无。

### Fixed

- 暂无。

## [0.37.0]

### Added

- 新增 Independent Code Review Protocol。
- 新增独立只读 code reviewer。
- 新增 request / review skills。
- 新增最小上下文包，用于向独立 reviewer 传递任务摘要、diff/stat、changed files、验证输出和已知风险。
- 新增 `pass` / `needs-fix` / `manual-review` review gate。

### Changed

- 明确 self-review 不能冒充 independent review。
- reviewer 不可用时必须记录为 `manual-review`，而不是伪造通过。

## [0.36.0]

### Added

- 新增 Versioned Migration Upgrade Model。
- 新增 `.forgekit/state.json` 驱动的新项目升级模型。
- 新增 `forgekit-upgrade.py check` / `plan` / `apply --safe` 三步升级流程。

### Changed

- v0.36.0 及以后初始化的新项目使用 state + migrations 进行安全升级。
- v0.35.x 及更早项目不再视为可自动升级项目，而是按既有项目 adoption 流程处理。
- 明确 `apply --safe` 只执行 migration 中标记为 safe 的动作，不做三方 merge、不改 business docs、不自动提交。

## [0.35.2]

### Changed

- 新增 Managed Docs Writeback Policy。
- 区分业务实现范围与 ForgeKit 治理写回范围。
- 恢复任务完成后的最小治理写回：`work-log.md`、状态确实变化的 `task-board.md`、用户/版本可见变化的 `changelog.md` 和当前 change artifacts。
- 明确用户只有显式禁止文档写入时，才关闭治理写回。
- 保持 `review-only` 与 report-only 工具的不写入、不自动修复边界。

## [0.35.1]

### Fixed

- 修复 Codex custom agent TOML schema 问题。
- 确保 `name`、`description`、`developer_instructions` 均为字符串，避免 table/map schema 报错。

## [0.35.0]

### Added

- 新增 Review-Ready Handoff Package。
- 新增 report-only 交付包，用于汇总来源、需求、任务、变更、验证、风险和 `TODO_REVIEW`。

### Changed

- 明确 handoff package 不自动修复、不提交、不创建 PR。

## [0.34.0]

### Added

- 新增 Source Trace Report v2。
- 新增 report-only 来源追溯报告，用于检查 `Source ID -> requirement -> task -> change -> verification -> work-log/changelog` 链路断点。

### Changed

- 明确来源追溯报告只报告问题，不自动补链或修复文档。

## [0.33.0]

### Added

- 新增 Doc Health Report v2。
- 新增 report-only managed-docs 健康汇总，用于检查文档过长、重复事实、职责错位和 workflow-router 边界风险。

### Changed

- 明确文档健康报告只报告问题，不自动修复。

## [0.32.0]

### Added

- 新增 `.forgekit/docs/workflow-router.md`。
- 新增用户意图路由机制，用于把请求路由到正确的 Read / Write / Do Not Write 文档。

### Changed

- 减少 AI 默认全量读取 docs 的倾向。
- 减少同一事实在多个 managed docs 中重复写入的问题。

## [0.31.0]

### Added

- 新增 Bounded Auto Loop Policy。
- 新增 `one-step`、`bounded-auto`、`review-only` 三种授权边界。
- 新增 scope、stages、budget、stop conditions、agent mode gate 和 handoff 规则。

### Changed

- 明确 ForgeKit 不提供 runner、daemon、scheduler、自动 PR 或 worktree 编排。

## [0.30.1]

### Changed

- 强化 Native Agent Adapter Verification。
- 明确 generated config 不等于 runtime registered。
- 新增 native / fallback / simulated 状态字段和验证清单。

## [0.30.0]

### Added

- 新增 Native Agent Adapter。
- 支持将 ForgeKit loop / maker-checker / verification 协议导出为 Claude Code / Codex 可审查的原生 agent 配置模板。

### Changed

- 明确 Native Agent Adapter 只生成配置，不提供自动执行、runner、dispatcher、worktree 自动化、merge、commit、push 或 PR。

## [0.29.0]

### Added

- 新增 Guided Upgrade Workflow。
- 新增独立升级脚本，用于生成 upgrade-plan、upgrade-actions 和候选模板。

### Changed

- 降低旧项目升级时的人工判断成本和 token 消耗。

## [0.28.5]

### Changed

- 新增 Work Source Unification。
- 将公司派发、个人规划、用户反馈、bug、技术债等统一纳入 `Source ID -> Task ID -> Work Log` 链路。

## [0.28.4]

### Changed

- 强化 Source-to-Task Alignment。
- 收紧 `task-intake`、`task-board`、`work-log` 的对应关系。
- 补充和确认默认归并到已有 Source。
- `task-board.md` 只接收可执行任务。

## [0.28.3]

### Changed

- 将 loop、maker-checker、worktree 和 change 模板改为中文用户可读文案。
- 保留机器字段稳定，避免影响自动检查和脚本处理。

## [0.28.2]

### Changed

- 新增 Managed Docs Responsibility Matrix v2。
- 收紧 managed docs 的职责、默认读取策略和重复写入边界。
- 让用户可读文档更短、更自然。

## [0.28.1]

### Added

- 新增 `.forgekit/docs/task-intake.md`。

### Changed

- 建立任务来源优先流程：保留任务派发原文、AI 分析、任务反链和人工确认状态，再判断是否生成可执行任务。

## [0.28.0]

### Added

- 新增 Worktree Playbook。
- 新增手动 worktree 并行隔离指南和入口短规则。

### Changed

- 明确 ForgeKit 不提供自动 worktree 调度。

## [0.27.0]

### Added

- 新增 Optional Loop Operation Mode。
- 新增显式触发的 loop dry-run / one-step / continue / stop-handoff 操作协议。

### Changed

- 明确该模式不提供自动 runner。

## [0.26.0]

### Added

- 新增 Maker / Checker Protocol。
- 新增 managed docs 模板和 review 证据字段，用于分离实现和复核。

### Changed

- 明确 ForgeKit 不提供自动多 agent 调度。

## [0.25.0]

### Added

- 新增 Loop Readiness / Loop Blueprint。
- 新增 managed docs 模板和入口短规则，用于评估与设计可审查 loop。

### Changed

- 明确 ForgeKit 不提供自动 runner。

## [0.24.0]

### Added

- 新增 Smart Archive Apply。

### Changed

- 在 Git clean 且用户显式确认后，只归档 Smart Archive Advisor 标记为 `auto_archive_candidate` 的 change。
- 新增 apply report 输出。

## [0.23.0]

### Added

- 新增 Smart Archive Advisor。
- 综合 archive plan、reference report 和 sync report 生成智能归档建议报告。

### Changed

- 明确 Smart Archive Advisor 仍为 report-only。

## [0.22.0]

### Added

- 新增 Current Docs Sync Check。
- 基于 archive plan candidates 生成 current docs 同步证据报告。

### Changed

- 明确该检查不修改项目事实文件。

## [0.21.1]

### Added

- 新增 Work Log managed doc template。
- 新增 `.forgekit/docs/work-log.md`，用于个人工作顺序、交接上下文和中断恢复记录。

## [0.21.0]

### Added

- 新增 Archive Reference Check。
- 基于 archive plan candidates 生成引用报告。
- 检查 current docs、活跃 change 和入口文档中的字符串引用。

## [0.20.0]

### Added

- 新增 Archive Apply。

### Changed

- 在 Git clean 且用户显式 `--confirm` 后，按 dry-run plan 移动候选 change。
- 新增 apply report 输出。

## [0.19.0]

### Added

- 新增 Archive Plan。
- 新增 dry-run 归档计划。

### Changed

- dry-run 只生成或覆盖 `.forgekit/archive-plan.md`，不移动文件。

## [0.18.0]

### Added

- 新增 Document Lifecycle。
- 新增 current docs / changes / archive 三层规则。

### Changed

- archive 默认不进入 AI 默认上下文。
- done change 只提示可归档，不自动归档。

## [0.17.0]

### Added

- 新增 Template Versioning。
- 新增 template manifest / lock。

### Changed

- 升级时只生成 report-only 分类和候选模板。
- 不自动覆盖项目文件。

## [0.16.0]

### Added

- 新增 Boundary First。
- 新增 `.forgekit/project-boundary.yml`。

### Changed

- 新项目默认把 ForgeKit managed docs 写入 `.forgekit/docs`。
- 新项目默认把 change artifacts 写入 `.forgekit/changes`。

## [0.15.0]

### Changed

- 将 ForgeKit 定位升级为轻量级 AI 工程交付工具包。
- 新增 AI Engineering Loop。
- 新增风险分级 change templates。
