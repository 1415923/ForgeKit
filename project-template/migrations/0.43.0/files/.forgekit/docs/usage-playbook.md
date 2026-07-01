# ForgeKit 使用提示词手册

## Purpose

本手册提供日常可复制提示词。先替换 `<...>` 占位，再交给 Claude Code、Codex 或其他受 ForgeKit 规则约束的 AI。提示词只是入口，不扩大写入权限，也不替代用户确认。

## 1. 初始化新项目

> 请使用 ForgeKitRoot 的统一入口初始化 `<project-root>`，先展示检测结果和计划；不要自动 commit、push 或创建 PR。

## 2. 接手已有项目

> 把 `<project-root>` 当作既有项目接手。先只读盘点代码、验证能力、风险和当前文档，不假装旧项目可自动升级；给出 adoption 计划后等我确认。

## 3. 更新项目中的 ForgeKit

> 我已经更新外层 ForgeKit。请对 `<project-root>` 执行 upgrade check 和 plan，展示 safe/manual actions；没有我的确认不要 apply。升级后提醒我刷新会话。

## 4. 开始今天工作

> 请先按 workflow router 读取当前任务、最近 work-log、开放风险和必要验证入口，给我一个简短的当前状态与今天下一步；不要全量读取 `.forgekit/docs/**`。

## 5. 执行具体任务

> 执行 `<Task ID 或任务描述>`。先确认 Source/需求、实现范围、验证方式和 managed docs 写回级别；只修改授权范围，完成后做最小 checkpoint。

## 6. 文档 Checkpoint

> 对本轮做一次 Checkpoint Update。只把已确认的进展、真实状态变化、验证结论、风险和下一步写入负责文档；无变化的文档不要改。

## 7. Compact / Clear 前保存上下文

> 在 compact、clear 或换会话前做 pre-compact checkpoint，只保存可恢复工作的关键事实和证据路径；不要复制完整聊天或长日志。

如果 auto compact 已经发生：

> 先做 post-compact recovery check。对照当前 task/change/work-log 和工作区证据恢复状态；不确定内容标记 `TODO_REVIEW`，不要直接继续实现。

## 8. 提交前检查

> 提交前检查本次 diff、验证证据、独立 review gate、开放风险和最小 managed docs 写回。不要自动 commit；给出可审查摘要和建议 commit message。

## 9. 阶段结束归档

> 这个阶段准备收口。先检查 current docs integrity，再生成 Archive Capsule plan；不要直接 apply、移动文件或把 active work 写成 completed phase。

## 10. 生成 Handoff

> 根据当前 Source、任务、change、验证、风险和已有报告生成 review-ready handoff。缺证据标记 `TODO_REVIEW`，不要编造 commit、测试或文件列表。

## 11. 多项目 Workspace 只读分析

> 对当前 multi-project workspace 做只读分析。读取 workspace map 和命中的 project/repo 范围，汇总跨项目状态、依赖和风险；不要启用 map、创建 capsule、生成 Repo Lite 或修改项目文件。

## 12. 启用 Multi-Project Map 前检查

> 在启用 multi-project map 前运行 workspace integrity check，检查 Project/Repo/Artifact/Archive 边界和 docs profile；只给 adoption guidance，不自动启用或创建 Project Capsule。

## 13. 创建一个最小 Project Capsule

> `<project-id>` 已在启用的 workspace map 中设为 `project-capsule`。请先运行 `bootstrap-project-capsule.py plan`，展示最小写入清单；没有我的确认不要 apply，不要修改 map、拆分 workspace docs 或创建其他 project capsule。

## Writeback Reminder

- 默认 `ManagedDocsWriteback: minimal`。
- “只改业务文件”不自动关闭 ForgeKit 最小写回；用户明确说不改 ForgeKit docs 时才关闭。
- Micro Update 不写 ForgeKit governance docs，但仍可在授权范围内修改业务代码、业务 README、注释、测试或配置。
- 未确认内容不写成事实；report-only / review-only 不借机修改 current docs。
