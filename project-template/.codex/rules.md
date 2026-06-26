# Codex 项目级规则

## 总原则

- 先读取 `governance/overview.md`，再按项目入口选择新项目、接手项目、Bug 修复、发布或安全审查流程。
- 先读取 `.forgekit/project-boundary.yml`，确认 ForgeKitRoot、ProjectRoot、managed docs root、change root、business docs roots 和 write policy。
- 修改前先阅读相关代码、文档和配置。
- 不要默认全量读取 `.forgekit/docs/**`；先看 `.forgekit/docs/document-responsibility.md` 和 `.forgekit/docs/codebase-map.md`，再按任务触发读取相关文档。
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
- 文档生命周期或归档判断必须参考 `.forgekit/docs/document-lifecycle.md`；归档只作为历史材料，不替代 current docs。
- commands、hooks、plugin、MCP、CI、issue/PR 集成必须先参考 `governance/team-agent-rollout.md`。

## Boundary First

- ForgeKitRoot 是工具包、模板和规则来源；除非当前任务是维护 ForgeKit 本体，否则默认只读。
- ProjectRoot 是业务仓库和 Git 提交位置。
- ForgeKit 治理文档默认写入 `.forgekit/docs`。
- 中高风险 change 工件默认写入 `.forgekit/changes`。
- 业务 `docs/` 默认是 read-mostly 证据源：允许读取、引用和抽取事实，不写 ForgeKit 治理模板。
- `.forgekit/template-lock.json` 是安装基线；report-only upgrade 期间不要写回 lock。
- `.forgekit/upgrade-export/**` 是候选模板对比材料，不是当前态文档、活跃 change、发布证据或 changelog 内容。
- `.forgekit/docs/**` 是 current state docs，只保留当前事实和稳定结论，不堆长期过程流水。
- 更新 managed docs 前先判断内容类型：任务来源、需求事实、任务状态、验证方法、工作顺序、版本变化、风险、设计决策或历史证据。
- 同一事实只写到负责的文档；其他文档只做引用，不复制长段内容。
- 触发式文档只有事件发生才更新；不要把缺陷复盘、事故复盘、依赖审查、威胁建模、发布流水线、traceability、loop、maker-checker 或 worktree 文档当作日常必填项。
- 给用户看的文档要短、自然、可确认；先写结论，再写必要证据，避免模板腔和长篇 AI 过程叙述。
- `.forgekit/changes/<change-id>/**` 是 change process docs，只记录单次中高风险变更的 proposal/design/tasks/verification/review/ship/retro。
- `.forgekit/archive/**` 是 archive docs，不是当前事实来源；默认不读，只有用户要求历史、审计、回归、复盘、事故复盘、解释历史决策或比对旧版本时才读取。
- `.forgekit/archive-plan.md` 是 dry-run 生成产物，不是 current docs 或 active change；每次 dry-run 可以覆盖它。
- `.forgekit/archive-apply-report.md` 是 apply 生成产物，不是 current docs、active change 或发布证据。
- `.forgekit/archive-reference-report.md` 是 reference-check 生成产物，不是 current docs、active change 或发布证据。
- `.forgekit/current-docs-sync-report.md` 是 sync-check 生成产物，不是 current docs、active change，也不等于 current docs 语义正确性证明。
- `.forgekit/smart-archive-report.md` 是 smart-check 生成的 report-only 建议，不是归档许可，不替代用户确认，也不是 current truth。
- `.forgekit/docs/task-intake.md` 是工作来源台账。领导任务、微信任务、计划表格子、会议任务、文档任务、个人规划、用户反馈、bug、技术债、测试失败和调研发现都先归并来源，再生成任务；补充、确认、改期或责任修正默认写入已有 Source 的 `Update Notes`，不要默认创建新任务。
- `.forgekit/docs/task-board.md` 只接收可执行任务：必须有动作、owner 或待确认 owner、下一步、`Source ID`、完成标准或验证方式。过时任务必须标为 `Superseded` / `Dropped`，不要继续出现在当前重点。
- `.forgekit/docs/work-log.md` 只记录推进过程、验证、提交/推送、阻塞和确认，并引用 `Task ID` / `Source ID`。工作日志里的后续跟进不自动成为任务；先回到 task-intake 做 Task Decision。
- 拆解任务必须引用 Source ID；未经人工确认的派发内容必须保持 `Human Review: pending`，不得视为最终事实；不得把账号、密码、token、证书、环境地址或敏感配置原样写入 managed docs。
- `.forgekit/docs/work-log.md` 是个人工作顺序记录，用于交接上下文和中断会话恢复；用户要求“更新 ForgeKit 文档”且本轮包含阶段收口、验证、提交/推送、阻塞、领导/组长确认时应同步，用户明确要求“同步工作日志”时必须同步；仅更新稳定技术事实时不强制同步。
- `.forgekit/upgrade/**` 是升级引导生成物。先读 `upgrade-actions.md`，候选模板只用于对比，不是当前态文档。
- `.forgekit/docs/loop-readiness.md` 和 `.forgekit/docs/loop-blueprint.md` 是可审查的 loop 设计文档，不是自动执行授权。
- `.forgekit/docs/loop-operations.md` 是显式触发的操作协议，不是自动 runner 或无人值守 loop 授权。
- `.forgekit/docs/bounded-auto-loop-policy.md` 只是 bounded-auto policy；用户未明确授权时不得进入 bounded-auto。
- `.forgekit/docs/maker-checker-protocol.md` 是审查协议，不是多 agent 调度或自动 checker 授权。
- `.forgekit/docs/worktree-playbook.md` 是手动隔离指南，不是自动 worktree 调度或 agent 编排。
- `.forgekit/docs/native-agent-adapter.md` 是 opt-in 原生 agent 配置适配说明，不授权自动执行、调度、merge、commit、push 或 PR。
- 生成 native agent 配置不等于 runtime 已注册；不得把 fallback 或 simulated 执行称为 native agent 成功。
- native lifecycle 分为 generated、installed、registered、invoked；`native_agent_status` 只允许 available/unavailable/unverified，invoked 写入 `native_agent_lifecycle` 或 `agent_invocation_observed`。
- 原生调用证据由父运行时记录，子 agent 不自行判断 `native_agent_status`。
- 如果 Codex 只暴露 default、explorer 或 worker，必须记录 `native_agent_status: unavailable`，不得称为 native 成功。
- 如果 spawn 因 thread limit、`max_threads` 或已完成 agent 未关闭而失败，记录为容量阻塞，不得写成 native unavailable。
- native-only verification 默认只读；除非用户明确要求“记录到文档”，不得自动写 task-intake、work-log 或 loop state。
- fallback 必须有用户明确允许，或由 workflow 规则明确允许。
- bounded-auto 或 loop 执行必须写明 `agent_mode`；native custom agent 未观察到前，`native_agent_status` 必须是 `unverified`。
- loop 必须有状态文件、验证命令、停止条件和人工升级入口。
- loop 不默认修改 business docs、secrets、deploy 或 CI。
- 不得自行进入 loop mode；只有用户明确要求 loop dry-run、one-step、bounded-auto、review-only、continue 或 stop/handoff 时才按 loop operation 规则执行。
- one-step 或 bounded-auto 前必须复述 scope、stages、budget、forbidden actions、stop conditions、agent mode 和本轮是否会修改文件。
- bounded-auto 遇到范围不清、超预算、验证失败、触及 forbidden actions 或 agent mode 不满足时必须停。
- one-step 每轮结束必须停；review-only 绝不能改文件或运行写操作。
- loop continue 不得自动连续运行，每一轮都需要用户明确触发。
- scope 不清、预算超限、验证失败或触及 forbidden paths 时必须停止并升级给人。
- loop 输出必须写回 `.forgekit/docs/work-log.md` 或指定 state file；bounded-auto 每阶段必须 checkpoint，最终必须 handoff。
- 不得默认修改 business docs、secrets、deploy、CI 或 `.forgekit/template-lock.json`。
- 中高风险代码变更应区分 Maker phase 和 Checker phase。
- Maker phase 可以声明 `ready for check`，但不得把自己的实现视为最终通过。
- Checker phase 应优先复核 diff、验证结果、风险和文档同步，并输出 `pass`、`needs-fix` 或 `manual-review`。
- Checker 不应扩大需求范围，不应顺手实现新功能，除非用户明确要求。
- 对公司或业务项目，Checker 必须检查是否误写敏感信息、业务 docs、secrets、deploy 或 CI。
- 不得自行创建 worktree，除非用户明确要求。
- 创建 worktree 前必须确认 `git status --short` 干净，并说明 base branch、worktree path、branch name、allowed paths、validation command 和 cleanup plan。
- 不得自动 merge、push、delete branch、remove worktree、创建 PR、启动 agent 或调度 worktree 任务。
- worktree 结果必须写回 `.forgekit/docs/work-log.md` 或 scoped change review。
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
- Native Agent Adapter 生成的 `.codex/agents/` 和 `.claude/agents/` 只作为可审查配置模板，需用户显式启用。
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
