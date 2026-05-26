# ForgeKit Codex Workflow

English documentation: [README.md](README.md)

**ForgeKit 是一套面向真实软件项目的 Codex 工作流插件。**

它不是业务框架脚手架，也不是自动部署工具。它做的是把一个新项目或既有项目整理成 Codex 能稳定接手的工程现场：有入口、有方案访谈、有技术栈规则、有项目文档、有审查和发布检查，也有高风险动作确认。

换句话说，ForgeKit 让 Codex 先问清楚目标、方案、风险和验证方式，再进入编码。

## 指南

如果你是第一次使用，只需要看三块：

| 主题 | 该看什么 |
| --- | --- |
| 快速开始 | 直接按下面 3 步初始化并启动 Codex |
| 常用技术栈 | 不知道 `-Stacks` 怎么填时看这里 |
| 安全边界 | 想知道插件会不会自动安装、部署、push 时看这里 |

生成项目后，Codex 的第一入口永远是目标项目里的 `AGENTS.md`。

## 最新动态

当前 plugin 已经具备：

- 项目初始化、既有项目接手、代码审查、发布检查、安全审查等 skills。
- Lite / Standard / Enterprise 三种项目模式，初始化时通过 `-Mode` 写入项目。
- Java、Vue、React、Python、Node、C#/.NET、Go、Laravel、Rust、Flutter、C++、Kotlin、Swift、Rails、R、FPGA 等技术栈模板。
- 只读工具链检测和 harness 结构检查脚本。
- plugin 分发包校验，避免把个人路径、外部开发记录或 `.git/` 打包进去。

## 快速开始

### 第一步：在 plugin 目录生成项目

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\projects\my-app" -ProjectName "my-app" -Mode Standard -Stacks java-springboot,vue
```

不确定技术栈时可以先不传 `-Stacks`：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\projects\my-app" -ProjectName "my-app" -Mode Standard
```

### 第二步：进入生成出来的项目

```powershell
cd D:\projects\my-app
codex
```

如果你的 Codex 启动命令不是 `codex`，就用你平时的启动方式；关键是工作目录必须是生成后的项目根目录。

### 第三步：把这句话发给 Codex

```text
请读取 AGENTS.md，并按 ForgeKit 流程帮我初始化这个项目。
```

这一步才会真正开始项目方案访谈。Codex 会先读入口文件和初始化信息，再根据 `-Mode`、`-Stacks` 和你的项目简报继续追问。

## 模式怎么选

| 模式 | 适用项目 | 命令参数 |
| --- | --- | --- |
| Lite | 小脚本、小工具、个人验证项目 | `-Mode Lite` |
| Standard | 普通应用、API、内部系统、数据处理项目 | `-Mode Standard` |
| Enterprise | 团队交付、生产系统、高风险变更、接手项目 | `-Mode Enterprise` |

不确定时先选 `Standard`。模式会写入 `.codex/init.generated.md`，Codex 启动时可以直接读取。

## 常用技术栈

| 项目类型 | `-Stacks` 填什么 |
| --- | --- |
| Java + Vue 前后端 | `java-springboot,vue` |
| Java 后端 | `java-springboot` |
| Vue 前端 | `vue` |
| React 前端 | `react` |
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

只选择当前项目实际需要的技术栈，不要一次性全选。

## 跨平台支持

ForgeKit 的核心资产是 Markdown、Codex skills 和 PowerShell 脚本。

| 平台 | 支持情况 |
| --- | --- |
| Windows | 当前主要支持平台，初始化和校验脚本为 PowerShell |
| macOS / Linux | 生成后的 Markdown、skills 和项目规则可用；初始化脚本需要 PowerShell 7 或手动复制 |
| Codex CLI | 通过生成项目的 `AGENTS.md`、`.codex/`、`.agents/skills/` 工作 |

ForgeKit 不会自动安装 JDK、Node、Python、Flutter、Xcode、Rust、CMake 等工具。缺什么工具由检测脚本记录，再由用户决定是否安装。

## 检测和工具

验证 plugin 包：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-plugin-assets.ps1
```

生成烟测项目：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\tmp\forgekit-plugin-smoke" -ProjectName "forgekit-plugin-smoke" -Mode Standard -Stacks java-springboot,vue -Force
```

在生成项目中检查 harness 入口：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-harness-check.ps1
```

在生成项目中检测本地工具链：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\detect-local-toolchain.ps1
```

这些脚本只做检查和复制模板，不会自动安装工具、启动服务或部署项目。

## 里面有什么

```text
forgekit-codex-workflow/
├─ .codex-plugin/
│  └─ plugin.json                 # plugin 元数据
├─ skills/                        # Codex 可发现的 ForgeKit skills
├─ scripts/
│  ├─ init-project-template.ps1    # 初始化目标项目
│  ├─ validate-plugin-assets.ps1   # 校验 plugin 分发包
│  ├─ detect-local-toolchain.ps1   # 只读工具链检测
│  └─ run-harness-check.ps1        # 只读 harness 检查
└─ assets/
   ├─ project-template/            # 生成项目的基础模板
   ├─ templates/                   # 各技术栈模板
   ├─ questionnaires/              # 初始化问答
   └─ docs/                        # 安装、升级、安全、反馈说明
```

生成到目标项目后，主要入口是：

```text
AGENTS.md
.codex/
.agents/skills/
docs/
governance/
scripts/
```

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

## ForgeKit 会怎样约束 Codex

新项目阶段，Codex 应该先做这些事：

1. 追问产品目标、用户场景和真正要解决的问题。
2. 给出多个可实现方案，并说明取舍。
3. 确认技术栈、环境、数据、部署、测试和验收方式。
4. 输出执行前确认摘要。
5. 等你明确确认后，才开始写业务代码、安装依赖、初始化 Git、commit、push、部署或写外部目录。

接手既有项目时，Codex 应该先做审计、代码库地图、工具链检查、P0/P1 风险识别，再谈大改。
