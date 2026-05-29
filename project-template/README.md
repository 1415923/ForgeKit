# 项目模板

把本目录内容复制到具体项目根目录后使用。

## 初始化顺序

1. Codex 读取 `AGENTS.md`；Claude Code 读取 `CLAUDE.md`，确认任务路由和禁止动作。
2. 读取 `docs/代码库地图.md`，找到代码搜索起点、推荐启动目录和局部验证命令。
3. 读取 `docs/本地工具链检查.md`，确认 LSP、lint、test、build 和局部验证能力。
4. 读取 `docs/Codex下一步工作单.md`，把初始化摘要推进为方案访谈和任务拆分。
5. 可选运行 `scripts/detect-local-toolchain.ps1` 和 `scripts/run-harness-check.ps1`，只记录事实，不自动安装或改配置。
6. 读取 `governance/流程总览.md`，判断项目入口。
7. 填写 `.codex/project.md`，明确项目基本信息。
8. 填写 `.codex/scope.md`，明确当前版本范围。
9. 填写 `.codex/commands.md`，记录本项目常用命令。
10. 如果已有问答内容，优先使用 `project-bootstrap-fill` 根据 `.codex/questionnaires/项目初始化问答.md` 补齐第一版文档。
11. 新项目填写 `docs/项目开发方案.md` 和 `docs/版本路线图.md`。
12. 接手项目填写 `docs/既有项目接手审计.md` 和 `docs/缺陷修复计划.md`。
13. 重要方案讨论写入 `docs/rfc/`，重要架构决策写入 `docs/adr/`。
14. 需求、RFC、ADR、任务、测试、缺陷关系写入 `docs/追踪矩阵.md`。
15. 高风险写入 `docs/风险登记册.md`。
16. 高影响变更写入 `docs/变更影响评估.md`。
17. 严重事故或重复缺陷写入 `docs/事故复盘.md` 或 `docs/缺陷复盘.md`。
18. 安全敏感变更写入 `docs/安全威胁建模.md`，依赖变更写入 `docs/依赖安全审查.md`。
19. 环境和发布链路写入 `docs/环境矩阵.md` 和 `docs/发布流水线.md`。
20. 模块负责人和评审责任写入 `docs/代码所有权.md`。
21. Epic、Feature、Task、Bug 写入 `docs/项目任务看板.md`。
22. 技术债写入 `docs/技术债记录.md`，版本质量写入 `docs/质量指标记录.md`。
23. 开始编码前，确认 Definition of Ready；完成时确认 Definition of Done。

## 可选增强

- `.agents/skills/`：Codex 项目级 skills，内置项目初始化、代码审查、发布检查和安全审查。
- `.claude/skills/forgekit-project-workflow/`：Claude Code 轻量入口 skill，按 ECC 式薄入口思路路由到共享项目文档和治理规则，不复制全量 skills。
- `.codex/agents/`：多 agent 角色设计，默认不启用。
- `.codex/config.example.toml`：Codex 配置示例，默认不覆盖用户配置。

## 项目级规则边界

这里的规则只描述当前项目，不记录用户电脑上的固定路径和个人权限偏好。

## Agent Harness

- `AGENTS.md`：Codex 第一入口，只放任务路由、上下文规则和禁止动作。
- `CLAUDE.md`：Claude Code 第一入口，只放任务路由、上下文规则和禁止动作。
- `docs/代码库地图.md`：代码搜索起点，记录模块、入口文件、常用关键词和局部验证命令。
- `docs/本地工具链检查.md`：记录各技术栈 LSP、lint、test、build 和局部验证能力。
- `governance/agent-harness.md`：说明 AGENTS 分层、agentic search、停止编码条件和输出要求。
- `governance/large-change-execution.md`：说明大任务探索、计划、分会话执行和 review 闸门。
- `governance/team-agent-rollout.md`：说明 commands、hooks、plugin、MCP、CI 和团队推广的启用顺序。
- `governance/agent-suitability.md`：说明项目是否适合直接套用 Codex agent 工作流。
- `docs/探索报告.md`、`docs/实施计划.md`：跨模块或高风险改动前的执行产物。
- `docs/项目适用性评估.md`、`docs/真实项目试用记录.md`：初始化前判断适用性，并把真实项目经验回灌。
- `docs/Codex下一步工作单.md`：初始化后继续访谈、确认 MVP、落地条件和验证方式。
- `.codex/commands-catalog.md`、`.codex/hooks.md`：可选命令和 hook 候选，默认不自动启用。
- `.codex/automation-decision.md`：判断重复流程应该做成 skill、command、hook、script、plugin、MCP 还是保留文档。
- `scripts/detect-local-toolchain.ps1`、`scripts/run-harness-check.ps1`、`scripts/check-doc-sync.ps1`、`scripts/check-doc-sync.sh`：只读检测脚本，用于把 harness 从文档推进到可执行检查。
- `scripts/install-hooks.ps1`、`scripts/install-hooks.sh`：opt-in 安装、查看、卸载 Git hook，不默认启用。

使用优先级：Codex 从 `AGENTS.md` 开始，Claude Code 从 `CLAUDE.md` 开始，然后进入 `docs/代码库地图.md` -> `docs/本地工具链检查.md` -> `docs/Codex下一步工作单.md` -> `.codex/` -> 相关 `.codex/stacks/<stack>/` -> 任务相关治理文件。不要默认读取全部治理文档。

常见 stack 名称：`java-springboot`、`vue`、`react`、`python-fastapi`、`node-express`、`csharp-dotnet`、`go-service`、`php-laravel`、`rust-cli-service`、`flutter-dart`、`cpp-cmake`、`kotlin-spring`、`swift-ios`、`ruby-rails`、`r-data-analysis`、`fpga-vivado-vitis`。只读取当前项目实际选择的 stack，避免把无关语言规则混入上下文。

大任务优先级：先完成 `docs/探索报告.md`，再完成 `docs/实施计划.md`，确认后才进入分阶段编码。

团队工具链优先级：先沉淀 command，再考虑 hook；跨项目稳定后再考虑 plugin；MCP 默认只读优先，写操作必须人工确认。文档同步类 hook 建议从 `scripts/check-doc-sync.ps1` 或 `scripts/check-doc-sync.sh` 的只提示模式开始，确认噪音可接受后再使用 strict 模式。

ForgeKit v0.12.0 改为 ECC 式根级统一 plugin 表面：`.codex-plugin/`、`.claude-plugin/` 和共享 `skills/` 位于仓库根，不再维护 Codex/Claude 两个 plugin 子目录。生成项目仍应按本文件、`AGENTS.md` 和 `CLAUDE.md` 的边界执行，不因安装 plugin 而默认启用 hook、MCP 或外部写操作。

Claude Code 入口是薄入口：`CLAUDE.md` 和 `.claude/skills/forgekit-project-workflow/` 只负责路由和门禁；共享项目事实仍写入 `.codex/`、`docs/` 和 `governance/`，避免为不同 AI 工具维护多套项目事实。

适用性优先级：无 Git、目录混乱、无法验证、大量二进制或非工程师主导的项目，不应直接套用 Standard / Enterprise，应先补工程条件或走 Custom。

## 接手既有项目

如果不是新项目，而是接手已有项目，应先使用 `.agents/skills/handover-review/`：

1. 完成 `docs/既有项目接手审计.md`。
2. 完成 `docs/缺陷修复计划.md`。
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
