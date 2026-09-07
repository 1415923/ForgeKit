# Universal Finding 与 Maker / Checker 协议

用途：定义所有 reviewer/checker 共用的 finding、gate 与 checker-exit 合同，并在实际启用独立审查时分离 Maker 实现证据和 Checker 复核证据。

本文不是多 agent 调度器、自动 checker runner、daemon、MCP 集成、worktree 自动化或自动 PR 流程。Canonical repository source 是本文件；生成项目中的 managed target 是 `.forgekit/docs/maker-checker-protocol.md`。

<!-- forgekit:section s-24a939c5facc -->
## Universal Finding Contract

本节适用于 code review、security review、release check、handover review、reasoning/adversarial review、native/Claude reviewers 和静态 checkers。它们都是消费者，不互为上级。后续 Maker / Checker 角色章节只在实际启用独立审查时适用。

### Severity × Blocking

```text
Impact Severity: CRITICAL | MAJOR | MINOR | NOTE
Blocking: YES | NO
```

Impact Severity 描述 finding 的 consequence 一旦实现时的影响量级。Blocking 回答当前 scoped action 是否必须停止。Severity 不拥有 gate authority，也不得隐式决定 Blocking。

`CRITICAL + Blocking=NO` 是合法组合：潜在影响严重，但当前证据没有证明该 scoped action 必须停止。反之，较低 Severity 也不能在缺少完整 failure path 时被标成 Blocking。

### Consequence Codes

| Code | Meaning |
| --- | --- |
| `C1` | harm / irreversible consequence |
| `C2` | authority / credential / budget envelope |
| `C3` | claim / evidence integrity |
| `C4` | target executability / correct scoped write |

C1-C4 只用于 consequence，不用于 Formal evidence 章节或其他条款编号。

### Required Finding Fields

每条 finding 都应明确：

```text
ImpactSeverity: CRITICAL | MAJOR | MINOR | NOTE
Blocking: YES | NO
Evidence:
```

每条 `Blocking=YES` finding 还必须包含：

```text
PrimaryConsequence: C1 | C2 | C3 | C4
FailurePath:
BlockedScope:
```

必要时可增加：

```text
SecondaryConsequences:
ValidationRelevance:
```

- 每条 Blocking finding 只有一个 `PrimaryConsequence`。
- `FailurePath` 必须把可定位 evidence 连接到该 consequence 和当前动作。
- `BlockedScope` 只限定必须停止的动作，不得扩为无关项目或全局 stop。
- `SecondaryConsequences` 不得在没有独立证据时扩大 scope。
- `ValidationRelevance` 说明验证结果与当前 claim/action 的关系；它不由命令退出码自动推导。

### Gate and Checker Exit

```text
checker nonzero != project Blocking
```

- Review/gate decision 只读取 canonical Blocking 及适用的明确 user/frozen gate，不从 Impact Severity 推导。
- `--strict` 可因 `Blocking=NO` warning 返回非零；strict 改变 command exit，不改写 finding。
- Checker error、missing evidence 或无法建立独立 reviewer identity 可以产生 `manual-review` 或 command failure，但不伪造一个 project-level Blocking finding。
- 新 v0.46 governance consumer 使用 `impact_severity` 和 `blocking`。Stage C machine serialization 可 additive 保留 legacy `severity=blocking|warning`，但 legacy field 不拥有新 gate authority。

### Review Decision

- `pass`：适用 gate 已满足，且 reviewed scope 内没有 `Blocking=YES` finding。
- `needs-fix`：至少一个 `Blocking=YES` finding 阻止当前 named action。
- `manual-review`：scope、authority、evidence 或 reviewer independence 无法支持自动决定；不得伪报 pass。

Decision 只适用于声明的 `BlockedScope` / authorized stage，不隐式授权 commit、external smoke、full execution、tag、release 或 deploy。

<!-- forgekit:section s-cb0d70bf808f -->
## Independent Review Trigger

Independent review 由以下任一条件触发：

- 用户或已冻结合同明确设置 independent-review gate；
- 真实影响和证据表明当前动作存在需要独立判断的 C1-C4 consequence；
- release、migration、security、data、permission 或其他高影响流程的适用 owner 明确要求该 gate。

