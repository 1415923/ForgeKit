DesignStatus: stage-a-frozen-awaiting-independent-review

# ForgeKit v0.46.0 Semantic Contract

## 1. 合同解释边界

本文件是 v0.46 neutral semantics 与 Ownership Matrix 的唯一仓库内 Stage A owner。它忠实表示 `proposal.md` 引用的批准合同；不因文件名获得 authority，也不实现任何 consumer。Acceptance IDs 及其完整合同只由 `verification.md` 承载。

规范词 `必须`、`不得`、`只有` 与 `as applicable` 按字面执行。后续 stage 只能在其指定 owner 中应用这里的合同，不得复制成长篇平行定义或新增隐式 gate。

## 2. Neutral protocol ownership

### 2.1 Execution owner

现有 `project-template/governance/ai-engineering-loop.md` 是以下跨任务语义的 neutral owner：

- Execution Intent；
- progress-preserving execution；
- Expected Change vs Post-Freeze Drift；
- Formal evidence boundary；
- Governance Stop-Loss heuristic。

`large-change-planning` 只在 large-change 场景中应用和展开这些 invariant，不是全局语义 owner。

### 2.2 Effect owner

现有 `project-template/governance/agent-entry-contract.md` 是以下语义的 neutral owner：

- Effect Risk；
- external / irreversible authorization；
- bounded effect envelope；
- credential、budget、retry 与 destructive boundary；
- root resolution 与全局入口边界。

### 2.3 Finding owner

Canonical repository source `project-template/docs/maker-checker-protocol.md` 是 universal finding contract 的 neutral owner；其 generated managed target 是 `.forgekit/docs/maker-checker-protocol.md`：

- Severity × Blocking；
- C1～C4 consequence；
- Primary / Secondary Consequence；
- FailurePath；
- BlockedScope；
- Evidence；
- ValidationRelevance；
- checker exit interpretation；
- review/gate decision。

Universal finding contract 适用于所有 reviewers/checkers。Maker/Checker 独立角色章节只在实际启用独立审查时适用。code-review、security-review、release-check、handover-review 与静态 checker 都是消费者，不互为上级。

## 3. Execution Intent 与 Effect Risk

### 3.1 Execution Intent

Execution Intent 只有三个值：

| Intent | 冻结含义 |
| --- | --- |
| `DIAGNOSTIC` | bring-up/debug；允许修复后重跑；不建立 Formal identity。 |
| `SMOKE` | 证明真实链路可运行；在 bounded Effect envelope 内允许修复后重跑；不自动成为 Formal 或 release。 |
| `FORMAL` | claim-bearing evidence；只有它涉及 claim-critical freeze。 |

### 3.2 Effect Risk

Effect Risk 与 Execution Intent 正交，只负责：

- external action；
- credentials；
- budget；
- retry；
- destructive / irreversible effects；
- user authorization。

真实调用或付费调用本身不等于 `FORMAL`。任一 Intent 都必须独立遵守其真实 Effect envelope；Intent 不降低外部或不可逆动作的授权要求。

## 4. Formal Evidence contract

### 4.1 First valid Formal evidence

First valid Formal evidence：

- 不得为了改善 claim outcome 被静默覆盖、替换、隐藏、丢弃或 cherry-pick；
- 必须按项目适用的 evidence / retention policy 保持 provenance 可追溯；
- 可按既有 policy 压缩、迁移、归档或经授权清理，但 active claim 不得因此失去可追溯性或可验证性；
- 不意味着永久物理保存，ForgeKit 不建立永久保存制度。

### 4.2 Authority chain

```text
Formal execution
→ first valid evidence retained and traceable
→ applicable acceptance / aggregate / review required by the predeclared Formal contract
→ current fact owner references accepted evidence
→ current authority
```

Acceptance、aggregate、review、checker 均为 **as applicable**。是否需要它们只由预声明 Formal contract 与真实 C1～C4 consequence 决定；first valid evidence 不自动获得 current authority；该链路不自动增加 gate。

## 5. Finding contract

