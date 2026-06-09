# ForgeKit

English documentation: [README.en.md](README.en.md)

**ForgeKit 是一套轻量级 AI 工程交付工具包。**

它不是业务框架脚手架，也不是自动部署工具。ForgeKit 的目标是把 Codex、Claude Code 等 AI 编程工具从随意提示拉回可审查的工程交付：先澄清目标和风险，再按风险等级生成必要工件，最后完成验证、审查、发布记录和复盘。

一句话：ForgeKit 提供一个轻量 AI Engineering Loop，让 AI 助手先问清楚目标、方案、风险和验证方式，再进入编码和交付。

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

模式选择：

| 模式 | 适用项目 |
| --- | --- |
| `Lite` | 小脚本、小工具、个人验证项目 |
| `Standard` | 普通应用、API、内部系统、数据处理项目 |
| `Enterprise` | 团队交付、生产系统、高风险变更、接手项目 |

不确定时先选 `Standard`。`Mode` 只写入初始化 metadata，用于后续 AI 填充优先级和治理强度讨论；当前版本不按模式裁剪复制文件。不要在这一步急着选择技术栈；新项目的技术栈应在方案讨论后确定，既有项目应先由 AI 扫描现有文件推断。

### 2. 进入生成项目并启动 AI 工具

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

## 核心能力

- `project-init`：初始化访谈和项目入口整理。
- `project-suitability`：判断项目适合 Lite / Standard / Enterprise 还是 Custom。
- `document-backfill`：逐篇读取既有业务文档，并回填 ForgeKit managed docs root。
- `handover-review`：接手既有项目时做审计和风险识别。
- `large-change-planning`：大范围、跨模块、迁移或重构前先做探索和实施计划。
- `code-review`、`release-check`、`security-review`：代码审查、发布检查和安全审查。
- AI Engineering Loop：低风险轻流程，中风险需要 proposal / tasks / verification / review，高风险增加 design / ship，retro 只在重大变更后推荐。
- 可选文档同步检查和 Git hook：提示相关文档未同步、过期描述和版本记录缺少原因。

生成项目后，Codex 从 `AGENTS.md` 开始，Claude Code 从 `CLAUDE.md` 开始。两者共享 `.codex/`、`.forgekit/`、`governance/` 和 `.agents/skills/`。

生成项目里的关键文件：

- `.forgekit/docs/codebase-map.md`：代码入口、模块地图和局部验证命令。
- `.forgekit/docs/local-toolchain.md`：本地 lint、test、build、LSP 和工具链能力。
- `.forgekit/project-boundary.yml`：ForgeKitRoot、ProjectRoot、managed docs root、change root 和写入策略。
- `governance/ai-engineering-loop.md`：风险分级、change 工件和交付闭环。
- `.forgekit/changes/_template/`：proposal、design、tasks、verification、review、ship、retro 模板。
- `.codex/commands.md`：当前项目常用命令。
- `.agents/skills/`：项目自包含 skills。

默认情况下，ForgeKit 治理文档写入 `.forgekit/docs/`，中高风险变更工件写入 `.forgekit/changes/`。业务已有 `docs/` 是 read-mostly 证据源：AI 可以读取和引用，但不应默认把 ForgeKit 治理模板写进去。

## 升级已有项目

从旧版本 ForgeKit 升级到新版本时，使用升级模式，不要用 `-Force` / `--force`：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\projects\my-app" -ProjectName "my-app" -Mode Standard -Upgrade -ExportUpgradeTemplates
```

```bash
./scripts/init-project-template.sh --target-path "$HOME/projects/my-app" --project-name "my-app" --mode Standard --upgrade --export-upgrade-templates
```

升级会：

- 只生成报告和候选模板，不覆盖任何项目文件。
- 保留已有项目事实、`.forgekit/template-lock.json`、business `docs/`、`.codex/`、`AGENTS.md`、`CLAUDE.md`。
- 把 skip / can_replace / needs_merge_report / can_restore / ask / readonly 分类写入 `.forgekit/upgrade-report.md`。
- 把新版候选模板按目标路径导出到 `.forgekit/upgrade-export/<version>/`，方便人工或 AI 做 diff 合并。
- 旧项目缺少 `.forgekit/template-lock.json` 时只输出 `legacy_no_lock` 报告，不自动补 lock。

升级后可让 AI 执行：

```text
请读取 .forgekit/upgrade-report.md，对比 .forgekit/upgrade-export/，只把有价值的新模板段落合并进现有项目文件，不要覆盖项目真实事实，也不要把 upgrade-export 当作当前态文档。
```

## 既有项目和旧文档

接手已有项目时，AI 不应先问技术栈。它应该先读 README、安装说明、启动脚本、测试说明、部署说明、API 文档、构建文件和依赖文件，从证据里抽取答案；只有文档缺失、冲突或过期时才追问。

如果旧文档很多，使用：

```text
请使用 document-backfill，逐篇阅读 <旧文档目录> 里的文档，并一边读一边补全 ForgeKit managed docs root。不要一次性全部读进去总结。
```

## 可选 Hook

ForgeKit 默认不启用 hook。需要文档同步提醒时，可以安装 opt-in Git hook。

Windows：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-hooks.ps1 -Profile docs-warn -Target git
```

Ubuntu / macOS：

```bash
./scripts/install-hooks.sh --profile docs-warn --target git
```

`docs-warn` 只提示不阻断；团队确认噪音可接受后再使用 `docs-strict`。

## 检查命令

验证模板：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-template.ps1
```

验证插件分发内容：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-plugin-assets.ps1
```

生成项目内检查 harness：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-harness-check.ps1
```

生成项目内检查文档同步：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check-doc-sync.ps1
```

```bash
./scripts/check-doc-sync.sh
```

这些脚本只做检查、复制模板或安装本地 opt-in hook，不会自动安装依赖、启动服务、部署、commit、tag 或 push。

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

ForgeKit 默认不启用：

- hook
- MCP
- memory / session tracking
- 多 agent runtime
- 外部账号集成
- 自动部署
- 自动创建 issue / PR
- 自动 commit / tag / push

ForgeKit 可以和 ECC 共存：ECC 增强 AI 工具，ForgeKit 约束项目现场。

## 最近版本

| 版本 | 用户可感知变化 |
| --- | --- |
| `0.19.0` | Archive Plan：新增 dry-run 归档计划，只生成或覆盖 `.forgekit/archive-plan.md`，不移动文件。 |
| `0.18.0` | Document Lifecycle：新增 current docs / changes / archive 三层规则，archive 默认不读，done change 只提示可归档。 |
| `0.17.0` | Template Versioning：新增 template manifest / lock，升级时只生成 report-only 分类和候选模板，不自动覆盖项目文件。 |
| `0.16.0` | Boundary First：新增 `.forgekit/project-boundary.yml`，新项目默认把 ForgeKit managed docs 写入 `.forgekit/docs`，change 工件写入 `.forgekit/changes`。 |
| `0.15.0` | 将定位升级为轻量级 AI 工程交付工具包，加入 AI Engineering Loop 和风险分级 change 模板。 |
| `0.14.0` | 修复发布可用性：英文文件名模板、mode 语义说明、upgrade 防误用、跨平台 smoke test、通用模板路径隔离。 |
| `0.13.0` | 新增项目适用性、大任务计划、文档同步检查、可选 Git hook、升级报告和模板 diff 支持。 |
| `0.12.x` | Codex / Claude Code 统一根级 plugin 分发，生成项目同时支持 `AGENTS.md` 和 `CLAUDE.md`。 |
| `0.11.x` | 加强 Claude Code 入口和跨工具共享项目事实。 |
