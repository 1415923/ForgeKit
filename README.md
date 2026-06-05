# ForgeKit

English documentation: [README.en.md](README.en.md)

**ForgeKit 是一套面向真实软件项目的 AI 协作工作流插件。**

它不是业务框架脚手架，也不是自动部署工具。ForgeKit 的目标是把一个新项目或既有项目整理成 Codex、Claude Code 等 AI 编程工具能稳定接手的工程现场：有入口、有方案访谈、有项目文档、有按需加载的技术栈规则、有审查和发布检查，也有高风险动作确认。

一句话：ForgeKit 让 AI 助手先问清楚目标、方案、风险和验证方式，再进入编码。

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

不确定时先选 `Standard`。不要在这一步急着选择技术栈；新项目的技术栈应在方案讨论后确定，既有项目应先由 AI 扫描现有文件推断。

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
- `document-backfill`：逐篇读取既有文档，并回填 ForgeKit `docs/`。
- `handover-review`：接手既有项目时做审计和风险识别。
- `large-change-planning`：大范围、跨模块、迁移或重构前先做探索和实施计划。
- `code-review`、`release-check`、`security-review`：代码审查、发布检查和安全审查。
- 可选文档同步检查和 Git hook：提示相关文档未同步、过期描述和版本记录缺少原因。

生成项目后，Codex 从 `AGENTS.md` 开始，Claude Code 从 `CLAUDE.md` 开始。两者共享 `.codex/`、`docs/`、`governance/` 和 `.agents/skills/`。

生成项目里的关键文件：

- `docs/代码库地图.md`：代码入口、模块地图和局部验证命令。
- `docs/本地工具链检查.md`：本地 lint、test、build、LSP 和工具链能力。
- `.codex/commands.md`：当前项目常用命令。
- `.agents/skills/`：项目自包含 skills。

## 升级已有项目

从旧版本 ForgeKit 升级到新版本时，使用升级模式，不要用 `-Force` / `--force`：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\projects\my-app" -ProjectName "my-app" -Mode Standard -Upgrade -ExportUpgradeTemplates
```

```bash
./scripts/init-project-template.sh --target-path "$HOME/projects/my-app" --project-name "my-app" --mode Standard --upgrade --export-upgrade-templates
```

升级会：

- 补齐新版本缺失的模板文件。
- 保留已有项目事实和文档，不覆盖 `docs/`、`.codex/`、`AGENTS.md`、`CLAUDE.md`。
- 把“已有文件和新版模板不同”的项目写入 `.codex/upgrade-report.md`。
- 可选把新版模板副本导出到 `.codex/upgrade-templates/`，方便人工或 AI 做 diff 合并。

升级后可让 AI 执行：

```text
请读取 .codex/upgrade-report.md，对比 .codex/upgrade-templates/，只把有价值的新模板段落合并进现有项目文件，不要覆盖项目真实事实。
```

## 既有项目和旧文档

接手已有项目时，AI 不应先问技术栈。它应该先读 README、安装说明、启动脚本、测试说明、部署说明、API 文档、构建文件和依赖文件，从证据里抽取答案；只有文档缺失、冲突或过期时才追问。

如果旧文档很多，使用：

```text
请使用 document-backfill，逐篇阅读 <旧文档目录> 里的文档，并一边读一边补全 ForgeKit docs。不要一次性全部读进去总结。
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
| `0.13.0` | 新增项目适用性、大任务计划、文档同步检查、可选 Git hook、升级报告和模板 diff 支持。 |
| `0.12.x` | Codex / Claude Code 统一根级 plugin 分发，生成项目同时支持 `AGENTS.md` 和 `CLAUDE.md`。 |
| `0.11.x` | 加强 Claude Code 入口和跨工具共享项目事实。 |