代码修改、文件数量、脚本修改或 bounded-auto 本身不机械产生 independent-review gate。Self-review 可以补充证据，但不能满足已经存在的 independent gate。Reviewer 不可用时只阻止该 gate 所保护的 scoped action，并返回 `manual-review`。

<!-- forgekit:section s-ad83b85c8d62 -->
## Roles When Independent Review Is Enabled

| Role | Responsible for | Not responsible for |
| --- | --- | --- |
| Maker | 理解任务、在授权范围实现、运行基础验证、记录实现证据 | 宣布独立 gate 最终通过 |
| Checker | 在 fresh read-only context 中审查 diff、验证证据、风险、文档同步与 finding contract | 修改文件、自动修复、扩大范围或新增功能 |
| User | 接受最终产品、业务、外部动作和风险决定 | 事后补造缺失证据 |

### Maker Evidence

Maker 对 medium/high-impact change 应以已冻结的 scope、trust boundary、non-goals、stage authorization 与 acceptance matrix 为合同，并记录：changed files、implementation summary、validation run、known risks、verification gaps 和 `TODO_REVIEW`。

Maker 可标记 `ready-for-check`、`blocked` 或 `partial`。`ready-for-check` 只表示 review packet 已准备，不是 gate pass。Maker 通过 `.claude/skills/forgekit-request-code-review/SKILL.md` 传递最小 packet；不得传完整会话、长工具输出或自我批准结论。

### Checker Evidence

Checker 从 fresh read-only context、当前 diff 和最小 Maker evidence 开始：

- 直接检查 frozen acceptance、真实 CLI/API/orchestration entry、diff 和验证结果；
- 不因 Maker 声称已修复而推断 close；
- findings 使用 universal contract，引用最接近的文件、行号、命令或测试；
- 保持 read-only，把修复交回 Maker；
- 不扩大 frozen trust boundary。

### Initial Review and Recheck

Initial review 检查 frozen contract 与真实 failure paths。Expected Change 不阻塞；只有违反 frozen contract，或证据建立当前 scoped C1-C4 failure path 时，finding 才能 `Blocking=YES`。

一轮正常 Maker 修复后，`blocker-recheck` 默认只复核先前 Blocking findings，并逐项输出 `Closed`、`Partially closed` 或 `Still open`。修复引入的新 regression 仍按 universal contract 判断；无关 hardening 作为 non-blocking follow-up。

Repeated governance-only blocking without new mainline evidence 时，在新增 reviewer/checker/governance layer 前先按 `ai-engineering-loop.md` 执行 simplification review；不得建立 counter、state 或 checker-of-checker。

<!-- forgekit:section s-5730125cae8c -->
## Evidence Location and Status

中高影响变更的 Maker/Checker evidence 通常记录在 `.forgekit/changes/<change-id>/review.md`。低影响变更如无 change folder，可在 handoff 中简述。

Maker status：`ready-for-check | blocked | partial`。

Checker status / decision：`pass | needs-fix | manual-review | not-run`。

Review type：`independent | self-review`。`self-review` 不得冒充 independent review。

<!-- forgekit:section s-b2439bcb8dee -->
## Output

Checker 输出至少包含：

```text
ReviewDecision: pass | needs-fix | manual-review
ReviewType: independent | self-review
ReviewerAgent:
ReviewMode: initial | blocker-recheck
ReviewedRange:
FrozenAcceptanceIDs:
AuthorizedStage:
Summary:
Findings:
- impact_severity: CRITICAL | MAJOR | MINOR | NOTE
  blocking: YES | NO
  primary_consequence: C1 | C2 | C3 | C4   # required when blocking=YES
  secondary_consequences:                  # optional
  failure_path:                            # required when blocking=YES
  blocked_scope:                           # required when blocking=YES
  validation_relevance:                    # when applicable
  file:
  line:
  issue:
  evidence:
  suggested_fix:
VerificationGaps:
FollowUps:
TODO_REVIEW:
FinalVerdict:
```

Maker 输出以 `ready for check`、`blocked` 或 `partial` 结束。Checker 以且只以 `pass`、`needs-fix` 或 `manual-review` 之一结束。

<!-- forgekit:user begin -->
<!-- forgekit:user end -->
