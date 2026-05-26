# ForgeKit Claude Workflow

English documentation: [README.md](README.md)

**ForgeKit Claude Workflow 是面向 Claude Code 的 ForgeKit 工作流插件。**

它是 `forgekit-codex-workflow` 的并列分发包，不替代 Codex 包。它把 ForgeKit 的项目初始化、方案访谈、既有项目接手、审查、发布和安全边界 skills 适配给 Claude Code 使用。

ForgeKit 不是业务框架脚手架，也不是自动部署工具。它让 Claude Code 在编码前先确认项目目标、方案状态、风险、验证方式和执行边界。

## 当前版本做什么

`v0.11.1` 提供 Claude Code plugin 分发包和生成项目入口：

- `.claude-plugin/plugin.json`，用于 Claude Code plugin 发现。
- `skills/`，包含 ForgeKit 工作流 skills。
- `assets/`，包含共享模板资产。
- `scripts/`，包含初始化、只读检测和校验脚本。
- `scripts/validate-plugin-assets.ps1`，用于独立校验 Claude 分发包。
- `CLAUDE.md` 和 `.claude/skills/forgekit-project-workflow/`，用于生成项目的 Claude Code 第一入口。

这一版不会默认启用 hook、MCP、subagent、slash command、部署、issue 写入、Git 写入或外部自动化。

Claude 入口按 ECC 式“共享核心资产 + 工具薄入口”思路设计：`.claude/skills/forgekit-project-workflow/` 只负责路由和门禁，不复制全量 skills；项目事实仍集中写入 `.codex/`、`docs/` 和 `governance/`。

## 与 ECC 的边界

ForgeKit Claude Workflow 不是“小 ECC”，也不和 ECC 竞争 Claude Code runtime。ECC 更像 AI 编程工具增强套件，覆盖 commands、hooks、memory、MCP、多 agent、安全工具和跨工具适配。

ForgeKit 的职责更窄：把一个真实项目整理成 Claude Code 可稳定接手的工程现场，重点是项目入口、方案访谈、既有项目扫描、项目文档、版本路线、任务拆分、审查门禁、发布检查和安全确认。

默认边界：

- 不默认启用 hook、MCP、memory、session tracking、subagent 或 slash command。
- 不复刻 ECC 的命令体系、安全工具、成本控制或自动化运行时。
- 可以和 ECC 共存：ECC 增强 AI 工具，ForgeKit 约束具体项目的交付流程。

## 快速开始

### 第一步：添加本地 plugin marketplace 或 plugin 路径

按团队的 Claude Code plugin 安装方式添加本地或仓库插件。插件目录是：

```text
plugins/forgekit-claude-workflow/
```

manifest 位置是：

```text
plugins/forgekit-claude-workflow/.claude-plugin/plugin.json
```

### 第二步：生成项目入口

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\projects\my-app" -ProjectName "my-app" -Mode Standard
```

这会生成 `CLAUDE.md` 和 `.claude/skills/forgekit-project-workflow/`，同时保留共享的 `.codex/`、`docs/` 和 `governance/` 项目事实目录。

### 第三步：在目标项目启动 Claude Code

```powershell
cd D:\projects\my-app
claude
```

如果你的 Claude Code 启动命令不是 `claude`，就用你平时的启动方式；关键是工作目录必须是目标项目根目录。

### 第四步：让 Claude Code 使用 ForgeKit

```text
请使用 ForgeKit 初始化或审查这个项目。实现前先确认 discovery state。
```

Claude Code 应该发现插件内置 skills，并按相关工作流执行。

## 方案访谈状态

Claude 包复用 Codex 包的 discovery state：

| 状态 | Claude Code 应该做什么 |
| --- | --- |
| `unclear` | 只追问目标、用户、痛点、成功标准和不做什么 |
| `options-needed` | 给 2 到 4 个可行产品形态或范围方案，并说明取舍和推荐默认值 |
| `research-needed` | 明确未知点、阻塞的决策、要查的官方资料/GitHub 项目/原型验证 |
| `existing-project-scan` | 先扫描现有项目文件，汇报推断出的技术栈、命令、测试和矛盾点 |
| `ready-for-plan` | 停止泛泛追问，输出项目方案、路线图、任务拆分和执行确认 |

## 检测

在 Claude plugin 目录校验分发包：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-plugin-assets.ps1
```

在仓库根目录校验：

```powershell
powershell -ExecutionPolicy Bypass -File .\plugins\forgekit-claude-workflow\scripts\validate-plugin-assets.ps1
```

## 包结构

```text
forgekit-claude-workflow/
├─ .claude-plugin/
│  └─ plugin.json
├─ skills/
├─ scripts/
└─ assets/
   ├─ project-template/
   ├─ templates/
   ├─ questionnaires/
   └─ docs/
```

## 路线边界

这是 Claude Code 的项目入口适配，不是 ECC 式运行时增强层。ForgeKit 不默认启用 hook、MCP、subagent 或 slash command。
