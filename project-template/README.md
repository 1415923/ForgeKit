# 项目模板

把本目录内容复制到具体项目根目录后使用。

ForgeKit 在生成项目内提供轻量 AI Engineering Loop：澄清目标、判断风险、准备必要 change 工件、实施、验证、审查、发布记录和复盘。低风险改动保持轻流程；中高风险改动使用 `.forgekit/changes/<id>/` 留下可审查工件。

## 初始化顺序

1. Codex 读取 `AGENTS.md`；Claude Code 读取 `CLAUDE.md`，确认任务路由和禁止动作。
2. 读取 `.forgekit/docs/document-responsibility.md`，判断哪些 managed docs 需要读、哪些不应更新。
3. 读取 `.forgekit/docs/codebase-map.md`，找到代码搜索起点、模块入口和局部验证命令。
4. 用户意图不清楚，或问题涉及任务来源、当前任务、验证结果、工作日志、汇报、loop、review、worktree、handoff 时，读取 `.forgekit/docs/workflow-router.md`。
5. 需要验证时读取 `.forgekit/docs/local-toolchain.md`；方向不清时读取 `.forgekit/docs/codex-next-work-order.md`。
6. 工作来自领导、微信、计划表、会议、个人规划、用户反馈、bug、技术债或测试失败时，先写 `.forgekit/docs/task-intake.md`；补充和确认默认归并到已有 Source，只有满足任务准入时才进入 `task-board.md`。
7. 中高风险变更使用 `.forgekit/changes/<id>/`；低风险改动保持轻流程。
8. 触发式文档只在事件发生时更新：缺陷复盘、事故复盘、依赖审查、威胁建模、发布流水线、traceability、loop、maker-checker、worktree 等都不是日常必填。
9. 长会话阶段边界、compact/clear 前、子 agent 返回关键结论后，以及 handoff/commit/tag 前，按 `.forgekit/docs/context-continuity.md` 做最小 checkpoint；不复制完整聊天或长日志。
10. 编码前分别确认业务 `Implementation Scope` 与 `Governance Writeback Scope`。默认 `ManagedDocsWriteback: minimal`：完成后最小更新实际进展、真实任务状态、用户/版本可见变化和当前 change；只有用户明确禁写文档时才关闭，不把同一事实重复写入多个文件。

## 升级兼容

从外层 ForgeKitRoot 统一检查当前项目：

```bash
python scripts/forgekit-project.py --target <project-root>
```

该统一入口属于 ForgeKitRoot，不复制到生成项目。它自动识别 init、up-to-date、upgrade-sync、工具版本过旧和 legacy adoption；非交互默认只展示计划，显式 `--yes` 才写入。下面的 `forgekit-upgrade.py` 是项目内高级入口。

v0.36.0 及以后初始化的项目使用 `.forgekit/state.json` 和 `migrations/` 做版本迁移：

```bash
python scripts/forgekit-upgrade.py check --repo-root .
python scripts/forgekit-upgrade.py plan --repo-root .
python scripts/forgekit-upgrade.py apply --safe --repo-root .
```

`check` 和 `plan` 不改文件；`apply --safe` 只执行 migration 明确标记为 safe 的动作。v0.35.x 及更早项目不自动升级，统一按接手既有项目做 adoption inventory，并在用户确认后建立新 state。旧 guided upgrade 脚本仅作为 legacy report-only 兼容入口保留；不要默认读取全量 candidates 或 upgrade-export。

## 项目维护

用户说“安装/初始化/更新/同步 ForgeKit”时，优先路由到 ForgeKitRoot 的统一入口并识别 `project-bootstrap`。用户说“整理一下升级”“阶段结束了”“归档一下”时，先读 `.forgekit/docs/project-maintenance.md` 并识别其他 `MaintenanceIntent`。所有维护动作先 plan；Archive Capsule 只有在用户确认后才 apply，并生成 summary、items log 和 archive index。

## 根因与失败路径审查

复杂问题、重复修补或高风险设计按需读取 `.forgekit/docs/reasoning-review.md`，先执行 First-Principles Pass；高风险收口前执行 Adversarial Review Pass。两者只输出推导、风险和验证项，不自动修代码，也不替代独立 reviewer。

## 可选增强

- `.agents/skills/`：项目本地 skills，内置项目初始化、代码审查、发布检查和安全审查；引用 skill 时优先读取 `.agents/skills/<skill>/SKILL.md`。
- `.claude/skills/forgekit-project-workflow/`：Claude Code 轻量入口 skill，按 ECC 式薄入口思路路由到共享项目文档和治理规则，不复制全量 skills。
- `.codex/agents/`：Codex native agent 模板；只有实际观察到 `forgekit-*` 被调用，才算 native 可用。
- `.codex/config.toml`：项目级 agents 安全设置，只放 `max_threads` / `max_depth` 等轻量配置，不写全局认证、provider 或 profile。
- `.codex/config.example.toml`：Codex 扩展配置示例，默认不覆盖用户真实配置。

