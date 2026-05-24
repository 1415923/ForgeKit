# Codex CLI 开发流程模板

这是一套用于不同语言、不同项目中复用的 Codex CLI 协作开发流程模板。

它分为两层：

- `user-rules/`：用户级规则，描述本机环境、权限策略、Git 使用习惯和通用协作偏好。
- `project-template/`：项目级模板，复制到具体项目根目录后，用于约束目标、范围、架构、代码风格、测试、文档和版本管理。

辅助目录：

- `prompts/`：项目初始化、需求分析、架构设计、代码实现、代码审查、版本发布等对话模板。
- `checklists/`：项目启动、功能开发、发布前检查清单。
- `references/`：外部项目和方法论的借鉴评估，目前包含 ECC。
- `templates/`：按技术栈拆分的项目模板补充，例如 Java、Vue、React、Python、Node、FPGA。
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

## 技术栈按需加载

全局规则只保留跨项目共性。Java、前端、Python、FPGA 等专用规则放在 `templates/`，按项目选择。

例如：

- Java 后端项目：加载 `project-template/` + `templates/java-springboot/`。
- Java + Vue 项目：加载 `project-template/` + `templates/java-springboot/` + `templates/vue/`。
- FPGA 项目：加载 `project-template/` + `templates/fpga-vivado-vitis/`。

不要让 Java 项目读取 FPGA 规则，也不要让 FPGA 项目读取前端规则。

## 初始化脚本示例

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 `
  -TargetPath "D:\JAVA-code\demo-fullstack" `
  -ProjectName "demo-fullstack" `
  -Stacks java-springboot,vue
```

脚本默认不覆盖已有文件。技术栈模板会放到目标项目的 `.codex/stacks/<stack>/`，再由 Codex 或人工按项目需要合并。

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
