AcceptanceStatus: frozen

# ForgeKit v0.46.0 Verification Contract

## 1. Frozen Acceptance Matrix 解释

- 本文件唯一承载批准计划中的 A1～A9 / B1～B12，不创建额外 testcase taxonomy。
- 每行的 Positive、Key rejection 与 Required evidence 只是既有 acceptance ID 的验证方向，不新增产品语义类别或自动 gate。
- Stage A 只检查合同完整性和一致性；产品行为证据由表中指定的后续 stage 在真实入口/consumer path 上取得。
- Acceptance、aggregate、review、checker 仍为 predeclared Formal contract 中的 **as applicable**，本矩阵本身不让每次 Formal execution 自动增加 gate。

## 2. Matrix A — Progress-Preserving Governance

| ID | Frozen contract | Positive case | Key rejection case | Required implementation evidence |
| --- | --- | --- | --- | --- |
| A1 | Diagnostic bring-up/0-call 失败可修复重跑，不创建 Formal identity。 | DIAGNOSTIC 失败后修复重跑，记录仍是 diagnostic。 | 把首次 diagnostic failure 冻结成 Formal identity。 | Stage B consumer contract + Stage D regression。 |
| A2 | Bounded external Smoke 遵守 Effect envelope，但不自动升级为 Formal 或 release。 | 真实 smoke 在授权的 credential/budget/retry envelope 内完成。 | 因真实或付费调用自动标记 Formal 或触发 release。 | Stage B protocol/consumer evidence + Stage D regression。 |
| A3 | First valid Formal evidence 不得因 claim outcome 被静默覆盖、替换、丢弃、隐藏或 cherry-pick；其 provenance 必须按项目适用 retention policy 保持可追溯，但不要求永久物理保存。只有预声明合同要求的 applicable acceptance/aggregate/review 完成，且 current fact owner 明确引用 accepted evidence 后，才形成 current authority。 | 首份 valid Formal evidence 可追溯，所需 applicable steps 完成后由 owner 引用。 | 为改善结果替换/隐藏 evidence，或仅凭 first-valid/文件名授予 authority，或强制永久保存。 | Stage B protocol/consumer evidence + Stage D retention/authority regression。 |
| A4 | 所有 code/security/release/handover/reasoning/native/Claude/checker consumers 均独立表达 impact severity 与 Blocking。高 Severity 不自动产生 Blocking；每个 Blocking=YES finding 必须具有唯一 PrimaryConsequence、FailurePath、Evidence 和 BlockedScope。 | Consumer 输出独立 Severity 与 Blocking，并给齐 Blocking 字段。 | 从高 Severity 推导 Blocking，或 Blocking finding 缺必要字段。 | Stage B 全部 active consumer inventory 与 convergence evidence；Stage C checker evidence。 |
| A5 | Blocking finding 有唯一 PrimaryConsequence、failure path、scope、evidence；secondary 不无依据扩 scope。 | 一个 primary C1～C4 与证据限定 scoped stop。 | 多个 primary，或 secondary 无证据扩大 blocked scope。 | Stage B protocol/consumer evidence + Stage C checker regression。 |
| A6 | Validation Relevance、checker exit、`--strict` 和 project Blocking 相互独立；strict warning 可 exit 1 且 `Blocking=NO`。 | Non-blocking warning 在 strict 下 nonzero，finding 仍 non-blocking。 | 由 nonzero/strict 自动产生 project Blocking。 | Stage C additive checker/stdout/exit compatibility tests。 |
| A7 | Expected Change 不阻塞；有明确 frozen reference 的 unauthorized post-freeze drift 才形成 C3。 | 合同内 expected change 正常推进。 | 无 frozen reference 或无 unauthorized drift 就报告 C3 Blocking。 | Stage B protocol/review consumer evidence + Stage D negative regression。 |
| A8 | Repeated governance-only blocking 且没有新的 mainline evidence 后，consumer 在增加新的 governance/review layer 前必须先做 simplification review，并给出新的受支持 C1～C4 consequence 或显式 user gate。bounded-auto 不得对每次 run 强制 independent review；被移除 loop docs 在 active v0.46 surface 上必须零引用。 | 无新 mainline evidence 时先简化；loop consumer 收敛后再移除旧文档。 | 实现 counter/第 N 次 trigger/validator，强制 every-run review，或 active reference 未清零就删除。 | Stage B complete active-consumer search、现有 validator/smoke evidence；Stage D regression。 |
| A9 | `release-check` 只用于实际版本/制品 release 准备或评估；external smoke 不触发 `release-check`。 | 真实 release candidate 才路由 release-check。 | External smoke 自动触发 release-check。 | Stage B release consumer contract + Stage D routing regression。 |

