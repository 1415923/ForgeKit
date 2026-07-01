# ForgeKit

English documentation: [README.en.md](README.en.md)

ForgeKit 是一套轻量级 AI 工程交付工具包，用来把 Codex、Claude Code 等 AI 编程工具约束在**可审查、可验证、可交接**的项目流程里。

它不生成业务框架代码，也不替你部署系统。ForgeKit 做的是：在项目本地生成一层 AI 交付工作区，让 AI 知道项目边界、任务来源、验证方式、风险、交接材料和什么时候该停下来等你确认。

---

## 一句话理解

```text
ForgeKit = 给 AI 编程工具用的本地项目交付规则、文档和检查工具。
```

它解决的不是“AI 会不会写代码”，而是：

```text
AI 该改哪里？
任务从哪来？
现在做到哪了？
怎么验证？
风险是什么？
什么时候写文档？
怎么交接给下一个会话 / reviewer / 同事？
```

---

## 什么时候用 ForgeKit

| 场景 | ForgeKit 帮你做什么 |
| --- | --- |
| 新项目启动 | 先澄清目标、边界、技术栈和验证方式，再让 AI 写代码 |
| 接手已有项目 | 先只读盘点 README、脚本、构建文件和旧文档，避免 AI 乱猜 |
| 中高风险变更 | 生成 proposal / tasks / verification / review，必要时增加 design / ship |
| 长会话开发 | 在阶段边界、compact 前、换会话前做 checkpoint，防止细节丢失 |
| 多 AI 工具协作 | 让 Codex 和 Claude Code 读取同一套项目事实和规则 |
| 多 repo / 多项目工作区 | 用 workspace map 区分 workspace、project、repo、artifact、archive |
| 阶段交付 | 生成 handoff、archive capsule、review-ready summary |

不适合：

| 不适合的事 | 原因 |
| --- | --- |
| 业务框架脚手架 | ForgeKit 不生成 Spring / React / FastAPI 业务模板 |
| 自动部署平台 | 不安装依赖、不启动服务、不部署、不发布 |
| 后台自动任务系统 | 不提供 runner、daemon、scheduler |
| 自动 Git 系统 | 不自动 commit、tag、push、PR |
| 外部账号集成 | 默认不接 GitHub issue、MCP、memory、云服务账号 |

---

## 快速开始

下面三步通常可在 3 分钟内完成。

### 1. 在 ForgeKit 仓库里初始化或同步目标项目

Windows PowerShell：

```powershell
python .\scripts\forgekit-project.py --target "D:\path\to\project"
```

macOS / Linux：

```bash
python3 ./scripts/forgekit-project.py --target "/path/to/project"
```

这个统一入口会自动判断：

| 目标状态 | ForgeKit 行为 |
| --- | --- |
| 未安装 ForgeKit | 展示初始化计划 |
| 已是当前版本 | 显示 up-to-date |
| 版本落后 | 先 check + plan，确认后才 apply |
| 工具版本太旧 | 停止并提示先更新外层 ForgeKit |
| legacy 项目 | 给 adoption guidance，不自动强行升级 |

默认不会直接写入；需要你确认或传入 `--yes` 才执行安全操作。

只有 v0.36.0 及以后初始化、且具有 `.forgekit/state.json` 的项目支持安全迁移；v0.35.x 及更早项目按“接手已有项目”处理，不自动升级。

