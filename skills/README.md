# 项目 Skills 目录

本目录用于放置项目级 Codex skills。

ECC 的 Codex 适配思路是：skills 放在 `.agents/skills/`，每个 skill 通常包含：

```text
skill-name/
├─ SKILL.md
└─ agents/
   └─ openai.yaml
```

本模板内置少量项目治理 skill，不内置 ECC 第三方 skill。

## 内置 Skills

| Skill | 用途 |
| --- | --- |
| `project-init` | 初始化或修复项目 `.codex/` 和 `docs/` |
| `project-bootstrap-fill` | 根据项目初始化问答补齐第一版 `.codex/` 和 `docs/` |
| `project-suitability` | 评估新项目或既有项目是否适合直接套用 ForgeKit AI 工作流 |
| `document-backfill` | 逐篇消化既有项目文档并回填 ForgeKit `docs/` |
| `handover-review` | 接手既有项目时做现状审计、兼容边界和缺陷修复计划 |
| `large-change-planning` | 大范围、跨模块、迁移、重构或高风险任务的探索和分阶段计划 |
| `code-review` | 审查改动中的 bug、回归、安全风险和测试缺口 |
| `release-check` | 发布前检查版本、文档、测试、构建、部署风险 |
| `security-review` | 审查密钥、权限、外部输入、外部动作等安全风险 |

## 何时创建项目 skill

- 某类任务会在项目中反复出现。
- 任务有稳定步骤、输入、输出和验证方式。
- 普通 prompt 太长，且容易遗漏关键约束。
- 需要把项目特定知识沉淀为可复用工作流。
- `AGENTS.md` 已经开始变长，应该把细节下沉到 skill。

## 大任务执行

跨模块、大范围、高风险、迁移或重构任务不应直接编码。优先使用 `large-change-planning`，并根据 `governance/large-change-execution.md` 维护探索报告和实施计划。

## Skill / Hook 边界

需要 AI 判断、访谈、方案取舍或审查意见的流程适合做 skill。固定、只读、可解释、可跳过的检查适合做 command 或 opt-in hook。新增前先参考生成项目中的 `.codex/automation-decision.md`，不要把简单脚本包装成 skill，也不要把产品或架构决策放进 hook。

## 团队工具链

重复流程先登记到 `.codex/commands-catalog.md`。自动化前先读取 `governance/team-agent-rollout.md` 和 `.codex/hooks.md`，不要默认启用 MCP 或外部写操作。

生成项目内可用的只读辅助脚本：

- `scripts/detect-local-toolchain.ps1`：检测本地工具链和 LSP 候选。
- `scripts/run-harness-check.ps1`：检查 AGENTS、治理入口、commands 和 hooks 是否完整。

初始化后如果项目方向仍不清楚，先读取 `docs/codex-next-work-order.md`，继续确认 MVP、落地环境、验证方式和依赖裁剪。

ForgeKit v0.12.0 起通过根级统一 plugin 分发稳定 skills 和模板资产：`.codex-plugin/`、`.claude-plugin/` 和共享 `skills/` 位于仓库根。plugin 只是分发入口；引入第三方或团队 plugin 前仍需审查权限、网络、凭据、写入范围和上下文污染风险。

## 推荐 Skill 类型

| Skill | 场景 |
| --- | --- |
| project-onboarding | 新成员或新会话快速理解项目 |
| api-design | 接口设计、错误码、响应格式 |
| db-migration-review | 数据库迁移审查 |
| release-check | 发布前检查 |
| security-review | 安全审查 |
| e2e-testing | 端到端测试 |

## 引入第三方 Skill 前检查

- 阅读 `SKILL.md`。
- 确认是否需要网络、凭据或外部服务。
- 确认是否会写入工作区之外。
- 确认是否与项目规则冲突。
- 确认是否会导致 Codex 默认读取过多无关上下文。
- 只复制需要的 skill，不全量复制大型技能库。
