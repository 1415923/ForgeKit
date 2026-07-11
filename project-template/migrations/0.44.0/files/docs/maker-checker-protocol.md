# Maker / Checker 协议

用途：为中高风险代码变更分离“实现证据”和“独立复核证据”。

本文是审查流程，不是多 agent 调度器、sub-agent 配置、自动 checker runner、daemon、MCP 集成、worktree 自动化或自动 PR 流程。

## 角色

| 角色 | 负责什么 | 不负责什么 |
| --- | --- | --- |
| Maker | 理解任务、修改代码、运行基础验证、记录实现证据 | 宣布变更最终通过 |
| Checker | 在独立上下文中只读审查 diff、验证证据、风险、文档同步和未决问题 | 修改文件、自动修复、扩大范围或新增功能 |
| User | 接受最终产品、业务、发布和风险决定 | 事后补充缺失的实现证据 |

## Maker 阶段

Maker 应该：

- 复述请求范围和风险等级
- 对 medium/high risk change，以已冻结的 scope、trust boundary、non-goals、stage authorization 和 acceptance matrix 为实现合同
- 只修改确认范围内需要修改的文件
- 将每个 acceptance ID 映射到代码与测试，并确认正式入口接入被测试的真实路径
- 可行时运行约定的基础验证命令
- 记录修改文件、实现摘要、验证运行、已知风险和未验证项
- 将变更标记为 `ready-for-check`、`blocked` 或 `partial`
- 矩阵外改进只记 follow-up；不得运行 proposal 未授权的 commit、smoke 或 full execution 阶段

Maker 不能把自己的实现视为最终批准。Maker 能给出的最强结论是 `ready-for-check`。

Maker 使用 `.claude/skills/forgekit-request-code-review/SKILL.md` 组装最小 review packet。只传任务摘要、review range、diff/stat、changed files、验证输出、已知风险和 `TODO_REVIEW`；不要传完整会话历史、长篇自我解释或“我已经修好了”的结论。

## Checker 阶段

Checker 使用 `forgekit-code-reviewer` 和 `.claude/skills/forgekit-code-review/SKILL.md`，应该：

- 从新的独立上下文、当前 diff 和最小 Maker 证据开始
- 审查代码行为、验证结果、风险说明和文档同步
- 检查是否意外修改了敏感信息、业务文档、secrets、deploy 文件或 CI
- 尽量用文件和行号报告发现的问题
- 给出 `pass`、`needs-fix` 或 `manual-review` 建议
- 首审优先执行 acceptance matrix 的关键拒绝反例，并检查正式 CLI/API/orchestration，而不只检查 helper

Checker 必须保持 read-only，不修改文件、不修代码、不扩大范围。不得因为 Maker 声称“已修复”就默认相信；必须以 diff 和验证证据为准。

## Finding 分类与审查边界

首审 findings 分三类：

1. 违反冻结 proposal 或 acceptance matrix：blocking。
2. 矩阵未列出，但会造成数据泄漏/污染、错误训练或评估、错误 checkpoint、artifact 覆盖、正式入口意外执行未授权任务、失败写成成功或实验结论明显不可信：可作为 blocking Critical finding。
3. 其余为 Minor/Follow-up，例如更强内部 token、抵抗开发者主动调用内部 helper、密码学级 provenance、更多日志字段、不影响正式路径的平台限制、风格或额外抽象。

Reviewer 不得擅自扩大冻结的 trust boundary。新问题仍可报告，但只有前两类自动阻塞。

## 限定复审与收敛

Maker 完成一轮正常修复后，Checker 使用 `blocker-recheck`，默认只复核上一轮 blocking findings，并逐项输出 `Closed`、`Partially closed` 或 `Still open`。本轮修复新引入且违反冻结合同或会造成真实错误的回归可以继续阻塞；与修复无关的新建议只能记为 follow-up。不得重新进行开放式架构审查或扩大 trust boundary。

若一轮修复后仍有多个 Major，不继续第三、第四轮无界小补丁；返回设计阶段，判断是否简化、拆分或重构。

## 阶段授权

以下阶段相互独立：`design-ready`、`implementation-ready-for-review`、`ready-for-commit`、`ready-for-minimal-real-smoke`、`ready-for-full-execution`。Checker 的 pass 只授权 proposal 声明的阶段。可提交不等于可真实 smoke，最小 smoke 通过也不等于完整执行获批。

## 默认触发

- 只改文档：independent review 可选，除非风险或用户规则要求。
- 修改代码：默认 independent review。
- 修改核心逻辑、API、数据、权限或脚本：mandatory independent review。
- 发版或 tag 前：mandatory independent review。
- bounded-auto 收口前：mandatory independent review。

## 单 agent 使用

单个 agent 可以做 self-review，但只能作为补充：

1. Maker 阶段：实现并写下 Maker 证据。
2. 上下文重置或明确切换阶段。
3. Checker 阶段：像复查另一个贡献者一样审查 diff 和 Maker 证据。

`ReviewType: self-review` 不得冒充或满足 independent review gate。需要 independent review 而 reviewer agent 不可用时，必须返回 `manual-review` 并交给用户或人工 reviewer。

## 多 agent 使用

ForgeKit 提供 Claude Code 和 Codex 的 `forgekit-code-reviewer` 配置，但不提供 runner、自动派发、并行审查、worktree 自动化或自动 PR。原生 agent 是否实际执行必须由父运行时观察；不可用时不能假装 independent review 成功。

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

Review type:

- `independent`：独立 reviewer agent 或人工 reviewer 使用最小 review packet 完成复查
- `self-review`：Maker 当前上下文中的自查；不能满足 mandatory independent review

Gate:

- `pass`：可以进入 proposal 中明确声明的下一阶段；不隐式授权 commit、真实 smoke 或完整执行。
- `needs-fix`：Maker 必须修复，或由用户明确接受风险；之后重新请求 review。
- `manual-review`：不得自动通过，必须人工确认。

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

Checker 按 `forgekit-code-review` 的结构输出 `ReviewDecision`、`ReviewType`、`ReviewerAgent`、`ReviewedRange`、结构化 Findings、`VerificationGaps`、`TODO_REVIEW` 和 `FinalVerdict`，并以且只以一个建议结束：

- `pass`
- `needs-fix`
- `manual-review`

