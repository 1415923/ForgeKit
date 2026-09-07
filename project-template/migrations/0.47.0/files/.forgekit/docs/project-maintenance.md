# 项目维护操作

<!-- forgekit:section s-d4e8830a71c7 -->
## Purpose

本文件把“同步、整理、归档、收口”等模糊请求路由到明确的维护动作。维护统一遵循：`intent -> plan -> confirm/apply -> summary/index`。

维护操作不等于业务开发，不自动改 business docs，不自动提交 Git，也不默认读取全量 archive。

Multi-project scoped docs 是显式启用能力。维护前读取 `.forgekit/state.json`；只有 state 与 `.forgekit/workspace-map.json` 都启用时才按 WorkspaceRoot / ProjectScope / RepoRoot 分层处理。缺少配置的 legacy single-project 项目只给 adoption guidance，不自动拆分文档或创建 capsule。

<!-- forgekit:section s-8738545b48b3 -->
## Maintenance Intents

| MaintenanceIntent | 常见说法 | 入口 | 默认行为 |
| --- | --- | --- | --- |
| `project-bootstrap` | 安装、初始化、更新、同步 ForgeKit | ForgeKitRoot `scripts/forgekit-project.py` | 自动检测后 init、up-to-date、upgrade plan 或 adoption |
| `upgrade-sync` | 更新了外层 ForgeKit、同步一下、升级后整理 | `scripts/forgekit-upgrade.py` | check + plan |
| `archive-capsule` | 阶段结束、归档一下、历史收起来 | `scripts/archive-capsule.py` | plan |
| `context-checkpoint` | 保存关键结论、compact 前收口 | `work-session-checkpoint.md` | 最小 checkpoint |
| `handoff` | 给领导、reviewer、测试看 | `scripts/handoff-package.py` | report-only |
| `doc-health` | 文档太乱、重复、太长 | `scripts/doc-health-report.py` | report-only |
| `source-trace` | 任务从哪来、完成有没有证据 | `scripts/source-trace-report.py` | report-only |

意图或范围不清时，先问一个聚焦问题，不直接执行重操作。

<!-- forgekit:section s-5e4b0c95bd53 -->
## Unified Project Bootstrap / Install-or-Upgrade Entry

推荐从 ForgeKitRoot 使用同一个入口，不要求用户先判断目标目录应初始化还是升级：

```bash
python scripts/forgekit-project.py --target <project-root>
```

| 检测状态 | 行为 |
| --- | --- |
| 未安装 ForgeKit | 计划初始化；非空目录需要 `--force-init`，但仍保留已有文件 |
| v0.36+ 且等于当前工具版本 | `up-to-date`，不写文件 |
| v0.36+ 且低于当前工具版本 | 调用 `forgekit-upgrade.py check` 和 `plan`，确认后才 `apply --safe` |
| 项目版本高于当前工具版本 | 停止，要求先更新 ForgeKitRoot |
| 有 `.forgekit` 但没有 state，或版本早于 v0.36 | `legacy-adoption`，不自动初始化或升级 |

`--dry-run` 和 `--no-apply` 只检测/展示；非交互环境默认不 apply，只有显式 `--yes` 才执行初始化或 safe apply。升级写入前必须显示 ProjectRoot、已安装版本、工具版本、检测动作、check、plan、safe/manual 数量，并以默认 No 的确认结束。

如果 safe migration 遇到 `review-needed` 文件，统一入口必须在同一轮解释目标文件、原因、影响和推荐选择，并让用户选择 replace template、manual-merge、show diff 或 abort。`manual-merge` 会保留本地文件，并导出 `.local`、`.incoming`、`.diff` 和 README，方便后续人工或 AI 辅助合并；`replace-template` 只覆盖该 action 对应的目标文件。非交互或 `--yes` 下遇到 review-needed 时，必须显式传入 `--review-needed-policy manual-merge` 或 `--review-needed-policy replace-template`，否则停止并输出可复制命令。`keep-local` 只作为兼容别名，按 `manual-merge` 处理。

