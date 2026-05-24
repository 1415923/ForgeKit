# Hooks 示例

本文记录可选 hook 设计。Opt-in only：默认不启用任何 hook；启用前必须确认权限、噪音、误阻断和维护成本。

## Hook 分级

| 等级 | 说明 | 示例 | 默认策略 |
| --- | --- | --- | --- |
| H0 | 只提示，不阻断 | 提醒更新任务看板、版本记录 | 可试用 |
| H1 | 本地只读检查 | 检查文件是否存在、规则是否引用 | 可选 |
| H2 | 本地验证 | lint、typecheck、测试 | 需确认耗时 |
| H3 | 外部系统只读 | 读取 issue、PR、CI 状态 | 需确认网络和凭据 |
| H4 | 外部系统写操作 | 创建 issue、更新 PR、触发部署 | 默认禁用 |

## 推荐 Hook 候选

| 触发点 | 动作 | 目的 | 风险 |
| --- | --- | --- | --- |
| 提交前 | 运行模板自检或项目 lint | 防止明显漂移 | 耗时、误阻断 |
| 大任务开始前 | 检查 `docs/探索报告.md` 和 `docs/实施计划.md` 是否存在 | 阻止直接大改 | 小任务误判 |
| 发布前 | 检查版本记录、任务状态、测试记录 | 强化 release gate | 规则过严 |
| 安全敏感变更 | 提醒安全审查和依赖审查 | 减少遗漏 | 需要准确识别 |

## 安全边界

- 不在 hook 中写入凭据。
- 不默认联网。
- 不默认触发部署、push、tag、issue/PR 写操作。
- 长耗时 hook 应可手动跳过，并记录跳过原因。
- hook 失败信息必须说明如何修复，不输出大段日志。

## 示例伪命令

```powershell
# H1: template validation
powershell -ExecutionPolicy Bypass -File .\scripts\validate-template.ps1

# H2: project test placeholder
# Replace with project-specific test command in .codex/commands.md
```
