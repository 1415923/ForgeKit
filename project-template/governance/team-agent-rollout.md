# 团队 Agent 工作流推广

本文定义如何把个人 Codex 使用经验沉淀为团队可复用资产。原则是先轻量、可审查、可退出，再逐步工具化。

## 推广顺序

| 层级 | 适用场景 | 进入条件 | 风险 |
| --- | --- | --- | --- |
| AGENTS | 全项目共性规则和任务路由 | 必须稳定、短小 | 过长会污染上下文 |
| Skill | 高频、稳定、可复用工作流 | 步骤、输入、输出、验证清楚 | 可能隐藏过多上下文 |
| Command | 固定提示词或固定本地动作 | 可重复、低风险、可审查 | 误触发外部动作 |
| Hook | 自动检查、提醒、阻断 | 规则明确、失败信息清楚 | 噪音、误阻断、权限风险 |
| Plugin | 跨项目分发和组织资产 | 多项目复用、版本维护明确 | 维护成本、供应链风险 |
| MCP | 需要外部系统上下文或动作 | 权限、网络、凭据、审计可控 | 数据外泄、误操作外部系统 |

默认顺序：`AGENTS -> skills -> commands -> hooks -> plugin -> MCP`。不要因为工具可用就提前启用 MCP。

## 角色责任

| 角色 | 责任 |
| --- | --- |
| Agent workflow owner | 维护 AGENTS、skills、commands、hooks、MCP 策略 |
| Tech lead | 审查架构、技术债、版本闸门和高风险自动化 |
| Security reviewer | 审查凭据、外部动作、MCP、依赖和发布风险 |
| CI owner | 维护 CI、coverage、secret scanning、dependency scanning |
| Project owner | 决定是否启用团队级工具链和外部集成 |

## 工具链映射

| 能力 | GitHub 风格模板 | 通用企业映射 | 默认策略 |
| --- | --- | --- | --- |
| 任务跟踪 | GitHub Issues / Projects | Jira / GitLab Issues / 飞书项目 | 可选，先保持 docs 映射 |
| PR 审查 | Pull Request + CODEOWNERS | GitLab MR / Gerrit / 内部评审系统 | 建议启用 |
| CI | GitHub Actions | GitLab CI / Jenkins / Azure DevOps | 项目成熟后启用 |
| Secret scanning | GitHub secret scanning | Gitleaks / TruffleHog / 企业安全平台 | 高风险项目建议启用 |
| Dependency scanning | Dependabot / dependency-review | SCA 平台 / Nexus IQ / Snyk | 生产项目建议启用 |
| Coverage | Codecov / coverage artifact | SonarQube / JaCoCo / Istanbul | 按项目要求启用 |
| MCP GitHub | GitHub MCP server | GitLab/Jira/内部 API MCP | 只读优先，写操作需确认 |

## 启用闸门

启用 command、hook、plugin 或 MCP 前，必须确认：

- 是否需要网络。
- 是否需要凭据。
- 是否会读取或修改外部系统。
- 是否会写入工作区之外。
- 是否有审计日志或可追踪记录。
- 是否有低技术方案替代。
- 是否可以在失败时安全跳过。

## 维护规则

- 高频重复流程先记录到 `project-template/.codex/commands-catalog.md`。
- 自动化动作先写成手动 command，再考虑 hook。
- 跨项目复用且稳定后，才考虑 plugin。
- MCP 默认只读优先；写操作、issue 创建、PR 更新、部署触发必须人工确认。
- 每个 review/refactor gate 检查工具链是否产生噪音、误阻断或维护负担。

