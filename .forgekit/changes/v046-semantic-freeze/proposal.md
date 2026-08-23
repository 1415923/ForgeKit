Status: active
ContractStatus: frozen-awaiting-independent-review
Risk: high
Created: 2026-08-24
Owner: ForgeKit Maintainers
Reason: 冻结 ForgeKit v0.46.0 后续 Stage B-E 的唯一实施合同。
AuthorizedStage: stage-a-independent-review

# ForgeKit v0.46.0 Semantic Freeze 提案

## 权威来源与工件职责

- 上游唯一实施合同是维护者批准状态为 `PLAN_APPROVED_FOR_STAGE_A` 的 `ForgeKit-v0.46.0-Frozen-Plan-r2.md`，并包含 targeted independent re-review 对 BF-01～BF-04 的关闭结论。权威来自被引用的批准与审查链，不来自文件名中的 `FINAL`、`FROZEN` 或版本候选字样。
- 本 change 套件是该批准合同在 ForgeKit 仓库内唯一、明确的 Stage A representation，不创设另一套产品语义。
- `proposal.md` 冻结范围、非目标、阶段授权和工件职责；`design.md` 唯一承载 v0.46 semantic contract 与 Ownership Matrix；`verification.md` 唯一承载 Acceptance Matrix A1～A9 / B1～B12；`review.md` 承载 reviewer closure provenance 和本轮独立审查状态；`tasks.md` 只记录 Stage A-E 边界与状态；`ship.md` 只记录当前无发布授权。
- 工件间以引用为主，不复制完整语义；如需改变任一冻结产品语义，必须返回已批准计划/设计阶段，不得通过 review finding 或后续实现静默扩张。

## 问题

v0.46 涉及执行意图、影响风险、Formal evidence、finding、Current Truth、统一入口 layout、README ownership 与 artifact/scratch 边界。若这些语义直接分散到 Skills、checkers、scripts 或迁移中，后续 Stage B-E 会产生多个隐式 owner、互相冲突的 gate 或未经批准的新机制。

## 目标

- 为后续 Stage B-E 建立一个稳定、可引用、无歧义的实施合同。
- 冻结 neutral protocol ownership、Execution Intent / Effect Risk / Formal evidence、Severity / Blocking / C1-C4、Current Truth fact trigger 与 closure writeback、unified-entry layout、Ownership Matrix、Acceptance Matrix 和 v0.46 non-goals。
- 吸收 BF-01～BF-04 的已关闭修正，并把 NF-01～NF-03 绑定到批准的后续 owner/stage。
- Stage A 只创建正常的高风险 change artifacts，不修改任何产品 consumer 或运行行为。

## 本轮范围

- 创建本 `.forgekit/changes/v046-semantic-freeze/` 高风险 change 套件。
- 将批准的语义、ownership、acceptance、review closure 与后续 stage boundary 忠实写入对应工件。
- 只执行 Stage A 文档存在性、唯一 ID、必需语义 marker、diff whitespace 和工作树范围检查。

## v0.46 产品非目标

- 不新增 protocol、Skill、checker、checker/test framework、registry、state machine、root registry、authority registry、shadow-root registry、cleanup database、stop-loss counter、pending-writeback registry 或持久 taxonomy。
- 不新增 persisted `workspace_root`、`repo_root`、layout 或其他 root identity；不新增 `--project-root` / `--repo-root`。
- 不把 Formal evidence retention 变成永久物理保存制度；不因 Formal 自动增加 acceptance、aggregate、review、checker 或独立审查 gate。
- 不让 Severity 拥有 gate authority；不让 checker nonzero 或 `--strict` 自动等同 project Blocking。
- 不让 active task 自动产生所有 current-doc owner 的 mandatory population；不为 checker 编造不存在的事实。
- 不让 ForgeKit 规定语言级源码目录、取得业务/workspace README ownership、移动 existing project layout，或把 artifact/scratch cleanup 变成长期分类系统。
- 不以 `FINAL`、`FROZEN`、`candidate-vN` 等文件名建立 authority。

## Stage A 明确非目标与保护边界

- 不修改 canonical Skills、`.agents` projections、`.claude` projections、native adapters、init scripts、`forgekit-project.py`、current-doc checker、workspace checker、migration、template manifest、README init behavior、loop consumers、`VERSION`、`CHANGELOG` release entry 或 release assets。
- 不进入 Stage B，不修改任何真实业务项目，不 commit、push、tag、publish、release 或 deploy。
- `usage.html` 是 unrelated user-owned dirty deletion：不恢复、不修改、不暂存，不改变其 validator/test/migration；禁止 `git add -A`。

## 信任边界

- 防止后续实现把 Execution Intent 与 Effect Risk 混为一轴，或把真实/付费调用自动视为 Formal。
- 防止 claim evidence 被结果导向覆盖、隐藏或 cherry-pick，同时避免发明永久保存制度。
- 防止 Severity、legacy checker disposition 或命令退出码获得隐式 gate authority。
- 防止 root discovery 采用 unrelated ancestor 或 nearest-ancestor guess，并防止 existing legacy-nested topology 被复制或移动。
- 防止 document ownership 被机械转化为无事实的 mandatory population。
- 防止 Stage A 借语义冻结之名提前修改 Stage B/C implementation surfaces。

## 阶段授权

- Frozen Plan r2 只授权 Stage A maker 落地；本轮 maker representation 完成后，下一步仅允许 fresh read-only independent review。
- Stage A independent review PASS 只可授权另行明确的 Stage B；本 change 当前不授权 Stage B、commit 或任何外部动作。
- Stage B-E 的已冻结边界见 `tasks.md`，其存在是实施路由合同，不表示已经授权或实施。

## 冻结规则

- `design.md` 与 `verification.md` 中的语义和 acceptance IDs 不得由 maker 自行重新解释。
- Reviewer 可验证忠实性、一致性与遗漏；不得借本轮 Stage A review 新增产品语义类别或新治理机制。
- BF-01～BF-04 已由上游 targeted review 关闭，本轮 representation 必须吸收其修正；NF-01～NF-03 仅作为后续 implementation notes。

## 生命周期说明

- 当前 `Status: active` 表示 v0.46 change 仍在推进，不表示产品实现完成。
- `ContractStatus: frozen-awaiting-independent-review` 表示 Stage A maker 已冻结仓库内 representation，但独立审查尚未执行。
- 只有 Stage B-E 实现、验证、current-owner writeback 与发布收口完成后，整个 v0.46 change 才可进入 `done`；Stage A 不更新版本或发布记录。
