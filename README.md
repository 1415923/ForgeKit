# ForgeKit

English documentation: [README.en.md](README.en.md)

ForgeKit **v0.47.0** 是面向 Codex、Claude Code 的本地项目治理脚手架，提供任务来源、当前事实、按需 Skills、检查和版本迁移。

本版针对 GPT-6 Astra 清理重复指令和过早停止，并将正常的文档定制纳入自动升级。双平台共用规则，不修改用户的模型配置。Astra 实际效果仍需目标客户端验证。

## 初始化或更新

在 ForgeKit 仓库中运行：

```powershell
python .\scripts\forgekit-project.py --target "D:\path\to\project"
```

macOS / Linux：

```bash
python3 ./scripts/forgekit-project.py --target "/path/to/project"
```

统一入口识别 init、current、upgrade、toolkit-too-old 和 legacy adoption。先展示计划；交互确认或显式 `--yes` 后写入。

全新项目默认 in-place。无人值守初始化必须明确 layout：

```powershell
python .\scripts\forgekit-project.py --target "D:\path\to\project" --yes --layout in-place
```

保留 `--layout legacy-nested`；已有项目布局不移动。业务根 README 由用户拥有，不创建、覆盖或删除。
v0.36.0 起具有有效 state 的项目沿精确版本链迁移；更早或缺失 state 的项目先只读接手，不强行初始化。
预检会显示完整迁移链。各步先在内存中依次转换，整条链无冲突后才整体应用；不是逐版安装旧工具，也不会跳过必要迁移直接覆盖最新版。
只查看计划可加 `--dry-run`；升级完成后再次运行会显示 `up-to-date`、零迁移动作。当前安装版本以 `.forgekit/state.json` 为准，boundary 文件中的版本表示其创建时的模板版本。

## 0.47.0 的主要变化

- 七个主要 Skill，合并填充／回填和适用性／接手；三个旧名称作为显式兼容入口保留。
- 入口只保留边界与按需导航，已定位的小任务无需重新扫描治理文档。
- 已授权的实现包含相关验证与必要修复；通过后不无故扩大测试或再次请求同义授权。
- 合并重复的 checkpoint、工具链和路由文档；保留任务来源、看板、日志的独立职责。
- 用户继续编辑 Markdown。隐藏标记区分模板章节与用户区，升级自动搬迁能够明确定位的定制内容。
- 退休 usage.html；日常示例统一见生成项目的 `.forgekit/docs/usage-playbook.md`。

## 七个按需 Skill

| Skill | 什么时候用 |
| --- | --- |
| project-init | 初始化或安装 |
| document-backfill | 显式要求初始化占位填充或既有事实回填 |
| project-assessment | 采用适用性评估或接手审计 |
| large-change-planning | 高影响变更的范围、验收与回滚规划 |
| code-review | 只读代码审查及定向复查 |
| security-review | 真实安全边界审查 |
| release-check | 明确发布候选的就绪检查 |

`project-bootstrap-fill` → document-backfill/bootstrap；`handover-review` → project-assessment/takeover；`project-suitability` → project-assessment/adoption。0.47.x 保留显式调用，不再作为主要自动路由。
根级 `skills/` 是语义来源，`.agents/skills/` 由白名单确定性投影，`.claude/skills/` 保留平台适配。Skills 不组成强制流水线。

## 保留定制的升级

0.46.0 → 0.47.0 使用旧模板、本地内容和新模板的三方迁移。普通填写、追加记录和 AGENTS 新增规则自动保留；文档合并按显式章节映射搬运，不调用模型猜测事实。

已写成项目事实的 API、需求、任务、测试和地图等文档可以使用自己的章节结构，升级完整保留成稿，仅修正需要搬迁的旧链接。该规则采用明确的事实 owner 白名单，不适用于治理协议、Skill 或入口规则。历史来源同时覆盖发布标签、已发布迁移素材和 LF／CRLF／BOM 等价形式。

