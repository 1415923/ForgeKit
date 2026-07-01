# ForgeKit

English documentation: [README.en.md](README.en.md)

ForgeKit 是一套轻量级 AI 工程交付工具包。它帮你把 Codex、Claude Code 等 AI 编程工具约束在一个**可审查、可验证、可交接**的项目流程里。

ForgeKit 不生成业务框架代码，也不替你部署系统。它只在项目本地放一层“AI 交付工作区”，让 AI 明确知道：哪些文件能改、任务从哪来、现在做到哪、怎么验证、风险是什么、什么时候该停下来等你确认。

---

## 一句话理解

```text
ForgeKit = 给 AI 编程工具用的本地交付规则、文档和检查工具。
```

它重点解决这些问题：

```text
AI 该改哪里？
任务从哪来？
现在做到哪了？
怎么验证？
还有什么风险？
什么时候该保存进展？
下一个会话或同事怎么接着做？
```

---

## 适合什么场景

| 场景 | ForgeKit 能帮你做什么 |
| --- | --- |
| 新项目启动 | 先确认目标、边界、技术栈和验证方式，再让 AI 写代码 |
| 接手已有项目 | 先只读盘点 README、脚本、构建文件和旧文档，避免 AI 乱猜 |
| 中高风险变更 | 要求先写方案、任务、验证和审查记录，必要时再补设计和发布说明 |
| 长会话开发 | 在上下文压缩、换会话或阶段结束前保存关键进展 |
| 多个 AI 工具协作 | 让 Codex 和 Claude Code 读取同一套项目事实 |
| 多仓库 / 多子项目 | 区分总工作区、子项目、代码仓库、证据目录和历史归档 |
| 阶段交付 | 生成交接材料、归档计划和可审查总结 |

不适合：

| 不适合的事 | 原因 |
| --- | --- |
| 业务脚手架 | 不生成 Spring、React、FastAPI 等业务模板 |
| 自动部署平台 | 不安装依赖、不启动服务、不部署、不发布 |
| 后台自动任务 | 不提供后台运行器、守护进程或定时器 |
| 自动 Git 操作 | 不自动 commit、tag、push 或创建 PR |
| 外部账号集成 | 默认不接 GitHub issue、MCP、memory 或云服务账号 |

---

## 快速开始

通常按下面三步走。

### 1. 初始化或同步目标项目

在 ForgeKit 仓库里执行：

Windows PowerShell：

```powershell
python .\scripts\forgekit-project.py --target "D:\path\to\project"
```

macOS / Linux：

```bash
python3 ./scripts/forgekit-project.py --target "/path/to/project"
```

这个统一入口会自动判断目标项目的状态：

| 目标状态 | ForgeKit 的处理方式 |
| --- | --- |
| 还没安装 ForgeKit | 展示初始化计划 |
| 已经是当前版本 | 显示 up-to-date |
| 版本落后 | 先检查并生成升级计划，确认后才应用安全迁移 |
| 外层 ForgeKit 太旧 | 停止，并提示先更新 ForgeKit |
| 很早期的旧项目 | 给出接手建议，不自动强行升级 |

默认不会直接写入。需要你确认，或显式传入 `--yes`，才会执行安全操作。

只有 v0.36.0 及以后初始化、且具有 `.forgekit/state.json` 的项目支持安全迁移。v0.35.x 及更早项目按“接手已有项目”处理，不自动升级。

