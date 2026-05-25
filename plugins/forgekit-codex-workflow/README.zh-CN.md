# ForgeKit Codex Workflow 中文说明

English documentation: [README.md](README.md)

**ForgeKit 是一套面向真实软件项目的 Codex 工作流插件。**

它的目标不是生成某个固定框架的 demo，也不是替你自动部署项目，而是把一个新项目或既有项目整理成 Codex 能稳定接手的工程现场：有清晰入口、有方案讨论、有任务拆分、有技术栈规则、有代码审查、有发布检查，也有高风险动作确认。

简单说，ForgeKit 让 Codex 不再从一句模糊需求直接跳到写代码，而是先像一个谨慎的项目协作者一样把目标、方案、风险、验证方式和执行边界问清楚。

## 适合谁

- 想用 Codex 开新项目，但不想一上来就乱写代码。
- 想把项目初始化、需求、架构、任务、测试、发布流程固定下来。
- 想把同一套 Codex 工作流分发给团队成员。
- 想接手既有项目，先审计、看风险、补文档，再逐步改代码。
- 想按不同技术栈只加载相关规则，避免上下文过重。

不适合的场景：

- 你只想要一个具体业务框架的脚手架代码。
- 你希望插件自动安装环境、创建仓库、部署服务或推送代码。
- 你希望一键启用 hook、MCP、CI、外部账号集成。

这些能力以后可以作为可选增强，但不会默认打开。

## 最快开始

在 plugin 目录下执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\projects\my-app" -ProjectName "my-app" -Stacks java-springboot,vue
```

然后进入生成出来的项目目录，让 Codex 从入口文件开始：

```text
请读取 AGENTS.md，并按 ForgeKit 流程帮我初始化这个项目。
```

如果你还不知道该选什么技术栈，可以先不传 `-Stacks`：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\projects\my-app" -ProjectName "my-app"
```

后续让 Codex 在方案阶段帮你判断技术栈，再补充对应 stack 规则。

## 常用技术栈怎么选

| 项目类型 | `-Stacks` 填什么 |
| --- | --- |
| Java + Vue 前后端 | `java-springboot,vue` |
| Java 后端 | `java-springboot` |
| Python API | `python-fastapi` |
| Node API | `node-express` |
| C# / .NET API 或 Worker | `csharp-dotnet` |
| Go 服务或 CLI | `go-service` |
| Laravel 后台或 API | `php-laravel` |
| Rust CLI 或服务 | `rust-cli-service` |
| Flutter App | `flutter-dart` |
| C++ CMake 工程 | `cpp-cmake` |
| Kotlin 后端 | `kotlin-spring` |
| iOS App | `swift-ios` |
| Rails Web 或 API | `ruby-rails` |
| R 数据分析 / Shiny | `r-data-analysis` |
| FPGA / HLS | `fpga-vivado-vitis` |

纯前端项目可以只选 `vue` 或 `react`。

## 生成项目后有什么

ForgeKit 会把一套项目级工作流放进目标项目：

- `AGENTS.md`：Codex 的第一入口，告诉它先读什么、不要做什么。
- `.codex/`：项目事实、范围、命令、安全、测试、代码风格和技术栈规则。
- `.agents/skills/`：项目初始化、既有项目接手、代码审查、发布检查、安全审查等 skill。
- `docs/`：需求、架构、任务看板、版本路线图、测试、部署、风险、发布、追踪矩阵等项目文档。
- `governance/`：轻量 SDLC、Definition of Ready/Done、变更、发布、事故、安全和 agent harness 规则。
- `scripts/`：只读工具链检查和 harness 结构检查脚本。

plugin 顶层也有一份 `skills/`，用于让 Codex 在项目生成前就能发现 ForgeKit 的能力。

## ForgeKit 会怎样约束 Codex

新项目阶段，Codex 应该先做这些事：

1. 追问产品目标、用户场景和真正要解决的问题。
2. 给出多个可实现方案，并说明取舍。
3. 确认技术栈、环境、数据、部署、测试和验收方式。
4. 输出执行前确认摘要。
5. 等你明确确认后，才开始写业务代码、安装依赖、初始化 Git、commit、push、部署或写外部目录。

接手既有项目时，Codex 应该先做审计、代码库地图、工具链检查、P0/P1 风险识别，再谈大改。

## 安全边界

这个 plugin 是分发包，不是自动化开关。

它不会默认启用：

- hook
- MCP
- 外部账号集成
- 自动部署
- 自动创建 issue / PR
- 自动 commit / tag / push

它也不包含：

- `user-rules/`，因为里面通常有个人电脑路径和权限偏好。
- 外部开发记录目录 `document/`。
- 凭据、token、私有服务地址或部署自动化。

高风险动作仍然必须由用户明确确认。

## 验证 plugin 是否完整

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-plugin-assets.ps1
```

可选烟测：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\tmp\forgekit-plugin-smoke" -ProjectName "forgekit-plugin-smoke" -Stacks java-springboot,vue -Force
```

然后进入生成的烟测项目运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-harness-check.ps1
```

## Lite / Standard / Enterprise 怎么选

| 模式 | 适用项目 |
| --- | --- |
| Lite | 小脚本、小工具、个人验证项目 |
| Standard | 普通应用、API、内部系统、数据处理项目 |
| Enterprise | 团队交付、生产系统、高风险变更、接手项目 |

默认建议从 Standard 开始。项目很小再降到 Lite；涉及生产、多人协作、安全、硬件或交付风险时用 Enterprise。

## 包结构说明

`assets/project-template/` 用于生成自包含项目。即使以后 plugin 不在，生成项目也能保留自己的规则、文档和 skills。

plugin 顶层 `skills/` 是刻意保留的，用于让 Codex 在安装 plugin 后能先发现 ForgeKit 的项目初始化、审查、发布和安全能力。

ForgeKit 后续推广时，推荐优先推广这个 plugin 包。
