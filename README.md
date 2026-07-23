# ForgeKit

English documentation: [README.en.md](README.en.md)

ForgeKit 是面向 Codex、Claude Code 等 AI 编程工具的**本地项目治理脚手架**。

它不会替你生成业务框架、部署系统或自动操作 Git。它做的是另一件更基础的事：把项目边界、任务来源、当前状态、验证证据、风险和交接方式放进仓库，让 AI 在一个**可审查、可验证、可恢复**的流程里工作。

```text
ForgeKit = 项目入口 + 按需 Skills + 当前事实文档 + 安全检查与迁移
```

## 它解决什么问题

AI 编程真正容易失控的地方，通常不是“不会写代码”，而是：

- 不清楚哪些目录可以改，误伤其他项目或历史材料；
- 忘记任务来源、已有结论和未完成事项；
- 实现完成了，却没有可靠验证或可复查证据；
- 会话压缩、换工具或换人后，无法接着做；
- review、修复、commit、push、release 的授权边界混在一起；
- 项目升级时，模板文件和用户定制文件互相覆盖。

ForgeKit 用项目内文件和检查脚本把这些事实固定下来。它是 AI 工作流脚手架，不是 Agent 运行时，也不是后台自动化平台。

## 快速开始

### 1. 初始化或同步目标项目

在 ForgeKit 仓库中运行：

Windows PowerShell：

```powershell
python .\scripts\forgekit-project.py --target "D:\path\to\project"
```

macOS / Linux：

```bash
python3 ./scripts/forgekit-project.py --target "/path/to/project"
```

统一入口会先判断目标状态，再决定下一步：

| 目标状态 | 处理方式 |
| --- | --- |
| 尚未安装 ForgeKit | 展示初始化计划 |
| 已是当前版本 | 显示 `up-to-date` |
| 可安全升级的旧版本 | 先展示检查结果和升级计划，确认后再应用 |
| 外层 ForgeKit 太旧 | 停止，并提示先更新 ForgeKit |
| 很早期或无法安全迁移的项目 | 按“接手已有项目”处理，不强行升级 |

默认先计划、后写入。安全写入需要交互确认或显式 `--yes`。

只有 v0.36.0 及以后初始化、并具有 `.forgekit/state.json` 的项目支持正式安全迁移。更早项目应先做只读接手检查。

### 2. 从项目根目录启动 AI 工具

Codex：

```powershell
cd D:\path\to\project
codex
```

Claude Code：

```powershell
cd D:\path\to\project
claude
```

### 3. 让 AI 先恢复项目上下文

Codex：

```text
请读取 AGENTS.md，并按项目内 ForgeKit 规则理解当前项目。先告诉我项目边界、当前任务、已有证据、风险和建议下一步，不要直接改文件。
```

Claude Code：

```text
请读取 CLAUDE.md，并按项目内 ForgeKit 规则理解当前项目。先告诉我项目边界、当前任务、已有证据、风险和建议下一步，不要直接改文件。
```

## v0.45.0 的工作方式

v0.45.0 将常驻入口和按需流程分开：

- `AGENTS.md` / `CLAUDE.md`：只保留始终有效的边界、授权和路由规则；
- 根级 `skills/`：九个共享 Skill 的语义权威源；
- 生成项目中的 `.agents/skills/`：由投影工具确定性同步；
- `.claude/skills/`：Claude 平台适配层，不是机械副本。

### 九个按需 Skill

| Skill | 什么时候用 |
| --- | --- |
| `project-init` | 初始化一个尚未使用 ForgeKit 的新项目 |
| `project-bootstrap-fill` | 补全已经初始化但仍有占位内容的项目 |
| `handover-review` | 只读接手已有项目，先盘点再决定是否改造 |
| `document-backfill` | 根据现有实现和证据回填事实文档 |
| `large-change-planning` | 为高影响变更冻结范围、授权、验收和回滚 |
| `code-review` | 只读审查已有实现、diff、测试和证据 |
| `security-review` | 审查真实安全边界，不把普通代码改动都升级为安全审查 |
| `release-check` | 检查明确的发布候选，不把普通 commit 当成 release |
| `project-suitability` | 只读评估项目是否适合采用 ForgeKit |

