# 项目 Skills

记录本项目推荐使用的 Codex skills 或专项工作流。

## 推荐 Skills

| Skill | 使用场景 | 备注 |
| --- | --- | --- |
| project-init | 项目初始化、补齐 `.codex/` 和 `docs/` | 已内置于 `.agents/skills/project-init/` |
| project-bootstrap-fill | 根据初始化问答生成第一版项目规则和文档 | 已内置于 `.agents/skills/project-bootstrap-fill/` |
| handover-review | 接手既有项目、现状审计、兼容边界、缺陷修复计划 | 已内置于 `.agents/skills/handover-review/` |
| code-review | 审查 diff、查找 bug、回归、安全风险、测试缺口 | 已内置于 `.agents/skills/code-review/` |
| release-check | 发布前检查、版本记录、测试构建、部署风险 | 已内置于 `.agents/skills/release-check/` |
| security-review | 权限、鉴权、凭据、外部输入、依赖变化 | 已内置于 `.agents/skills/security-review/` |
| api-design | REST/RPC 接口、错误码、响应格式 | 可按项目需要另建 |
| e2e-testing | 关键用户流程验证 | 可按项目需要另建 |
| docs-research | 查询官方文档、版本差异、迁移说明 | 需要网络时先确认 |

## 使用规则

- 只有在任务匹配时使用对应 skill。
- 使用 skill 前先阅读其说明。
- skill 不能覆盖本项目的明确规则。
- 使用 skill 前先通过 `AGENTS.md` 和 `docs/代码库地图.md` 确认入口，不要让 skill 触发全量读取。
- 第三方 skill 视为供应链输入，引入前需要审查权限、网络、凭据和写入范围。
- 不全量复制大型 skill 库，只复制当前项目实际需要的部分。

## Harness 关系

- `AGENTS.md` 负责判断是否应该使用 skill。
- `docs/代码库地图.md` 负责告诉 skill 从哪里开始找代码。
- `governance/agent-harness.md` 负责维护上下文分层、搜索方式和停止编码条件。
- `governance/team-agent-rollout.md` 负责判断重复流程应该沉淀为 command、hook、plugin 还是 MCP。
- 重复出现的长提示词应优先沉淀为项目 skill，而不是继续塞进 `AGENTS.md` 或 HTML。

## 项目自定义工作流

- 大任务、多模块改动、迁移、重构或高风险变更：先按 `governance/large-change-execution.md` 生成探索报告和实施计划，再进入编码。
- 高频重复动作：先登记到 `.codex/commands-catalog.md`；需要自动化时再评估 `.codex/hooks.md`。

## ECC 参考

ECC 的 Codex 适配使用 `.agents/skills/` 作为 skill 目录。本项目采用这个目录结构，但不内置 ECC 第三方 skill。
