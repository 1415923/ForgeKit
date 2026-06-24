# Maker / Checker 协议

用途：为中高风险代码变更分离“实现证据”和“独立复核证据”。

本文是审查流程，不是多 agent 调度器、sub-agent 配置、自动 checker runner、daemon、MCP 集成、worktree 自动化或自动 PR 流程。

## 角色

| 角色 | 负责什么 | 不负责什么 |
| --- | --- | --- |
| Maker | 理解任务、修改代码、运行基础验证、记录实现证据 | 宣布变更最终通过 |
| Checker | 从干净复查视角审查 diff、验证证据、风险、文档同步和未决问题 | 扩大范围或新增功能，除非用户明确要求 |
| User | 接受最终产品、业务、发布和风险决定 | 事后补充缺失的实现证据 |

## Maker 阶段

Maker 应该：

- 复述请求范围和风险等级
- 只修改确认范围内需要修改的文件
- 可行时运行约定的基础验证命令
- 记录修改文件、实现摘要、验证运行、已知风险和未验证项
- 将变更标记为 `ready-for-check`、`blocked` 或 `partial`

Maker 不能把自己的实现视为最终批准。Maker 能给出的最强结论是 `ready-for-check`。

## Checker 阶段

Checker 应该：

- 从当前 diff 和已记录的 Maker 证据开始
- 审查代码行为、验证结果、风险说明和文档同步
- 检查是否意外修改了敏感信息、业务文档、secrets、deploy 文件或 CI
- 尽量用文件和行号报告发现的问题
- 给出 `pass`、`needs-fix` 或 `manual-review` 建议

Checker 不应扩大请求范围、重写无关代码或新增功能，除非用户明确要求。

## 单 agent 使用

单个 agent 也可以通过分离上下文和输出使用本协议：

1. Maker 阶段：实现并写下 Maker 证据。
2. 上下文重置或明确切换阶段。
3. Checker 阶段：像复查另一个贡献者一样审查 diff 和 Maker 证据。

单 agent 使用仍然只是流程分离，不代表真正独立；高风险决定仍可能需要人工复查。

## 多 agent 使用

多个 agent、sub-agent 或人工 reviewer 可以使用同一协议，但它们只是可选实现方式。ForgeKit v0.26 不生成 sub-agent 配置、runner 代码、worktree 自动化或自动审查派发。

## Worktree 隔离

用户明确要求或确认方案时，Maker 和 Checker 可以使用 Git worktree 做隔离。Worktree 可用于分离并行任务、实验或干净复查视角。

ForgeKit v0.28 不要求 worktree，也不会自动创建 worktree。使用前必须确认源工作区干净、base branch、worktree path、branch name、allowed paths、validation command 和 cleanup plan。结果记录到工作日志或 change review。

## 证据位置

中高风险变更的 Maker 和 Checker 证据记录在：

- `.forgekit/changes/<change-id>/review.md`

低风险变更如果用户没有要求 change folder，可以在最终回复里简要总结 Maker/Checker 证据。

## 状态值

Maker status:

- `ready-for-check`：实现和基础验证证据已准备好复查
- `blocked`：缺少用户输入或外部状态，无法继续实现
- `partial`：实现未完成或验证未完成

Checker status:

- `pass`：审查范围内没有发现阻塞问题
- `needs-fix`：最终接受前应修复阻塞问题
- `manual-review`：需要用户或领域负责人判断
- `not-run`：尚未运行 checker 阶段

## 最小复查重点

Checker 优先检查：

- diff 行为和非预期副作用
- 验证命令和结果质量
- 已知风险和缺失验证
- 当前事实和 changelog 是否需要同步
- 是否意外修改业务文档、敏感信息、secrets、deploy 文件或 CI
- 实现是否保持在请求范围内

## 输出

Maker 输出应以明确的 `ready for check`、`blocked` 或 `partial` 结论结束。

Checker 输出应以且只以一个建议结束：

- `pass`
- `needs-fix`
- `manual-review`