### 5.1 Canonical fields

```text
Impact Severity: CRITICAL | MAJOR | MINOR | NOTE
Blocking: YES | NO
```

Severity 描述 finding 后果一旦实现时的影响量级；Blocking 描述当前 scoped action 是否必须停止。Severity 不拥有 gate authority。`CRITICAL + Blocking=NO` 是合法组合，表示潜在后果严重，但证据没有证明当前动作必须停止。

每个 `Blocking=YES` finding 必须提供：

```text
PrimaryConsequence: C1 | C2 | C3 | C4
FailurePath:
BlockedScope:
Evidence:
```

必要时可提供：

```text
SecondaryConsequences:
ValidationRelevance:
```

每个 Blocking finding 只有一个 PrimaryConsequence。SecondaryConsequences 不得在无证据时扩大 BlockedScope。

### 5.2 Consequence codes

| Code | 唯一含义 |
| --- | --- |
| `C1` | harm / irreversible consequence |
| `C2` | authority / credential / budget envelope |
| `C3` | claim / evidence integrity |
| `C4` | target executability / correct scoped write |

C1～C4 只用于 consequence。不得复用 C1/C2 给 Formal evidence 条款编号。

### 5.3 Checker exit

```text
checker nonzero != project Blocking
```

`--strict` 可以因 non-blocking warning 返回非零。Command exit、Validation Relevance 与 project-level Blocking 相互独立；新 gate 不得从 legacy `severity=blocking|warning` 推导 Blocking。

### 5.4 Canonical 与 legacy machine fields

| Field | v0.46 status | Contract |
| --- | --- | --- |
| `impact_severity` | Canonical | 表示 consequence realized 时的影响量级。 |
| `blocking` | Canonical | 表示当前 scoped action 是否必须停止。 |
| `primary_consequence` | Canonical when blocking | 唯一主要 C1～C4 consequence。 |
| `failure_path` | Canonical when blocking | finding 到 consequence 的证据路径。 |
| `blocked_scope` | Canonical when blocking | 只限定必须停止的动作。 |
| `validation_relevance` | Canonical when applicable | 表示 validation failure 与当前目标的关系。 |
| legacy `severity=blocking|warning` | Compatibility-only | 仅供 v0.45 legacy consumer；不拥有 v0.46 gate authority。 |
| `blocking_count` | Compatible aggregate | 保留字段，只由 `blocking=true` 汇总。 |
| `warning_count` | Compatible aggregate | 保留 non-blocking finding 计数，不拥有 gate authority。 |
| Checker exit code | Command-level | 可由 blocking、strict policy 或 checker error 产生，不等同 project Blocking。 |

新 v0.46 governance code 只使用 canonical `impact_severity` 与 `blocking`；新 gate 不读取 legacy `severity`。Legacy consumers 可在兼容期继续读取旧字段，v0.46 不删除 legacy field。Stage C 只能 additive 增加 canonical fields，不新增 schema registry/version system。

## 6. Expected Change、Post-Freeze Drift 与 Stop-Loss

- Expected Change 不阻塞。
- 只有存在明确 frozen reference 的 unauthorized post-freeze drift 才能形成 C3，并仍须满足 universal Blocking finding contract。
- Repeated governance-only blocking without new mainline evidence requires simplification review before another governance layer may be added.
- Stop-Loss 是 heuristic，不是 counter、state、第 N 次触发条件或 validator；simplification review 必须给出新的、受支持的 C1～C4 consequence 或显式 user gate，才能再增加 governance/review layer。

## 7. Current Truth 与 closure writeback

- Document ownership 不意味着 mandatory population。
- 只有真实事实变化才产生对应 owner 的 writeback obligation。
- Active work 中，confirmed fact 可暂存在 active change/checkpoint；micro edit 不要求即时写 current docs。
- Confirmed fact 不得在受影响的 task completion、change closure、phase close、handover 或 ship 之后仍只存在于 work-log、active change 或 checkpoint。
- 没有事实时不得为了 checker 编造 risk、testing、traceability、plan 或其他 owner 内容。
- 不新增 pending-writeback registry、counter 或状态文件。
- 如果用户禁止必需 writeback，只阻止相关 closure/handover/ship declaration，不阻止无关工作。
- Closure 时 responsible current owner 仍 stale 只有在证据建立真实 C1～C4 failure path 时，才能对受影响动作 scoped Blocking。