## 3. Matrix B — Current Truth / Workspace

| ID | Frozen contract | Positive case | Key rejection case | Required implementation evidence |
| --- | --- | --- | --- | --- |
| B1 | Fresh init 不复制 ForgeKit template README；absent/custom README 保持。 | README absent 时不创建 ForgeKit-owned business README；custom README byte-preserved。 | Fresh init 复制/拥有/覆盖业务 README。 | Stage C fresh init + manifest/install-lock tests；Stage D migration regression。 |
| B2 | Fresh unified init 遵守 `--layout` 合同；existing layout 只做发现、不移动。legacy outer GovernanceRoot entry 和 inner ProjectRoot entry 必须解析到同一 active topology，inner entry 不得创建第二套 `.forgekit`。 | Fresh explicit layout 正确；legacy outer/inner 两入口解析同一 topology。 | Existing layout 被移动，或 inner entry 创建第二个 GovernanceRoot。 | Stage C unified-entry outer+inner fixtures；Stage D migration regression。 |
| B3 | 启动时必须解析 GovernanceRoot、WorkspaceRoot、ProjectRoot、RepoRoot、ForgeKitRoot 和 CurrentWriteScope，且不新增 persisted identity。Direct-root、唯一 exact-match ancestor、zero-candidate 和 ambiguous-candidate 均遵守 Existing-Project Root Discovery；WorkspaceRoot 默认由 GovernanceRoot 派生，RepoRoot 继续来自 Git top-level 或 workspace-map。 | 六个 root/scope 值按 direct 或唯一 exact candidate 解析。 | Zero candidate 继承 unrelated ancestor、multiple candidate nearest-wins，或写入新 persisted root。 | Stage C direct/exact/zero/ambiguous fixtures 与 machine output；Stage D regression。 |
| B4 | Historical shadow 默认 non-blocking；只有写目标无法唯一确定时形成 scoped C4。 | 只读发现 historical shadow 仅 warning。 | 无 dependent write/ambiguity 就全局 Blocking。 | Stage C workspace checker compatibility + Stage D negative regression。 |
| B5 | Document ownership 不意味着 mandatory population。Active task + 无真实 risk/testing/traceability/plan fact 时，对应 lean/template owner 不得仅因 active task Blocking；不得为满足 checker 编造不存在的事实。 | Active task 无相关事实时 lean owner 可保持未填充且 non-blocking。 | 由 active task 机械要求所有 owner 非模板或虚构内容。 | Stage B docs/consumer convergence + Stage C current-doc checker negative fixture。 |
| B6 | Confirmed testing/risk/authority/status fact 可在 active checkpoint 暂存；如果 closure/handover/ship 被声明时 responsible current owner 仍 stale，只有证据建立真实 C1～C4 failure path 时才对受影响动作 scoped Blocking。 | Active work 暂存 confirmed fact；closure 前写回 owner。 | 无真实 failure path 就阻止普通工作，或 closure 后仍只留在 change/checkpoint。 | Stage B owner/checkpoint convergence + Stage C closure fixture + Stage D regression。 |
| B7 | Owner 可用现有 Markdown 结构引用 authority；first valid、`FINAL`/`FROZEN` 文件名或历史 evidence 不自动产生 authority。 | Owner 明确引用 accepted evidence 与适用 acceptance。 | 按 filename/first-valid/history 自动授予 authority。 | Stage B authority consumer contract + Stage D negative regression。 |
| B8 | Evidence/archive executable 默认 warning；active runtime/build/entry 引用或 source ambiguity 才 scoped C3/C4。 | 孤立 archive executable 仅 warning。 | 未被 active path 引用也 project-blocking。 | Stage B artifact contract + Stage C checker fixture。 |
| B9 | Stale README 默认 non-blocking；只有 authority contradiction + dependent write + failure path 才 scoped C4。 | Stale README 在只读盘点时 warning。 | 缺任一条件就 Blocking，或 ForgeKit 接管 README。 | Stage B consumer contract + Stage C workspace/init negative fixture。 |
| B10 | Scratch cleanup 使用一次性 Path/Evidence/Action/Reason/Confirmation，不形成持久 taxonomy。 | 现有 maintenance owner 记录一次性五字段计划。 | 创建 cleanup registry/database/taxonomy/state。 | Stage B `project-maintenance.md` convergence review；Stage D no-new-mechanism search。 |
| B11 | Boundary `created_with` 与 state current version 分开展示，不误报 VERSION MISMATCH。 | 历史 created-with 与 current version 同时正确展示。 | 因两者不同误报 mismatch。 | Stage C checker/unified-entry fixture + Stage D upgrade regression。 |
| B12 | Hygiene、strict command failure 和 project-level Blocking 分离；普通只读工作不因 hygiene 停止。 | Hygiene warning/strict exit 不阻止无关 read-only work。 | Command nonzero 被提升为全项目 stop。 | Stage C exit/output compatibility + Stage D read-only regression。 |

