# ForgeKit 使用提示词手册

## Purpose

本手册提供日常可复制提示词。先替换 `<...>` 占位，再交给 Claude Code、Codex 或其他受 ForgeKit 规则约束的 AI。提示词只是入口，不扩大写入权限，也不替代用户确认。

## 1. 初始化新项目

> 请使用 ForgeKitRoot 的统一入口初始化 `<project-root>`，先展示检测结果和计划；不要自动 commit、push 或创建 PR。

## 2. 接手已有项目

> 把 `<project-root>` 当作既有项目接手。先只读盘点代码、验证能力、风险和当前文档，不假装旧项目可自动升级；给出 adoption 计划后等我确认。

## 3. 更新项目中的 ForgeKit

> 我已经更新外层 ForgeKit。请对 `<project-root>` 执行 upgrade check 和 plan，展示 safe/manual actions；没有我的确认不要 apply。升级后提醒我刷新会话。

普通用户直接运行统一入口即可；它在同一个交互会话中完成 preview、diff、replace/manual-merge/cancel 和结果汇总，不要求先退出再执行第二条 apply 命令。下面的 `--yes`、`--dry-run` 和显式 policy 只用于非交互、CI 或高级排查。

如果升级中出现 `review-needed` 文件，仍使用同一个统一入口在本轮处理，不要手动查 `migration.json`。交互式终端按提示选择：

- `replace with current ForgeKit template`：确认该文件没有本地定制，使用当前 ForgeKit 模板替换。
- `manual-merge`：确认该文件是本地定制，保留本地文件，并生成 `.local`、`.incoming`、`.diff` 和 README，方便后续手动或 AI 辅助合并。
- `show diff`：先查看本地文件与 incoming template 的差异，再回到选择菜单。
- `abort`：停止本轮升级，不继续写入迁移结果。

非交互或 `--yes` 场景必须显式给出策略，例如：

```bash
python scripts/forgekit-project.py --target <project-root> --yes --review-needed-policy manual-merge
python scripts/forgekit-project.py --target <project-root> --yes --review-needed-policy replace-template
```

升级完成后项目可以正常使用。如果当前 AI 会话是在升级前打开的，建议新开会话，或让当前 AI 重新读取项目入口文档后再继续工作。新任务建议新开会话启动。

如果升级结果提示项目根 `AGENTS.md` 仍需人工合并，直接加入下面三行；不要覆盖项目已有业务规则：

```text
- For medium/high risk changes, read `.forgekit/docs/maker-checker-protocol.md` and the active `.forgekit/changes/<id>/` artifacts.
- Before implementation, freeze scope, trust boundary, non-goals, stage authorization, and a risk-proportional acceptance matrix.
- Re-review defaults to prior blockers; fix-introduced contract/real-error regressions may still block, while unrelated suggestions stay follow-up.
```

初始化 / 升级工具支持 `--lang zh-CN` 和 `--lang en-US`；也可以用 `FORGEKIT_LANG` 选择本轮显示语言。

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

## 8.1 Maker 实现

> 按已冻结的 proposal 和 Frozen Acceptance Matrix 实现，不扩大范围。把每个 acceptance ID 映射到代码和测试，确认正式入口接入被测试的真实路径；矩阵外改进只记 follow-up，不运行当前 Stage Authorization 未授权的任务。

## 8.2 Reviewer 首审

> 在独立上下文中按冻结合同只读首审。违反合同或会造成数据污染、错误执行/结果、artifact 覆盖或虚假成功的问题才作为 blocker；其他新增建议记 follow-up，不扩大 trust boundary。优先验证矩阵中的拒绝反例，并检查正式入口而不只检查 helper。

## 8.3 Reviewer 限定复审

> 默认只复核上一轮 blocking findings，逐项标记 Closed、Partially closed 或 Still open。本轮修复新引入且违反冻结合同或会造成真实错误的回归可以继续阻塞；与修复无关的新建议只记 follow-up。不要重新开放式审查或扩大 trust boundary。原 blocker 全部关闭后，按冻结边界和当前 Stage Authorization 给出结论。

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