需要在首次初始化时同时生成 Claude Code / Codex 的可审查 agent 配置，可以使用底层高级入口：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\path\to\workspace" -ProjectName "my-app" -Mode Standard -NativeAgentAdapter all
```

这个参数只生成配置，不代表运行时已经注册成功。首次真实使用时仍要验证。

---

### 2. 在项目根目录启动 AI 工具

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

---

### 3. 发送启动提示词

Codex：

```text
请读取 AGENTS.md，并优先使用项目内 .agents/skills/project-init/SKILL.md，按 ForgeKit 流程理解当前项目。先告诉我项目边界、当前任务、风险和建议下一步，不要直接改文件。
```

Claude Code：

```text
请读取 CLAUDE.md，按 ForgeKit 流程理解当前项目。先告诉我项目边界、当前任务、风险和建议下一步，不要直接改文件。
```

---

## 最常用提示词

详细说法见生成项目中的：

```text
.forgekit/docs/usage-playbook.md
```

日常先用下面这些短提示词就够了。

| 你想做什么 | 直接复制给 Claude / Codex |
| --- | --- |
| 初始化新项目 | `请使用 ForgeKit 统一入口初始化 <project-root>，先展示计划，不要自动提交。` |
| 接手已有项目 | `请先只读盘点 <project-root>，给出接手计划后等我确认。` |
| 更新项目中的 ForgeKit | `外层 ForgeKit 已更新，请对 <project-root> 做检查和升级计划，未经确认不要应用。` |
| 开始今天工作 | `请按 ForgeKit 流程读取当前任务、最近进展、风险和验证入口，给我今天的下一步。` |
| 执行一个任务 | `执行 <Task ID>，先确认范围和验证方式，完成后做最小进展保存。` |
| 保存当前进展 | `只把本轮已确认的状态、验证、风险和下一步最小写回负责文档。` |
| 上下文压缩 / 清空前 | `请做一次压缩前进展保存，并告诉我新会话应先读哪些文件。` |
| 压缩后恢复 | `刚发生上下文压缩 / 换会话。请先只读恢复当前目标、最近结论、风险、验证和下一步，不要改文件。` |
| 提交前检查 | `请检查 diff、验证、独立审查、风险和最小文档写回，不要自动 commit。` |
| 阶段结束归档 | `请先检查当前文档是否还能接上任务，再生成归档计划，不要直接应用。` |
| 生成交接材料 | `请生成可审查的交接材料，缺证据标 TODO_REVIEW，不要编造。` |
| 多项目只读分析 | `请按工作区地图只读分析命中的子项目和代码仓库，不启用地图、不创建子项目文档包。` |
| 启用多项目地图前检查 | `请先运行工作区边界检查，只给接手建议，不自动启用。` |
| 创建子项目文档包 | `请为 <project-id> 创建最小子项目文档包。先确认工作区地图中该项目已设为 project-capsule，然后运行 bootstrap plan，不要直接 apply。` |
| 第一性原理分析 | `请从第一性原理出发，重新分析这个问题的事实、假设、约束和最小正确机制。` |
| 对抗式审查 | `请做一次对抗式审查，专门找失败路径、边界条件和验证缺口。` |

说明：表格里的 `project-capsule`、`bootstrap plan`、`apply` 是脚本和配置里的固定写法，所以保留英文。其他概念尽量使用中文。

---

## 什么时候更新 ForgeKit 文档

ForgeKit v0.42 起，文档写回按事件触发，不按“每改一下就写”。

| 粒度 | 是否写 ForgeKit 治理文档 | 典型场景 |
| --- | --- | --- |
| 小改动 | 不写 | typo、小参数、临时试错、单次失败命令、未确认探索 |
| 进展保存 | 最小写回 | 小闭环完成、任务状态变化、根因确认、新风险、有效验证、准备中断或换会话 |
| 收口写回 | 收口检查并写回 | commit、tag、交接、归档、发布前 |

写回位置：

| 信息 | 写到哪里 |
| --- | --- |
| 今天做了什么、下一步 | `.forgekit/docs/work-log.md` |
| 任务状态变化 | `.forgekit/docs/task-board.md` |
| 验证结论和缺口 | `.forgekit/docs/testing.md` |
| 风险和阻塞 | `.forgekit/docs/risk-register.md` |
| 用户或版本可见变化 | `CHANGELOG.md` |
| 来源事实变化 | `task-intake.md` 或子项目的 `source-links.md` |

注意：

```text
“小改动不写文档”只是不写 ForgeKit 治理文档，
不代表禁止修改任务范围内的业务代码、业务 README、注释、测试或配置。
```

可预见的上下文压缩、清空或换会话前，先做一次进展保存。  
如果发生不可预见的自动压缩，恢复后第一步先做只读恢复检查。

---

## 常用命令

### 更新 / 同步项目中的 ForgeKit

Windows：

```powershell
python .\scripts\forgekit-project.py --target "D:\path\to\project"
powershell -ExecutionPolicy Bypass -File .\scripts\forgekit-project.ps1 --target "D:\path\to\project"
```

macOS / Linux：

```bash
python3 ./scripts/forgekit-project.py --target "/path/to/project"
bash ./scripts/forgekit-project.sh --target "/path/to/project"
```

### 低层升级入口

```bash
python scripts/forgekit-upgrade.py check --repo-root <project>
python scripts/forgekit-upgrade.py plan --repo-root <project>
python scripts/forgekit-upgrade.py apply --safe --repo-root <project>
```

| 命令 | 作用 |
| --- | --- |
| `check` | 检查版本和迁移资格，不写文件 |
| `plan` | 输出迁移计划，不写文件 |
| `apply --safe` | 只执行迁移包里标记为安全的动作 |

### 创建子项目文档包

当某个子项目需要长期独立维护局部任务、测试、风险和决策时，先在 `.forgekit/workspace-map.json` 中把它设为 `project-capsule`，再运行：

```powershell
python .\scripts\bootstrap-project-capsule.py plan --repo-root "D:\path\to\workspace" --project backend
python .\scripts\bootstrap-project-capsule.py apply --repo-root "D:\path\to\workspace" --project backend --confirm
```

这个命令只会创建最小子项目文档包。它不会拆分现有总文档，不会迁移任务，也不会生成代码仓库入口。

### 检查当前文档是否断链

Windows：

```powershell
python .\scripts\check-current-docs-integrity.py --repo-root "D:\path\to\project"
```

macOS / Linux：

```bash
python3 ./scripts/check-current-docs-integrity.py --repo-root "/path/to/project"
```

### 检查多项目工作区边界

Windows：

```powershell
python .\scripts\check-workspace-integrity.py --repo-root "D:\path\to\workspace"
```

macOS / Linux：

```bash
python3 ./scripts/check-workspace-integrity.py --repo-root "/path/to/workspace"
```

---

## 生成内容概览

| 路径 | 用途 |
| --- | --- |
| `AGENTS.md` | Codex 项目入口 |
| `CLAUDE.md` | Claude Code 项目入口 |
| `.agents/skills/` | 项目自包含 skills |
| `.codex/` | Codex 规则、命令、可选 agent 配置 |
| `.forgekit/state.json` | ForgeKit 项目版本和功能状态 |
| `.forgekit/project-boundary.yml` | 项目边界和写入策略 |
| `.forgekit/workspace-map.json` | 多项目工作区的机器可读边界地图，默认关闭 |
| `.forgekit/docs/` | 当前项目事实、任务、验证、风险、交接、工具链说明 |
| `.forgekit/projects/_template/` | 子项目文档包的最小模板 |
| `.forgekit/changes/` | 中高风险变更的方案、设计、任务、验证、审查记录 |
| `.forgekit/archive/` | 历史证据和归档包 |
| `scripts/` | 初始化、升级、检查、归档等脚本 |

已有业务 `docs/` 默认是只读证据。AI 可以读取和引用，但不应默认把 ForgeKit 治理模板写进去。

---

## 核心能力

| 能力 | 解决什么问题 |
| --- | --- |
| 边界优先工作区 | 避免 AI 搞错 ForgeKit 根目录、业务项目、代码仓库和证据目录 |
| 来源优先任务记录 | 先记录任务来源，再决定是否生成可执行任务 |
| 风险分级变更记录 | 按风险生成方案、任务、验证、审查、设计和发布记录 |
| 文档职责分工 | 明确哪些文档负责哪些事实，减少重复写入 |
| 工作会话进展保存 | 解决“每小改都写”和“一天结束也没写”的两极问题 |
| 上下文连续性 | 在上下文压缩、换会话、交接前保留关键事实 |
| 当前文档完整性检查 | 防止归档后当前任务接不上 |
| 项目维护流程 | 统一初始化、升级、归档、交接和报告入口 |
| 可选原生 agent 配置 | 可选生成 Claude Code / Codex agent 配置，是否注册和调用仍需验证 |
| 独立代码审查 | 实现者和只读审查者分离，避免自审冒充独立审查 |
| 第一性原理分析 | 复杂问题先从事实、假设、约束推导最小正确机制 |
| 对抗式审查 | 高风险收口前主动找失败路径 |
| 多项目分层文档 | 区分总工作区、子项目、代码仓库、证据目录和历史归档 |
| 安全迁移 | 版本升级先生成计划，安全应用不覆盖用户内容 |

---

## 多项目工作区怎么理解

ForgeKit v0.41 起支持可选的多项目工作区。

| 层级 | 通俗理解 | 作用 |
| --- | --- | --- |
| 总工作区文档 | 总账本 | 管跨项目事实，例如整体任务、联调状态、跨项目风险 |
| 子项目文档包 | 某个子项目的小账本 | 管项目局部事实，例如后端自己的任务、测试、风险 |
| 代码仓库 | 代码本体 | 保存业务代码，不成为第三套任务事实源 |
| 证据目录 | 附件 / 证据 | 报告样本、运行日志、构建物、测试输出 |
| 历史归档 | 旧材料 | 保存历史证据，不参与当前事实 |

默认只安装关闭状态的 `.forgekit/workspace-map.json` 和子项目文档包模板，不会自动启用，也不会自动拆分现有文档。

常见方式：

```text
先把子项目登记为 workspace-only，继续用总工作区文档管理；
等某个子项目长期独立推进，再切换为 project-capsule，并创建子项目文档包。
```

`Project Capsule` 在中文里可以理解成“子项目文档包”。它不是完整 ForgeKit 副本，也不是压缩包，只是某个子项目自己的最小局部文档集。

---

## 风险分级工件

| 风险 | 建议工件 |
| --- | --- |
| low | proposal / verification / review |
| medium | proposal / tasks / verification / review |
| high | proposal / design / tasks / verification / review / ship |

`retro` 只在重大变更、事故、失败交付或团队明确要求时使用。

---

## 常见误解

| 误解 | 实际情况 |
| --- | --- |
| ForgeKit 会生成业务项目代码 | 不会，它只生成 AI 交付工作区 |
| ForgeKit 会自动部署 / 发布 | 不会 |
| ForgeKit 会自动 commit / push | 不会 |
| 每次小改都要更新文档 | 不需要，小改动不写 ForgeKit 治理文档 |
| 一天结束不用写文档 | 不对，应该做最小进展保存 |
| 归档就是删除旧文件 | 不是，归档是可检索历史证据 |
| 多项目模式会自动拆文档 | 不会，只提供地图、模板和检查器 |
| 子项目文档包是完整 ForgeKit 副本 | 不是，它只是最小局部事实集 |
| Codex / Claude 自动读取了新规则 | 不一定，升级后新任务建议新开会话 |

---

## 文档地图

| 你想看 | 文件 |
| --- | --- |
| 日常怎么问 AI | `.forgekit/docs/usage-playbook.md` |
| 什么时候写文档 | `.forgekit/docs/work-session-checkpoint.md` |
| 哪些文档负责哪些事实 | `.forgekit/docs/document-responsibility.md` |
| 当前任务 | `.forgekit/docs/task-board.md` |
| 工作来源 | `.forgekit/docs/task-intake.md` |
| 验证方式和结论 | `.forgekit/docs/testing.md` |
| 风险和阻塞 | `.forgekit/docs/risk-register.md` |
| 项目边界 | `.forgekit/project-boundary.yml` |
| 多项目边界 | `.forgekit/workspace-map.json` |
| 当前版本变化 | `CHANGELOG.md` |

---

## 版本历史

完整版本历史、设计取舍和每个版本解决的真实痛点见：

```text
CHANGELOG.md
```

README 只保留当前定位、快速开始、常用入口和日常使用方式。
