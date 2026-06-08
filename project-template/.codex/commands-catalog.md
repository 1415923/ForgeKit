# Commands Catalog

本文记录可复用命令和固定提示词候选。它不是自动执行清单，Codex 执行前仍需遵守权限边界。

## 使用规则

- 先把重复流程写成手动 command。
- command 稳定、低风险、跨项目复用后，再考虑 skill 或 hook。
- 是否进入 skill、command、hook、script、plugin 或 MCP，先参考 `.codex/automation-decision.md`。
- 涉及外部系统、凭据、部署、Git push、长期服务的 command 必须人工确认。
- 项目真实命令仍以 `.codex/commands.md` 为准。

## 推荐提示词命令

| 名称 | 用途 | 输入 | 输出 |
| --- | --- | --- | --- |
| project-bootstrap | 初始化项目并访谈 | 项目简报 | `.codex/` 和 `docs/` 第一版 |
| handover-audit | 接手既有项目审计 | 现有代码库 | 审计、兼容边界、缺陷修复计划 |
| large-change-plan | 大任务拆分 | 大任务描述 | 探索报告和实施计划 |
| code-review | 审查当前 diff | git diff | findings、questions、test gaps |
| release-check | 发布前检查 | 版本号和目标 | release gate 结论 |
| security-review | 安全敏感变更审查 | diff 或范围 | 风险和修复建议 |

## 推荐本地命令候选

| 名称 | 命令来源 | 风险 | 备注 |
| --- | --- | --- | --- |
| validate-template | `scripts/validate-template.ps1` | 低 | 模板仓库使用 |
| harness-check | `scripts/run-harness-check.ps1` | 低 | 生成项目使用，检查入口和治理结构 |
| detect-local-toolchain | `scripts/detect-local-toolchain.ps1` | 低 | 只读检测本地工具和 LSP 候选 |
| check-doc-sync | `scripts/check-doc-sync.ps1` / `scripts/check-doc-sync.sh` | 低 | 只读检查文档同步、过期描述和版本记录原因 |
| install-hooks | `scripts/install-hooks.ps1` / `scripts/install-hooks.sh` | 中 | opt-in 安装、查看或卸载 Git 文档同步 hook |
| local-test | `.codex/commands.md` | 中 | 由项目填写 |
| local-build | `.codex/commands.md` | 中 | 可能耗时 |
| local-lint | `.codex/commands.md` | 低 / 中 | 取决于项目 |
| dependency-check | CI 或项目命令 | 中 / 高 | 可能联网 |
| secret-scan | CI 或安全工具 | 中 | 需要工具安装 |

## GitHub 风格集成候选

| 能力 | 候选做法 | 默认 |
| --- | --- | --- |
| Issue 创建 | 从 `docs/task-board.md` 映射到 GitHub Issues | 手动确认 |
| PR 检查 | code-review prompt + CI 结果 | 可选 |
| CODEOWNERS | 从 `docs/code-ownership.md` 生成 | 手动确认 |
| Actions | lint/test/build/security scan | 项目成熟后 |
| Dependabot | 依赖更新和安全提醒 | 生产项目建议 |
| Secret scanning | GitHub 或 gitleaks | 高风险项目建议 |