这些 Skill 不组成固定流水线。按任务意图和实际影响调用需要的 Skill 即可。

review、assessment 和 planning 默认只读。发现问题不等于自动获得修复权限；本地写入、commit、push、tag、publish、release、deploy 分别需要明确授权。

风险按实际影响判断，而不是按文件数或行数机械升级。重点看：

- 信任边界是否变化；
- 是否涉及外部或不可逆动作；
- 是否影响数据、权限或公共接口；
- 回滚是否困难；
- 证据是否不足。

## 常用提示词

更完整的日常用法见生成项目中的：

```text
.forgekit/docs/usage-playbook.md
```

常用短提示词：

| 目标 | 可直接复制 |
| --- | --- |
| 开始今天的工作 | `请读取当前任务、最近进展、风险和验证入口，告诉我今天最合理的下一步，不要先改文件。` |
| 接手已有项目 | `请使用 $handover-review 只读盘点 <project-root>，给出边界、现状、风险和接手建议，不要自动初始化或修复。` |
| 补全已初始化项目 | `请显式调用 $project-bootstrap-fill，只补现有证据支持的占位内容，保留用户定制。` |
| 回填事实文档 | `请显式调用 $document-backfill，只根据已有实现和验证证据做最小回填。` |
| 规划高影响变更 | `请显式调用 $large-change-planning，冻结范围、授权、验收、非目标和回滚。` |
| 审查代码 | `请使用 $code-review 只读审查现有 diff、测试和证据，不要自动修复。` |
| 审查安全边界 | `请使用 $security-review 审查明确的安全影响，只报告证据、风险和修复责任。` |
| 检查发布候选 | `请使用 $release-check 核对版本、migration、制品和门禁，不要执行发布。` |
| 评估是否适用 | `请使用 $project-suitability 只读评估当前项目是否适合 ForgeKit，不要自动初始化。` |
| 保存当前进展 | `只把本轮已确认的状态、验证、风险和下一步最小写回负责文档。` |
| 上下文压缩或换会话前 | `请做一次进展保存，并列出新会话应先读取的文件。` |
| 提交前检查 | `请检查 diff、验证、独立审查、风险和必要文档写回，不要自动 commit。` |

## 更新已有项目

普通用户继续使用统一入口即可：

Windows：

```powershell
python .\scripts\forgekit-project.py --target "D:\path\to\project"
```

macOS / Linux：

```bash
python3 ./scripts/forgekit-project.py --target "/path/to/project"
```

需要排查迁移细节时，可以使用低层入口：

```bash
python scripts/forgekit-upgrade.py check --repo-root <project>
python scripts/forgekit-upgrade.py plan --repo-root <project>
python scripts/forgekit-upgrade.py apply --safe --repo-root <project>
```

| 命令 | 作用 |
| --- | --- |
| `check` | 检查版本和迁移资格，不写文件 |
| `plan` | 输出迁移计划，不写文件 |
| `apply --safe` | 只执行 migration 中标记为安全的动作 |

### 从 v0.44.1 升级到 v0.45.0

正式 migration 会逐项区分目标文件状态：

| 状态 | 处理方式 |
| --- | --- |
| `stock` | 与旧版基线一致，可安全更新 |
| `custom` | 用户已经修改，不覆盖，进入 manual merge |
| `unknown` | 无法可靠识别，不覆盖 |
| `missing` | 按 action 合同安全处理 |
| rollback | 恢复本次升级开始前的状态 |

升级后，建议新开 AI 会话；或者先让当前会话重新读取项目入口和当前任务文档，避免继续沿用旧规则。

## 多项目工作区

ForgeKit 支持可选的多项目工作区，但默认不会自动启用或拆分文档。

| 层级 | 作用 |
| --- | --- |
| Workspace Docs | 管理跨项目任务、联调状态和整体风险 |
| Project Capsule | 管理某个长期独立子项目的局部任务、测试和风险 |
| Repo | 保存代码，不成为第三套任务事实源 |
| Artifact | 保存报告、日志、构建物和测试证据 |
| Archive | 保存历史材料，不参与当前事实 |