需要在首次初始化时同时生成可审查的 Claude Code / Codex agent 配置，可使用底层高级入口：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\path\to\workspace" -ProjectName "my-app" -Mode Standard -NativeAgentAdapter all
```

该参数只生成配置，不代表运行时已经注册 agent。

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

### 3. 发启动提示词

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

详细变体见生成项目中的：

```text
.forgekit/docs/usage-playbook.md
```

日常先用下面这些短提示词就够了。

| 你想做什么 | 直接复制给 Claude / Codex |
| --- | --- |
| 初始化新项目 | `请使用 ForgeKitRoot 统一入口初始化 <project-root>，先展示计划，不要自动提交。` |
| 接手已有项目 | `先只读盘点 <project-root>，按 existing-project adoption 给出计划后等我确认。` |
| 更新项目中的 ForgeKit | `外层 ForgeKit 已更新，请对 <project-root> 做 check 和 plan，未经确认不要 apply。` |
| 开始今天工作 | `按 workflow router 读取当前任务、最近进展、风险和验证入口，给我今天的下一步。` |
| 执行一个任务 | `执行 <Task ID>，先确认范围和验证方式，完成后做最小 checkpoint。` |
| 保存当前进展 | `只把本轮已确认的状态、验证、风险和下一步最小写回负责文档。` |
| compact / clear 前 | `做 pre-compact checkpoint，并告诉我新会话应先读哪些文件。` |
| compact 后恢复 | `刚发生 compact / 换会话。请先只读恢复当前目标、最近结论、风险、验证和下一步，不要改文件。` |
| 提交前检查 | `检查 diff、验证、独立 review、风险和最小写回，不要自动 commit。` |
| 阶段结束归档 | `先检查 current docs integrity，再生成 Archive Capsule plan，不要直接 apply。` |
| 生成交接材料 | `生成 review-ready handoff，缺证据标 TODO_REVIEW，不要编造。` |
| 多项目只读分析 | `按 workspace map 只读分析命中的 project/repo，不启用 map 或创建 capsule。` |
| 启用 multi-project 前检查 | `先运行 workspace integrity check，只给 adoption guidance，不自动启用。` |
| 第一性原理分析 | `从第一性原理出发，重新分析这个问题的事实、假设、约束和最小正确机制。` |
| 对抗式审查 | `做一次 adversarial review，专门找失败路径、边界条件和验证缺口。` |

---

## 什么时候更新 ForgeKit 文档

ForgeKit v0.42 起，文档写回按事件触发，不按“每改一下就写”。

| 粒度 | 是否写 ForgeKit managed docs | 典型场景 |
| --- | --- | --- |
| Micro Update | 不写 | typo、小参数、临时试错、单次失败命令、未确认探索 |
| Checkpoint Update | 最小写回 | 小闭环完成、任务状态变化、根因确认、新风险、有效验证、准备中断/换会话 |
| Ship Update | 收口写回 | commit、tag、handoff、archive、发布前 |

写回位置：

| 信息 | 写到哪里 |
| --- | --- |
| 今天做了什么、下一步 | `.forgekit/docs/work-log.md` |
| 任务状态变化 | `.forgekit/docs/task-board.md` |
| 验证结论和缺口 | `.forgekit/docs/testing.md` |
| 风险和阻塞 | `.forgekit/docs/risk-register.md` |
| 用户/版本可见变化 | `CHANGELOG.md` |
| 来源事实变化 | `task-intake.md` 或 project `source-links.md` |

注意：

```text
Micro Update 只是不写 ForgeKit governance docs，
不代表禁止修改任务授权范围内的业务代码、业务 README、注释、测试或配置。
```

可预见的 compact、clear 或换会话前，先做 pre-compact checkpoint。
如果发生不可预见的 auto compact，恢复后第一步先做 post-compact recovery check。

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
| `apply --safe` | 只执行 migration 标记为 safe 的动作 |

### 检查 current docs 是否断链

Windows：

```powershell
python .\scripts\check-current-docs-integrity.py --repo-root "D:\path\to\project"
```

macOS / Linux：

```bash
python3 ./scripts/check-current-docs-integrity.py --repo-root "/path/to/project"
```

### 检查 multi-project workspace 边界

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
| `.codex/` | Codex rules、commands、可选 agent 配置 |
| `.forgekit/state.json` | ForgeKit 项目版本和 feature 状态 |
| `.forgekit/project-boundary.yml` | 项目边界和写入策略 |
| `.forgekit/workspace-map.json` | 多项目 workspace 的机器可读边界地图，默认 disabled |
| `.forgekit/docs/` | 当前项目事实、任务、验证、风险、交接、工具链说明 |
| `.forgekit/projects/_template/` | Project Capsule 最小模板 |
| `.forgekit/changes/` | 中高风险变更的 proposal / design / tasks / verification / review |
| `.forgekit/archive/` | 历史证据和 archive capsule |
| `scripts/` | 初始化、升级、检查、归档等脚本 |

已有业务 `docs/` 默认是 read-mostly evidence。AI 可以读取和引用，但不应默认把 ForgeKit 治理模板写进去。

---

## 核心能力

| 能力 | 解决什么问题 |
| --- | --- |
| Boundary-first workspace | 避免 AI 搞错 ForgeKitRoot、ProjectRoot、业务 repo 和 artifact |
| Source-first task intake | 先记录任务来源，再决定是否生成可执行任务 |
| Risk-based change artifacts | 按风险生成 proposal / tasks / verification / review / design / ship |
| Managed docs responsibility | 明确哪些文档负责哪些事实，减少重复写入 |
| Work session checkpoint | 解决“每小改都写”和“一天结束也没写”的两极问题 |
| Context Continuity Protocol | compact、换会话、handoff 前保留关键事实 |
| Active current docs integrity | 防止 archive 后 current docs 接不上 active tasks |
| Project maintenance operations | 统一 init、upgrade、archive、handoff、doc-health 等维护入口 |
| Native Agent Adapter | 可选生成 Claude Code / Codex agent 配置；是否注册和调用仍需运行时验证 |
| Independent Code Review Protocol | maker 和 reviewer 分离，避免自审冒充独立审查 |
| First-principles pass | 复杂问题先从事实、假设、约束推导最小正确机制 |
| Adversarial review | 高风险收口前主动找失败路径 |
| Multi-project scoped docs | 区分 workspace、project、repo、artifact、archive 边界 |
| Safe migration | 版本升级先 plan，safe apply 不覆盖用户内容 |

---

## 多项目工作区怎么理解

ForgeKit v0.41 起支持 opt-in multi-project workspace。

| 层级 | 作用 |
| --- | --- |
| Workspace Docs | 管跨项目事实，例如 overall task、联调状态、跨项目风险 |
| Project Capsule | 管项目局部事实，例如 backend 的局部任务、测试、风险 |
| Repo Lite | 只作为代码仓库薄入口，不成为第三套事实源 |
| Artifact | 报告样本、运行日志、构建物、测试输出等证据位置 |
| Archive | 历史证据，不参与 current truth |

默认只安装 disabled `.forgekit/workspace-map.json` 和 `_template`，不会自动启用，也不会自动拆分现有文档。

常见方式：

```text
先使用 workspace-only 登记 project；
等某个 project 长期独立推进，再切换为 project-capsule。
```

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
| 每次小改都要更新文档 | 不需要，Micro Update 不写 ForgeKit governance docs |
| 一天结束不用写文档 | 不对，应该做最小 checkpoint |
| archive 就是删除旧文件 | 不是，archive 是可检索历史证据 |
| multi-project 会自动拆文档 | 不会，只提供 map、模板和检查器 |
| Project Capsule 是完整 ForgeKit 副本 | 不是，它只是最小局部事实集 |
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
