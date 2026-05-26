# Codex CLI 开发流程模板

这是一套用于不同语言、不同项目中复用的 Codex CLI 协作开发流程模板。

它分为两层：

- `user-rules/`：用户级规则，描述本机环境、权限策略、Git 使用习惯和通用协作偏好。
- `project-template/`：项目级模板，复制到具体项目根目录后，用于约束目标、范围、架构、代码风格、测试、文档和版本管理。

辅助目录：

- `prompts/`：项目初始化、需求分析、架构设计、代码实现、代码审查、版本发布等对话模板。
- `checklists/`：项目启动、功能开发、发布前检查清单。
- `references/`：外部项目和方法论的借鉴评估，目前包含 ECC。
- `templates/`：按技术栈拆分的项目模板补充，例如 Java、Vue、React、Python、Node、C#/.NET、Go、Laravel、Rust、Flutter、C++、Kotlin、Swift、Rails、R、FPGA。
- `scripts/`：初始化脚本，例如把模板复制到新项目。
- `questionnaires/`：项目启动问答表。

## 推荐使用方式

先判断项目入口：

- 新项目：先与 Codex 反复确认项目开发方案、技术栈选择、软硬件落地条件、环境矩阵、发布流水线、代码所有权、项目任务模型和版本路线图。
- 接手既有项目：先做现状审计、大规模代码审查、运行环境和 CI/CD 链路梳理、代码所有权梳理、任务/缺陷模型梳理、P0/P1 缺陷修复和兼容边界记录，不默认大改架构。

通用步骤：

1. 先完善 `user-rules/`，把你的电脑环境和固定偏好写清楚。
2. 用 `scripts/init-project-template.ps1` 或手动方式把 `project-template/` 复制到项目根目录。
3. 根据技术栈只选择需要的 `templates/<stack>/`，不要全量复制。
4. 先读取 `governance/流程总览.md`。
5. 新项目使用 `project-init`，它会合并初始化、问答填充和方案访谈。
6. 既有项目使用 `handover-review`，先审计和修 P0/P1，再规划后续开发。
7. 每次开发功能时，按 `checklists/功能开发检查清单.md` 执行。
8. 每次发布前，按 `checklists/发布前检查清单.md`、`checklists/版本推进闸门检查清单.md`、`docs/环境矩阵.md`、`docs/发布流水线.md`、`docs/代码所有权.md` 和 `docs/项目任务看板.md` 核对。

## 使用模式

| 模式 | 适用项目 | 建议维护内容 |
| --- | --- | --- |
| Lite | 小脚本、小工具、个人验证项目 | `.codex/`、`docs/项目开发方案.md`、`docs/版本更新记录.md`、必要命令 |
| Standard | 普通前后端、API、数据处理、内部业务项目 | Lite + 需求、架构、技术选型、版本路线图、任务看板、测试、发布检查 |
| Enterprise | 多人协作、接手项目、交付项目、高风险项目 | Standard + ADR/RFC、风险、变更影响、代码所有权、CI/CD、安全治理、事故复盘、质量指标 |

默认推荐 `Standard`。小项目可以从 `Lite` 开始；涉及公司交付、生产环境、安全、硬件或多人协作时，用 `Enterprise`。

## Codex 上下文入口

生成到具体项目后，Codex 应先读取 `AGENTS.md`。它是轻量入口，只负责路由任务和控制上下文，不要求一次性读取所有治理文档。

原则：

- 先读 `AGENTS.md`，再读 `docs/代码库地图.md` 定位代码入口。
- 按任务读取相关治理文件。
- 按技术栈只读取 `.codex/stacks/<stack>/` 中相关模板。
- 初始化阶段先访谈和确认方案，不直接编码。
- Lite 项目不强行加载 Enterprise 级治理。

推荐上下文优先级：

1. `AGENTS.md`
2. `docs/代码库地图.md`
3. `docs/本地工具链检查.md`
4. `docs/Codex下一步工作单.md`
5. `.codex/project.md`、`.codex/scope.md`、`.codex/commands.md`
6. 相关 `.codex/stacks/<stack>/`
7. 任务需要的治理文件，例如 `governance/agent-harness.md`、`governance/definition-of-ready.md`

## Agent Harness 演进

v0.3 之后的重点是把模板从“治理文档集合”推进为更成熟的 AI agent harness。规划见：

- `project-template/governance/v0.3-agent-harness-roadmap.md`

