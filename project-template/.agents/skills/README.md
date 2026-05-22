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
| `handover-review` | 接手既有项目时做现状审计、兼容边界和缺陷修复计划 |
| `code-review` | 审查改动中的 bug、回归、安全风险和测试缺口 |
| `release-check` | 发布前检查版本、文档、测试、构建、部署风险 |
| `security-review` | 审查密钥、权限、外部输入、外部动作等安全风险 |

## 何时创建项目 skill

- 某类任务会在项目中反复出现。
- 任务有稳定步骤、输入、输出和验证方式。
- 普通 prompt 太长，且容易遗漏关键约束。
- 需要把项目特定知识沉淀为可复用工作流。

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
- 只复制需要的 skill，不全量复制大型技能库。
