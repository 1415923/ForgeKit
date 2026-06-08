# 初始化填充流程

本文件定义如何把 `init-questionnaire.md` 或用户粘贴的问答内容转换成项目第一版 `.codex/` 规则和 `.forgekit/docs/` managed docs。

## 目标

让用户不必手工逐个编辑 Markdown。Codex 应先读取问答事实，再把稳定信息合并到核心文档中，并把未知项保留为待确认问题。

## 输入

| 来源 | 说明 |
| --- | --- |
| `.codex/init.generated.md` | 初始化脚本生成的项目名和技术栈 |
| `.codex/questionnaires/init-questionnaire.md` | 项目事实的主要来源 |
| `.codex/stacks/<stack>/` | 技术栈规则、命令和检查清单 |
| 用户当前对话补充 | 优先级高于空模板，低于项目已有明确事实 |
| 现有 README / 构建配置 | 接手或已有项目的真实事实 |

## 输出文档映射

| 问答内容 | 目标文档 |
| --- | --- |
| 项目名称、目标、用户、交付形式、阶段 | `.codex/project.md`、`.forgekit/docs/project-plan.md` |
| 当前版本范围、必须做、不做、验收标准 | `.codex/scope.md`、`.forgekit/docs/version-roadmap.md`、`.forgekit/docs/task-board.md` |
| 技术栈选择、替代方案、选型理由 | `.forgekit/docs/tech-decisions.md`、`.codex/style.md`、`.codex/commands.md` |
| 运行环境、中间件、外部 API、硬件 | `.forgekit/docs/environment-matrix.md`、`.forgekit/docs/release-pipeline.md`、`.forgekit/docs/risk-register.md` |
| 数据、接口、鉴权、兼容要求 | `.forgekit/docs/requirements.md`、`.forgekit/docs/api.md`、`.forgekit/docs/database-design.md` |
| 安全、权限、凭据、外部动作 | `.codex/security.md`、`.forgekit/docs/threat-model.md`、`.forgekit/docs/dependency-review.md` |
| 测试、构建、验证要求 | `.codex/testing.md`、`.forgekit/docs/testing.md`、`.codex/commands.md` |
| Git、版本号、发布说明 | `.codex/git.md`、`.forgekit/docs/changelog.md` |
| CI/CD、部署、回滚、打包 | `.forgekit/docs/release-pipeline.md`、`.forgekit/docs/deployment.md` |
| 负责人、模块边界、评审责任 | `.forgekit/docs/code-ownership.md` |
| Epic、Feature、Task、Bug | `.forgekit/docs/task-board.md`、`.forgekit/docs/traceability.md` |

## 填充原则

- 只写入问答中能支持的事实，不编造项目细节。
- 对未知信息保留 `待确认` 或 `TBD`，并在输出中列为问题。
- 对用户答不上来的关键问题，给出候选方案、取舍、推荐默认值和验证办法，不要只留下空问题。
- 对需要外部资料的问题，提出查阅路径，例如官方文档、同类项目、技术选型对比或小型原型；需要联网时先确认。
- 如果文件已有真实内容，以合并为主，不整体覆盖。
- 如果问答和已有项目文件冲突，优先保留已有项目事实并提醒用户确认。
- 技术栈规则只读取选中的 `.codex/stacks/<stack>/`。
- 对 Lite 项目只填最小必要文档；对 Standard 和 Enterprise 项目补齐更多治理文档。
- `.forgekit/docs/version-roadmap.md` 和 `.forgekit/docs/task-board.md` 在生成项目中只能保留真实项目计划和通用空模板，不应保留 ForgeKit 自身的 Agent Harness 历史任务。

## 模式差异

| 模式 | 必填文档 |
| --- | --- |
| Lite | `.codex/project.md`、`.codex/scope.md`、`.codex/commands.md`、`.forgekit/docs/project-plan.md`、`.forgekit/docs/changelog.md` |
| Standard | Lite + `.forgekit/docs/requirements.md`、`.forgekit/docs/architecture.md`、`.forgekit/docs/tech-decisions.md`、`.forgekit/docs/version-roadmap.md`、`.forgekit/docs/task-board.md`、`.forgekit/docs/testing.md` |
| Enterprise | Standard + ADR/RFC、风险、变更影响、环境矩阵、发布流水线、代码所有权、安全治理、质量指标 |

## 完成标准

- 核心文档不再只是空模板。
- `.forgekit/docs/task-board.md` 至少有初始 `EPIC-001`、`FEAT-001`、`TASK-001`。
- `.forgekit/docs/version-roadmap.md` 至少有 v0.1.0 和 v0.1.1 的第一版结论。
- `.codex/commands.md` 至少说明可运行命令、未知命令或需要用户确认的命令。
- 输出明确说明是否允许进入编码；如果不允许，应说明还差哪些决策、推荐默认值是什么、如何验证。