该路线图会逐步补齐 AGENTS 分层、代码库地图、LSP / 子目录启动、大任务多会话执行、hooks / commands / plugin / MCP 规划，以及项目适用性评估。

`v0.3.0` 已把 Agent Harness 基线落入模板：新增 `governance/agent-harness.md` 和 `docs/代码库地图.md`，并要求 HTML 工作台、README、AGENTS 和自检脚本都围绕这个入口体系维护。

`v0.4.0` 补齐技术栈级启动和验证：Java、Vue、React、Python、Node、FPGA 模板现在都记录推荐启动目录、符号搜索 / LSP 方式、局部验证命令和忽略建议；生成项目内新增 `docs/本地工具链检查.md`。

`v0.5.0` 补齐大任务多会话执行协议：跨模块、高风险、重构、迁移、接手整改等任务应先写 `docs/探索报告.md` 和 `docs/实施计划.md`，再拆分会话执行。

`v0.6.0` 补齐团队工具链集成规划：新增 commands catalog、hooks 示例、team rollout 治理，并明确 plugin / MCP 不应过早启用。

`v0.7.0` 补齐项目适用性评估和真实项目回灌：初始化时先判断项目是否适合 AI agent 工作流，不适合时先补工程条件或定制流程。

`v0.8.0` 开始把文档型 harness 推进为可执行 harness：生成项目内提供本地工具链检测、harness 结构检查、Codex 下一步工作单和更明确的 hook/command 候选，但默认仍不自动启用外部工具或长期服务。

`v0.9.0` 补齐 plugin 分发第一版：新增 `plugins/forgekit-codex-workflow/` 和 `.agents/plugins/marketplace.json`，把稳定 skills、只读脚本和模板资产打包为团队可安装的 Codex plugin。plugin 默认不启用 hook、MCP、外部写操作或公开市场发布。

`v0.9.1` 完成 plugin review/refactor gate：检查分发包体积、重复资产、安全边界和升级路径，补齐安装、升级、安全和真实项目试用反馈文档。plugin 内顶层 `skills/` 与 `assets/project-template/.agents/skills/` 的重复是刻意保留，前者用于 plugin 发现，后者用于生成项目自包含。

`v0.9.2` 回灌真实项目试用反馈：强化初始化阶段的多轮方案访谈，要求用户答不上来时给出候选方案、推荐默认值和查阅资料路径；同时清理生成项目路线图和任务看板中的 ForgeKit 自身历史任务。

`v0.9.3` 强化新项目执行门禁：方案商讨必须作为独立阶段，编码、依赖安装、Git 初始化、commit、push、部署或外部写操作前，必须先在会话中展示执行前确认摘要并等待用户明确确认完整方案。

`v0.9.4` 扩展第一批主流语言包：新增 C#/.NET、Go Service、PHP Laravel 技术栈模板，并吸收 AGENTS.md、Microsoft skills、Arc、Superpowers、BMAD、YAAH、Harness Skills、CodeAlive 等项目的低风险实践：按需加载、初始化追问、最小验证命令、危险命令确认和共享输出契约意识。默认仍不启用 MCP、hook、session tracking 或多 agent 运行时。

`v0.9.5` 扩展第二批语言包：新增 Rust CLI/Service、Flutter Dart、C++ CMake 技术栈模板，覆盖系统工具/高性能服务、跨端 App 和 C/C++ 工程。重点记录 Cargo、Flutter SDK、CMake/编译器、签名/证书、unsafe/FFI、ABI、平台差异和大下载/发布动作的确认边界。

`v0.9.6` 扩展第三批语言包：新增 Kotlin Spring、Swift iOS、Ruby Rails、R Data Analysis 技术栈模板，覆盖 JVM Kotlin 后端、iOS 原生、Rails Web/API 和 R 可复现分析。重点记录协程、Xcode 签名、Rails migration/队列、多数据库、renv、隐私数据和报告渲染边界。

`v0.9.7` 重写 plugin 推广文档：中英文 README 先说明 ForgeKit 是什么、适合谁、为什么要用，再给最短初始化路径、常见 stack 选择、生成内容和安全边界，避免用户一上来被资产清单和繁琐参数劝退。

`v0.9.8` 修正初始化模式入口：`Lite / Standard / Enterprise` 不再放在 README 后半段作为说明，而是前置到 Quick Start，并新增初始化脚本 `-Mode` 参数写入 `.codex/init.generated.md`，让用户复制命令前就确定项目治理深度。

