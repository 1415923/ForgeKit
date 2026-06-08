# Codex 项目级规则

## 总原则

- 先读取 `governance/overview.md`，再按项目入口选择新项目、接手项目、Bug 修复、发布或安全审查流程。
- 先读取 `.forgekit/project-boundary.yml`，确认 ForgeKitRoot、ProjectRoot、managed docs root、change root、business docs roots 和 write policy。
- 修改前先阅读相关代码、文档和配置。
- 优先遵循本项目已有风格。
- 只修改与当前任务相关的文件。
- 大范围架构调整前必须先给出方案。
- 修改后运行 `.codex/commands.md` 中对应的验证命令。
- 涉及用户可见行为变化时，更新 `.forgekit/docs/changelog.md`。
- 安全敏感、权限、外部动作、凭据、部署相关变更必须参考 `.codex/security.md`。
- 版本推进必须参考 `.codex/version-gates.md` 和 `.forgekit/docs/version-roadmap.md`。
- 接手既有项目必须先参考 `.codex/handover.md`，先审计和修复明确问题，再规划后续开发。
- 复杂任务优先拆分为计划、实现、验证、审查四个阶段。
- 中高风险任务必须参考 `governance/ai-engineering-loop.md`，并按 `.forgekit/changes/<change-id>/` 的风险工件推进。
- commands、hooks、plugin、MCP、CI、issue/PR 集成必须先参考 `governance/team-agent-rollout.md`。

## Boundary First

- ForgeKitRoot 是工具包、模板和规则来源；除非当前任务是维护 ForgeKit 本体，否则默认只读。
- ProjectRoot 是业务仓库和 Git 提交位置。
- ForgeKit 治理文档默认写入 `.forgekit/docs`。
- 中高风险 change 工件默认写入 `.forgekit/changes`。
- 业务 `docs/` 默认是 read-mostly 证据源：允许读取、引用和抽取事实，不写 ForgeKit 治理模板。
- `.forgekit/template-lock.json` 是安装基线；report-only upgrade 期间不要写回 lock。
- `.forgekit/upgrade-export/**` 是候选模板对比材料，不是当前态文档、活跃 change、发布证据或 changelog 内容。
- 如果用户要求把 ForgeKit 事实合并进业务 `docs/`，先列出目标文件、写入原因、与现有内容的关系和覆盖风险，等用户确认后再写。
- `src/**`、`tests/**`、`scripts/**` 属于 task_scoped：任务开始前确认范围，确认后可在本任务范围内修改。

## AI Coding 四条基本规则

这四条规则用于所有实现任务，目标是让 AI 先收敛问题，再做小而可验证的修改。外部文章中提到的准确率数字不作为项目指标；ForgeKit 只吸收可执行的工作方式。

### Think Before Coding：先想清楚再编码

- 不假设隐藏的产品、架构、数据、部署或兼容性约束。
- 当一个需求存在多个合理解释时，先追问或给出方案选项，不直接编码。
- 修改前说明关键取舍、风险和准备采用的最小可行路径。

### Simplicity First：简洁优先

- 写能解决已确认问题的最小实现。
- 不主动增加未请求的功能、框架、抽象、依赖或配置层。
- 如果已有实现可以用更少代码清晰表达，优先删除无用复杂度，而不是继续叠加。

### Surgical Changes：精准修改

- 只改当前任务真正需要的文件、接口和行为。
- 不因为附近代码“不够理想”就顺手重构。
- 命名、目录、测试、错误处理和提交粒度优先匹配项目现有风格。

### Goal-Driven Execution：目标驱动验证

- 把模糊任务转成可观察的成功标准。
- 修 Bug 时，优先找到或补一个能复现问题的验证方式。
- 完成后明确说明用哪个测试、命令、检查或人工步骤证明结果成立。

## 开发边界

当前允许修改的范围：

- 待补充

当前避免修改的范围：

- 待补充

## 决策顺序

当规则冲突时，按以下优先级处理：

1. 用户在当前对话中的明确要求。
2. 当前项目 `.codex/` 规则。
3. 项目现有代码和文档体现出的约定。
4. 用户级通用规则。
5. 通用工程最佳实践。

## 需要先确认的变更

- 改变技术栈。
- 改变目录结构。
- 改变公共接口。
- 改变数据库结构。
- 删除兼容逻辑。
- 引入新的重量级依赖。
- 修改部署、权限、鉴权、安全策略。
- 启用或修改 MCP、agent、skill、hook、插件。
- 启用会联网、读取凭据、写外部系统或自动阻断流程的 command / hook / MCP。
- 跳过 review/refactor 中版本，直接推进下一个大版本。

## 风险分级工作流

- low：单文件、小文案、局部测试或无公共行为影响的修复；可轻流程推进，但仍需说明验证结果。
- medium：多文件、小功能、脚本、模板或用户可见流程变化；先准备 `proposal.md`、`tasks.md`、`verification.md`、`review.md`。
- high：架构、迁移、安全、权限、部署、跨平台脚本或兼容性风险；先准备 `proposal.md`、`design.md`、`tasks.md`、`verification.md`、`review.md`、`ship.md`。
- `retro.md` 只在高风险、重大变更或用户要求时推荐，不强制所有变更都有。

## 可选增强规则

- 项目 skill 放在 `.agents/skills/`，只在任务匹配时使用。
- 多 agent 角色放在 `.codex/agents/`，默认不启用。
- `.codex/config.example.toml` 只能作为示例，不能直接覆盖用户级配置。
- 技术栈专用规则按需从 `templates/<stack>/` 引入，不加载无关技术栈内容。

## 开发方案与版本路线图

- SDLC、架构治理、版本治理、质量指标统一记录在 `governance/`。
- 项目初期必须先讨论并形成 `.forgekit/docs/project-plan.md`。
- 大版本规划必须写入 `.forgekit/docs/version-roadmap.md`。
- 重要架构决策必须写入 `.forgekit/docs/adr/`。
- 重要方案讨论必须先写入 `.forgekit/docs/rfc/`。
- 需求、RFC、ADR、任务、测试、缺陷应维护在 `.forgekit/docs/traceability.md`。
- 高风险必须写入 `.forgekit/docs/risk-register.md`。
- 高影响变更必须写入 `.forgekit/docs/change-impact.md`，并参考 `governance/change-management.md`。
- 开发前检查 `governance/definition-of-ready.md`，完成时检查 `governance/definition-of-done.md`。
- 如果项目开发方案、技术选型、软硬件落地条件没有明确结论，不应直接进入大规模编码。
- 每个大版本结束后，必须先完成 review/refactor 中版本，再推进下一个大版本。
