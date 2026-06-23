# 任务派发原文台账

## 用途

本文是任务来源优先的记录表。任何领导任务、微信任务、计划表格子、会议任务、文档任务或手工记录，都应先在这里保留脱敏后的原文，再转换成需求、任务看板、工作日志或版本记录。

本文回答一个问题：这件事原本是谁在什么时间、通过什么来源、要求谁做什么，以及是否经过人工确认。

边界：

- 必须保留脱敏后的原文，不能只留下 AI 总结。
- 不记录密码、token、证书、私钥、内部地址、私有包内容或敏感配置值。
- 本文不是 `requirements.md`、不是 `task-board.md`、不是 `work-log.md`、也不是 `changelog.md`。
- 原文未经人工确认时，`Human Review` 必须保持 `pending`。

## 什么时候使用

工作来自以下来源时，创建一条来源记录：

- 领导计划表格子
- 微信任务
- 会议任务
- 文档任务
- 手工记录

## 来源记录模板

```text
Source ID: SRC-YYYYMMDD-001
Source Type: leader-plan-cell | wechat | meeting | document | manual-note
Received At: YYYY-MM-DD HH:MM
Sender / Source: <name or source label>
Original Location: <chat, meeting note, document path, plan row, or pointer>
Human Review: pending | confirmed | corrected | rejected
Confidentiality: normal | sensitive-redacted
Derived Task IDs: TASK-001, BUG-001, FEAT-001
```

### 原文

粘贴脱敏后的任务派发原文。文字要足够接近原始表述，方便人工确认 AI 是否误解、漏掉或过度精简。

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

### 拆解任务

| Task ID | 标题 | Source ID | 状态 |
| --- | --- | --- | --- |
| TASK-001 | 待定 | SRC-YYYYMMDD-001 | Todo |

### 待确认问题

| 问题 | 为什么重要 | 负责人 | 状态 |
| --- | --- | --- | --- |
| 待定 | 待定 | 待定 | Open |

### 人工确认状态

| 字段 | 值 |
| --- | --- |
| Human Review | pending |
| 复查人 | 待定 |
| 复查说明 | 待定 |
| 修正后的理解 | 待定 |

## 脱敏规则

- 原文包含敏感信息时，先脱敏再写入，并设置 `Confidentiality: sensitive-redacted`。
- 保留足够上下文，确保意思不变，但不要复制密钥或私密值。
- 人工确认后，只把稳定需求事实同步到 `requirements.md`。
- 执行状态同步到 `task-board.md`，并保留 Source ID 反链。
- 用户可见的完成结果同步到 `changelog.md`；不要把任务原文复制过去。
