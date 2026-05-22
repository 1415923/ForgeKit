# ECC 到本模板的映射

## 能力层级

```text
本模板
├─ 用户级规则：环境、权限、Git、AI 协作
├─ 项目级规则：目标、范围、命令、风格、测试、安全、版本
├─ 项目文档：需求、架构、接口、数据库、部署、测试、版本记录
└─ 可选增强：skills、agents、MCP、外部工具

ECC
├─ agents
├─ skills
├─ commands
├─ rules
├─ hooks
├─ MCP configs
└─ security / evaluation / memory / orchestration
```

ECC 的内容主要映射到“可选增强”和“项目级规则”，而不是替代项目文档。

## 推荐吸收清单

### 第一优先级

- 安全边界：外部动作必须确认。
- secrets 规则：不硬编码密钥，泄露后立即轮换。
- 验证闭环：实现后运行测试、构建、lint 或替代验证。
- skills-first：复杂工作流沉淀为 skill，而不是堆积长 prompt。

### 第二优先级

- 多 agent 角色：explorer、reviewer、docs-researcher。
- MCP 示例配置：GitHub、Context7、Playwright、Memory、Sequential Thinking。
- 架构和 API 设计规则。

### 第三优先级

- TDD 强约束。
- 覆盖率门槛。
- 自动记忆和持续学习。
- dashboard、daemon、operator workflow。

## 项目启用建议

| 项目规模 | 建议 |
| --- | --- |
| 小脚本、小工具 | 只使用 `.codex/rules.md` 和 `commands.md` |
| 普通业务项目 | 启用 docs、testing、security、skills 清单 |
| 中大型项目 | 增加 agents 角色、MCP 示例、发布检查 |
| 高安全项目 | 增加安全审查、依赖扫描、secret scanning、权限隔离 |
