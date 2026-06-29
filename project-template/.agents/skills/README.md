# 项目 Skills

本目录放项目级 Codex skills。只有任务匹配时才加载对应 skill，不要把整个目录当作默认上下文读取。

## 内置 Skills

| Skill | 场景 |
| --- | --- |
| `project-init` | 新项目初始化、方案访谈、补齐项目入口 |
| `project-bootstrap-fill` | 根据初始化问答生成第一版 `.codex/` 和 `.forgekit/docs/` |
| `project-suitability` | 判断项目适合 Lite / Standard / Enterprise 还是 Custom |
| `document-backfill` | 逐篇阅读既有文档并回填 ForgeKit managed docs root |
| `handover-review` | 接手既有项目时审计现状、兼容边界和修复计划 |
| `large-change-planning` | 大范围、迁移、重构或高风险任务前的探索和实施计划 |
| `code-review` | 审查 diff、回归、安全风险和测试缺口 |
| `forgekit-request-code-review` / `forgekit-code-review` | Claude Code 专用的 Maker 请求与独立只读 Reviewer gate；位于 `.claude/skills/` |
| `release-check` | 发布前检查版本、文档、测试、构建和部署风险 |
| `security-review` | 审查凭据、权限、外部输入、依赖和外部动作 |

## 使用边界

- 先从 `AGENTS.md` 或 `CLAUDE.md` 判断任务路由，再按需读取 skill。
- skill 不能覆盖当前项目规则、用户明确要求或安全边界。
- 需要 AI 判断、访谈、方案取舍或审查意见的流程适合做 skill。
- 固定、只读、可解释、可跳过的检查优先做 command、script 或 opt-in hook。
- 是否新增 skill、command、hook、script、plugin 或 MCP，先参考 `.codex/automation-decision.md` 和 `governance/team-agent-rollout.md`。
- 第三方 skill 视为供应链输入，引入前检查权限、网络、凭据、写入范围和上下文污染风险。

ForgeKit 采用根级统一 plugin 分发：`.codex-plugin/`、`.claude-plugin/` 和共享 `skills/` 位于模板仓库根。生成项目只保留实际运行需要的项目 skills。