常见做法：

```text
先把项目登记为 workspace-only；
只有长期独立推进的项目，再切换为 project-capsule。
```

创建最小 Project Capsule：

```powershell
python .\scripts\bootstrap-project-capsule.py plan --repo-root "D:\path\to\workspace" --project backend
python .\scripts\bootstrap-project-capsule.py apply --repo-root "D:\path\to\workspace" --project backend --confirm
```

它不会自动拆分总文档、迁移任务或移动业务仓库。

## 生成内容

| 路径 | 用途 |
| --- | --- |
| `AGENTS.md` | Codex 项目入口 |
| `CLAUDE.md` | Claude Code 项目入口 |
| `.agents/skills/` | 项目内按需 Skills |
| `.codex/` | Codex 规则、命令和可选配置 |
| `.forgekit/state.json` | 当前 ForgeKit 版本和功能状态 |
| `.forgekit/project-boundary.yml` | 项目边界和写入策略 |
| `.forgekit/workspace-map.json` | 可选的多项目边界地图 |
| `.forgekit/docs/` | 当前任务、来源、验证、风险、交接和工具链事实 |
| `.forgekit/projects/` | 可选的 Project Capsule |
| `.forgekit/changes/` | 中高风险变更的方案、任务、验证和审查记录 |
| `.forgekit/archive/` | 可检索的历史证据 |
| `scripts/` | 初始化、升级、检查和归档脚本 |

已有业务 `docs/` 默认作为只读证据使用。ForgeKit 不会默认把治理模板写进业务文档目录。

## 什么时候写回文档

文档写回按事件触发，不按“每改一次就写”。

| 场景 | 建议 |
| --- | --- |
| typo、临时试错、未确认探索 | 不写 ForgeKit 治理文档 |
| 任务状态变化、根因确认、新风险、有效验证 | 做最小 checkpoint |
| commit、交接、归档、发布准备 | 做收口写回 |
| 可预见的上下文压缩或换会话 | 先保存当前目标、结论、风险、验证和下一步 |

“小改动不写治理文档”不代表禁止修改任务范围内的业务代码、README、注释、测试或配置。

## 安全边界

ForgeKit 默认不会：

- 生成 Spring、React、FastAPI 等业务项目模板；
- 安装依赖、启动服务或部署业务系统；
- 在后台持续运行 Agent、守护进程或定时任务；
- 自动 commit、push、tag、创建 PR 或发布 release；
- 自动启用多项目模式或拆分现有文档；
- 自动覆盖用户定制的受管文件；
- 把一次 review 结果自动转化为修复授权。

AI 工具是否正确加载平台 Skill、如何选择 Skill，以及实际上下文收益，仍受具体客户端和版本影响。这些真实运行项继续标记为 `NEEDS_TEST`；首次在目标环境中使用时应做一次轻量验证。

## 常用检查

检查当前文档是否还能支撑未完成任务：

```powershell
python .\scripts\check-current-docs-integrity.py --repo-root "D:\path\to\project"
```

检查多项目边界：

```powershell
python .\scripts\check-workspace-integrity.py --repo-root "D:\path\to\workspace"
```

## 文档地图

| 你想看 | 文件 |
| --- | --- |
| 日常怎么问 AI | `.forgekit/docs/usage-playbook.md` |
| 什么时候写回文档 | `.forgekit/docs/work-session-checkpoint.md` |
| 哪个文档负责哪个事实 | `.forgekit/docs/document-responsibility.md` |
| 当前任务 | `.forgekit/docs/task-board.md` |
| 任务来源 | `.forgekit/docs/task-intake.md` |
| 验证方式和结论 | `.forgekit/docs/testing.md` |
| 风险和阻塞 | `.forgekit/docs/risk-register.md` |
| 项目边界 | `.forgekit/project-boundary.yml` |
| 多项目边界 | `.forgekit/workspace-map.json` |
| 版本变化 | `CHANGELOG.md` |

## 版本历史

完整版本历史和升级注意事项见 [CHANGELOG.md](CHANGELOG.md)。