| 情况 | 处理 |
| --- | --- |
| stock 或只有模板变化 | 自动更新 |
| 用户区、填充字段、非重叠编辑 | 保留或搬迁 |
| 同一规则冲突、未知基线、重复标识 | 集中展示冲突，整个应用停止，项目版本不变 |
| 规划后文件变化 | 重新规划，不能执行过期计划 |
| 写入失败 | 尝试恢复所有已变更文件；无法恢复时报告路径并保留回滚备份 |

迁移结果保存实际动作和回滚材料。不能用旧 `manual-merge` 策略绕过结构化冲突或把部分升级报告为成功。
低层 `forgekit-upgrade.py check/plan/apply --safe` 继续可用，新格式支持 `--json` 与应用时的 `--plan-hash`。
AGENTS 和 CLAUDE 入口随迁移自动更新，正常升级无需手工粘贴规则。升级后启动新会话，旧会话只做最小 checkpoint 和收口。

## 模板规则、项目约束与当前事实

| 内容 | 放在哪里 | 升级时如何处理 |
| --- | --- | --- |
| ForgeKit 通用规则 | 入口模板区、治理协议、Skills | 按版本链更新 |
| 项目额外约束与路由 | 入口的现有用户区；细节引用地图和内层项目文档 | 保留用户区，不用整份项目入口替换模板区 |
| 当前版本、运行状态和验收结论 | 对应事实来源及其负责文档 | 按证据核实，模板升级不猜测或自动刷新业务状态 |

编辑 AGENTS / CLAUDE 时，将项目补充放入已有的 `<!-- forgekit:user begin -->` 与 `<!-- forgekit:user end -->` 之间，不创建嵌套或重复用户区。易变的 release、commit、Scheduler/source 状态应引用对应清单或状态来源；磁盘清单、运行健康与用户验收分别需要证据。历史验收记录保留日期和证据，不能继续冒充当前状态。

如果旧 AGENTS / CLAUDE 已整份重写，报错行号只是首个基线差异。维护者应先对照准确的已安装版本模板，复核项目约束和过时事实；经授权把入口整理成模板区＋项目用户区，再运行普通升级命令。模板升级只处理受管文件，不会顺带重写业务仓库的内层 AGENTS。

另有 `--entry-resolutions <resolution.json>`，用于复核后明确选择完整保留旧入口的情况。材料绑定项目、版本和内容哈希，必须显式传入；完整保留不等于事实已更新，不能替代入口整理与语义审查。格式见 [入口合并说明](project-template/docs/project-maintenance.md#整份定制入口的显式合并)。普通升级无需此参数。

## 使用与边界

从项目根启动 Codex 或 Claude Code，读取对应 AGENTS.md 或 CLAUDE.md。告诉工具目标、范围和完成标准；必要命令见 `.forgekit/docs/testing.md`，定位不明时使用 codebase-map。
审查、诊断和规划默认只读。commit、push、tag、发布、部署、生产数据或权限变更仍需要对应授权。高风险独立审查不能由 self-review 代替。
Severity 与 Blocking 独立；DIAGNOSTIC、SMOKE、FORMAL 描述证据用途，真实调用不自动成为 Formal。详见 maker-checker-protocol 与 ai-engineering-loop。
仅在确认事实变化时最小写回；task-intake 保存来源，task-board 保存执行状态，work-log 保存推进记录。owner 存在不要求填满模板。

多项目为 opt-in，机器入口是 workspace-map；仅长期独立子项目启用 project capsule。不会自动拆分文档或创建第二套事实源。
维护和归档继续 plan、确认、apply、summary/index，操作前后检查 current docs；Archive 不是删除。

## 检查与资料

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-template.ps1
python .\scripts\check-current-docs-integrity.py --repo-root "D:\path\to\project"
```

版本记录见 [CHANGELOG.md](CHANGELOG.md)。运行时加载、真实 Astra 行为及模型收益必须有实际证据；静态通过不等于客户端实测。
