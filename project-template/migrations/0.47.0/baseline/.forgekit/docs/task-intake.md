# 工作来源台账

本文只记录工作来源、原始表述、补充、人工确认和“是否生成任务”的判断。它是 `Source ID` 的来源，不是任务看板、需求文档、工作日志或版本记录。

工作来源可以来自公司派发，也可以来自个人独立开发中的自我规划、用户反馈、bug 发现、技术债、测试失败、调研发现或发布后跟进。不同来源用同一套 `Source ID -> Task ID -> Work Log` 链路处理。

核心规则：

- 先保留脱敏原文或原始想法，再做 AI 理解和任务判断。
- 补充、确认、改期、责任修正默认写入已有 `Source ID` 的 `Update Notes`，不要新建任务。
- 只有出现新的目标、交付物、缺陷、责任人、时间窗口或验收条件时，才创建新的 Source Record。
- 未经人工确认的派发内容必须保持 `Human Review: pending`，不能写成 confirmed。
- 原文含账号、密码、token、证书、环境地址、内网 IP、私有包内容或敏感配置时，必须脱敏，并设置 `Confidentiality: sensitive-redacted`。

## Source Record

```text
Source ID: SRC-YYYYMMDD-001
Source Type: leader-plan-cell | wechat | meeting | document | manual-note | self-planned | user-feedback | bug-found | tech-debt | refactor-idea | research-finding | test-failure | release-followup
Received At: YYYY-MM-DD HH:MM
Sender / Source: <name or source label>
Original Location: <chat, meeting note, document path, plan row, or pointer>
Human Review: pending | confirmed | corrected | rejected
Confidentiality: normal | sensitive-redacted
Derived Task IDs: TASK-001, TASK-002
Supersedes: <Source ID or none>
Superseded By: <Source ID or none>
```

### 原文

粘贴脱敏后的任务派发原文、用户反馈、个人原始想法、bug 现象、测试失败摘要或调研发现。文字要足够接近原始表述，方便人工确认 AI 是否误解、漏掉或过度精简。

个人独立开发时，不需要伪造“领导原文”；直接记录自己的原始想法或发现，例如“我想先做本地导入和标签管理”。

### Update Notes

小的补充、确认、改期、责任修正或范围澄清写在这里。不要因为每条补充都新建任务。

| 时间 | 来源 | 内容摘要 | 影响 | Human Review |
| --- | --- | --- | --- | --- |
| YYYY-MM-DD HH:MM | 待补充 | 待补充 | update-existing-task | pending |

影响取值：

- `note-only`：只作为背景或确认，不生成任务。
- `update-existing-task`：更新已有任务的范围、时间、owner、状态或验证方式。
- `create-task`：确实产生新的可执行任务。
- `reject`：确认不采纳或已无效。

### 责任拆分

| 人员 / 角色 | 责任 | 确认状态 |
| --- | --- | --- |
| <name or role> | <responsibility> | pending |

### 时间窗口

| 字段 | 值 |
| --- | --- |
| 预计开始 | 待定 |
| 预计完成 | 待定 |
| 截止时间 / 检查点 | 待定 |
| 时间不确定点 | 待定 |

### AI 理解

保持简短，只写人工可确认的理解。

- 意图：
- 范围：
- 非范围：
- 假设：

### Task Decision

把来源内容转换为任务前必须先判断。没有可执行动作、owner 或待确认 owner、下一步、完成/验证标准的内容，不进入 `task-board.md`。

| Decision | Task ID | Source ID | Reason |
| --- | --- | --- | --- |
| create-task | TASK-001 | SRC-YYYYMMDD-001 | 有明确交付物和验证方式 |
| update-existing-task | TASK-001 | SRC-YYYYMMDD-001 | 只是调整截止时间或责任 |
| note-only | 无 | SRC-YYYYMMDD-001 | 只是背景或确认 |
| reject | 无 | SRC-YYYYMMDD-001 | 已被人工拒绝或后续来源覆盖 |

### Derived Tasks

| Task ID | 标题 | Source ID | Task Gate | 状态 |
| --- | --- | --- | --- | --- |
| TASK-001 | 待定 | SRC-YYYYMMDD-001 | ready | Todo |

`Task Gate` 取值：

- `draft`：来源已记录，但还缺 owner、下一步或验证方式。
- `ready`：可进入 `task-board.md`。
- `note-only`：不进入看板。
- `rejected`：不采纳。

### Open Questions

| 问题 | 为什么重要 | 负责人 | 状态 |
| --- | --- | --- | --- |
| 待定 | 待定 | 待定 | Open |

### Human Review Status

| 字段 | 值 |
| --- | --- |
| Human Review | pending |
| 复查人 | 待定 |
| 复查说明 | 待定 |
| 修正后的理解 | 待定 |

## 同步规则

- `task-board.md` 只接收 `Task Gate: ready` 的任务，并必须反链 `Source ID`。
- `requirements.md` 只记录已确认的稳定需求事实，不复制原文。
- `work-log.md` 只记录推进过程、验证、提交/推送、阻塞和确认，不自动创建任务。
- `changelog.md` 只记录用户或版本可见变化，不保存任务派发原文。

## 使用场景

| 场景 | 推荐 Source Type | 说明 |
| --- | --- | --- |
| 公司领导或组长安排 | `leader-plan-cell` / `wechat` / `meeting` | 保留脱敏后的原文和人工确认状态 |
| 个人独立开发计划 | `self-planned` | 记录自己的原始目标和范围，不伪造外部来源 |
| 用户反馈 | `user-feedback` | 保留反馈原文或摘要，敏感信息先脱敏 |
| 开发中发现 bug | `bug-found` | 记录现象、复现入口和影响 |
| 技术债或重构想法 | `tech-debt` / `refactor-idea` | 先记录来源和原因，再判断是否进入看板 |
| 调研或测试发现 | `research-finding` / `test-failure` | 记录证据和是否需要派生任务 |
| 发布后跟进 | `release-followup` | 记录兼容性、回滚、补丁或用户通知需求 |