`v0.9.9` 按 ECC README 框架重排 plugin 推广文档：补齐指南、最新动态、三步快速开始、跨平台支持、检测和工具、里面有什么，并把进入目标项目后启动 Codex 和发送启动提示词写成明确步骤。

`v0.10.0` 修正项目初始化和方案确认流程：不再要求用户初始化时选择技术栈；新项目先通过多轮方案访谈、资料查阅和 v0.1.0 最小闭环确认来收敛方案；既有项目先扫描 README、依赖、构建、脚本、测试和源码目录推断现有技术栈，新增功能、修复和重构默认沿用现状。

## Plugin 分发

本仓库提供 repo/team marketplace 示例：

- `.agents/plugins/marketplace.json`
- `plugins/forgekit-codex-workflow/`

plugin 用于分发 ForgeKit 的 skills、初始化脚本、只读检查脚本和模板资产。它不包含 `user-rules/` 或外部开发记录目录。验证 plugin 包：

```powershell
powershell -ExecutionPolicy Bypass -File .\plugins\forgekit-codex-workflow\scripts\validate-plugin-assets.ps1
```

从 plugin 资产初始化烟测项目：

```powershell
powershell -ExecutionPolicy Bypass -File .\plugins\forgekit-codex-workflow\scripts\init-project-template.ps1 `
  -TargetPath "D:\tmp\forgekit-plugin-smoke" `
  -ProjectName "forgekit-plugin-smoke" `
  -Mode Standard
```

## 技术栈按需加载

全局规则只保留跨项目共性。Java、前端、Python、Node、C#/.NET、Go、Laravel、Rust、Flutter、C++、Kotlin、Swift、Rails、R、FPGA 等专用规则放在 `templates/`，但不要求初始化时选择。新项目在方案访谈后按需加入；既有项目先由 Codex 扫描项目文件推断。

例如：

- Java 后端项目：加载 `project-template/` + `templates/java-springboot/`。
- Java + Vue 项目：加载 `project-template/` + `templates/java-springboot/` + `templates/vue/`。
- C# 企业 API / Worker：加载 `project-template/` + `templates/csharp-dotnet/`。
- Go 服务 / CLI：加载 `project-template/` + `templates/go-service/`。
- Laravel 后台 / API：加载 `project-template/` + `templates/php-laravel/`。
- Rust CLI / Service：加载 `project-template/` + `templates/rust-cli-service/`。
- Flutter 跨端 App：加载 `project-template/` + `templates/flutter-dart/`。
- C++ CMake 工程：加载 `project-template/` + `templates/cpp-cmake/`。
- Kotlin 后端：加载 `project-template/` + `templates/kotlin-spring/`。
- Swift iOS App：加载 `project-template/` + `templates/swift-ios/`。
- Rails Web / API：加载 `project-template/` + `templates/ruby-rails/`。
- R 数据分析 / Shiny：加载 `project-template/` + `templates/r-data-analysis/`。
- FPGA 项目：加载 `project-template/` + `templates/fpga-vivado-vitis/`。

不要让 Java 项目读取 FPGA 规则，也不要让 Laravel 项目读取 C# 规则；只加载当前项目实际需要的 stack，避免 context rot。

## 初始化脚本示例

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 `
  -TargetPath "D:\JAVA-code\demo-fullstack" `
  -ProjectName "demo-fullstack" `
  -Mode Standard
```

脚本默认不覆盖已有文件。初始化后 `.codex/stacks/README.md` 会说明技术栈尚未选择是正常状态；后续确认或推断出技术栈后，再把对应模板放到目标项目的 `.codex/stacks/<stack>/`。

## ECC 借鉴策略

本模板参考 ECC 的 agents、skills、rules、MCP 和安全边界思想，但不要求安装 ECC。

采用原则：

- 把 ECC 当作能力库和规则参考，不当作本模板的替代品。
- 默认保持模板轻量，内置少量项目治理 skills，并预留 `.codex/agents/` 和 `.codex/config.example.toml`。
- 需要安全审查、E2E、API 设计、多 agent、MCP 时，再按项目选择性引入。
- 不全量复制第三方 skills、hooks、commands 或 MCP 配置。

## 分层原则

用户级规则回答：Codex 在我的电脑上应该怎么做事。

项目级规则回答：Codex 在这个项目里应该怎么设计、实现、测试和交付。

不要把项目业务需求写进用户级规则；不要把本机路径、个人权限偏好写进项目级规则。
