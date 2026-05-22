# 初始化填充流程

本文件定义如何把 `项目初始化问答.md` 或用户粘贴的问答内容转换成项目第一版 `.codex/` 规则和 `docs/` 文档。

## 目标

让用户不必手工逐个编辑 Markdown。Codex 应先读取问答事实，再把稳定信息合并到核心文档中，并把未知项保留为待确认问题。

## 输入

| 来源 | 说明 |
| --- | --- |
| `.codex/init.generated.md` | 初始化脚本生成的项目名和技术栈 |
| `.codex/questionnaires/项目初始化问答.md` | 项目事实的主要来源 |
| `.codex/stacks/<stack>/` | 技术栈规则、命令和检查清单 |
| 用户当前对话补充 | 优先级高于空模板，低于项目已有明确事实 |
| 现有 README / 构建配置 | 接手或已有项目的真实事实 |

## 输出文档映射

| 问答内容 | 目标文档 |
| --- | --- |
| 项目名称、目标、用户、交付形式、阶段 | `.codex/project.md`、`docs/项目开发方案.md` |
| 当前版本范围、必须做、不做、验收标准 | `.codex/scope.md`、`docs/版本路线图.md`、`docs/项目任务看板.md` |
| 技术栈选择、替代方案、选型理由 | `docs/技术选型.md`、`.codex/style.md`、`.codex/commands.md` |
| 运行环境、中间件、外部 API、硬件 | `docs/环境矩阵.md`、`docs/发布流水线.md`、`docs/风险登记册.md` |
| 数据、接口、鉴权、兼容要求 | `docs/需求文档.md`、`docs/接口文档.md`、`docs/数据库设计.md` |
| 安全、权限、凭据、外部动作 | `.codex/security.md`、`docs/安全威胁建模.md`、`docs/依赖安全审查.md` |
| 测试、构建、验证要求 | `.codex/testing.md`、`docs/测试文档.md`、`.codex/commands.md` |
| Git、版本号、发布说明 | `.codex/git.md`、`docs/版本更新记录.md` |
| CI/CD、部署、回滚、打包 | `docs/发布流水线.md`、`docs/部署文档.md` |
| 负责人、模块边界、评审责任 | `docs/代码所有权.md` |
| Epic、Feature、Task、Bug | `docs/项目任务看板.md`、`docs/追踪矩阵.md` |

## 填充原则

- 只写入问答中能支持的事实，不编造项目细节。
- 对未知信息保留 `待确认` 或 `TBD`，并在输出中列为问题。
- 如果文件已有真实内容，以合并为主，不整体覆盖。
- 如果问答和已有项目文件冲突，优先保留已有项目事实并提醒用户确认。
- 技术栈规则只读取选中的 `.codex/stacks/<stack>/`。
- 对 Lite 项目只填最小必要文档；对 Standard 和 Enterprise 项目补齐更多治理文档。

## 模式差异

| 模式 | 必填文档 |
| --- | --- |
| Lite | `.codex/project.md`、`.codex/scope.md`、`.codex/commands.md`、`docs/项目开发方案.md`、`docs/版本更新记录.md` |
| Standard | Lite + `docs/需求文档.md`、`docs/架构设计.md`、`docs/技术选型.md`、`docs/版本路线图.md`、`docs/项目任务看板.md`、`docs/测试文档.md` |
| Enterprise | Standard + ADR/RFC、风险、变更影响、环境矩阵、发布流水线、代码所有权、安全治理、质量指标 |

## 完成标准

- 核心文档不再只是空模板。
- `docs/项目任务看板.md` 至少有初始 `EPIC-001`、`FEAT-001`、`TASK-001`。
- `docs/版本路线图.md` 至少有 v0.1.0 和 v0.1.1 的第一版结论。
- `.codex/commands.md` 至少说明可运行命令、未知命令或需要用户确认的命令。
- 输出明确说明是否允许进入编码。
