# ECC 借鉴评估

来源项目：Everything Claude Code / ECC

- GitHub：https://github.com/affaan-m/ECC
- 参考文件：
  - `README.md`
  - `AGENTS.md`
  - `.codex/AGENTS.md`
  - `the-security-guide.md`

## 结论

ECC 适合作为 AI coding 能力库参考，不适合作为本模板的直接替代品。

本模板的核心目标是建立跨项目可复用的开发流程、项目文档、权限边界、版本管理和交付规范。ECC 的核心价值在于提供 agents、skills、rules、commands、MCP、安全扫描和多工具适配。

因此，本模板采用“选择性吸收”的策略：

- 吸收 ECC 的协作原则、安全边界、skills-first 思路、验证循环、MCP 配置策略。
- 不全量安装 ECC。
- 不把 ECC 的完整 agents、commands、hooks、MCP 配置复制进项目。
- 不让 ECC 的强制规则覆盖项目自身需求。

## 采用内容

| ECC 思路 | 本模板落点 | 采用方式 |
| --- | --- | --- |
| Plan Before Execute | `.codex/rules.md` | 大改前先方案，小改可直接执行 |
| Security First | `.codex/security.md`、`user-rules/permissions.md` | 安全检查和外部动作确认 |
| Skills First | `.codex/skills.md`、`.agents/skills/README.md` | skills 作为可选增强层 |
| Verification Loop | `.codex/testing.md`、`checklists/功能开发检查清单.md` | 测试、构建、lint、审查闭环 |
| External Action Boundaries | `user-rules/permissions.md` | 网络工具默认只读，发布类动作需确认 |
| Codex MCP Baseline | `.codex/config.example.toml` | 提供示例，不自动启用 |
| Multi-Agent Roles | `.codex/agents/README.md` | 仅作为高级项目选项 |

## 暂不采用内容

| ECC 内容 | 暂不采用原因 |
| --- | --- |
| 完整安装脚本 | 会修改用户环境，当前阶段只做模板设计 |
| Claude Code hooks | Codex CLI 不具备同等 hook 机制 |
| 全量 agents | 对多数项目过重，且角色应按项目启用 |
| 全量 skills | 供应链和维护成本较高，应按需引入 |
| 全量 MCP 配置 | MCP 涉及外部服务、凭据和权限，必须逐项确认 |
| 强制 80% 覆盖率 | 可作为推荐，不能对所有项目一刀切 |
| 强制 TDD | 适合高风险核心模块，不适合所有变更 |

## 推荐使用策略

新项目默认使用本模板即可。

当项目进入下列场景时，再按需引入 ECC 思路或具体 skill：

- 需要系统性代码审查。
- 需要安全审查。
- 需要 E2E 测试。
- 需要 API 设计规范。
- 需要复杂架构设计。
- 需要多 agent 并行分析。
- 需要 MCP 连接 GitHub、文档检索、浏览器自动化等外部工具。

## 引入前检查

- 该 skill 或 MCP 是否真的解决当前项目问题。
- 是否需要网络、凭据或外部账号。
- 是否会修改用户级配置。
- 是否会引入重复规则或重复自动化。
- 是否有明确的禁用和回滚方式。
