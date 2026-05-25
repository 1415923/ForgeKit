# 代码所有权和评审责任

本文件定义模块负责人、评审责任和 CODEOWNERS 风格规则。目标是让 Codex 在修改代码时知道哪些区域需要额外确认，避免无人负责的核心模块被随意改动。

## 核心产物

| 文档 | 用途 |
| --- | --- |
| `docs/代码所有权.md` | 记录模块、负责人、评审人、风险等级和替补人 |
| `.codex/git.md` | 记录分支、提交和合并前要求 |
| `docs/变更影响评估.md` | 记录跨模块或高风险改动的影响 |

## 所有权等级

| 等级 | 说明 | 评审要求 |
| --- | --- | --- |
| Critical | API、数据、安全、部署、硬件、计费、核心业务流 | 必须有负责人或人工确认 |
| Shared | 多模块复用组件、公共库、公共配置、CI/CD | 至少确认影响范围和调用方 |
| Local | 局部功能、页面、测试、文档 | 按普通代码审查执行 |
| Unknown | 接手项目中尚未识别负责人 | 先补事实，不默认大改 |

## CODEOWNERS 风格规则

项目可以在 `docs/代码所有权.md` 中用类似格式记录：

```text
# path pattern                 owner              reviewer            risk
/src/main/java/**              backend-owner      backend-reviewer    Shared
/src/main/resources/db/**      data-owner         data-reviewer       Critical
/frontend/src/**               frontend-owner     frontend-reviewer   Shared
/.github/workflows/**          devops-owner       devops-reviewer     Critical
/hardware/**                   fpga-owner         fpga-reviewer       Critical
```

没有真实人员信息时，可以先写角色，例如 `backend-owner`、`security-reviewer`、`customer-tech-contact`。

## 必须升级确认的改动

以下改动默认需要负责人或人工确认：

- Critical 区域变更。
- 跨两个以上模块的行为变更。
- 公共库、公共配置、脚手架、构建和 CI/CD 变更。
- API、数据库、鉴权、权限、部署、硬件接口、安全策略变更。
- 接手项目中 Unknown 区域的结构性改动。
- 删除、迁移、重命名大量文件。

## Codex 行为

- 修改前先识别影响路径，并对照 `docs/代码所有权.md`。
- 如果命中 Critical 或 Unknown 区域，应提醒用户需要负责人或人工确认。
- 如果缺少 `docs/代码所有权.md`，接手项目先建立初版所有权矩阵，不把未知区域当作可自由重构区域。
- 代码审查时检查是否遗漏必要评审人、影响范围或变更影响评估。
- 发布前检查 Critical 区域变更是否已有评审结论。

## 接手项目特殊规则

接手项目通常缺少清晰负责人。此时先用事实建立初版矩阵：

- 哪些目录是核心业务。
- 哪些目录对外暴露 API。
- 哪些目录包含数据库迁移、部署配置、鉴权权限、硬件接口。
- 哪些目录无法判断责任人。
- 哪些目录暂时只允许修 P0/P1，不做结构性重构。

如果责任不清但必须修改，应记录原因、影响路径、验证方式和回滚方案。
