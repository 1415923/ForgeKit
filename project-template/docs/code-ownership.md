# 代码所有权

用于记录模块负责人、评审责任、风险等级和替补确认人。没有真实人员信息时，可以先写角色。

## 所有权矩阵

| 路径 / 模块 | 说明 | 所有者 | 必要评审人 | 风险等级 | 备注 |
| --- | --- | --- | --- | --- | --- |
| `/` | 项目整体 | 待补充 | 待补充 | Shared | 待补充 |
| `/docs/**` | 项目文档 | 待补充 | 待补充 | Local | 待补充 |
| `/.codex/**` | Codex 项目规则 | 待补充 | 待补充 | Shared | 待补充 |
| `/src/**` | 主业务代码 | 待补充 | 待补充 | Shared | 待补充 |
| `/config/**` | 配置 | 待补充 | 待补充 | Critical | 如不存在可删除 |
| `/db/**` | 数据库迁移和脚本 | 待补充 | 待补充 | Critical | 如不存在可删除 |
| `/deploy/**` | 部署配置 | 待补充 | 待补充 | Critical | 如不存在可删除 |

## CODEOWNERS 风格记录

```text
# path pattern                 owner              reviewer            risk
/docs/**                       docs-owner         docs-reviewer       Local
/.codex/**                     workflow-owner     workflow-reviewer   Shared
/src/**                        app-owner          app-reviewer        Shared
/config/**                     config-owner       config-reviewer     Critical
/db/**                         data-owner         data-reviewer       Critical
/deploy/**                     devops-owner       devops-reviewer     Critical
```

## Critical 区域

| 路径 / 模块 | 为什么关键 | 修改前要求 | 发布前要求 |
| --- | --- | --- | --- |
| 待补充 | 待补充 | 待补充 | 待补充 |

## Unknown 区域

接手项目中无法判断责任人的目录先登记在这里。

| 路径 / 模块 | 不确定原因 | 临时处理规则 | 后续确认人 |
| --- | --- | --- | --- |
| 待补充 | 待补充 | 待补充 | 待补充 |

## 本次版本涉及的所有权确认

| 日期 | 版本 / 任务 | 影响路径 | 所有者 / 评审人 | 结论 |
| --- | --- | --- | --- | --- |
| 待补充 | 待补充 | 待补充 | 待补充 | 待补充 |
