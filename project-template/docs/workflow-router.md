# Workflow Router

本文用来把用户的一句话路由到正确的 ForgeKit 文档和工作流。先判断意图，再决定读取、写入和禁止写入的目标；不要默认全量读取 `.forgekit/docs/**`。

## Purpose

- 帮助 AI 先回答“该看哪个文档、该写哪个文档、哪些文档不要动”。
- 减少 `task-intake.md`、`task-board.md`、`work-log.md`、`requirements.md`、`testing.md`、`changelog.md` 之间的重复写入。
- 让用户问“领导原文、当前任务、验证结果、今天做了什么、准备汇报、继续 loop、收口版本”时，先得到正确入口。

本文不是任务看板、不是执行器、不是自动 runner，也不授权修改代码或启动 loop。

## How to Use

1. 先识别用户意图。
2. 按 Intent Routing Table 选择 Read Targets。
3. 写入前确认 Write Targets、Do Not Write 和触发条件。
4. 没有明确写入触发时，只输出 Required Output，不改 managed docs。
5. 同一事实只写到一个负责文档，其他文档用 `Source ID`、`Task ID` 或链接引用。

## Intent Routing Table

| 用户意图 | Read Targets | Write Targets | Do Not Write | Required Output |
| --- | --- | --- | --- | --- |
| 查看任务派发原文 / 领导原话 / 微信任务 | `task-intake.md` | none | `task-board.md`, `requirements.md`, `changelog.md` | source summary + `Source ID` |
| 记录新任务来源 | `task-intake.md`, `document-responsibility.md` | `task-intake.md` | `task-board.md` unless task is confirmed | Source record |
| 查看当前任务状态 / 看板 / 下一步 | `task-board.md` | none | `task-intake.md`, `changelog.md` | compact task status |
| 拆解任务 | `task-intake.md`, `requirements.md`, `task-board.md` | `task-board.md` | `changelog.md` | derived tasks with `Source ID` |
| 更新今天进展 / 工作日志 | `work-log.md`, `task-board.md` | `work-log.md` | `requirements.md`, `changelog.md` unless facts changed | work-log entry |
| 查看或更新需求事实 | `requirements.md`, `task-intake.md` | `requirements.md` | `task-intake.md` original text | requirement facts with `Source ID` |
| 查看验证方法 | `testing.md` | none | `work-log.md`, change verification files | verification commands / checklist |
| 记录验证结果 | `testing.md`, `work-log.md`, `.forgekit/changes/<id>/verification.md` | `work-log.md` or `.forgekit/changes/<id>/verification.md` | `testing.md` unless method changed | verification result |
| 查看版本变化 / 生成 changelog | `changelog.md`, `work-log.md`, `.forgekit/changes/*` | `changelog.md` only for user/version-visible changes | `task-intake.md`, `task-board.md` | changelog summary |
| 风险 / 阻塞 / 待确认 | `risk-register.md`, `task-board.md`, `work-log.md` | `risk-register.md` for open risks | `changelog.md` unless user-visible | risk summary |
| 检查文档健康 / 文档太乱了 / 哪些文档该瘦身 | `document-responsibility.md`, `workflow-router.md`, `task-intake.md`, `task-board.md`, `work-log.md`, `requirements.md`, `testing.md`, `changelog.md` | `.forgekit/doc-health-report.md` only | managed docs unless user explicitly authorizes manual fixes | doc health summary |
| 检查任务来源追溯 / 任务从哪来 / 完成状态有没有证据 | `task-intake.md`, `requirements.md`, `task-board.md`, `work-log.md`, `testing.md`, `changelog.md`, `.forgekit/changes/*` | `.forgekit/source-trace-report.md` only | Source ID / Task ID / requirements / task-board unless user explicitly authorizes manual fixes | source trace summary |
| loop / bounded-auto 授权 | `bounded-auto-loop-policy.md`, `loop-blueprint.md`, `loop-operations.md`, `native-agent-adapter.md` | loop state or `work-log.md` only if executing | source/task/changelog docs unless their facts changed | authorization recap + stop conditions |
| maker/checker review | `maker-checker-protocol.md`, `.forgekit/changes/<id>/review.md` | `.forgekit/changes/<id>/review.md` | `task-board.md` unless task status changes | `pass` / `needs-fix` / `manual-review` |
| worktree 使用 | `worktree-playbook.md` | `work-log.md` only if user asks to execute or record | `task-board.md` unless task status changes | worktree plan / commands |
| 生成交付包 / 阶段收口 / 给领导汇报 / reviewer 审查 / handoff package | `task-intake.md`, `requirements.md`, `task-board.md`, `work-log.md`, `testing.md`, `changelog.md`, `risk-register.md`, `.forgekit/doc-health-report.md`, `.forgekit/source-trace-report.md`, `.forgekit/changes/<id>/*` | `.forgekit/handoff-package.md` or `.forgekit/changes/<id>/handoff.md` only when user asks to generate handoff | current docs, business docs, task status, changelog, Git, PR | review-ready handoff with TODO_REVIEW for missing evidence |