## 4. Stage A contract consistency checks

仅允许以下有限检查；结果在实际执行后记录，不替代 Stage A independent review：

- A1～A9 与 B1～B12 各出现一次且无缺号/新增 ID。
- Execution Intent、finding fields、C1～C4、六个 root/scope 名称、BF/NF closure markers、non-goals 和 Stage boundaries 均可定位。
- 新增文件全部位于本 change 目录；`usage.html` 保持原 dirty deletion；无产品代码/模板/Skill/checker/migration/version diff。
- `git diff --check` 无 whitespace error。

## 5. Actual checks

执行日期：2026-08-24。

| Check | Result |
| --- | --- |
| Inline PowerShell Stage A artifact/ID/marker/scope check | PASS：artifact set 为六个既有 high-risk change files；A1～A9 顺序完整；B1～B12 顺序完整；17 个 design markers 与 7 个 BF/NF markers 存在。 |
| Inline trailing-whitespace check for all six new artifacts | PASS。 |
| `git diff --cached --check` 与 `git diff --check` | PASS；均无输出。 |
| `git status --short --untracked-files=all` scope assertion | PASS：六个 Stage A artifacts 为 staged added；既有 `usage.html` 仍是 unstaged deletion；无其他变化。 |
| Explicit staging assertion (`git diff --cached --name-status`) | PASS：暂存区仅包含本 change 的六个明确列名文件；未使用 `git add -A`。 |
| Unstaged assertion (`git diff --name-status`) | PASS：仅 `D usage.html`。 |
| `usage.html` preservation assertion | PASS：worktree 仍为删除状态，index blob 为 `240b6c2c9174abd08c8c7879e72d75cc94b24c29`。 |
| `VERSION` read-only assertion | PASS：仍为 `0.45.0`。 |

未运行 `scripts/validate-template.ps1`、product checker、init、migration、smoke 或 Stage B/C tests；Stage A 没有修改 template structure、Skills、prompts、scripts 或 HTML，不扩大验证范围。

## 6. 未验证项

- Stage B/C/D/E 的 protocol、consumer、checker、init、migration 与 release 行为均未实现、未运行，也不得由 Stage A 文档检查推断通过。
- Stage A fresh read-only independent review 尚未执行。