## 8. Authority contract

- Authority is referenced, not named.
- `FINAL`、`FROZEN`、`candidate-vN` 文件名不产生 authority。
- Owner 可使用现有 Markdown 结构引用 accepted evidence；first-valid 标签或历史 evidence 也不自动产生 current authority。
- Current authority 必须遵守第 4.2 节的 authority chain。

## 9. Root 与 unified-entry layout contract

### 9.1 Required resolution

v0.46 必须解析并输出：

```text
GovernanceRoot
WorkspaceRoot
ProjectRoot
RepoRoot
ForgeKitRoot
CurrentWriteScope
```

- `GovernanceRoot`：被选择的 active `.forgekit/state.json` 与 boundary 所在根。
- `WorkspaceRoot = GovernanceRoot`：v0.46 derived operational alias/default，不新增 persisted `workspace_root`。
- 未启用 workspace-map 时，`ProjectRoot` 使用现有 boundary；`RepoRoot` 由 current task/path 的 Git top-level 推导。
- 启用 workspace-map 时，`WorkspaceRoot` 仍为 GovernanceRoot；map 只解析其下具体 project/repo scope。
- `ForgeKitRoot` 使用现有 boundary 字段。
- `CurrentWriteScope` 由 boundary policy、task scope 与用户授权共同推导。
- 无法唯一推导时报告 `UNKNOWN/AMBIGUOUS`；只有在相关写操作前才可形成 scoped C4。
- 不新增 persisted workspace/repo/layout/root identity、root registry 或 authority registry。

### 9.2 Existing legacy-nested discovery

该规则只适用于 existing-project discovery，不是通用的“向上找任意 `.forgekit`”规则。

1. Direct GovernanceRoot：requested target 自身具有有效 `.forgekit/state.json` 与 `.forgekit/project-boundary.yml` 时，target 是 GovernanceRoot，并由现有 boundary 解析 ProjectRoot。
2. Legacy inner ProjectRoot：target 自身没有 active state 时，只检查 ancestor candidates。候选必须同时具有有效 state 与 boundary；其 `boundary.project_root` 相对 candidate GovernanceRoot 规范化后必须 **exactly equal** requested target；且候选未被现有 archive / artifact / materialized-workspace classification 排除。
3. 恰好一个 exact candidate：复用该 topology，不在 inner ProjectRoot 创建第二套 `.forgekit`。
4. Zero candidate：不得继承 unrelated ancestor；fresh init 可进入 fresh-layout flow，upgrade/adoption/existing operation 报 `NOT_FOUND/UNKNOWN`。
5. Multiple candidates：报告 `AMBIGUOUS`；在受影响 init/adoption/write 前形成 scoped C4。
6. 禁止 `nearest ancestor wins`；不新增 registry。

### 9.3 Fresh unified high-level contract

`--target` 表示实际 `ProjectRoot`，除非 caller 显式请求 legacy nested layout。

唯一 layout 参数：

```text
--layout in-place | legacy-nested
```

- Fresh interactive 未指定 layout：默认 `in-place`，确认提示显示最终 GovernanceRoot 与 ProjectRoot。
- Dry-run 未指定 layout：按 `in-place` 展示计划，不写文件。
- Fresh noninteractive + `--yes`：必须显式给出 layout；缺失时安全停止并显示两条兼容命令，防止旧 automation 静默改变。
- `in-place`：不传非空 ProjectName，ProjectRoot 等于 target。
- `legacy-nested`：保留 existing derived ProjectName 行为并创建原有子目录。
- Current / upgrade / adoption 不移动 existing layout；layout 参数不重写 existing layout。
- PowerShell/Bash 低层显式 ProjectName 行为保持，不把它描述为仅 metadata。
- 不新增 `--project-root`、`--repo-root` 或 persisted layout/root field。

