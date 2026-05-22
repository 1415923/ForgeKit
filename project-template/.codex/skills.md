# 项目 Skills

记录本项目推荐使用的 Codex skills 或专项工作流。

## 推荐 Skills

| Skill | 使用场景 | 备注 |
| --- | --- | --- |
| project-init | 项目初始化、补齐 `.codex/` 和 `docs/` | 已内置于 `.agents/skills/project-init/` |
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
- 第三方 skill 视为供应链输入，引入前需要审查权限、网络、凭据和写入范围。
- 不全量复制大型 skill 库，只复制当前项目实际需要的部分。

## 项目自定义工作流

- 待补充

## ECC 参考

ECC 的 Codex 适配使用 `.agents/skills/` 作为 skill 目录。本项目采用这个目录结构，但不内置 ECC 第三方 skill。