## 项目级规则边界

这里的规则只描述当前项目，不记录用户电脑上的固定路径和个人权限偏好。

## Agent Harness

- `AGENTS.md`：Codex 第一入口，只放任务路由、上下文规则和禁止动作。
- `CLAUDE.md`：Claude Code 第一入口，只放任务路由、上下文规则和禁止动作。
- `.forgekit/docs/document-responsibility.md`：管理文档职责矩阵，记录读者、默认读取策略、触发条件、写什么和不写什么。
- `.forgekit/docs/codebase-map.md`：代码搜索起点，记录模块入口、常用关键词和局部验证命令，不做项目百科。
- `.forgekit/docs/workflow-router.md`：用户意图路由表，决定一句话该读什么、写什么、不要写什么。
- `.forgekit/docs/context-continuity.md`：定义关键事实、checkpoint 触发和上下文存活位置，防止结论只留在聊天里。
- `.forgekit/docs/local-toolchain.md`：记录各技术栈 LSP、lint、test、build 和局部验证能力。
- `governance/agent-harness.md`：说明 AGENTS 分层、agentic search、停止编码条件和输出要求。
- `governance/ai-engineering-loop.md`：说明 low / medium / high 风险分级、change 工件和交付闭环。
- `governance/large-change-execution.md`：说明大任务探索、计划、分会话执行和 review 闸门。
- `governance/team-agent-rollout.md`：说明 commands、hooks、plugin、MCP、CI 和团队推广的启用顺序。
- `governance/agent-suitability.md`：说明项目是否适合直接套用 Codex agent 工作流。
- `.forgekit/docs/exploration-report.md`、`.forgekit/docs/implementation-plan.md`：跨模块或高风险改动前的执行产物。
- `.forgekit/docs/project-suitability.md`、`.forgekit/docs/project-trial-record.md`：初始化前判断适用性，并把真实项目经验回灌。
- `.forgekit/docs/codex-next-work-order.md`：初始化后继续访谈、确认 MVP、落地条件和验证方式。
- `.forgekit/docs/loop-readiness.md`、`.forgekit/docs/loop-blueprint.md`：判断项目是否适合安全运行 loop，并定义可审查的 loop 设计图纸；它们不是自动执行授权。
- `.forgekit/docs/loop-operations.md`：定义用户显式触发的 loop dry-run、one-step、bounded-auto、review-only、continue、stop/handoff；它不是后台自动化或无人值守 runner。
- `.forgekit/docs/bounded-auto-loop-policy.md`：定义有限授权的多阶段推进边界、预算、停止条件和 handoff；它不是自动 runner。
- Managed docs 写回默认是 `minimal`：业务文件范围不会隐式禁止 `work-log.md`、必要的 `task-board.md` / `changelog.md` / 当前 change 写回；`review-only` 和 report-only 报告仍不写或自动修复文档。
- `.forgekit/docs/native-agent-adapter.md`：说明 Claude Code / Codex 原生 agent 配置适配、验证清单和 fallback 记录规则；生成配置不等于 runtime 已注册，只有 invoked 才能记录为 native 可用。
- `.forgekit/docs/maker-checker-protocol.md`：定义 Maker 与独立只读 Checker 的审查协议；代码默认 independent review，self-review 不能冒充独立审查。
- `.claude/skills/forgekit-request-code-review/`：Maker 组装最小 review packet 并请求 `forgekit-code-reviewer`；`.claude/skills/forgekit-code-review/`：Reviewer 的只读流程和按需 references。
- `.forgekit/docs/worktree-playbook.md`：定义手动 worktree 并行隔离、命名、检查、Maker/Checker 用法和清理规则；它不是自动调度器。
- `.forgekit/docs/task-intake.md`：记录工作来源原文或原始想法、Update Notes、Task Decision、Derived Task IDs 和人工确认状态；它不是需求文档、任务看板或 changelog。`.forgekit/docs/task-board.md` 只接收有动作、owner、下一步、Source ID 和验证方式的可执行任务。
- `.codex/commands-catalog.md`、`.codex/hooks.md`：可选命令和 hook 候选，默认不自动启用。
- `.codex/automation-decision.md`：判断重复流程应该做成 skill、command、hook、script、plugin、MCP 还是保留文档。
- `.forgekit/changes/_template/`：proposal、design、tasks、verification、review、ship、retro 模板。
- `scripts/detect-local-toolchain.ps1`、`scripts/run-harness-check.ps1`、`scripts/check-doc-sync.ps1`、`scripts/check-doc-sync.sh`、`scripts/check-codex-native-agents.py`：只读检测脚本，用于把 harness 和 native adapter 从文档推进到可执行检查。
- `scripts/doc-health-report.py`、`scripts/source-trace-report.py`、`scripts/handoff-package.py`：report-only 脚本，分别生成文档健康报告、来源追溯报告和 review-ready 交付包；不自动修复、不补链、不提交、不创建 PR。
- `scripts/install-hooks.ps1`、`scripts/install-hooks.sh`：opt-in 安装、查看、卸载 Git hook，不默认启用。