初始化 / 升级工具支持 `--lang zh-CN` 和 `--lang en-US`；未显式指定时，交互式终端会询问本轮显示语言，非交互或 `--yes` 默认 `en-US`。

review-needed 记录写入 `.forgekit/reports/upgrade-review-needed.md` 和 `.forgekit/reports/upgrade-review-needed.json`，只作为审查记录，不要求用户手动查 migration 文件，也不是独立 resolve 入口。

该脚本只属于 ForgeKitRoot，不复制进 ProjectRoot。旧 `init-project-template.*` 与 `forgekit-upgrade.py` 继续作为底层和高级入口。

## 整份定制入口的显式合并

读者是处理升级冲突的维护者；仅在 AGENTS.md / CLAUDE.md 已替换旧模板规则时使用。此处不记录业务事实或项目专用合并内容。

错误中的行号指首个基线差异，不代表仅改了标题。默认升级继续停止。先比较完整本地入口和即将安装的新入口；确认项目启动顺序、授权和生产边界与新版规则兼容，保留更具体的项目约束。不能仅凭哈希一致宣称完成语义审查。

`--entry-resolutions <resolution.json>` 显式选择经过复核的保留候选，统一入口的预检和应用使用同一材料，写入仍有正常确认。低层 check / plan / apply 同样支持此参数。候选仅支持「新版模板 + 完整本地原文用户区」，不允许删改原规则。已有用户区的整份重写不能嵌套保留，需要先人工整理冲突。

JSON 格式为 `schema_version: 1`、`project_root`（绝对路径）、`from_version`、非空 `entries` 数组。每个条目包含：

| 字段 | 内容 |
| --- | --- |
| target | AGENTS.md 或 CLAUDE.md，不重复 |
| migration_id | 实际应用此候选的迁移 ID |
| local_sha256 | 该迁移步骤本地入口原始字节的 SHA-256 |
| incoming_sha256 | 该步骤传入模板原始字节的 SHA-256 |
| resolved_text | 完整可审阅候选正文，UTF-8、LF |
| resolved_sha256 | 候选 UTF-8 字节的 SHA-256，64 位小写十六进制 |

维护者可用 `structured_upgrade.preserved_entry_candidate(local_bytes, incoming_bytes)` 生成候选后复核；该函数不判断规则兼容性。项目专用材料放在本地目录，不写进模板或共享迁移包。版本、输入、材料变化后重新生成复核；材料未用上或后续迁移改变了候选也会停止。实际结果记录材料与候选哈希，回滚备份保留原文件。

<!-- forgekit:section s-2589cd7ff083 -->
## Upgrade Sync

用户说“我更新了外层 ForgeKit，帮项目同步”时：

1. 优先从 ForgeKitRoot 运行 `python scripts/forgekit-project.py --target <ProjectRoot>` 完成状态分流。
2. 高级排查时确认 `ProjectRoot` 与 `ForgeKitRoot`，读取 `.forgekit/state.json`。
3. 运行 `python scripts/forgekit-upgrade.py check --repo-root <ProjectRoot>`。
4. 运行 `python scripts/forgekit-upgrade.py plan --repo-root <ProjectRoot>`。
5. 展示一屏迁移计划、冲突和人工项。
6. 只有用户确认，或 bounded-auto 的授权明确覆盖该次升级时，才运行 `apply --safe`。
7. 如果出现 review-needed，在同一轮完成选择、记录和后续 safe migration；不要新增独立 resolve 命令。
8. apply 后执行 `ManagedDocsWriteback: minimal`，输出 upgrade summary。
9. 按 `work-session-checkpoint.md` 执行 Post-Upgrade Session Refresh。

v0.35.x 及更早项目按既有项目接手，不假装自动升级。

<!-- forgekit:section s-a4ddfa454e49 -->
## Archive Capsule

归档不是删除。阶段材料先形成计划，确认后移动到按日期和阶段命名的 capsule，并生成摘要、项目清单和索引。详细规则见 `archive-capsule.md`。

