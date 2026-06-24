# 项目任务看板

本文只记录可执行任务的当前状态。工作来源和原始表述在 `.forgekit/docs/task-intake.md`，最近推进过程在 `.forgekit/docs/work-log.md`，用户可见完成结果在 `.forgekit/docs/changelog.md`。

## 任务准入

进入本看板前必须满足：

- 有明确可执行动作。
- 有 owner，或明确为待确认 owner。
- 有下一步。
- 有 `Source ID` 反链。
- 有完成标准或验证方式。

以下内容不要进入看板：

- 纯确认、解释、背景、聊天补充、重复提醒。
- 只调整时间、责任或范围的小补充；这类内容先写入 `task-intake.md` 的 `Update Notes`。
- 个人规划、用户反馈、bug、技术债或测试失败本身不是任务；只有通过 Task Decision 且满足准入条件后才进看板。
- 已被后续来源覆盖的旧任务；应标为 `Superseded` 或 `Dropped`。
- 工作日志里的个人待办，除非用户确认它是任务。

## 当前重点

只放正在推进或近期明确要推进的任务。过时任务不要继续上浮。

| 优先级 | Task ID | 标题 | Owner | 状态 | 下一步 | Source ID | 验证方式 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P0 | TASK-001 | 待补充 | 待补充 | Todo | 待补充 | SRC-YYYYMMDD-001 | 待补充 |

## Backlog

已确认但未排期或暂不进入当前重点的任务。

| Task ID | 类型 | 标题 | Owner | 状态 | Source ID | 进入条件 |
| --- | --- | --- | --- | --- | --- | --- |
| TASK-002 | Task | 待补充 | 待补充 | Backlog | SRC-YYYYMMDD-001 | 待补充 |

## Task / Bug

| Task ID | 类型 | 标题 | Owner | 状态 | 下一步 | Source ID | 关联需求 | 验证方式 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-001 | Task | 待补充 | 待补充 | Todo | 待补充 | SRC-YYYYMMDD-001 | REQ-001 | 待补充 |
| BUG-001 | Bug | 待补充 | 待补充 | Open | 待补充 | SRC-YYYYMMDD-001 | 待补充 | 待补充 |

## 阻塞项

| Task ID | 阻塞原因 | 影响 | Owner | 解除条件 | Source ID |
| --- | --- | --- | --- | --- | --- |
| TASK-001 | 待补充 | 待补充 | 待补充 | 待补充 | SRC-YYYYMMDD-001 |

## Closed / Dropped / Superseded

完成、裁剪、放弃或被替代的任务放这里，避免继续混入当前重点。

| Task ID | 最终状态 | Source ID | Superseded By | Closed Reason | 结论 |
| --- | --- | --- | --- | --- | --- |
| TASK-000 | Superseded | SRC-YYYYMMDD-000 | TASK-001 | 被新来源覆盖 | 不再推进 |

## 状态定义

| 状态 | 说明 |
| --- | --- |
| Backlog | 已确认，未准备开发 |
| Ready | 已满足开始条件 |
| Todo | 已排入当前范围，尚未开始 |
| In Progress | 正在实现 |
| Review | 等待审查或验收 |
| Done | 已完成并通过验证 |
| Blocked | 被阻塞，原因和解除条件已记录 |
| Superseded | 被后续来源或任务替代 |
| Dropped | 已裁剪或放弃，原因已记录 |

## 对齐检查

更新看板时检查：

- 每个当前任务都有有效 `Source ID`。
- 每个 `Source ID` 在 `task-intake.md` 中能找到原文或补充记录。
- `task-intake.md` 中 `Task Gate: ready` 的任务已经进入看板。
- `Update Notes` 不被重复拆成多个任务。
- 已过时任务已进入 `Closed / Dropped / Superseded`，不再出现在当前重点。