使用优先级：Codex 从 `AGENTS.md` 开始，Claude Code 从 `CLAUDE.md` 开始；如果任务命中 ForgeKit skill，优先读取项目内 `.agents/skills/<skill>/SKILL.md`，不要假设用户级或系统级 skill 路径存在；然后进入 `.forgekit/docs/document-responsibility.md` -> `.forgekit/docs/codebase-map.md` -> 必要的 `.forgekit/docs/workflow-router.md` / `.forgekit/docs/local-toolchain.md` / `.forgekit/docs/codex-next-work-order.md` -> `.codex/` -> 相关 `.codex/stacks/<stack>/` -> 任务相关治理文件。不要默认读取全部 `.forgekit/docs/**` 或治理文档。

常见 stack 名称：`java-springboot`、`vue`、`react`、`python-fastapi`、
ode-express`、`csharp-dotnet`、`go-service`、`php-laravel`、`rust-cli-service`、`flutter-dart`、`cpp-cmake`、`kotlin-spring`、`swift-ios`、`ruby-rails`、`r-data-analysis`、`fpga-vivado-vitis`。只读取当前项目实际选择的 stack，避免把无关语言规则混入上下文。

大任务优先级：先完成 `.forgekit/docs/exploration-report.md`，再完成 `.forgekit/docs/implementation-plan.md`，确认后才进入分阶段编码。

团队工具链优先级：先沉淀 command，再考虑 hook；跨项目稳定后再考虑 plugin；MCP 默认只读优先，写操作必须人工确认。文档同步类 hook 建议从 `scripts/check-doc-sync.ps1` 或 `scripts/check-doc-sync.sh` 的只提示模式开始，确认噪音可接受后再使用 strict 模式。

ForgeKit 采用根级统一 plugin 表面：`.codex-plugin/`、`.claude-plugin/` 和共享 `skills/` 位于模板仓库根。生成项目仍应按本文件、`AGENTS.md` 和 `CLAUDE.md` 的边界执行，不因安装 plugin 而默认启用 hook、MCP 或外部写操作。

Claude Code 入口是薄入口：`CLAUDE.md` 和 `.claude/skills/forgekit-project-workflow/` 只负责路由和门禁；共享项目事实仍写入 `.codex/`、`.forgekit/docs/` 和 `governance/`，避免为不同 AI 工具维护多套项目事实。

适用性优先级：无 Git、目录混乱、无法验证、大量二进制或非工程师主导的项目，不应直接套用 Standard / Enterprise，应先补工程条件或走 Custom。

## 接手既有项目

如果不是新项目，而是接手已有项目，应先使用 `.agents/skills/handover-review/`：

1. 完成 `.forgekit/docs/handover-audit.md`。
2. 完成 `.forgekit/docs/defect-fix-plan.md`。
3. 先修复 P0/P1 问题，不默认改变大架构。
4. 记录兼容边界。
5. 再基于当前技术栈、实际需求和版本闸门规划后续开发。

## 治理层

- `governance/sdlc.md`：通用 SDLC。
- `governance/architecture-governance.md`：arc42 轻量映射和 ADR 规则。
- `governance/rfc-process.md`：RFC / Design Proposal 流程。
- `governance/adr-process.md`：ADR 流程。
- `governance/traceability.md`：追踪编号体系。
- `governance/definition-of-ready.md`：进入开发前检查。
- `governance/definition-of-done.md`：完成标准。
- `governance/risk-management.md`：风险管理流程。
- `governance/change-management.md`：变更管理流程。
- `governance/incident-process.md`：事故 / 缺陷复盘流程。
- `governance/security-governance.md`：威胁建模、依赖审查和安全发布闸门。
- `governance/cicd-environment-governance.md`：环境矩阵、发布流水线和回滚治理。
- `governance/code-ownership-review-governance.md`：代码所有权、必要评审人和 Critical 区域规则。
- `governance/project-management-task-model.md`：Epic、Feature、Task、Bug 状态流和版本映射。
- `governance/project-bootstrap-fill.md`：初始化问答到第一版项目文档的填充映射。
- `governance/agent-harness.md`：Codex 上下文入口、代码搜索和 AGENTS 分层规则。
- `governance/version-governance.md`：版本路线图和推进闸门。
- `governance/quality-metrics.md`：DORA 风格轻量质量指标。
- `governance/technical-debt-management.md`：技术债管理流程。
