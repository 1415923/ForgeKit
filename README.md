# ForgeKit

English documentation: [README.en.md](README.en.md)

**ForgeKit 是一套面向真实软件项目的 AI 协作工作流插件。**

它不是业务框架脚手架，也不是自动部署工具。它做的是把一个新项目或既有项目整理成 Codex、Claude Code 等 AI 编程工具能稳定接手的工程现场：有入口、有方案访谈、有项目文档、有技术栈按需加载、有审查和发布检查，也有高风险动作确认。

换句话说，ForgeKit 让 AI 助手先问清楚目标、方案、风险和验证方式，再进入编码。

## 指南

如果你是第一次使用，只需要看三块：

| 主题 | 该看什么 |
| --- | --- |
| 快速开始 | 直接按下面 3 步初始化并启动 AI 助手 |
| 方案访谈 | 不知道技术栈或产品形态时，让 AI 助手先追问和调研 |
| 安全边界 | 想知道插件会不会自动安装、部署、push 时看这里 |

生成项目后，Codex 的第一入口是目标项目里的 `AGENTS.md`，Claude Code 的第一入口是 `CLAUDE.md`。两者共享同一套 `.codex/`、`docs/` 和 `governance/` 项目事实。

## 与 ECC 的边界

ForgeKit 不是“小 ECC”，也不和 ECC 竞争 agent runtime。ECC 更像 AI 编程工具增强套件，覆盖 commands、hooks、memory、MCP、多 agent、安全工具和跨工具适配。

ForgeKit 的职责更窄：把一个真实项目整理成 AI 助手可稳定接手的工程现场，重点是项目入口、方案访谈、既有项目扫描、项目文档、版本路线、任务拆分、审查门禁、发布检查和安全确认。

默认边界：

- 不默认启用 hook、MCP、memory、session tracking 或多 agent 运行时。
- 不复刻 ECC 的命令体系、安全工具、成本控制或自动化运行时。
- 可以和 ECC 共存：ECC 增强 AI 工具，ForgeKit 约束具体项目的交付流程。

## 最新动态

当前 plugin 已经具备：

- 项目初始化、既有项目接手、代码审查、发布检查、安全审查等 skills。
- Codex / Claude Code 通用的根级 plugin 结构。
- Lite / Standard / Enterprise 三种项目模式，初始化时通过 `-Mode` 写入项目。
- 多种技术栈模板可在方案确认后再加载，不要求用户在初始化前选择。
- 方案访谈状态机：`unclear`、`options-needed`、`research-needed`、`existing-project-scan`、`ready-for-plan`。
- 只读工具链检测和 harness 结构检查脚本。
- plugin 分发校验，避免把个人路径、外部开发记录或 `.git/` 打包进去。

## 快速开始