## Read Targets

- 先读 `document-responsibility.md` 和 `codebase-map.md`，再读本文件。
- 只读取路由表命中的文档。
- 业务 `docs/` 仍然是 read-mostly 证据源；只有用户要求时才读取相关文件。
- `.forgekit/archive/**` 默认不读，除非任务涉及历史、审计、回归、复盘或用户明确要求。

## Write Targets

- `task-intake.md`：只记录来源原文、补充、责任、时间范围、人工确认和 `Source ID`。
- `task-board.md`：只记录通过任务准入的可执行任务、状态、owner、下一步、验证方式和 `Source ID`。
- `work-log.md`：只记录近期推进、验证、提交/推送、阻塞和交接恢复。
- `requirements.md`：只记录稳定需求事实和验收标准。
- `testing.md`：只记录验证方法；运行结果写 `work-log.md` 或 change verification。
- `changelog.md`：只记录用户或版本可见变化。
- `risk-register.md`：只记录仍开放、仍影响交付的风险。

## Do Not Write

- 不要把任务原文复制到 `requirements.md`、`task-board.md` 或 `changelog.md`。
- 不要把验证运行日志写进 `testing.md`，除非验证方法改变。
- 不要把工作流水写进 `changelog.md`。
- 不要为了“同步 ForgeKit 文档”而更新所有 managed docs。
- 不要把敏感信息、账号、密码、token、证书、真实环境地址原样写进 managed docs。

## Required Output

路由完成后，输出应包含：

- intent：识别到的用户意图。
- read：本轮需要读取的文档。
- write：本轮允许写入的文档；无写入时写 `none`。
- do_not_write：本轮禁止或不应更新的文档。
- result：用户需要的摘要、记录、任务拆解、验证结果、风险摘要或 handoff。

## Escalation Rules

- 用户意图不明确时，先给出 1-3 个可能路由并追问。
- 写入目标不明确时，不改 managed docs。
- 同一事实可能落入多个文档时，优先写入职责最窄的文档，其他文档只引用。
- 涉及 loop、bounded-auto、worktree、发布、风险、安全或业务 docs 写入时，先复述边界和停止条件。
- 涉及文档健康、文档太长或职责混乱时，先生成或建议 `.forgekit/doc-health-report.md`；不要自动按报告修改 managed docs。
- 涉及任务来源、完成证据或追溯链断裂时，先生成或建议 `.forgekit/source-trace-report.md`；不要自动补 Source ID 或改写任务状态。
- 涉及阶段收口、领导汇报、reviewer 审查或测试交接时，可以生成 `.forgekit/handoff-package.md` 或 scoped change `handoff.md`；它只汇总已有信息，缺证据写 `TODO_REVIEW`，不得编造提交、验证、风险或文件列表。
- 用户要求 native-only、bounded-auto、worktree 或发布收口时，必须按对应触发式文档确认前置条件。

## Examples

用户说：“我要看领导昨天微信里到底派了什么。”

- Read Targets: `task-intake.md`
- Write Targets: none
- Required Output: 按 `Source ID` 汇总原文、时间、责任和人工确认状态。

用户说：“把今天验证通过的情况记一下。”

- Read Targets: `testing.md`, `work-log.md`
- Write Targets: `work-log.md`
- Do Not Write: `testing.md` unless validation method changed
- Required Output: 验证命令、结果、时间、关联 `Task ID` / `Source ID`。

用户说：“准备给组长汇报现在进展。”

- Read Targets: `task-intake.md`, `task-board.md`, `work-log.md`, `testing.md`, `changelog.md`, `risk-register.md`
- Write Targets: none by default
- Required Output: 人能直接确认的进展、完成项、验证、风险、待确认和下一步。