## 10. README、artifact 与 scratch

### 10.1 README ownership

- Business/workspace README 是 user-owned。
- Fresh v0.46 不应让 ForgeKit 获得业务 README ownership，不复制 ForgeKit template README。
- README manifest/install-lock/update 的具体收敛属于 Stage C 的 NF-01 implementation note，不在 Stage A 实现。
- Stale README 默认 non-blocking。只有 current authority 已明确推翻其中事实、Agent 正准备依赖该事实执行具体写操作，且能提供 failure path 时，才形成 scoped C4。

### 10.2 Artifact boundary

- Evidence/archive 中 executable source 默认 non-blocking warning。
- Test/Harness executable authority 由业务项目选择的位置承载；ForgeKit 不规定语言级目录。
- 只有 active runtime/build/entry 实际引用 evidence/archive/scratch 中 executable，或形成 source/authority ambiguity，才可形成 scoped C3/C4。

### 10.3 Scratch cleanup

Scratch cleanup 只使用一次性计划：

```text
Path
Evidence
Proposed Action
Reason
Confirmation
```

不建立 persistent taxonomy、cleanup database 或长期状态。该一次性计划由现有 `project-maintenance.md` 在 Stage B 按 NF-03 承载。

## 11. Ownership Matrix

| Contract | Neutral owner | Specific consumers / boundary |
| --- | --- | --- |
| Execution Intent、Formal boundary、Expected Change / Post-Freeze Drift、Stop-Loss | `project-template/governance/ai-engineering-loop.md` | `large-change-planning` 与各执行流程 |
| Effect Risk、external envelope、不可逆授权 | `project-template/governance/agent-entry-contract.md` | `security-review`、`project-init`、所有执行者 |
| Severity × Blocking、C1～C4、finding/gate contract | Canonical repository source: `project-template/docs/maker-checker-protocol.md`; generated managed target: `.forgekit/docs/maker-checker-protocol.md` | 所有 Skills、reviewers、checkers、migration/release gates |
| Large-change 应用 | `skills/large-change-planning/SKILL.md` | 仅 high-impact / multi-stage planning |
| Code correctness review | `skills/code-review/SKILL.md` | 应用 universal finding contract |
| Security domain assessment | `skills/security-review/SKILL.md` | 主要识别 C1/C2 failure paths |
| Actual release assessment | `skills/release-check/SKILL.md` | 仅真实版本/制品发布 |
| Root resolution 与全局入口边界 | `project-template/governance/agent-entry-contract.md` | `project-init`、`project-suitability`、workspace checker |
| Init layout 与 README ownership | `skills/project-init/SKILL.md` | unified/init scripts |
| Existing-project topology/shadow assessment | `skills/project-suitability/SKILL.md` | workspace checker |
| Fact-owner mapping | `project-template/.forgekit/docs/document-responsibility.md` | `project-bootstrap-fill`、`document-backfill` |
| Closure writeback deadline | `project-template/.forgekit/docs/work-session-checkpoint.md` | `handover-review`、ship/change closure |
| Current-state factual repair | `skills/document-backfill/SKILL.md` | 显式授权后的有限写入 |
| Recoverability assessment | `skills/handover-review/SKILL.md` | 只读报告，不自动修复 |
| Current-doc structural checks | `scripts/check-current-docs-integrity.py` | archive/maintenance/unified entry |
| Workspace/root structural checks | `scripts/check-workspace-integrity.py` | scoped-doc 与 topology workflows |
| Bounded loop rules | `project-template/docs/bounded-auto-loop-policy.md` | explicit loop execution |
| Cleanup planning | `project-template/docs/project-maintenance.md` | 一次性计划，不持久化 taxonomy |

Specific Skill 只引用和应用 neutral contract，不复制完整定义。以上 owner 路径是 Stage B/C 的目标 ownership；Stage A 不修改这些文件。
