# ForgeKit

English documentation: [README.en.md](README.en.md)

ForgeKit 是一套轻量级 AI 工程交付工具包，用来把 Codex、Claude Code 等 AI 编程工具约束在可审查、可验证、可交接的项目流程里。

它不是业务框架脚手架，也不是自动部署平台。ForgeKit 生成的是项目内工作流骨架：入口说明、项目边界、AI skills、风险分级 change 工件、治理文档、检查脚本和可选 hook。

## 适用场景

ForgeKit 适合：

- 新项目启动时，让 AI 先澄清目标、边界、技术栈和验证方式，再开始编码。
- 接手既有项目时，让 AI 从 README、构建文件、脚本和旧文档中提取事实，而不是先猜技术栈。
- 中高风险变更前，要求 proposal / tasks / verification / review，必要时增加 design / ship / retro。
- 团队希望 Codex 和 Claude Code 使用同一套项目事实、命令、skills 和交付规则。

ForgeKit 不做：

- 不生成业务框架代码。
- 不安装依赖、启动服务或部署。
- 不默认启用 hook、MCP、memory、多 agent runtime 或外部账号集成。
- 不自动创建 issue / PR。
- 不自动 commit、tag 或 push。

## 快速开始

### 1. 生成项目模板

Windows PowerShell：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\projects\my-app" -ProjectName "my-app" -Mode Standard
```

Ubuntu / macOS：

```bash
./scripts/init-project-template.sh --target-path "$HOME/projects/my-app" --project-name "my-app" --mode Standard
```

模式只写入初始化 metadata，不裁剪复制文件：

| 模式 | 适用项目 |
| --- | --- |
| `Lite` | 小脚本、小工具、个人验证项目 |
| `Standard` | 普通应用、API、内部系统、数据处理项目 |
| `Enterprise` | 团队交付、生产系统、高风险变更、接手项目 |

不确定时先选 `Standard`。不要在生成模板时急着选择技术栈；新项目应在需求和约束澄清后确定，既有项目应先让 AI 从真实文件中推断。

### 2. 在生成项目中启动 AI 工具

Codex：

```powershell
cd D:\projects\my-app
codex
```

Claude Code：

```powershell
cd D:\projects\my-app
claude
```

### 3. 发送启动消息

Codex：

```text
请读取 AGENTS.md，并优先使用项目内 .agents/skills/project-init/SKILL.md，按 ForgeKit 流程帮我初始化这个项目。不要读取用户级或系统级 project-init 路径。
```

Claude Code：

```text
请读取 CLAUDE.md，并优先使用项目内 .agents/skills/project-init/SKILL.md，按 ForgeKit 流程帮我初始化这个项目。不要读取用户级或系统级 project-init 路径。
```

## 生成项目包含什么

生成项目后，Codex 从 `AGENTS.md` 开始，Claude Code 从 `CLAUDE.md` 开始。两者共享 `.codex/`、`.forgekit/`、`governance/` 和 `.agents/skills/`。

关键文件：

| 路径 | 用途 |
| --- | --- |
| `.forgekit/project-boundary.yml` | ForgeKitRoot、ProjectRoot、managed docs root、change root 和写入策略 |
| `.forgekit/docs/document-responsibility.md` | 管理文档职责矩阵：读者、触发条件、写什么、不写什么、默认读取策略 |
| `.forgekit/docs/codebase-map.md` | 代码搜索入口、模块入口和局部验证命令，不做项目百科 |
| `.forgekit/docs/local-toolchain.md` | 本地 lint、test、build、LSP 和工具链能力 |
| `.forgekit/docs/changelog.md` | 当前版本更新记录 |
| `.forgekit/docs/version-roadmap.md` | 版本路线图和推进闸门 |
| `.forgekit/docs/task-intake.md` | 工作来源台账：统一记录公司派发、个人规划、用户反馈、bug、技术债等来源，再判断是否生成可执行任务 |
| `.forgekit/docs/loop-readiness.md` | 判断项目是否具备安全运行 loop 的状态、验证、边界、停止和升级条件 |
| `.forgekit/docs/loop-blueprint.md` | 可审查的 loop 设计图纸，不是自动执行授权 |
| `.forgekit/docs/loop-operations.md` | 显式触发的 loop dry-run、one-step、continue、stop/handoff 操作协议，不是自动 runner |
| `.forgekit/docs/maker-checker-protocol.md` | Maker 写代码、Checker 独立复核的证据协议，不是自动多 agent 系统 |
| `.forgekit/docs/worktree-playbook.md` | 手动 worktree 并行隔离指南，不自动创建、调度、merge、push 或 PR |
| `.forgekit/changes/_template/` | proposal、design、tasks、verification、review、ship、retro 模板 |
| `.codex/commands.md` | 当前项目常用命令 |
| `.agents/skills/` | 项目自包含 skills |
| `governance/ai-engineering-loop.md` | 风险分级、change 工件和交付闭环 |

默认情况下，ForgeKit 治理文档写入 `.forgekit/docs/`，中高风险 change 工件写入 `.forgekit/changes/`。业务已有 `docs/` 是 read-mostly 证据源：AI 可以读取和引用，但不应默认把 ForgeKit 治理模板写进去。

## 核心能力

| 能力 | 作用 |
| --- | --- |
| `project-init` | 初始化访谈、项目入口整理、第一版项目事实 |
| `project-suitability` | 判断项目适合 Lite / Standard / Enterprise 还是 Custom |
| `document-backfill` | 逐篇读取既有业务文档，并回填 ForgeKit managed docs root |
| `handover-review` | 接手既有项目时做审计和风险识别 |
| `large-change-planning` | 大范围、跨模块、迁移或重构前先做探索和实施计划 |
| `code-review` | 面向 bug、回归风险和测试缺口的代码审查 |
| `release-check` | 发布前检查版本闸门、验证、回滚和交付记录 |
| `security-review` | 安全风险审查 |

Loop Readiness / Loop Blueprint 只提供 managed docs 模板和入口规则，用于评估一个项目是否适合安全运行 loop；ForgeKit 不提供自动 loop runner、daemon、cron、MCP、connector、自动 PR、多 agent 调度或 worktree 自动化。

Optional Loop Operation Mode 只定义用户显式触发的 dry-run、one-step、continue、stop/handoff 协议；loop 默认关闭，不提供后台自动化、无人值守 runner 或连续循环。

Maker / Checker Protocol 只定义中高风险代码变更的实现证据和独立复核证据：Maker 负责实现并声明 ready for check，Checker 复核 diff、验证、风险和文档同步后给出 pass / needs-fix / manual-review。它不是自动多 agent 系统。

Worktree Playbook 只提供手动 worktree 隔离规范，用于并行任务、实验分支和 AI 多会话协作；ForgeKit 不自动创建 worktree，不自动启动 agent，不自动 merge、push 或创建 PR。

工作来源统一要求公司派发、个人规划、用户反馈、bug 发现、技术债、测试失败或调研发现先写入 `.forgekit/docs/task-intake.md`：保留脱敏原文或原始想法、Update Notes、Task Decision、Derived Task IDs 和 `Human Review` 状态。小补充和确认默认更新已有 Source，不默认创建新任务。`task-board.md` 只接收有动作、owner、下一步、Source ID 和验证方式的可执行任务；`work-log.md` 只记录推进过程并引用 Task ID / Source ID。

管理文档职责矩阵 v2 把 `.forgekit/docs/**` 分成 `core`、`current`、`working`、`triggered`、`reference`、`generated`、`archive`。AI 默认先读 `document-responsibility.md` 和 `codebase-map.md`，再按任务触发读取相关文档；不要全量读取 docs，也不要把同一事实重复写进多个文档。

AI Engineering Loop 按风险控制工件数量：

| 风险 | 建议工件 |
| --- | --- |
| low | proposal / verification / review |
| medium | proposal / tasks / verification / review |
| high | proposal / design / tasks / verification / review / ship |

`retro` 只在重大变更、事故、失败复盘或团队要求时推荐。

## 常用命令

### 模板仓库验证

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-template.ps1
```

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-plugin-assets.ps1
```

```bash
bash scripts/smoke-test.sh
python3 scripts/update-template-manifest.py --check --repo-root .
```

### 生成项目内检查

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-harness-check.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\check-doc-sync.ps1
```

```bash
./scripts/check-doc-sync.sh
```

这些脚本只做检查、复制模板或安装本地 opt-in hook，不会自动安装依赖、启动服务、部署、commit、tag 或 push。

## 变更归档

ForgeKit 把当前事实和历史过程分开：

- 当前事实放在 `.forgekit/docs/`。
- 活跃或刚完成的变更放在 `.forgekit/changes/`。
- 历史变更放在 `.forgekit/archive/changes/YYYY/`。

归档链路：

```bash
python3 scripts/archive-changes.py --dry-run
python3 scripts/archive-changes.py --reference-check --plan .forgekit/archive-plan.md
python3 scripts/archive-changes.py --sync-check --plan .forgekit/archive-plan.md
python3 scripts/archive-changes.py --smart-check --plan .forgekit/archive-plan.md --reference-report .forgekit/archive-reference-report.md --sync-report .forgekit/current-docs-sync-report.md
python3 scripts/archive-changes.py --smart-apply --report .forgekit/smart-archive-report.md --confirm
```

`--smart-apply` 只会在 Git clean 且用户显式 `--confirm` 后，移动 `.forgekit/smart-archive-report.md` 中 `Smart-Status: auto_archive_candidate` 的条目，并生成 `.forgekit/smart-archive-apply-report.md`。

## 升级已有项目

从旧版本 ForgeKit 升级到新版本时，使用升级模式，不要用 `-Force` / `--force`：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\projects\my-app" -ProjectName "my-app" -Mode Standard -Upgrade -ExportUpgradeTemplates
```

```bash
./scripts/init-project-template.sh --target-path "$HOME/projects/my-app" --project-name "my-app" --mode Standard --upgrade --export-upgrade-templates
```

升级模式只生成报告和候选模板，不覆盖项目文件：

- 保留已有项目事实、`.forgekit/template-lock.json`、business `docs/`、`.codex/`、`AGENTS.md`、`CLAUDE.md`。
- 把 skip / can_replace / needs_merge_report / can_restore / ask / readonly 分类写入 `.forgekit/upgrade-report.md`。
- 把新版候选模板按目标路径导出到 `.forgekit/upgrade-export/<version>/`。
- 旧项目缺少 `.forgekit/template-lock.json` 时只输出 `legacy_no_lock` 报告，不自动补 lock。

升级后可让 AI 执行：

```text
请读取 .forgekit/upgrade-report.md，对比 .forgekit/upgrade-export/，只把有价值的新模板段落合并进现有项目文件，不要覆盖项目真实事实，也不要把 upgrade-export 当作当前态文档。
```

## 接手既有项目

接手已有项目时，AI 不应先问技术栈。它应该先读 README、安装说明、启动脚本、测试说明、部署说明、API 文档、构建文件和依赖文件，从证据里抽取答案；只有文档缺失、冲突或过期时才追问。

如果旧文档很多，使用：

```text
请使用 document-backfill，逐篇阅读 <旧文档目录> 里的文档，并一边读一边补全 ForgeKit managed docs root。不要一次性全部读进去总结。
```

## 可选 Hook

ForgeKit 默认不启用 hook。需要文档同步提醒时，可以安装 opt-in Git hook：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-hooks.ps1 -Profile docs-warn -Target git
```

```bash
./scripts/install-hooks.sh --profile docs-warn --target git
```

`docs-warn` 只提示不阻断；团队确认噪音可接受后再使用 `docs-strict`。

## Plugin Distribution

ForgeKit 使用根级统一分发结构：

```text
.codex-plugin/plugin.json
.claude-plugin/plugin.json
.agents/plugins/marketplace.json
.claude-plugin/marketplace.json
skills/
project-template/
templates/
questionnaires/
scripts/
```

`.codex-plugin/plugin.json` 和 `.claude-plugin/plugin.json` 都指向共享的 `./skills/`。

## 与 ECC 的边界

ECC 更像 AI 编程工具增强套件，覆盖 commands、hooks、memory、MCP、多 agent、安全工具和跨工具适配。ForgeKit 的职责更窄：约束具体项目的交付流程，让项目更适合 AI 稳定接手。

ForgeKit 可以和 ECC 共存：ECC 增强 AI 工具，ForgeKit 约束项目现场。

## 最近版本

| 版本 | 用户可感知变化 |
| --- | --- |
| `0.28.5` | Work Source Unification：把公司派发、个人规划、用户反馈、bug、技术债等统一纳入 Source ID -> Task ID -> Work Log 链路。 |
| `0.28.4` | Source-to-Task Alignment：收紧 task-intake、task-board、work-log 的对应关系，补充和确认默认归并到已有 Source，任务看板只接收可执行任务。 |
| `0.28.3` | 触发式管理文档中文化：loop、maker-checker、worktree 和 change 模板改为中文用户可读文案，保留机器字段。 |
| `0.28.2` | 管理文档职责矩阵 v2：收紧管理文档职责、默认读取策略和重复写入边界，让用户可读文档更短、更自然。 |
| `0.28.1` | 任务来源优先：新增 `.forgekit/docs/task-intake.md`，保留任务派发原文、AI 分析、任务反链和人工确认状态。 |
| `0.28.0` | Worktree Playbook：新增手动 worktree 并行隔离指南和入口短规则，不提供自动 worktree 调度。 |
| `0.27.0` | Optional Loop Operation Mode：新增显式触发的 loop dry-run / one-step / continue / stop-handoff 操作协议，不提供自动 runner。 |
| `0.26.0` | Maker / Checker Protocol：新增 managed docs 模板和 review 证据字段，用于分离实现和复核，不提供自动多 agent 调度。 |
| `0.25.0` | Loop Readiness / Loop Blueprint：新增 managed docs 模板和入口短规则，用于评估与设计可审查 loop，不提供自动 runner。 |
| `0.24.0` | Smart Archive Apply：在 Git clean 且用户显式确认后，只归档 Smart Archive Advisor 标记为 `auto_archive_candidate` 的 change，并生成 apply 报告。 |
| `0.23.0` | Smart Archive Advisor：综合 archive plan、reference report 和 sync report 生成智能归档建议报告，仍然 report-only。 |
| `0.22.0` | Current Docs Sync Check：基于 archive plan candidates 生成 current docs 同步证据报告，不修改项目事实文件。 |
| `0.21.1` | Work Log Managed Doc Template：新增 `.forgekit/docs/work-log.md`，用于个人工作顺序、交接上下文和中断恢复记录。 |
| `0.21.0` | Archive Reference Check：基于 archive plan candidates 生成引用报告，检查 current docs、活跃 change 和入口文档中的字符串引用。 |
| `0.20.0` | Archive Apply：在 Git clean 且用户显式 `--confirm` 后，按 dry-run plan 移动候选 change 并生成 apply report。 |
| `0.19.0` | Archive Plan：新增 dry-run 归档计划，只生成或覆盖 `.forgekit/archive-plan.md`，不移动文件。 |
| `0.18.0` | Document Lifecycle：新增 current docs / changes / archive 三层规则，archive 默认不读，done change 只提示可归档。 |
| `0.17.0` | Template Versioning：新增 template manifest / lock，升级时只生成 report-only 分类和候选模板，不自动覆盖项目文件。 |
| `0.16.0` | Boundary First：新增 `.forgekit/project-boundary.yml`，新项目默认把 ForgeKit managed docs 写入 `.forgekit/docs`，change 工件写入 `.forgekit/changes`。 |
| `0.15.0` | 将定位升级为轻量级 AI 工程交付工具包，加入 AI Engineering Loop 和风险分级 change 模板。 |
