# 项目 Skills

记录本项目推荐使用的 Codex skills 或专项工作流。

## 推荐 Skills

| Skill | 使用场景 | 备注 |
| --- | --- | --- |
| project-init | 项目初始化、补齐 `.codex/` 和 `.forgekit/docs/` | 已内置于 `.agents/skills/project-init/` |
| project-bootstrap-fill | 根据初始化问答生成第一版项目规则和文档 | 已内置于 `.agents/skills/project-bootstrap-fill/` |
| project-suitability | 初始化、接手或风险不明时评估是否适合 ForgeKit 工作流 | 已内置于 `.agents/skills/project-suitability/` |
| document-backfill | 逐篇阅读既有项目文档并回填 ForgeKit managed docs root | 已内置于 `.agents/skills/document-backfill/` |
| handover-review | 接手既有项目、现状审计、兼容边界、缺陷修复计划 | 已内置于 `.agents/skills/handover-review/` |
| large-change-planning | 大任务、跨模块、高风险、迁移或重构前的探索和实施计划 | 已内置于 `.agents/skills/large-change-planning/` |
| code-review | 审查 diff、查找 bug、回归、安全风险、测试缺口 | 已内置于 `.agents/skills/code-review/` |
| release-check | 发布前检查、版本记录、测试构建、部署风险 | 已内置于 `.agents/skills/release-check/` |
| security-review | 权限、鉴权、凭据、外部输入、依赖变化 | 已内置于 `.agents/skills/security-review/` |

## 使用规则

- 只有在任务匹配时使用对应 skill。
- 使用 skill 前先阅读其说明。
- skill 不能覆盖本项目的明确规则。
- 使用 skill 前先通过 `AGENTS.md` 和 `.forgekit/docs/codebase-map.md` 确认入口，不要让 skill 触发全量读取。
- 第三方 skill 视为供应链输入，引入前需要审查权限、网络、凭据和写入范围。
- 不全量复制大型 skill 库，只复制当前项目实际需要的部分。

## Harness 关系

- `AGENTS.md` 负责判断是否应该使用 skill。
- `.forgekit/docs/codebase-map.md` 负责告诉 skill 从哪里开始找代码。
- `governance/agent-harness.md` 负责维护上下文分层、搜索方式和停止编码条件。
- `governance/team-agent-rollout.md` 负责判断重复流程应该沉淀为 command、hook、plugin 还是 MCP。
- 重复出现的长提示词应优先沉淀为项目 skill，而不是继续塞进 `AGENTS.md` 或 HTML。
- 是否做成 skill、command、hook、script、plugin 或 MCP，先参考 `.codex/automation-decision.md`。

## 项目自定义工作流

- 大任务、多模块改动、迁移、重构或高风险变更：优先使用 `large-change-planning`，按 `governance/large-change-execution.md` 生成探索报告和实施计划，再进入编码。
- 高频重复动作：先登记到 `.codex/commands-catalog.md`；需要自动化时再评估 `.codex/hooks.md`。
- `api-design`、`e2e-testing`、`docs-research` 等不要默认内置；只有当项目内反复出现且输入输出稳定时再自建。
- 初始化后方向不清楚：先读 `.forgekit/docs/codex-next-work-order.md`，必要时运行 `scripts/detect-local-toolchain.ps1` 和 `scripts/run-harness-check.ps1` 作为只读事实检查。

## ECC 参考

ECC 的 Codex 适配使用 `.agents/skills/` 作为 skill 目录。本项目采用这个目录结构，但不内置 ECC 第三方 skill。

## Plugin 分发

ForgeKit 采用根级统一 plugin 表面：`.codex-plugin/`、`.claude-plugin/` 和共享 `skills/` 位于模板仓库根。plugin 不应包含个人 `user-rules/`、本机路径、凭据或外部开发记录，也不应默认启用 hooks、MCP 或外部写操作。团队引入或升级 plugin 前，先按 `governance/team-agent-rollout.md` 做权限和维护责任审查。
