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
5. 新项目使用 `project-init`，既有项目使用 `handover-review`。
6. 每次开发功能时，按 `checklists/功能开发检查清单.md` 执行。
7. 每次发布前，按 `checklists/发布前检查清单.md`、`checklists/版本推进闸门检查清单.md`、`docs/环境矩阵.md`、`docs/发布流水线.md`、`docs/代码所有权.md` 和 `docs/项目任务看板.md` 核对。

## 使用模式

| 模式 | 适用项目 | 建议维护内容 |
| --- | --- | --- |
| Lite | 小脚本、小工具、个人验证项目 | `.codex/`、`docs/项目开发方案.md`、`docs/版本更新记录.md`、必要命令 |
| Standard | 普通前后端、API、数据处理、内部业务项目 | Lite + 需求、架构、技术选型、版本路线图、任务看板、测试、发布检查 |
| Enterprise | 多人协作、接手项目、交付项目、高风险项目 | Standard + ADR/RFC、风险、变更影响、代码所有权、CI/CD、安全治理、事故复盘、质量指标 |

默认推荐 `Standard`。小项目可以从 `Lite` 开始；涉及公司交付、生产环境、安全、硬件或多人协作时，用 `Enterprise`。

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