### 第一步：在 ForgeKit 目录生成项目

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\projects\my-app" -ProjectName "my-app" -Mode Standard
```

不要在这一步急着选择技术栈。新项目的技术栈应在产品形态、用户场景、运行环境、验证方式和约束条件讨论清楚后再确定；既有项目则应先扫描现有代码和配置来识别技术栈。

模式是第一步里唯一需要先确定的参数：

| 模式 | 适用项目 | 命令参数 |
| --- | --- | --- |
| Lite | 小脚本、小工具、个人验证项目 | `-Mode Lite` |
| Standard | 普通应用、API、内部系统、数据处理项目 | `-Mode Standard` |
| Enterprise | 团队交付、生产系统、高风险变更、接手项目 | `-Mode Enterprise` |

不确定时先选 `Standard`。模式会写入 `.codex/init.generated.md` 和 `.claude/init.generated.md`，AI 助手启动时可以直接读取。

### 第二步：进入生成出来的项目

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

如果你的启动命令不同，就用你平时的启动方式；关键是工作目录必须是生成后的项目根目录。

### 第三步：把这句话发给 AI 助手

Codex：

```text
请读取 AGENTS.md，并按 ForgeKit 流程帮我初始化这个项目。
```

Claude Code：

```text
请读取 CLAUDE.md，并按 ForgeKit 流程帮我初始化这个项目。
```

这一步才会真正开始项目方案访谈。AI 助手会先读入口文件和初始化信息，再根据 `-Mode`、项目现状和你的项目简报继续追问。

## 方案访谈怎么进行

新项目不要先问 5 个固定技术问题。AI 助手应该先把问题本身聊清楚：

1. 这个项目服务谁，解决什么痛点，成功标准是什么。
2. 可能的产品形态有哪些，各自范围、成本、风险和不做什么。
3. 是否需要查官方文档、公开项目、同类产品或技术资料。
4. 先确定 v0.1.0 最小闭环，再讨论架构和技术栈。
5. 用户答不上来时，给候选方案、推荐默认值和验证办法，而不是重复追问。

既有项目不要先问技术栈。AI 助手应该先扫描项目目录、README、构建文件、依赖文件、启动脚本和测试命令，基于现状推断技术栈；新增功能、修复和重构默认基于现有技术栈进行，除非用户明确要求迁移或重构架构。

ForgeKit 会把访谈推进到一个明确状态：

| 状态 | AI 助手应该做什么 |
| --- | --- |
| `unclear` | 只追问目标、用户、痛点、成功标准和不做什么 |
| `options-needed` | 给 2 到 4 个可行产品形态或范围方案，并说明取舍和推荐默认值 |
| `research-needed` | 明确未知点、阻塞的决策、要查的官方资料/GitHub 项目/原型验证 |
| `existing-project-scan` | 先扫描现有项目文件，汇报推断出的技术栈、命令、测试和矛盾点 |
| `ready-for-plan` | 停止泛泛追问，输出项目方案、路线图、任务拆分和执行确认 |

## Root-level plugin surface

ForgeKit 0.12.0 起不再维护 Codex / Claude Code 两个独立 plugin 子目录。仓库根目录就是统一分发表面：

```text
ForgeKit/
├─ .codex-plugin/
│  └─ plugin.json                 # Codex plugin metadata
├─ .claude-plugin/
│  ├─ plugin.json                 # Claude Code plugin metadata
│  └─ marketplace.json            # Claude Code local marketplace example
├─ .agents/plugins/
│  └─ marketplace.json            # Codex local marketplace example
├─ skills/                        # Codex / Claude Code 共享 skills
├─ scripts/
│  ├─ init-project-template.ps1    # 初始化目标项目
│  └─ validate-plugin-assets.ps1   # 校验根级 plugin 分发表面
├─ project-template/               # 生成项目的基础模板
├─ templates/                      # 各技术栈模板
└─ questionnaires/                 # 初始化问答
```

` .codex-plugin/plugin.json` 和 `.claude-plugin/plugin.json` 都指向 `./skills/`。两个 marketplace 都把仓库根 `./` 作为 source。

## 跨平台支持

ForgeKit 的核心资产是 Markdown、skills 和 PowerShell 脚本。

| 平台 | 支持情况 |
| --- | --- |
| Windows | 当前主要支持平台，初始化和校验脚本为 PowerShell |
| macOS / Linux | 生成后的 Markdown、skills 和项目规则可用；初始化脚本需要 PowerShell 7 或手动复制 |
| Codex CLI | 通过生成项目的 `AGENTS.md`、`.codex/`、`.agents/skills/` 工作 |
| Claude Code | 通过生成项目的 `CLAUDE.md`、`.claude/skills/` 和共享项目文档工作 |

ForgeKit 不会自动安装 JDK、Node、Python、Flutter、Xcode、Rust、CMake 等工具。缺什么工具由检测脚本记录，再由用户决定是否安装。

## 检测和工具

验证根级 plugin 表面：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-plugin-assets.ps1
```

验证模板结构：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-template.ps1
```

生成烟测项目：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\tmp\forgekit-plugin-smoke" -ProjectName "forgekit-plugin-smoke" -Mode Standard -Force
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

## 生成项目里有什么

```text
AGENTS.md                         # Codex 入口
CLAUDE.md                         # Claude Code 入口
.codex/                           # Codex 项目上下文、命令、规则、初始化记录
.claude/                          # Claude Code 轻量入口和初始化记录
.agents/skills/                   # 生成项目自包含 skills
docs/代码库地图.md                # 代码入口和模块地图
docs/本地工具链检查.md            # 工具链和验证能力记录
docs/Codex下一步工作单.md         # 下一步工作单
docs/
governance/
scripts/
```

## 技术栈按需加载

全局规则只保留跨项目共性。Java、Vue、React、Python、Node、C#/.NET、Go、Laravel、Rust、Flutter、C++、Kotlin、Swift、Rails、R、FPGA 等专用规则放在 `templates/`，但不要求初始化时选择。

新项目在方案访谈后按需加入；既有项目先由 AI 助手扫描项目文件推断。

不要让 Java 项目读取 FPGA 规则，也不要让 Laravel 项目读取 C# 规则；只加载当前项目实际需要的 stack，避免 context rot。

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

## ForgeKit 会怎样约束 AI 助手

新项目阶段，AI 助手应该先做这些事：

1. 追问产品目标、用户场景和真正要解决的问题。
2. 给出多个可实现方案，并说明取舍。
3. 确认环境、数据、部署、测试、验收方式，并在方案足够清楚后再确认技术栈。
4. 输出执行前确认摘要。
5. 等你明确确认后，才开始写业务代码、安装依赖、初始化 Git、commit、push、部署或写外部目录。

接手既有项目时，AI 助手应该先做审计、代码库地图、工具链检查、P0/P1 风险识别，再谈大改。