Archive plan/apply 前后必须运行 `check-current-docs-integrity.py`。active tasks 存在时只能创建 provisional、legacy transition、evidence 或 active-work cleanup snapshot；完整性失败先做 Current State Restoration Pass，不得继续 apply。

如果阶段包含高风险变更，归档计划应确认 Adversarial Review 是否完成。maintenance summary 可以引用 First-Principles 结论或 adversarial findings 的摘要和证据路径，但不复制全文。

```powershell
python scripts/archive-capsule.py plan --repo-root . --name phase-close --reason "阶段完成" --item .forgekit/changes/<change-id>
python scripts/archive-capsule.py apply --repo-root . --plan .forgekit/archive-capsule-plan.md --confirm
```

默认只接受显式 `--item`；不扫描全量 changes 或 archive，不移动 `.forgekit/docs/**`、business docs、state、lock 或旧 archive。

<!-- forgekit:section s-bcb81ad7f260 -->
## Checkpoint / Handoff / Reports

- 上下文可能丢失：走 `context-checkpoint`。
- 阶段成果需要给人审阅：走 `handoff`。
- 文档职责混乱：走 `doc-health`。
- 来源、任务、验证链路不清：走 `source-trace`。

这些报告不会自动修复项目事实。

<!-- forgekit:section s-9abf0faca88b -->
## Plan before Apply

所有维护动作先说明 intent、范围、可写路径、禁止动作和预期输出。report-only 动作可直接生成报告；会移动或改写文件的动作必须先 plan。

跨项目维护计划还必须列出 WorkspaceRoot、Project ID、Repo ID 和 Artifact ID。Artifact 只作为 evidence index；Archive 不是 current docs。`check-workspace-integrity.py` 只检查跨层关系，不替代 `check-current-docs-integrity.py` 的单作用域事实检查。

### One-Time Cleanup Plan

scratch、重复材料或临时文件 cleanup 只使用本次维护计划中的逐项记录：

```text
Path:
Evidence:
Proposed Action:
Reason:
Confirmation:
```

`Path` 必须是已解析的具体目标；`Evidence` 说明为何该项属于本次 cleanup；`Proposed Action` 说明保留、移动、归档或经确认清理；`Reason` 解释必要性；`Confirmation` 记录本次用户决定。未确认项不 apply。

该计划是一次性 review artifact，不建立 `CURRENT/HISTORICAL` 等持久 taxonomy，不建立 inventory database、逐文件 registry、cleanup state 或自动 cleanup。后续维护重新从当前 evidence 生成新计划，不把旧计划当权威库存。

<!-- forgekit:section s-8583bf260bc6 -->
## Confirmation Rules

- Archive Capsule apply 必须有本次明确确认和 `--confirm`。
- Upgrade `apply --safe` 必须在用户确认或明确 bounded-auto 授权范围内。
- 确认只覆盖展示过的计划，不自动扩展到新文件、新阶段或 legacy archive。

<!-- forgekit:section s-0d4f520362cc -->
## Post-Operation Summary

维护摘要必须包含 current docs integrity 状态。若为 needs-fix，列出 restoration 入口和 blocking evidence，不得声明维护完成。

维护完成后输出：MaintenanceIntent、实际动作、变更路径、未执行项、验证结果、风险、索引/摘要路径和下一步。升级后补充会话刷新提示；归档后必须给出 capsule summary 与 archive index 路径。

<!-- forgekit:section s-e68ee04dff59 -->
## Examples

- “我更新了外层 ForgeKit，帮这个项目同步一下。” -> `upgrade-sync`，先 check/plan。
- “这个阶段结束了，帮我归档成 capsule。” -> `archive-capsule`，先列明 items 和目标路径。
- “帮我生成维护计划，不要直接 apply。” -> 只生成 plan，不移动或改写文件。

<!-- forgekit:user begin -->
<!-- forgekit:user end -->
