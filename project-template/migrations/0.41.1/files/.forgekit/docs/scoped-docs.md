# 多项目工作区与分层文档

## Purpose

本协议用于一个交付工作区包含多个项目或 Git 仓库的场景。Workspace Docs 记录跨项目当前事实，Project Capsule 记录项目局部当前事实，Repo Lite 只提供代码仓库入口和本地命令。Archive 仍是历史证据，不是 current truth。

v0.41 不自动拆分现有文档，也不自动创建真实 Project Capsule。只有用户确认并把 `.forgekit/workspace-map.json` 的 `enabled` 设为 `true` 后，才启用多项目检查。

## Boundary Model

| 边界 | 职责 |
| --- | --- |
| ForgeKitRoot | 工具、模板和 migration 来源 |
| WorkspaceRoot | 跨项目治理根目录；兼容旧版 ProjectRoot 语义 |
| ProjectScope | 产品、服务、组件或职责范围 |
| RepoRoot | 单一 Git 仓库和 commit 边界 |
| ArtifactRoot | 构建物、测试报告和导出物等证据位置 |
| ArchiveRoot | 历史证据，默认不参与当前事实判断 |

一个 Workspace Task 可以关联多个 ProjectScope 和 RepoRoot；一个 commit 只能属于一个 RepoRoot。项目局部完成不等于跨项目任务整体完成。

## Scope Selection

每次读取或写入前先选择 `Scope: workspace | project | repo`，并记录需要时的 `Project ID`、`Repo ID`、`Workspace Task ID`、`Local Task ID` 和 `Source ID`。现有 `SRC-*`、`TASK-*`、`RISK-*`、`TEST-*` 继续合法，不强制迁移 ID 前缀。

- Workspace Docs：只保留跨项目来源、主任务、总体状态、集成验证和跨项目风险。
- Project Capsule：只保留该项目的局部任务、验证、风险、来源引用和决策。
- Repo Lite：只保留 workspace/project 指针、代码入口和仓库本地命令，不成为第三套任务事实源。
- Artifact：只提供 evidence index，不生成任务、来源或风险文档。

## Docs Profiles

| 配置位置 | Profile | 含义 |
| --- | --- | --- |
| `workspace.docs_profile` | `workspace-full` | Workspace Docs 是跨项目事实入口，兼容既有 workspace 管理方式。 |
| `project.docs_profile` | `workspace-only` | Project 已登记，但当前事实仍由 Workspace Docs 管理；不要求 `docs_path` 或 Project Capsule 存在。 |
| `project.docs_profile` | `project-capsule` | Project 使用最小 capsule；`docs_path` 缺失属于 blocking。 |
| `repo.docs_profile` | `repo-lite` | Repo 仅有薄入口和本地命令，不成为第三套事实源。 |

Profile 不能跨位置使用。`workspace-only` 是显式的渐进采用状态，不会自动创建 capsule，也不会产生 capsule 缺失 warning。
为兼容已启用的 v0.41.0 map，缺少 `workspace.docs_profile` 时按 `workspace-full` 处理；新配置应显式填写。Project 和 Repo 的 profile 必须明确填写。

## Project Capsule

默认 capsule 位于 `.forgekit/projects/<project-id>/`，只包含：

- `project-card.md`
- `source-links.md`
- `task-board.md`
- `testing.md`
- `risk-register.md`
- `decisions/*.md`

`work-log.md` 默认不创建。只有项目长期独立推进且 workspace work-log 已明显膨胀时，才由用户确认启用。`handoff.md` 是按需生成物，不是默认模板。

## Source Rules

原始 Source 尽量只保留在 workspace `task-intake.md`。Project `source-links.md` 只记录 Source ID、局部解读、责任拆分、派生任务、开放问题和人工确认。只有 standalone project 没有 workspace source 时，才允许保存脱敏原文。

示例 ID 和模板占位不参与真实引用检查。未经人工确认的局部解读不能写成 workspace 事实。

## Status Rules

Workspace task 的 overall status 与各项目或仓库局部状态分开维护，例如 backend 为 `Backend Ready`、frontend 为 `Waiting`、scanner 为 `Waiting Data`、testing 为 `Pending E2E`。局部状态不能自动把 overall status 改为完成。

## Decision Records

重要边界采用一事一文的 ADR-style decision record，记录 Context、Decision、Consequences、Evidence 和 Supersedes。可推荐 `ADR-<project>-0001`，但不强制替换现有 Decision ID，也不依赖外部 ADR 工具。

## Activation

- `.forgekit/state.json` 中 `multi_project_scoped_docs_available` 表示已安装能力。
- `multi_project_scoped_docs_enabled` 表示用户已选择启用。
- `.forgekit/workspace-map.json` 的 `enabled` 是工作区配置。
- available=true、enabled=false 时属于 not-enabled；默认 map 中的 `TODO_REVIEW` 不参与校验。
- state enabled=true 时，map 必须存在、`enabled=true` 且使用真实 workspace ID。
- scoped docs 启用后，checker 会检查 WorkspaceRoot 和 listed repo 的 Git 状态。WorkspaceRoot 不是 Git repo 只产生 warning：它提示 workspace 级 `.forgekit` 文档可能无法随 root commit/push；多 repo 工作区中的各子 repo 仍可独立作为 Git repo 使用。

## Boundaries

- 不自动创建 ProjectScope、RepoRoot 或 ArtifactRoot。
- 不自动拆分、移动或重写现有 managed docs。
- 不把完整 ForgeKit docs、AGENTS、CLAUDE、governance、skills 或 agents 复制到 capsule。
- 不把 archive 或 artifact 配置为 current docs。
- 不自动创建 repo、commit、push 或修改 business docs。
