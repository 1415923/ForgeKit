# v0.45.0 设计复查

## Maker 摘要

MakerStatus: ready-for-check
FilesChanged: `.forgekit/changes/v045-rule-ownership-skill-convergence/*.md` only
ImplementationSummary: 仅完成规则所有权、Skill 职责、风险、兼容、测试和分阶段实施设计；未实施产品变更。
ValidationRun: 见 `verification.md` 第 8 节。
KnownRisks: 同名 Skill 的真实客户端行为、Claude metadata 行为和模型行为证据仍需测试。
NotVerified: 所有 v0.45.0 目标行为、升级 migration、sync checker 和 prompt 兼容均未实施。

## Checker 复查

CheckerStatus: needs-fix
ReviewDecision: needs-fix
ReviewType: independent
ReviewerAgent: Codex independent checker (`/root`)
ReviewedOn: 2026-07-20
ReviewMode: initial
ReviewedRange: six v0.45.0 artifacts; current AGENTS/CLAUDE; shared and Claude Skills; governance/references; prompts; plugin metadata; init, upgrade, distribution, release and smoke validation paths
FrozenAcceptanceIDs: A01-A22
AuthorizedStage: design-ready
DiffReviewed: yes
ValidationReviewed: yes
DocsReviewed: yes
RisksReviewed: yes
Findings: 0 BLOCKER, 4 MAJOR, 3 NOTE
BlockingFindings: none at BLOCKER severity; MAJOR findings prevent stage A authorization
FollowUps: revise design artifacts only, then request blocker-recheck against M-01 through M-04
RequiredFixes: see `最小设计修订清单`
VerificationGaps: real Codex/Claude selector and behavior evidence remains `NEEDS_TEST`, as intended for stage A/E
TODO_REVIEW: Recheck only M-01 through M-04 after the design documents are revised.
FinalRecommendation: FAIL for entry into stage A. Overall direction is sound, but frozen decisions and implementable distribution/test contracts are not yet consistently represented.

## 审查结论

**FAIL**。

没有发现 BLOCKER 级的错误仓库事实、静默覆盖方向、升级链破坏、阶段 A 运行时语义修改，或已经把单次非确定模型结果接入自动 CI 的实现。但是四项 MAJOR 都直接影响阶段 A 的合同，必须先修订设计并复审。

## 基线与范围

- Branch: `main`。
- Version: `0.44.1`。
- Initial worktree: 原有 `D usage.html`，以及六个未跟踪 v0.45.0 design artifacts。
- 除上述路径外没有其他初始改动。
- `.forgekit/changes/` 中另有 v0.44 的 `maker-checker-review-convergence`，不是重复的 v0.45.0 artifact。
- 六份工件符合 high-risk change 的 proposal/design/tasks/verification/review/ship 结构。
- proposal 为 `draft/high/design-ready`，ship 为 `not-ready`；没有声称 v0.45.0 已实施、行为验证通过或已发布。
- `usage.html` 被明确排除在本次审查范围外，未读取为设计证据，也未修改或恢复。

## 证据真实性矩阵

| 设计陈述 | 结论 | 独立证据 |
| --- | --- | --- |
| 根 AGENTS 较短，模板 AGENTS/CLAUDE 承载大量条件流程 | VERIFIED | 根 AGENTS 55 行；模板 AGENTS 181 行；模板 CLAUDE 166 行；入口实际包含长 startup、routing、archive、loop、checkpoint、review 和 worktree 规则 |
| document-responsibility 将 AGENTS/CLAUDE 定义为简短启动、边界和路由入口 | VERIFIED | `project-template/.forgekit/docs/document-responsibility.md:33` 明确排除长清单和模板正文 |
| 根 `skills/` 与模板 `.agents/skills/` 有九组同构 Skill | VERIFIED | 九组目录均只含 `SKILL.md` 与 `agents/openai.yaml`；逐文件 SHA-256 全部一致 |
| `.claude/skills/` 是有意平台适配而非机械投影 | VERIFIED | 六个不同命名的 Claude Skill；独立 reviewer、request skill 和按需 review references 存在通用 Skill 没有的平台 wiring |
| 当前共享 Skill 发布校验只覆盖 code-review | VERIFIED | `validate-plugin-assets.ps1:111-130`、`smoke-test.py:1759-1766` 只比较两份 `code-review/SKILL.md`；mutation 也只覆盖该对文件 |
| project-init、handover-review、document-backfill 职责重叠 | VERIFIED | project-init 内嵌 backfill/large-change/bootstrap；handover 同时 audit、backfill、fix；document-backfill 立即写 managed docs |
| large-change-planning 使用固定文件/模块阈值 | VERIFIED | Trigger 明确写 `more than 5 files or more than 2 modules` |
| release-check 默认加载范围过宽 | VERIFIED | Workflow 第一步无条件列出九份 governance、五份 `.codex` 规则和多类 managed docs |
| first-principles 强制固定八章节 | VERIFIED | Claude Skill 明确写 `Output exactly these sections` 并列出八项 |
| prompts 使用旧 `docs/` 路径、固定清单和固定输出 | VERIFIED | 七个 prompts 中初始化、发布、需求、架构、实现等文件存在对应路径和固定格式 |
| 初始化将项目本地 Skills 分发给新项目 | VERIFIED | `init-project-template.ps1:108-126` 递归复制未排除的 template 文件；模板实际包含 `.agents/skills/` |
| 现有 upgrade 能用 baseline 区分 stock/custom 并保留 custom | VERIFIED | `replace_file_if_baseline_matches` 比较 target/source/baseline SHA-256；不匹配返回 review-needed；manual merge 导出 local/incoming/diff |
| plugin 与项目本地同名 Skill 可以同时存在 | SUPPORTED | plugin manifest 指向根 `./skills/`，生成项目又包含 `.agents/skills/`；实际客户端选择行为不由仓库静态配置证明 |
| 同名 Skill 的 selector 展示、显式调用和隐式优先级 | UNVERIFIED | 需要 DECISION-02 指定的真实客户端测试；设计正确保留为 NEEDS_TEST |
| 精简入口后的 context 收益和模型授权行为 | UNVERIFIED | 当前尚未实施，必须由阶段 A/B 行为证据验证 |
| 三个维护者决定仍然待确认 | INCORRECT | 本轮已冻结 DECISION-01、02、03，但五份工件仍保留 NEEDS_DECISION/待确认表述 |

关键推荐没有建立在错误仓库事实上；未验证的同名路由也没有被伪装成当前保证。

## BLOCKER

无。

## MAJOR

### M-01：三个冻结决定没有进入设计真相，且 DECISION-02 存在相反建议

证据：

- `proposal.md:71,91-93` 仍要求确认三个决定。
- `tasks.md:13-14,35-37` 仍把决定和客户端版本列为待办/前置确认。
- `design.md:451-453` 仍列三个 `NEEDS_DECISION`；`ship.md:10` 仍要求确认。
- `design.md:165,435,459` 仍保留阶段 A 增加来源 display name/来源标识的可能；`design.md:169` 优先提出 plugin 命名空间化，未体现 DECISION-02 冻结的“阶段 A 不加 display name、不改公共 name，长期优先评估入口型/操作型职责拆分”。
- DECISION-03 已选择仓库原生跨平台 Python runner，但 proposal/tasks 仍把 runner 形式写成待决定或“最小接口”。

影响：多个工件对阶段 A 的前置条件给出互相冲突的真相，maker 无法判断哪些选择已经关闭，也可能在阶段 A 实施被明确排除的 display-name 方案。

最小修订：把 DECISION-01/02/03 写为冻结决定，关闭 D-006 和对应前置项；删除阶段 A display-name/name 变体；把长期职责拆分保留为阶段 E 的 NEEDS_TEST 分支。

### M-02：共享投影与 custom upgrade 只有原则，没有足以实施的身份合同

证据：

- `design.md:151-157` 要求显式投影清单和 baseline guard，但没有冻结清单存放路径和 schema。
- 当前九组通用 Skill 的实际共享文件恰好是 `SKILL.md` 与 `agents/openai.yaml`；设计没有说明这两类是否全部受管，也没有定义未来 `references/`、`scripts/`、`assets/` 是默认包含、默认排除还是逐项 opt-in。
- 没有定义 sync apply 的目标根解析、路径 allowlist、额外文件处理和“不得触碰 `.claude/skills/`”的写时保护方式。
- `design.md:157,444-446` 提到已知 v0.44.1 baseline，却没有选择 baseline 身份保存在 migration `baseline/`、content manifest 还是其他具体位置，也没有定义版本链选择哪个 baseline。
- manual merge 目标只写 incoming diff；没有冻结报告必须显示来源版本、目标版本、baseline/actual/incoming checksum 和实际 diff。当前脚本已有大部分字段，可明确复用，而不是重新发明。
- 新项目实际由初始化脚本复制 template；设计没有明确“发布前先生成/校验 template projection，初始化只复制已发布投影，不在用户项目运行 sync apply”。

影响：阶段 A 可以产生多个都符合文字原则、但兼容性和覆盖边界不同的实现；无法可靠验收 DECISION-01 的“确定性投影”和 stock/custom 保护。

最小修订：冻结 manifest 路径/schema、当前九组的精确文件集合、未来附属资源 opt-in 规则、sync 写集合/路径保护、新项目投影时点、v0.44.1 baseline 存储与选择、review-needed 版本/checksum/diff 字段及 rollback 身份。

### M-03：DECISION-03 的 Python runner、隔离和证据模型未形成可验收合同

证据：

- `verification.md:61-73` 定义了 prompt fixture 和人工结果，但 runner 只记录所选 Skill、读取范围、写入路径和外部动作；未要求保存客户端版本、模型、原始提示、原始输出、adapter、grader 版本/依据。
- 未定义仓库原生跨平台 Python runner 的入口、数据 manifest 最小字段或 Codex/Claude adapter 合同。
- 未定义 live/behavior case 必须在临时副本或其他隔离工作区运行，因此“git diff oracle”不足以保证不会修改真实项目。
- 未定义环境/客户端不可用、adapter 失败、Skill 路由失败、越权写入、grader 不确定和真实行为失败的独立状态。
- `verification.md:101-113` 把代表性 Codex/Claude 行为放入“发布 blocker 集”，但没有明确区分：确定性检查是自动 CI blocker；单次非确定结果只是需独立 checker 复核的发布证据，不能无条件成为自动 CI 判定。

影响：A01-A03、A08-A16、A19-A22 的证据可能不可重放、污染真实项目或把基础设施失败误判为模型越权；也可能违背 DECISION-03 的自动门禁边界。

最小修订：冻结 Python runner + data manifest + 两个 adapters；规定临时副本/禁止真实项目写入；保存版本、模型、prompt、output、tool/write trace、grader 和依据；定义至少 `environment-error / adapter-error / routing-failure / unauthorized-write / behavior-failure / grader-inconclusive / pass`；明确确定性自动 blocker 与代表性人工复核证据的区别。

### M-04：权威矩阵仍有未拆分的多权威表达

证据：

- `design.md:111` 将风险分类同时交给 `ai-engineering-loop.md` 和未命名 risk reference。
- `design.md:113` 把 code-review 流程交给 Skill，但 `design.md:88` 又把 review convergence 归入第三层，没有指定 convergence 的唯一规范文件。
- `design.md:114` 的“唯一权威层/位置”同时列第二层 maintenance/archive workflow 和第三层 archive protocol。
- `design.md:115` 的 checkpoint/context continuity 没有区分 checkpoint 触发、存活位置和写回粒度分别由哪个文档负责。
- `design.md:117` 同时列 document-responsibility 和 workflow-router，没有明确前者拥有事实/文档职责、后者只拥有意图路由。

影响：阶段 A 的核心目标正是消除规则重复；若不先拆分“规范语义、任务步骤、确定性执行”，迁移后仍可能出现两个位置分别维护完整规则。

最小修订：对上述规则逐项指定一个规范性文件，并把其他位置明确标为 application/reference/enforcement；单独列出 code-review convergence 的权威文件。引用不得反向重新定义规范。

## NOTE

### N-01：核心 Skill 方向正确，但目标合同字段不完全对称

十个 Skill 都有当前职责、目标边界、写入模式、隐式策略和验收方向；七个首批 Skill 也有触发/不触发 fixture。`project-bootstrap-fill`、`project-suitability`、first-principles 尚未明确列出完整 input/output/not-trigger 行为合同。它们不阻塞阶段 A 基础设施，但必须在各自阶段 C/D 修改前冻结。

### N-02：A21 的“来源可辨”措辞需与 DECISION-02 对齐

A21 的关键目标应是同构语义、真实 selector/显式/隐式证据和不依赖未证实优先级；阶段 A 不应把 UI 来源标签设为必须成功的 positive case。长期职责拆分留到阶段 E。

### N-03：静态 marker 应保持最小

入口 marker 只能检查不可丢失的安全合同，不能以大段固定文本重新制造旧式提示词僵化。现有设计已意识到该风险，阶段 A 实施时保持语义级最小断言即可。

## 三个维护者决策符合性

| 决策 | 结论 | 说明 |
| --- | --- | --- |
| DECISION-01 | PARTIAL | 推荐方案方向一致；工件仍标为未决，且精确投影/baseline 身份合同不足，见 M-01/M-02 |
| DECISION-02 | NOT COMPLIANT | NEEDS_TEST 被诚实保留，但阶段 A display-name 可能性和长期命名空间建议与冻结方向不一致，见 M-01/N-02 |
| DECISION-03 | PARTIAL | 已区分静态、fixture、模型和人工测试，也要求一个 Codex/Claude 证据；Python runner、adapter、证据字段、失败分类和自动 blocker 边界未冻结，见 M-01/M-03 |

## 四层规则所有权结论

模型本身可接受：入口保留始终生效的安全语义；Skills 负责条件流程；governance/references 负责详细规范；scripts/validators 负责确定性检查。AGENTS/CLAUDE 不会被削成空链接页，scripts 也没有被设计成判断开放式模型语义。

进入阶段 A 前必须关闭 M-04，将同一矩阵单元中的多位置拆成“唯一规范、应用流程、确定性执行/检查”，否则核心目标不可验收。

## Skill 权威源、投影与 custom upgrade 结论

- 根 `skills/` 为共享语义源、`.agents` 为同构投影、`.claude` 为平台适配的总体方向正确。
- 新项目保留本地 Skill，existing custom 不静默覆盖，sync apply 仅维护者显式运行、CI/release 仅 check，均符合冻结方向。
- 当前仓库确有可复用的 baseline SHA-256 和 REVIEW-NEEDED/manual-merge 机制。
- 但 v0.45.0 的精确 manifest、受管文件、baseline 版本身份和 safe target 合同未冻结，因此当前不能实施，见 M-02。
- plugin + local 重复被诚实保留为 NEEDS_TEST；实际 selector 行为未被当成事实。

## AGENTS/CLAUDE 瘦身边界结论

PASS。

反事实检查结果：设计保留项目/写入边界、证据优先、audit read-only、明确修复授权、不重复确认、外部/不可逆保护、基础风险路由、Skill 路径和最小验证入口。下沉的是长路由、文档矩阵和特定维护协议；即使 Skill 未触发，也不会因此直接失去核心安全保护。Codex/Claude 共享语义和平台调用差异也有明确区分。

## 核心 Skills 职责结论

PASS WITH NOTES。

- project-init 保持轻量编排器，不拆成微型 Skill 群。
- project-bootstrap-fill 与 document-backfill 分工明确，前者处理确认问答，后者处理历史来源。
- handover-review 收敛为默认只读审计，不自动修 P0/P1。
- document-backfill 改为可审查小批次，禁止 governance 接收业务事实。
- large-change 使用影响模型，不再以文件数定风险。
- release-check 按发布类型/diff 渐进加载。
- code-review 不强制所有低风险变更独立审查，并保留 initial/blocker-recheck 收敛。
- project-suitability 默认只读且允许“不适合”。
- security-review 证据不足时降级并要求人工复核。
- first-principles 不再强制八章节。

完整 input/output/not-trigger fixture 的补齐时点见 N-01。

## 风险模型反例

| 反例 | 结果 | 依据 |
| --- | --- | --- |
| 单文件认证/权限修改 | PASS：至少中风险 | 权限策略被列为强触发 |
| 单个数据库 migration | PASS：至少中风险 | schema/data migration 被列为强触发 |
| 二十个确定性投影文件 | PASS：可为低风险 | 无语义变化且 validator 完整时允许低风险 |
| 多仓库只读分析 | PASS：不因数量自动变成高风险写入 | 高风险条件是跨仓库协调部署/难回滚等客观影响；只读范围仍需边界确认 |
| 已授权破坏性操作 | PASS：客观风险不下降 | 设计明确授权只降低执行不确定性 |
| 小 diff 破坏公共 API | PASS：至少中风险 | 公共合同被列为强触发 |
| 大规模格式化且可靠回滚 | PASS：可为低风险 | 多文件机械变更不由数量升级 |
| 证据不足的安全结论 | PASS：降级并人工复核 | security-review 使用 Verified/Supported/Unverified，无法验证不写安全通过 |

模型是定性影响判断，没有引入新评分系统。

## A01-A22 一致性

- ID 集合完整且唯一：A01 至 A22，共 22 项，无重复。
- 正常路径、关键拒绝反例和证据列均存在；静态检查没有被宣称为模型行为证明。
- A07 覆盖 stock/custom AGENTS、CLAUDE 和 Skill；A12/A13 是 initial/recheck 成对测试；A11/B06/B07 覆盖单文件高风险和多文件低风险。
- self-review 明确不能满足独立 gate。
- 需要修订的项目：A04 依赖 M-04 的唯一权威合同；A07 依赖 M-02 的 baseline 身份；A21 需按 DECISION-02 调整；所有模型行为证据依赖 M-03 的 runner/隔离/失败分类。
- 当前工件没有已经实施“一次非确定结果作为无条件自动 CI blocker”，但文字尚未充分区分自动 blocker 与人工复核发布证据，必须按 M-03 明确。

结论：矩阵结构通过，四项合同在设计修订后才可作为阶段 A 验收基线。

## 阶段 A 范围

阶段 A 的范围本身足够小、可独立验收和回滚：只涉及所有权/风险规范、投影清单与 sync 基础、确定性测试骨架、行为 manifest/runner 骨架和 baseline/custom 合同；明确不瘦身入口、不重构 Skills、不迁移 prompts、不改变普通用户运行时语义。

当前不允许进入阶段 A，不是阶段划分过大，而是 M-01 至 M-04 尚未把阶段 A 的输入合同冻结到可实施状态。

## 兼容性结论

设计覆盖新 plugin、新项目、v0.44.1 stock/custom、plugin+local、Codex-only、Claude-only 和仓库外 prompt 用户。单命令升级、REVIEW-NEEDED/manual-merge、用户定制保护和版本/schema/创建版本分离均被保留。prompts 至少保留 v0.45/v0.46，最终删除版本仍为 OPEN，v0.45.0 不删除。

## 最小设计修订清单

1. 将 DECISION-01/02/03 从 NEEDS_DECISION 改为冻结事实，并同步 proposal、design、tasks、verification、ship 的相关前置条件和 wording。
2. 冻结共享投影 manifest 的路径/schema、九个 Skill 当前受管文件、附属资源 opt-in 规则、sync safe-target 保护和新项目投影时点。
3. 冻结 v0.44.1 baseline 的保存/选择方式，以及 REVIEW-NEEDED/manual-merge 的来源版本、目标版本、checksum、diff 和 rollback 字段。
4. 冻结跨平台 Python behavior runner、数据 manifest、Codex/Claude adapters、隔离策略、证据字段和失败分类；区分确定性自动 blocker 与独立复核的代表性行为证据。
5. 消除权威矩阵中的多权威表达，单列 code-review convergence 的规范性文件。
6. 调整 A21，使阶段 A 不要求 display name；长期入口型/操作型职责拆分保留为阶段 E NEEDS_TEST。

完成以上最小修订后，只需对 M-01 至 M-04 做 blocker-recheck，不需要重开全仓开放式审计。

## 文档同步

- 本轮只允许并实际只更新本 `review.md`。
- 设计尚未通过，不应同步为 README、governance、Skills、prompts、版本或发布事实。

## 当前态文档同步元信息

CurrentDocsSync: not-needed
ChangelogUpdated: not-needed
ArchitectureUpdated: not-needed
TestingUpdated: not-needed
RequirementsUpdated: not-needed

## Blocker Recheck

RecheckedOn: 2026-07-20
ReviewMode: blocker-recheck
ReviewType: independent
ReviewedRange: M-01 through M-04 only; A04, A07, A21, and model-behavior acceptance revisions; six v0.45.0 artifacts; actual upgrade implementation fields and output paths
OriginalReviewIntegrity: verified before append; SHA-256 `8e6831585957b0b49bd759c6b53fefe30a7fde9e55223f0066e0f4c3fa752ba2`
RecheckDecision: FAIL
AuthorizedStage: design-revised-awaiting-blocker-recheck

### Recheck Status

| Finding | Status | Result |
| --- | --- | --- |
| M-01 | CLOSED | DECISION-01/02/03 are frozen consistently across the five maker artifacts. No related `NEEDS_DECISION`, stage A display-name/public-name change, namespace-first recommendation, or unresolved runner/gate choice remains. |
| M-02 | OPEN | Manifest, sync, safe-target, baseline identity, four classifications, packet fields, rollback identity, and single-command behavior are substantially frozen, but the design does not name the existing review/manual-merge output locations. |
| M-03 | CLOSED | Runner/manifest/adapter paths, case schema, isolation, run record, failure classes, evidence handling, and deterministic-versus-behavior gate boundary are uniquely specified. |
| M-04 | OPEN | The matrix has 26 unique IDs, but several rows still use a multi-file or parameterized owner rather than one concrete normative owner. |

### M-01 Decision Compliance

- DECISION-01: compliant. Root `skills/` is the only shared semantic source; `.agents` is the deterministic projection; `.claude` is excluded as an adapter layer; only stock auto-upgrades; custom/unknown-baseline use REVIEW-NEEDED/manual-merge; CI/release is check-only and apply is maintainer-explicit.
- DECISION-02: compliant. Stage A does not add display names or change public Skill names; source/projection remain isomorphic; selector/explicit/implicit behavior remains `NEEDS_TEST`; stage E prioritizes entry-versus-local-operation responsibility research; namespaces/display variants remain tested fallbacks only.
- DECISION-03: compliant. The cross-platform data-driven Python runner is frozen; deterministic failures are automatic blockers; Codex and Claude each require representative independently reviewed evidence; one nondeterministic result is not an unconditional CI blocker; unauthorized writes or lost safety boundaries may be escalated by the checker.

### M-02 Remaining Major

The design correctly references `.forgekit/state.json[forgekit_version]`, versioned migration descriptors, `replace_file_if_baseline_matches`, the `source`/`baseline`/`target` fields, existing review fields, and `export_path`/`exported_files`. It does not freeze the actual existing destinations from `scripts/forgekit-upgrade.py`: `.forgekit/reports/upgrade-review-needed.md`, `.forgekit/reports/upgrade-review-needed.json`, and `.forgekit/reports/review-needed/`. It also does not say whether the new rollback artifact must remain under that export root. The recheck contract explicitly requires the current output location to be named; without it, stage A still has to choose storage/compatibility behavior. M-02 therefore remains OPEN.

### M-03 Closure

The unique paths are `scripts/test-skill-behavior.py`, `tests/skill-behavior/cases.json`, `scripts/skill_behavior_adapters/codex.py`, and `scripts/skill_behavior_adapters/claude.py`. Case fields and authorization modes are complete. Adapters are limited to client invocation and record capture. Each case uses a copied isolated fixture, pre/post tree hashes, changed-path enforcement, non-execution of external actions, cleanup on normal/abnormal exit, and evidence outside the fixture. Run records contain the required environment, client/model, prompt, fixture, sanitized command, output, trace, file-change, grader, failure-class, and independent-review evidence without secrets. Failure classes and automatic/manual blocker boundaries match DECISION-03. M-03 is CLOSED.

### M-04 Remaining Major

The matrix contains exactly 26 unique `rule_id` values and correctly assigns single concrete owners for risk, review convergence, archive, checkpoint, document ownership, maker-checker, worktree, release, initialization state/orchestration, projection, upgrade, version, and source-task rules. In particular, review convergence is owned by root `skills/code-review/SKILL.md`; `.agents` is a projection, entry files route, and validators enforce deterministic consistency.

However, `ENTRY-BOUNDARY`, `ENTRY-EVIDENCE`, `ENTRY-AUDIT`, `ENTRY-AUTH`, `ENTRY-EXTERNAL`, and `WRITEBACK-BASE` use `AGENTS/CLAUDE shared-entry contract` as their normative owner while explicitly defining that contract across two platform entry files. This is the prohibited “multiple files jointly normative” form, not one concrete owner with the other entry as an application site. `SKILL-ROUTING` and `CLAUDE-ADAPTER` likewise use “corresponding ... file” as parameterized sets of owners within one rule row. Stage A still must decide whether to split those rules or establish one normative source. M-04 therefore remains OPEN.

### Acceptance Recheck

- A04: OPEN. The ID and single-owner assertion are present, but the underlying matrix still contains multi-file/parameterized owners.
- A07: OPEN. Baseline identity, four classifications, packet content, REVIEW-NEEDED, rollback byte identity, and fixtures are present; the required existing output-location contract is not frozen.
- A21: CLOSED. It does not require a UI display name; source observability is explicitly the loaded path, Skill name, and client observation in diagnostics/run records.
- Model-behavior acceptance revisions: CLOSED at design-contract level. They consistently reference the Python runner, adapters, isolated fixtures, unified run record, failure taxonomy, and independent checker boundary. Actual behavior remains correctly marked `NEEDS_TEST` for implementation stages.

### Current Findings

- New BLOCKER: 0.
- Remaining MAJOR: 2 (`M-02`, `M-04`).
- New NOTE: 0.
- Prior N-01 and N-03 remain non-blocking future implementation guidance; prior N-02 is closed by the revised A21 wording.

### Stage Decision

Stage A is not authorized. Artifact status remains `design-revised-awaiting-blocker-recheck`.

Minimum remaining design changes:

1. Name and preserve the existing review report/export locations, including the location contract for rollback artifacts.
2. Replace multi-file/parameterized normative owners with one concrete owner per atomic rule; list the other entry/adapter/Skill files only as application sites, or split the row where separate semantic owners are intentional.

## Second Blocker Recheck

RecheckedOn: 2026-07-20
ReviewMode: second-directed-blocker-recheck
ReviewType: independent
ReviewedRange: M-02, M-04, A04, and A07 only; five revised maker artifacts, prior review history, current upgrade review/export implementation, and repository path existence
PriorReviewIntegrity: verified before append; review SHA-256 `F1BC7E46C0D7C84348A0F7F5E261CEA36AE624D51DF3EC00690983A096C228F3`
RecheckDecision: PASS
ArtifactStatus: design-approved-for-stage-a

### Second Recheck Status

| Finding | Status | Result |
| --- | --- | --- |
| M-02 | CLOSED | The existing three review/export locations, deterministic packet identity and tree, in-packet rollback, four classifications, summary references, and compatibility boundary are uniquely frozen. |
| M-04 | CLOSED | The matrix has 41 unique atomic rule IDs and one concrete normative owner per row; only the two explicitly frozen stage A paths do not yet exist. |
| A04 | CLOSED | Acceptance explicitly checks owner uniqueness, concrete-path format, the two-future-path allowlist, shared-entry ownership, concrete Claude Skill paths, and application-site separation. |
| A07 | CLOSED | Acceptance observably checks all three fixed outputs, packet ID/tree, in-packet rollback, both indexes, four classifications, original bytes/checksums, non-overwrite behavior, missing-file semantics, forbidden top-level roots, and the single-command upgrade experience. |

### M-02 and A07 Closure

- Review/export remains a compatible extension of `scripts/forgekit-upgrade.py`: `.forgekit/reports/upgrade-review-needed.md` is the user-facing index, `.forgekit/reports/upgrade-review-needed.json` is the machine index, and `.forgekit/reports/review-needed/` is the sole packet root. No parallel review, merge, backup, or rollback top-level system is permitted.
- Packet ID is fixed as `<target-version>--<managed-path-sha256-prefix>`, using the UTF-8 SHA-256 of the safe, normalized POSIX managed relative path and the first 16 lowercase hexadecimal characters. Absolute paths, empty/`.`/`..` segments, escapes, and unsafe filename characters are rejected.
- Each packet has the fixed `packet.json`, `local/<managed-relative-path>`, `incoming/<managed-relative-path>`, `rollback/<managed-relative-path>`, and `diff.patch` structure. Artifact references in the JSON summary are relative to `.forgekit/reports/`; machine absolute paths are forbidden.
- Rollback stays in the same packet and preserves pre-write original bytes with a verified SHA-256. Stock must prepare and verify it before overwrite. Custom and unknown-baseline produce REVIEW-NEEDED packets without overwrite. Missing follows migration policy and does not fabricate local or rollback bytes; restoration may be recorded as deletion of an upgrade-created file.
- The source-version/managed-path/baseline-checksum identity, Markdown/JSON indexing, unresolved resolution status, user action, and single-command check/plan/apply experience are fixed. Stage A does not need to choose storage, packet identity, classification behavior, or index semantics.

### M-04 and A04 Closure

- `project-template/governance/agent-entry-contract.md` is the single frozen future owner for ENTRY-BOUNDARY, ENTRY-EVIDENCE, ENTRY-AUDIT, ENTRY-AUTH, ENTRY-EXTERNAL, WRITEBACK-BASE, and SKILL-ROUTING under their named headings. It is not created in this design recheck. `project-template/AGENTS.md` and shared portions of `project-template/CLAUDE.md` are application sites only; stage B performs the entry-text migration.
- The matrix contains exactly 41 unique rule IDs. Every `normative_owner` is one repository-relative file path, optionally with one heading anchor; no owner is a directory, wildcard, placeholder, natural-language role, parameterized expression, or multi-file combination.
- The only non-existent owner paths are the two already frozen for stage A: `project-template/governance/agent-entry-contract.md` and `config/skill-projections.json`. All nine root Skill trigger owners and all six Claude Skill owners resolve to existing concrete `SKILL.md` files. `CLAUDE-ENTRY-ADAPTER` is owned only by `project-template/CLAUDE.md` and is limited to Claude-specific entry adaptation.
- REVIEW-CONVERGENCE remains owned by root `skills/code-review/SKILL.md`; `.agents` is only its projection, entry files only route, and validators only enforce deterministic consistency. Existing risk, archive, checkpoint, document ownership, maker-checker, worktree, release, initialization, upgrade, version, and source-task domains remain represented.

### Current Findings

- BLOCKER: 0.
- MAJOR: 0.
- NOTE: 0.

### Stage Decision

M-02, M-04, A04, and A07 are CLOSED. Stage A is authorized to begin under the approved design.

`design-approved-for-stage-a` is a design approval state only. Stage A has not been implemented, A01-A22 have not all been executed or passed, and v0.45.0 has not passed release acceptance or been released.

## Stage A Independent Review

ReviewedOn: 2026-07-20
ReviewType: independent
ReviewerAgent: Codex independent checker (`/root`)
ReviewDecision: FAIL
ArtifactStatus: stage-a-implemented-awaiting-independent-check
StageAApproved: no
StageBAuthorized: no

### Baseline and Scope

- Branch / design HEAD: `main` / `077fcfae3fd9ae3ff9ddebd5e17601a2e1b4a8db`.
- Version remains `0.44.1`.
- Reviewed the full tracked diff and every untracked Stage-A file, not only maker summaries or test output.
- Read all six design artifacts, both blocker-rechecks, task--acceptance mapping, 41 ownership rows, A01--A22, and final M-02/M-04 contract.
- `usage.html` remained the pre-existing out-of-scope deletion; only the disposable smoke copy materialized it from HEAD.
- No AGENTS/CLAUDE slimming, Skill body/name/display-name change, prompt migration, release migration, version update, or Stage B--E implementation was found.

### Change Range and Stage-A Mapping

| Task | Actual files | Result |
| --- | --- | --- |
| SA-01 | entry contract, risk governance, ownership validator/test | Required foundation; no later-stage entry or Skill change |
| SA-02 | projection manifest, sync tool/tests | Apply preflight and manifest-authority findings remain |
| SA-03 | root/template packet helper/upgrader, tests, template manifest | Rollback/atomicity/path findings remain |
| SA-04 | behavior runner, adapters, cases/fixture/tests | Skeleton only; deterministic safety gaps remain |
| SA-05 | plugin/template/release/smoke gates and tests | Normal gates pass but miss required failure paths |
| SA-06 | `tasks.md`, `verification.md`, `ship.md` | Honest boundary; no release-ready or Stage-B claim |

Template manifest changes are limited to the two generated-project files and changed template checksums; template/schema version stays `0.44.1` / `1`. Root-only config, maintenance scripts, and tests were not added.

### Commands Re-run

- Baseline Git commands, full diff/content reads, and root/template SHA-256 comparisons.
- Projection check: PASS, 18 files. Ownership validator: PASS, 41 rules.
- Behavior `validate`, `list`, and `dry-run --temp-root D:\tmp`: PASS; 3 dry-run records were honestly `GRADER_UNCERTAIN`, no real client invocation.
- Unit tests: PASS, 27/27.
- Plugin validation, template validation, and manifest check: PASS.
- Release consistency: PASS; marketplace plus 18 manifest-derived mutations restored byte-for-byte; independent before/after SHA-256 change count was zero.
- Full isolated smoke: PASS. It included tracked and untracked Stage-A files, materialized only its own HEAD `usage.html`, and was removed in `finally`.
- Adapter probes: Codex `0.144.6`, Claude Code `2.1.210`; no real prompt/model behavior was run.

### Independent Mutation Summary

| Check | Expected | Actual |
| --- | --- | --- |
| target `SKILL.md` and YAML drift | nonzero | both nonzero |
| manifest target escape / managed `..` | reject before copy | both rejected |
| `.claude` mutation | projection PASS | PASS |
| duplicate rule / wildcard owner | reject | both rejected with diagnostics |
| packet escape/absolute/drive/backslash | reject | all rejected |
| read-only adapter creates empty directory | `UNAUTHORIZED_WRITE` | `GRADER_UNCERTAIN`, no changed path |
| seven failure classes | exact classes | all direct classifier checks matched |
| target parent is regular file | fail before copy | failed after first target changed |
| two stock migrations, same path | keep upgrade-start rollback | rollback became intermediate bytes; two items shared one packet ID |
| fail second packet at `packet.json` | keep consistency or invalidate | old JSON remained, artifacts changed, checksum mismatch |
| root packet helper drift | gate failure | template/plugin/manifest gates all passed |
| `..`, `CON`, trailing-dot/space paths | reject/normalize safely | accepted |
| token/API-key/password/bearer/home | redact | password/bearer only; other fixed forms remained |

All mutations ran only in disposable `D:\tmp` fixtures/copies and were removed.

### BLOCKER

#### B-01: repeated stock writes destroy the upgrade-start rollback

`prepare_safe_write_packet` uses the final target version, while packet ID is only target version plus managed path. Two pending migrations that update one managed path reuse one packet directory. The second packet overwrites `rollback/<managed-path>` with intermediate bytes. Independent reproduction completed successfully but proved the final rollback was not the upgrade-start original.

This violates A07/M-02 and can restore the wrong version. Evidence: `scripts/forgekit-upgrade.py:926-999`, `scripts/upgrade_review_packets.py:40-44`, `scripts/upgrade_review_packets.py:108-167`. `TODO_REVIEW`: preserve and test a durable upgrade-start rollback across repeated same-path writes without silently changing the frozen packet contract.

#### B-02: adapters are not isolated from user configuration or fixture-external reads

Codex uses `workspace-write` but omits available `--ignore-user-config`; Claude uses `acceptEdits` but omits available setting-source and strict-MCP isolation. Both inherit host environment/user config. Neither enforces a fixture read boundary. User hooks/plugins/MCP wiring can run outside the authorization oracle, and external reads can enter records.

This creates unapproved external-action/data-leak capability when `run` is used. Evidence: `scripts/skill_behavior_adapters/codex.py:35-47`, `scripts/skill_behavior_adapters/claude.py:34-45`, and current client help. `TODO_REVIEW`: establish a tested configuration/tool/read boundary before any real behavior run.

### MAJOR

1. Projection apply partially writes on a preflight-detectable parent-file conflict. Evidence: `scripts/sync-skill-projections.py:189-203`.
2. Packet publication is not atomic/invalidation-safe. A metadata-write failure can leave old completed JSON pointing at new mismatched artifacts. Evidence: `scripts/upgrade_review_packets.py:119-171`.
3. Windows policy accepts target version `..`, device names such as `CON`, reserved segments, and trailing dot/space forms without a cross-platform reject/normalize contract.
4. Root/template packet helpers have no drift gate. A root-only mutation passed template, plugin, and manifest checks; only `forgekit-upgrade.py` is compared at `scripts/validate-template.ps1:1148-1152`.
5. The behavior oracle records only regular files; empty-directory changes are invisible. Cleanup uses unverified `rmtree(..., ignore_errors=True)`. Evidence: `scripts/test-skill-behavior.py:179-186,390`.
6. Redaction misses `--token value`, space-form API keys, and home paths. Evidence: `scripts/test-skill-behavior.py:56-60,203-218`.
7. `run` always exits 0 regardless of `UNAUTHORIZED_WRITE`, deterministic behavior failure, or adapter failure. Evidence: `scripts/test-skill-behavior.py:420-438`.
8. Adapters always return no model, tool trace, or loaded Skill identity; Claude's allowlist also lacks a Skill-routing tool. Required routing/source evidence cannot be produced.
9. `EXPECTED_SKILLS` duplicates the formal nine-Skill list, making the sync script a second machine authority. Evidence: `scripts/sync-skill-projections.py:21-31,165-166`.
10. The 27-test suite misses same-path migration chains, whole-chain rollback, packet failure/retry, Windows reserved paths, helper drift, directory-only mutations, complete redaction, and CLI exit semantics.

### NOTE

1. Extreme I/O interruption during projection apply has no transaction rollback; after normal preflight errors are fixed, a detectable/repeatable failure may remain documented.
2. Reparse validation retains a local TOCTOU window; reasonable for a local maintainer tool if non-racy checks are complete.
3. Review JSON changed to schema 2 and removed absolute `project_root`. Repository consumers do not rely on it and the bump is explicit; external consumers still need release migration documentation.

### Component Conclusions

- `agent-entry-contract.md`: PASS. Seven frozen anchors exist once; only always-on shared rules are present; AGENTS/CLAUDE remain unchanged as Stage A requires.
- `ai-engineering-loop.md`: PASS. It only lands the impact risk owner, keeps low risk light, and does not implement Stage B/C/D.
- Manifest/check: strict roots/entries/files and `.claude` exclusion work; duplicated nine-name authority and apply partial-write path fail.
- Upgrade: one-step stock/custom/missing/unknown, raw bytes, relative paths, fixed roots, and root/template upgrader equality work; repeated rollback, packet atomicity/retry, Windows safety, and helper mirror gate fail.
- Behavior/adapters: schema, fixture copying, file allowlist, seven labels, basic cleanup, and probes work; directory oracle, redaction, exit status, invocation isolation, and evidence capture fail.
- Rule ownership validator: PASS. It rejected duplicate IDs/wildcards, verified paths/anchors, rejected `.agents` owners, and preserved REVIEW-CONVERGENCE. Parser edits fail closed.
- Unit tests: 27/27 PASS with the critical gaps above. Isolated smoke: PASS and cleaned.

### Stage-A Deterministic Acceptance

| Acceptance | Status | Reason |
| --- | --- | --- |
| A04 | PASS | 41 owners, anchors/application sites, routes, REVIEW-CONVERGENCE validated |
| A05 | FAIL | preflight-detectable partial write; duplicated nine-name authority |
| A06 | PASS | `.claude` ignored; tested escape/reparse targets rejected |
| A07 | FAIL | rollback overwrite; non-atomic retry; incomplete Windows safety |
| A11 deterministic | PASS | impact risk owner landed without count scoring or low-risk regression |
| A18 deterministic | PASS | version/template/schema remain separate; mutations restored exact bytes |

SA-01 and SA-06 pass. SA-02, SA-03, and SA-04 fail. SA-05 is partial because normal gates pass while required independent mutations expose uncaught defects.

### Stage Decision

Stage A does not pass. Status remains `stage-a-implemented-awaiting-independent-check`. Stage B is not authorized.

The repository is still `0.44.1`; the real A01--A03/A08--A16/A19--A22 behavior matrix has not run; v0.45.0 release acceptance has not passed; and this checker did not commit, push, tag, release, modify maker implementation, enter Stage B, or repair findings.

## Stage A Findings Recheck

ReviewedOn: 2026-07-20
ReviewType: independent findings recheck
ReviewerAgent: Codex independent checker (`/root`)
ReviewDecision: FAIL
ArtifactStatus: stage-a-implemented-awaiting-independent-check
StageAApproved: no
StageBAuthorized: no

### Recheck Baseline and Scope

- Branch / design HEAD: `main` / `077fcfae3fd9ae3ff9ddebd5e17601a2e1b4a8db`; `VERSION` remains `0.44.1`.
- Rechecked only the two BLOCKER and ten MAJOR findings recorded in the preceding `Stage A Independent Review`, using the current implementation diff, new tests, formal gates, and independent disposable fixtures.
- Did not reopen the accepted entry contract, risk-governance scope, 41-rule matrix, A04, A11/A18 deterministic results, or the Stage A versus B--E boundary.
- `usage.html` remained the user's pre-existing out-of-scope deletion. No implementation file was changed by this checker.

### Finding Status

| Prior finding | Status | Recheck evidence |
| --- | --- | --- |
| B-01 repeated same-path migrations destroy upgrade-start rollback | CLOSED | The upgrader snapshots each managed path once before the migration chain. An independent two-migration apply produced final bytes `FINAL`, retained rollback bytes `ORIGIN` from source version `0.43.2`, and restoring the rollback returned the file to the upgrade start. A conflicting existing packet identity failed closed without changing the packet. |
| B-02 adapters inherit user configuration and lack fixture/external-action isolation | CLOSED | Runner context uses disposable HOME/USERPROFILE/XDG/CODEX/CLAUDE roots plus an environment allowlist. Both adapters use argument arrays and fixture cwd. Fake clients observed the isolated roots, literal prompt, excluded host secrets, and structured evidence. When fixture-only read/network denial cannot be proved, both adapters stop before launching the prompt and return environment unavailable. No real model prompt was run. |
| M-01 projection apply can partially write on a preflightable conflict | CLOSED | The complete plan is preflighted before the first write. An independent later parent-file conflict returned `ProjectionError`; every previously existing target remained byte-identical and an earlier drift sentinel was untouched. |
| M-02 packet publication is not atomic/invalidation-safe | OPEN | Normal staging faults and an injected summary failure now restore the old packet plus both summaries and leave no `.tmp-*`/`.old-*`. However, an independent failure while deleting the old packet after the new packet and summary were published caused the helper to restore the old `custom` packet while leaving the new `stock` summary. It returned `PacketError` with no staging sibling, but the valid packet and valid summary disagreed. |
| M-03 Windows/target-version path policy is incomplete | CLOSED | Strict semantic-version validation rejects `.`, `..`, injection, and non-semver versions. Managed paths reject traversal, drive/UNC/device forms, reserved devices, invalid characters, and trailing dot/space; legal Unicode paths remain deterministic. Independent `..` and `CON` checks rejected and a Unicode path succeeded. |
| M-04 root/template packet helper drift is ungated | CLOSED | Root/template packet helpers and upgraders are byte-identical. Formal release consistency detected/restored helper drift. An independent isolated root-helper mutation changed template validation from exit 0 to exit 1 with an explicit mirror SHA-256 diagnostic. |
| M-05 behavior oracle misses directories and cleanup is unverified | CLOSED | Snapshots contain files, directories, and types. An independent read-only empty-directory addition became `UNAUTHORIZED_WRITE`; a no-op cleanup became `ADAPTER_ERROR` because the run root still existed. Normal and exceptional cleanup tests pass. |
| M-06 redaction misses fixed token/API-key/home forms | OPEN | `--token value`, space/equal API keys, Bearer values, password-like text, command arrays, and home/run paths are redacted across prompt/stdout/stderr/tool trace/command. But an independent adapter diagnostic containing `environment: {OPENAI_API_KEY: env-583}` persisted the secret value verbatim; sensitive dictionary keys are passed through recursion but not value-redacted. |
| M-07 `run` always exits zero for non-PASS results | CLOSED | `run` maps all seven failure classes to stable CLI codes. Independent CLI runs returned 23 with an `UNAUTHORIZED_WRITE` record and 0 with a `PASS` record; the 42-test suite checks every class. |
| M-08 adapters cannot provide honest model/tool/Skill evidence | CLOSED | Records now contain capability flags and per-capability unavailable reasons; structured adapters expose model/tool trace/Skill source only when observed. Missing Skill-source evidence independently classified as `GRADER_UNCERTAIN`, never PASS. |
| M-09 `EXPECTED_SKILLS` is a second nine-Skill machine authority | CLOSED | `EXPECTED_SKILLS` and equivalent named nine-item lists are absent. The manifest is the only projection list; ownership validation derives the route set from the approved matrix instead of copying names into the sync/release scripts. |
| M-10 critical failure paths lack real tests | OPEN | The suite expanded from 27 to 42 passing tests and covers the principal rollback, projection, packet, Windows, helper, directory, cleanup, exit, evidence, and adapter paths. It does not cover the still-failing old-packet cleanup/summary rollback sequence or sensitive values in a nested environment/authentication mapping, so this original coverage finding is not fully closed. |

Result: both prior BLOCKER findings are CLOSED. Seven prior MAJOR findings are CLOSED; M-02, M-06, and M-10 remain OPEN. No new product BLOCKER was found.

### Formal Gates Re-run

- `python -B scripts/sync-skill-projections.py check`: PASS, all 18 declared files byte-identical with source/target SHA-256 output.
- `python -B scripts/validate-rule-ownership.py`: PASS, 41 unique owners. This was only a gate rerun; the accepted matrix finding was not reopened.
- Behavior `validate`: PASS, 3 cases; `list`: PASS, 3 cases; `dry-run`: PASS, 3 non-invoking records with verified cleanup. No real model prompt was executed.
- `python -B -m unittest discover -s tests -p "test_*.py"`: PASS, 42/42.
- Plugin validation, template validation, template-manifest check, and `git diff --check`: PASS.
- Release consistency: PASS. Marketplace, shared-helper, and all 18 manifest-derived projection mutations failed as expected and restored the checked baseline.
- Full smoke in a complete disposable copy: PASS. The copy included tracked and untracked Stage-A files, materialized `usage.html` from HEAD only inside the copy, and removed the copy in `finally`.

The first sandboxed unit-test attempts were invalid because Python could not write the sandbox's TEMP roots; the authoritative 42-test result was rerun with host temporary-directory access. Known fixture directories from those invalid attempts were removed. Three associated host Python processes continued recreating TEMP fixtures; terminating host processes was not authorized by the repository-scoped review, so host-TEMP residue is reported below rather than silently ignored. The repository worktree itself has no cache, evidence, mutation, packet, smoke-copy, or temporary-directory residue.

### Independent Checks

| Check | Expected | Actual |
| --- | --- | --- |
| two migrations, same managed path | rollback is upgrade-start bytes and restores start | PASS: `ORIGIN` survived `MIDDLE`/`FINAL` and restored exactly |
| existing packet identity conflict | fail closed without overwrite | PASS: checksum identity conflict; packet tree unchanged |
| projection later parent conflict | reject before any copy | PASS: nonzero exception; all existing targets unchanged |
| packet summary publish failure | old packet/summaries restored; no staging | PASS |
| old-packet cleanup failure after summary publish | packet and summaries remain mutually consistent | FAIL: packet restored to `custom`, summary remained `stock` |
| target version `..` | reject | PASS |
| Windows `CON` managed component | reject | PASS |
| legal Unicode managed path | deterministic safe ID | PASS |
| helper drift | formal gate nonzero | PASS: exit 1 with both mirror hashes |
| read-only empty-directory addition | `UNAUTHORIZED_WRITE` | PASS |
| cleanup leaves run root | non-PASS with cleanup reason | PASS: `ADAPTER_ERROR` |
| `--token value`, API key, Bearer, home across record channels | secret values absent | PARTIAL: fixed text/command/path forms passed; nested `OPENAI_API_KEY` value leaked |
| non-PASS and PASS CLI exits | stable nonzero / zero matching record | PASS: 23 / 0 |
| adapter isolation unavailable | stop before prompt | PASS for Codex and Claude fake probes |
| fake client isolated invocation | fixture cwd, isolated roots, allowlisted env, literal prompt | PASS for Codex and Claude |
| missing Skill source evidence | cannot PASS | PASS: `GRADER_UNCERTAIN` |

All independent filesystem mutations ran in disposable copies or fixtures, not in the real repository. No real model behavior matrix was run.

### BLOCKER

None open. Both prior BLOCKER findings are closed.

### MAJOR

1. M-02 remains open: a post-summary old-packet cleanup failure rolls the packet back without rolling the summary back, leaving two individually valid but mutually inconsistent published artifacts.
2. M-06 remains open: fixed authentication values in a nested environment/authentication mapping can be persisted unredacted in the run record.
3. M-10 remains open: there are no real regression tests for the two still-failing paths above.

### NOTE

1. The recheck created no repository residue, but three Python processes from invalid sandbox-only test attempts continued recreating ForgeKit fixture directories in the host TEMP directory. Known directories were cleaned twice; host-process termination requires separate user authority and was not performed.
2. The previously accepted projection I/O-interruption and local reparse TOCTOU notes remain notes; this findings-only recheck did not reopen them.

### Stage Decision

Stage A does not pass because three prior MAJOR findings remain open. Status remains `stage-a-implemented-awaiting-independent-check`. Stage B is not authorized.

The repository has not been updated to v0.45.0; the real model behavior matrix has not run; v0.45.0 is not release-ready. This checker did not commit, push, tag, release, modify maker implementation, or enter Stage B.

## Stage A Final Findings Recheck

ReviewedOn: 2026-07-20
ReviewType: final independent findings recheck
ReviewerAgent: Codex independent checker (`/root`)
ReviewDecision: PASS WITH NOTES
ArtifactStatus: stage-a-approved-for-stage-b
StageAApproved: yes
StageBAuthorized: yes

### Scope and Baseline

- Rechecked only M-02, M-06, and M-10 from the preceding findings recheck. Previously closed B-01, B-02, M-01, M-03, M-04, M-05, M-07, M-08, and M-09 were not reopened.
- Baseline remained branch `main`, design HEAD `077fcfae3fd9ae3ff9ddebd5e17601a2e1b4a8db`, and `VERSION` `0.44.1`.
- The worktree remained limited to Stage-A implementation, prior/current checker review writeback, and the user's pre-existing deleted `usage.html`; no Stage B, Skill/body, prompt-migration, release-migration, or version-metadata work was found.

### Final Finding Status

| Finding | Status | Independent result |
| --- | --- | --- |
| M-02 post-commit `.old-*` cleanup failure | CLOSED | The commit point now follows canonical packet publication, artifact verification, both summary publications/readbacks, and packet/summary cross-validation. Independent cleanup denial returned success with the new `stock` canonical, JSON, and Markdown mutually consistent across packet ID, managed path, source/target versions, classification, incoming/rollback checksums, and artifact paths. The old `custom` packet remained only under a non-canonical `.old-*` name, emitted an observable cleanup warning, was ignored by canonical enumeration, was not referenced by summaries, and was safely removed by a retry. A separate pre-commit summary fault restored the exact prior canonical and both summaries with no staging sibling. |
| M-06 final recursive record sanitization | CLOSED | A single final recursive sanitizer now runs before evidence persistence and CLI JSON output, handling dictionaries, lists, tuples, commands, text, sensitive keys, and path placeholders. Independent values covering nested `adapter_diagnostics.environment.OPENAI_API_KEY`, vendor/camel/hyphen/space key forms, nested objects, command tokens, Bearer stdout, API-key stderr, tool trace, grader/exception diagnostics, and the real home path were absent from the final JSON, returned record, actual evidence file, CLI stdout, and serialization-error output. Ordinary values remained intact. |
| M-10 missing real regression tests | CLOSED | The packet test injects `.old-*` deletion failure and verifies new canonical/JSON/Markdown consistency, warning, stale-old exclusion, retry cleanup, no new top-level roots, and preserved pre-commit rollback behavior. The redaction test scans independent secrets through deep structures and an actual evidence file. Both focused tests passed, and the complete suite passed 44/44. |

No new BLOCKER or MAJOR was introduced by these fixes.

### Independent Fault Injection

- Post-commit cleanup denial: `prepare_packet` returned normally; canonical classification stayed `stock`; JSON and Markdown stayed `stock`; all eight cross-checked identity/checksum/artifact groups matched; one non-canonical old `custom` directory and one cleanup warning remained; no `.tmp-*` or extra rollback/backup/review/merge root appeared.
- Retry after cleanup denial: stale `.old-*` was removed, the canonical packet remained `stock`, and no `.old-*`/`.tmp-*` sibling remained.
- Pre-commit summary failure after JSON publication: operation returned `PacketError`; prior canonical packet, JSON summary, and Markdown summary were restored byte-for-byte; no staging sibling remained.
- Canonical enumeration: accepted only the complete fixed packet ID directory; ignored `.old-*`, `.tmp-*`, and an incomplete canonical-looking directory.
- Nested sanitization: all independently generated `vault-final-*` values were absent from final serializer output, actual record/evidence, CLI stdout, and error output. `<REDACTED>` and stable home placeholders were present; normal strings/numbers/booleans survived.

### Tests and Gates

- `python -B -m unittest discover -s tests -p "test_*.py"`: PASS, 44/44.
- Focused packet cleanup-failure test: PASS, 1/1.
- Focused recursive sanitizer/evidence test: PASS, 1/1.
- Projection check: PASS, 18 declared files.
- Rule ownership validator: PASS, 41 rules. This was regression confirmation only; the closed ownership finding was not reopened.
- Behavior `validate`, `list`, and non-invoking `dry-run`: PASS, 3 cases; dry-run cleanup passed.
- Plugin validation, template validation, template-manifest check, release-consistency mutation gate, and `git diff --check`: PASS.
- Full smoke in a disposable copy containing all tracked and untracked Stage-A files: PASS. Only the copy materialized HEAD `usage.html`; the copy and its archive were removed.
- Regression gates showed no regression in the two closed BLOCKER findings or the other closed MAJOR findings. No real Codex or Claude prompt was executed.

### BLOCKER

None.

### MAJOR

None.

### NOTE

1. The three previously reported external host-TEMP fixtures (`forgekit-behavior-tests-17tiznwt`, `forgekit-behavior-tests-30acgwpo`, and `forgekit-behavior-tests-chwxq72x`) still exist and remain environment noise. They were not created, modified, or removed by this recheck and do not affect the decision.
2. Every temporary directory created by this recheck was removed. The repository contains no checker mutation, evidence, packet, smoke-copy, cache, or temporary residue.
3. Approval here is Stage-A approval only. It does not represent completion of the real model behavior matrix or v0.45.0 release acceptance.

### Stage Decision

M-02, M-06, and M-10 are CLOSED. Stage A passes with notes. Status is `stage-a-approved-for-stage-b`; Stage B may begin, but this checker did not enter or implement Stage B.

`VERSION` remains correctly at `0.44.1`. This is an in-development v0.45.0 stage result; the real model behavior matrix has not run, v0.45.0 release preparation has not begun, and v0.45.0 is not release-ready. This checker did not commit, push, tag, or release.

## Stage B Independent Review

ReviewedOn: 2026-07-20
ReviewType: independent
ReviewerAgent: Codex independent checker (/root)
BaselineCommit: 506cecf8d377a17a2616bf3b9eeea483ee4039a4
ReviewDecision: FAIL
ArtifactStatus: stage-b-implemented-awaiting-independent-check
StageBApproved: no
StageCAuthorized: no

### Baseline, scope, and task mapping

- Branch main; HEAD and Stage-A baseline commit 506cecf; VERSION remains 0.44.1.
- Read all six change artifacts, the Stage-B task--acceptance mapping, all 41 ownership rows, the seven always-on anchors, Stage-A final approval, A01--A22 Stage-B portions, every tracked diff, and every untracked file.
- SB-01: project-template/AGENTS.md, project-template/CLAUDE.md, template manifest, and generated-project harness. These are necessary entry/runtime-routing changes and do not change Skill bodies.
- SB-02: root/template forgekit-upgrade.py and change-local stage-b-migration-draft. These are necessary safe root-entry and development fixture changes.
- SB-03: both validators/tests, behavior cases/fixture, run-harness-check, validate-template, release-consistency, and smoke. These are necessary deterministic gates; two gate-coverage MAJOR findings remain.
- SB-04: tasks.md, verification.md, and ship.md. These are necessary maker status/evidence writeback and do not change user runtime.
- Root AGENTS.md, nine shared Skills, six Claude Skills, metadata, prompts, README, formal migrations, and release/version metadata are unchanged. The user's D usage.html stayed deleted and was materialized only inside the smoke copy.

### Entry size and conditional-flow result

| Entry | Before | After | H1/H2 | Conditional categories | Skill/governance path references total/unique |
| --- | --- | --- | --- | --- | --- |
| AGENTS | 181 lines / 25,003 bytes | 36 lines / 4,831 bytes | 1/5 -> 1/3 | 8 -> 0 | 16/9 -> 11/3 |
| CLAUDE | 166 lines / 23,279 bytes | 37 lines / 5,027 bytes | 1/4 -> 1/3 | 7 -> 0 | 14/8 -> 11/3 |

Maker size claims are exact. Full archive, checkpoint, worktree, loop, maker-checker, review-convergence, large-change, release, backfill, handover, project-init, security, first-principles, and old-prompt protocols are no longer always-on. Short routes remain. No fixed file/module/question/eight-section threshold, universal independent review, repeated bounded-write confirmation, audit auto-fix, universal artifact chain, or fabricated-fact writeback remains in either entry.

### Seven always-on contracts and platform comparison

Project/write boundary, evidence/no fabrication, audit default, bounded local authorization, external/irreversible actions, minimum evidence-based writeback, and Skill routing each have a readable entry summary plus the correct agent-entry-contract anchor. AGENTS and CLAUDE are semantically equivalent for all seven. Both preserve read-only audit, do not repeat an already granted bounded local authorization, protect release/push/deploy/destructive actions, and do not treat routing as authorization.

All nine portable Skills are discoverable from both intent tables. Claude-only project-workflow, request/reviewer, maintenance, first-principles, and adversarial routes resolve to real repository paths. The metadata/agent-wiring/permission-mode statement limits these to invocation mechanics and does not create a Claude authorization policy.

### Counterfactual cases

1. Skill-not-triggered read-only diagnosis: PASS; read-only, evidence, no auto-fix, and no fabrication follow directly.
2. Authorized low-risk local fix: PASS; bounded reversible edits and proportionate validation proceed without repeated confirmation or forced full planning/checker.
3. Insufficiently specific “release it too”: PASS; release remains a specifically authorized external action.
4. Single-file auth/permission/migration/public API: PASS; objective impact, not count, controls risk.
5. Eighteen deterministic projection files: PASS; count alone does not force heavy flow.
6. Adjacent project: PASS; the project/task boundary forbids automatic inclusion.
7. Document writeback: PASS; only minimum confirmed facts go to the owning document, never business facts into governance.

### Authority, migration identity, and actual behavior

- The seven ENTRY/WRITEBACK/SKILL-ROUTING rules remain owned by project-template/governance/agent-entry-contract.md. AGENTS/CLAUDE are application sites. ai-engineering-loop.md does not re-own ENTRY rules. REVIEW-CONVERGENCE remains mapped to skills/code-review/SKILL.md; Stage B did not modify it.
- The draft is change-local and marked development-fixture-only / fixture-only-not-released. Default production discovery scans only formal migrations/*/migration.json. Independent production check reported latest/planned 0.44.1 and zero pending migrations.
- Baseline AGENTS/CLAUDE are byte-identical to commit 506cecf with SHA-256 e3fb...5374 and dacb...a969. Incoming files are byte-identical to current template entries with SHA-256 7812...7b1 and b987...503.
- Descriptor actions are the existing safe replace_file_if_baseline_matches type and target only AGENTS.md/CLAUDE.md. Root/template upgraders are byte-identical; the only product change is the exact SAFE_ROOT_FILES allowlist for those two names.
- Independent real fixtures passed stock, custom, unknown-baseline, missing, and mixed AGENTS-stock/CLAUDE-custom. Custom/unknown were preserved. Missing created no fake local/rollback bytes. Mixed rollback matched upgrade-start bytes. AGENTS and CLAUDE packet IDs were distinct and stable; both appeared in one summary; JSON artifact paths were relative with no machine root.

### Independent mutations

Twenty-seven assertions ran only in D:\tmp\fb-b-review and were restored before the copy was deleted.

- Missing AGENTS/CLAUDE anchors, copied blocker-recheck protocol, old 5-files/2-modules threshold, one-byte baseline drift, formal migrations/0.45.0, and behavior-fixture drift all failed as expected.
- Custom AGENTS, custom CLAUDE, mixed stock/custom, unknown, missing, rollback, stable/distinct packet IDs, relative summary, and production discovery behaved correctly.
- Two negative entry mutations incorrectly passed: retaining markers while adding “audits may edit automatically,” and deleting the individual project-bootstrap-fill route.
- Two negative migration mutations incorrectly passed: changing baseline bytes together with descriptor checksum so the baseline no longer came from 506cecf, and redirecting production default discovery to the change-local draft.

### Gates and smoke

| Gate | Result |
| --- | --- |
| Stage-B validators | PASS, subject to the MAJOR coverage gaps below |
| Projection / ownership | PASS; 18 files / 41 rules |
| Behavior validate/list/dry-run | PASS; 3 GRADER_UNCERTAIN/not-run records; no real client |
| Unit tests | PASS; 56/56 using D:\tmp\fb-stageb-unittest |
| Plugin/template/manifest | PASS; template ran with -NoProfile; version 0.44.1 |
| Release-consistency mutation | PASS; all bytes restored |
| Full smoke | PASS; copy D:\tmp\fb-b-review; generated D:\tmp\frt\forgekit-smoke-d_s5aq6x\generated; entries, contract, manifest, upgrader, harness checked |
| git diff --check | PASS |

The authoritative D:\tmp runs passed and cleaned. Earlier sandbox-TEMP permission failures were invalid environment attempts, not product results. The 22 TEMP directories created by those attempts were precisely removed; earlier host TEMP noise was not changed. All checker-owned copies, generated projects, runtime packets, evidence, caches, and temporary directories are gone.

### BLOCKER

None. Actual entry safety, production isolation, custom/unknown preservation, baseline identity, and rollback behavior pass.

### MAJOR

1. scripts/validate-agent-entries.py remains a marker plus limited-regex gate. It does not validate all nine individual routes and ignores explicit contradictory prose when the markers remain. Removing project-bootstrap-fill or adding audit auto-write text both passed. tests/test_agent_entries.py lacks these negative paths.
2. scripts/validate-stage-b-entry-migration.py does not bind baseline bytes to commit 506cecf, inspect production discovery, or run stock/custom/unknown/missing/mixed/rollback behavior. A coherently changed baseline/checksum and a production-discovery redirect both passed. Current product behavior passes separate tests, but this validator and tests/test_stage_b_entry_migration.py do not meet the frozen Stage-B migration-gate scope.

### NOTE

1. Real Codex/Claude prompts, selector/Skill-source observations, and actual token/context improvement remain NEEDS_TEST; this is not the failure reason.
2. Historical Stage-A paragraphs in ship.md retain stale “not entered Stage B / awaiting Stage-A checker” wording, while its header and Stage-B handoff are current. This is a readability note only.

### Stage decision

Stage B FAIL. There are 0 BLOCKER and 2 MAJOR. Status remains stage-b-implemented-awaiting-independent-check and Stage C is not authorized.

VERSION remains 0.44.1. No real model prompt was executed; no formal v0.45.0 release migration was created or updated; v0.45.0 is not release-ready. This checker did not fix implementation, enter Stage C, commit, push, tag, or release.

## Stage B Findings Recheck

ReviewedOn: 2026-07-20
ReviewType: final directed findings recheck
ReviewerAgent: Codex independent checker (/root)
BaselineCommit: 506cecf8d377a17a2616bf3b9eeea483ee4039a4
ReviewDecision: FAIL
ArtifactStatus: stage-b-implemented-awaiting-independent-check
StageBApproved: no
StageCAuthorized: no

### Actual recheck scope

本轮严格限定为上轮两个 validator 级 finding：M-B1（入口 validator）与 M-B2（Stage-B migration validator），以及它们的定向测试、正式门禁接入、release mutations 和含 `.git` 的隔离 smoke。未重新打开已通过的入口正文、七项 always-on 合同、条件流程下沉、平台语义、规则所有权、migration 产品语义或 Stage A 基础设施。

基线为 `main` / `506cecf8d377a17a2616bf3b9eeea483ee4039a4`；`VERSION` 仍为 `0.44.1`。未发现 Stage C、Skill 或正式 `migrations/0.45.0` 变更。用户原有 `usage.html` 仍保持删除。

### M-B1: OPEN

- 通用 Skill 名称由 `config/skill-projections.json` 动态读取；validator 和测试中没有 `EXPECTED_SKILLS`、手写九项 collection 或第二份清单。测试的九项循环同样由 manifest 派生。
- AGENTS 与 CLAUDE 的九项 inline-code route 逐项删除 mutation 全部得到 exit 1，并定位 `missing manifest Skill route: <skill>`；`project-bootstrap-fill`、任意其他 route、CLAUDE 通用 route 及 Claude-only route 不能替代缺失通用 route 均符合预期。重复引用不能掩盖另一项缺失，routing parser 不依赖固定行号。
- 指定 audit 反例 `Audits may automatically modify files without a repair request.` 与短句 `audits may edit automatically` 均得到 exit 1；fenced code block 中同一反例得到 exit 0；正常只读/外部授权措辞得到 exit 0。
- 但 contradiction gate 仍未满足冻结范围中的完整 Audit 最小集合。保留全部正向 marker 时，以下明确反向声明均得到 exit 0：`Assessments may automatically modify files without a repair request.`、`Diagnosis may automatically modify files without a repair request.`、`Planning may automatically modify files without a repair request.`、`Reviews may directly fix files by default.`、`Files may be written without a repair request.`。因此 assessment/diagnosis/planning 自动写、review 默认直接修复、无 repair request 仍可写文件仍可绕过。
- 其他抽查的 bounded authorization、external authorization、evidence、boundary 与 writeback 明确反向声明均被识别。实现保持小型、数据驱动且未复制共享合同全文，但上述明确漏检使 M-B1 的关闭条件不成立。

### M-B2: CLOSED

- Validator 内置且不接受 descriptor 改写的审批锚点 `506cecf8d377a17a2616bf3b9eeea483ee4039a4`，通过 `git show <approved commit>:project-template/<entry>` 读取 Git object，而不是当前工作树。Descriptor `source_commit` 必须精确等于该完整 SHA。
- 独立重算 Git baseline：AGENTS `e3fb19418f0827681c519f9e99f5e86a2dc201c1861a2e2d7a586700a0e95374`；CLAUDE `dacb9123a43259d98e413699c5fd8ad41fdba67d09ae51ead71afa4ea0a7a969`。两份 draft baseline 与 Git bytes、descriptor checksum 均一致。
- Incoming 与当前模板逐字节一致：AGENTS `7812abe759870806ff939645ff19345c6108b71c66eacbff87ed23388b1577b1`；CLAUDE `b9873ee5cbc0b85a3d2f62851981f114b90ff9822c98367c4facdc6a53f5c503`。
- 隔离 mutation：baseline AGENTS 与 descriptor checksum 同步篡改得到 exit 1，错误同时报告 managed path、approved commit、Git/draft/descriptor SHA；`source_commit` 改为另一真实 SHA 得到 exit 1；incoming CLAUDE 与 checksum 同步篡改得到 exit 1。每项后均逐字节恢复并复跑通过。
- 实际 production `check` 未传 development migration source，返回 Current/Latest/Planned `0.44.1`、Pending `0`，无 0.45.0/draft 暴露，state、项目与 reports 不变。将默认 discovery 重定向到 change-local draft 后，实际结果暴露 Latest/Planned `0.45.0`、Pending `1`，validator 得到 exit 1；upgrader 随后逐字节恢复。
- Validator 默认真实执行 stock、custom、unknown-baseline、missing、mixed 与 same-path multi-migration behavior。分类分别正确；custom/unknown 保留，missing 无伪造 local/rollback bytes，mixed rollback 恢复升级起点，chain rollback 保留 `stage-a-origin\r\n`。所有 fixture 在正常与异常路径均清理。无 `.git` 的 archive 副本因无法读取审批 Git object 而按预期拒绝。

### Directed tests and formal gates

- `tests.test_agent_entries`: PASS，15/15。
- `tests.test_stage_b_entry_migration`: PASS，17/17。
- 定向合计：PASS，32/32。测试真实覆盖 manifest 派生 route 删除、指定 audit contradiction、fenced/safe wording、baseline+checksum、incoming+checksum、source commit、真实 discovery redirect、stock/custom/unknown/missing/mixed/rollback 与清理；但没有覆盖本次发现的五个 Audit 同义明确反例。
- 全量 unittest：PASS，76/76。
- 两个增强 validator、Skill projection、41-rule ownership、behavior validate/list/dry-run、plugin assets、template、manifest、release consistency 和 `git diff --check` 全部 PASS。Dry-run 仍为 `GRADER_UNCERTAIN/not-run`。
- Release consistency 已接入 audit contradiction、manifest-derived 单项 route 删除、baseline+checksum 同步篡改和 production discovery redirect；所有 mutation 后均验证逐字节恢复。
- `validate-template.ps1` 在 `powershell -NoProfile` 下通过，并在 `D:\tmp\复核 空格` 的空格/非 ASCII 路径副本通过。
- 完整 smoke 在含 `.git`、全部 tracked/untracked Stage-B 文件且仅在副本恢复 HEAD `usage.html` 的短路径 `D:\tmp\fbr` 中通过。记录的生成项目为 `D:\tmp\fbr-smoke-record\forgekit-smoke-k2e16kwp\generated`；AGENTS、CLAUDE 与 shared contract 存在，完整 smoke 通过后已清理。

### BLOCKER

None.

### MAJOR

1. M-B1 remains OPEN. The route-completeness half is fixed, but the contradiction gate still accepts explicit unauthorized-write reversals for assessment, diagnosis, planning, direct-by-default review repair, and generic writes without a repair request while all positive markers remain. The frozen M-B1 closure conditions therefore are not satisfied.

### NOTE

1. Real Codex/Claude prompts were not executed. Selector behavior, actual Skill source/context/token benefit, and manual-merge readability remain NEEDS_TEST and do not cause this failure.
2. Historical Stage-A wording in `ship.md` remains a non-blocking readability note; its header and current handoff are not reopened here.
3. All checker-owned mutation, runtime, smoke, path, and no-Git copies were deleted. No packet, report, evidence, cache, `.pyc`, `__pycache__`, or temporary residue remains in the real worktree.

### Stage decision

M-B1 is OPEN and M-B2 is CLOSED. Stage B findings recheck FAILS with 0 BLOCKER and 1 MAJOR. Status remains `stage-b-implemented-awaiting-independent-check`; Stage B is not approved and Stage C is not authorized.

`VERSION` remains `0.44.1`. No real model prompt was executed; no formal v0.45.0 release migration was created or updated; v0.45.0 is not release-ready. This checker did not fix implementation, enter Stage C, commit, push, tag, or release.

## Stage B Final M-B1 Recheck

ReviewedOn: 2026-07-20
ReviewType: final single-finding recheck
ReviewerAgent: Codex independent checker (/root)
Finding: M-B1 validate-agent-entries.py contradiction gate
ReviewDecision: FAIL
ArtifactStatus: stage-b-implemented-awaiting-independent-check
M-B1: OPEN
StageBApproved: no
StageCAuthorized: no

### Scope and baseline

本轮只复核 M-B1 contradiction gate、对应测试、release mutation 和必要回归门禁。未重新打开九项 route 架构、M-B2、migration/upgrader 产品行为、入口正文、Claude 平台适配或 Stage A。分支为 `main`，`VERSION` 为 `0.44.1`；AGENTS、CLAUDE 和两份 upgrader 的 bytes/hash 与上轮一致，Skills、prompts 和正式 migrations 无新增 diff。M-B2 保持 CLOSED。

### Required contradictions and independent combinations

- 五个原漏检反例均在保留全部正向 marker 的真实 CLI mutation 中得到 exit 1，错误包含文件、`audit-auto-write` rule ID、`audit-default` category 和完整 matched text：assessment 自动修改、diagnosis 自动修改、planning 自动编辑、review 默认直接应用修复、generic no-repair write 全部通过预期。
- 五个独立组合也全部得到 exit 1：`Auditing can automatically write project files.`、`A review may directly fix files.`、`Assessing quality will modify files by default.`、`Diagnostic checks should auto-edit files.`、`Plans can apply fixes by default.`。
- 实现使用 subject、automatic action、generic write、no-repair request 和 explicit-negation 数据族进行句段组合，不是五个完整句子的逐字硬编码；合理大小写、单复数与 may/can/should/will 抽查通过。

### Safe negation and preprocessing

- 提示要求的八条安全句以及额外普通 `not` 句全部得到 exit 0：read-only unless repair、must not、never、cannot、do not、普通 not 和 `No audit` 的否定作用域抽查通过。
- Fenced code block 中的 assessment 反例得到 exit 0；当前正式 AGENTS 与 CLAUDE 均通过。
- 但 Markdown/Skill 预处理仍不符合冻结条件。真实 CLI 对以下四条本应安全的名词性/导航文本错误返回 exit 1：`The \`code-review\` route documents auto-edit behavior.`、`See [handover-review](.agents/skills/handover-review/SKILL.md) for auto-edit guidance.`、`.agents/skills/code-review/SKILL.md documents auto-edit terminology.`、`## Review auto-edit terminology`。输出把 Skill 名、link/path 或 heading 中的 `review` 与 `auto-edit` 词共现误判为授权写入。
- 代码仅调用 `strip_fenced_code_blocks`；没有排除 inline code、Markdown link/path 或 heading 后再做 contradiction 判断。现有 path/link 测试只使用不含 action-family 词的样例，因此未覆盖该系统性误报边界。

### Skill route minimal regression

- AGENTS 随机删除 manifest-derived `project-suitability`：exit 1，正确报告缺失 route。
- CLAUDE 随机删除 `security-review`：exit 1；用 Claude-only `forgekit-project-workflow` 替代 `project-bootstrap-fill`：exit 1。
- Skill 名继续从 `config/skill-projections.json` 动态派生；未发现第二份九项硬编码清单。Route finding 不重新打开。

### Tests, release mutation, gates, and smoke

- `python -B scripts/validate-agent-entries.py`: PASS。
- `python -B -m unittest tests.test_agent_entries`: PASS，31/31；相较上轮新增 16 项。五个旧漏检、subject/action、generic no-repair、安全否定、fenced、基础 Skill/path/link 和 route deletion 均有覆盖，但没有覆盖带 action-family 词的 Markdown/Skill 名词性引用误报。
- 全量 unittest：PASS，92/92。
- Release consistency 包含原 audit、assessment 和 generic no-repair 三类真实 CLI mutation；均返回非零，新增两项断言 category/matched text，所有文件逐字节恢复，恢复后 validator 通过。
- Agent-entry validator、M-B2 validator、projection、41-rule ownership、behavior validate/list/dry-run、plugin assets、template、manifest、release consistency 和 `git diff --check` 全部 PASS。Dry-run 仍为 `GRADER_UNCERTAIN/not-run`，未执行真实模型。
- 完整 smoke 在包含 `.git`、全部 tracked/untracked Stage-B 文件且仅在副本恢复 HEAD `usage.html` 的 `D:\tmp\fb1` 中通过；生成项目为 `D:\tmp\fb1-gates\forgekit-smoke-_14ixv03\generated`，AGENTS、CLAUDE 和 shared contract 存在。所有 smoke/mutation/temp 目录已删除。

### BLOCKER

None.

### MAJOR

1. M-B1 remains OPEN because the contradiction scanner does not exclude inline-code Skill names, Markdown link/path text, or headings before subject/action matching. Ordinary documentation/navigation text containing a `review`-family Skill reference and an `auto-edit`-family term is rejected even though it does not authorize writes. This is a systematic false-positive class explicitly prohibited by the final M-B1 acceptance scope.

### NOTE

1. More complex natural-language contradiction detection remains outside this deterministic gate.
2. Real Codex/Claude behavior, selector/Skill-source observations, token/context benefit, and manual-merge readability remain NEEDS_TEST and do not cause this failure.
3. Historical Stage-A wording in `ship.md` remains a non-blocking note.

### Stage decision

M-B1 remains OPEN. Stage B final M-B1 recheck FAILS with 0 BLOCKER and 1 MAJOR. Status remains `stage-b-implemented-awaiting-independent-check`; Stage B is not approved and Stage C is not authorized. M-B2 remains CLOSED.

`VERSION` remains `0.44.1`. No real model prompt was executed; no formal v0.45.0 release migration was created or updated; v0.45.0 is not release-ready. This checker did not modify implementation, enter Stage C, commit, push, tag, or release.

## Stage B Markdown Structure Recheck

ReviewedOn: 2026-07-20
ReviewType: final M-B1 Markdown structure recheck
ReviewerAgent: Codex independent checker (/root)
ReviewDecision: PASS WITH NOTES
ArtifactStatus: stage-b-approved-for-stage-c
M-B1: CLOSED
StageBApproved: yes
StageCAuthorized: yes

### Actual scope and implementation structure

本轮仅复核 `validate-agent-entries.py` 的 Markdown/navigation policy-prose 提取与 contradiction detection 分层、对应测试及必要回归。未重新打开 M-B2、route 设计、产品入口正文、migration/upgrader、Stage A 或其他已通过范围。分支为 `main`；`VERSION` 为 `0.44.1`。AGENTS、CLAUDE、两份 upgrader 与 M-B2 validator 的 bytes/hash 均与上轮一致，Skills、prompts 和正式 migrations 无新增 diff；M-B2 保持 CLOSED。

代码已清晰分为 `extract_policy_prose(...)` 与 `detect_policy_contradictions(...)`。Anchor、route 和 forbidden-protocol 检查继续使用结构文本；contradiction detector 只扫描已提取 prose。提取器只处理中性化/排除 Markdown 导航结构，不拥有 contradiction 语义；subject/action family 未缩小，也没有四个 checker 句子的完整字符串白名单。

### Markdown/navigation extraction

- 三反引号、三波浪号及带语言标记 fence 内文本均排除。
- ATX 1--6 级 heading（含可选 closing 语法）和 Setext heading 本身排除；heading 后普通正文仍扫描。
- 单/多反引号 inline code 中性化，内部 Skill、path、review/planning/auto-edit 术语均不参与匹配。
- Inline/reference links 保留非导航自然语言 label，同时中性化 destination、URL/title、Skill/navigation label；images 与 autolink 中性化。Link 后 prose 不被整行跳过。
- 九个通用 Skill 从 `config/skill-projections.json` 动态派生；Claude Skill 从实际 `project-template/.claude/skills/` 目录发现，无第二份手写清单。Skill ID、SKILL.md、Windows/POSIX/repo-relative path、URL/file token 均中性化；普通 prose 中的 review/assessment 等保留。
- 提取器不跳过全部 routing section、列表或表格；真实 policy list/table 仍进入 detector。

### Independent Markdown mutations

- 四个原结构误报均为 expected 0 / actual 0，stdout 为 `[ok] Agent entry contracts passed`，stderr 无失败；每次 AGENTS 均逐字节恢复：inline `code-review`、handover-review Markdown link、skills/code-review/SKILL.md path、ATX review/auto-edit heading。
- 六个补充导航样例全部 exit 0：inline link 与独立 adapter term、Claude reviewer path、ATX planning heading、Setext heading、navigation-only table、handover-review list/link。精确反引号 table 另行复测仍为 exit 0。
- Backtick 与 tilde fenced contradiction 均 exit 0；image、reference link、autolink、多反引号、动态 Claude Skill navigation 均有正式 CLI 测试覆盖。

### Contradiction anti-escape and safety

- 原五个 contradiction 全部 expected nonzero / actual exit 1，输出包含文件、`audit-auto-write`、`audit-default` 和 matched text。
- 导航后、heading 后、inline code 后、link 后、list 中、table 中及自然语言 link label 内的真实 contradiction 七项全部 exit 1；提取器没有粗暴跳过整行或 block。
- Auditing/automatically write、Review/directly fix、Assessing/modify by default、Diagnostic/auto-edit、Plans/apply fixes by default 五项词族组合全部 exit 1，证明不是完整句硬编码。
- 十条安全否定句全部 exit 0，覆盖 read-only、must not、never、cannot、can't、may not、do not 和 `No audit`；无系统性否定误报。

### Route regression, tests, and formal gates

- AGENTS 删除 manifest-derived `project-suitability`、CLAUDE 删除 `security-review`、Claude-only route 替代 `project-bootstrap-fill` 均 exit 1；route finding 保持 CLOSED。
- `tests.test_agent_entries`: PASS，58/58，较上轮新增 27 项。测试使用真实 CLI 临时入口副本并检查 exit code、category 与 matched text；覆盖四个误报、ATX/Setext、inline code、links/images/paths、navigation table/list、防逃逸、五个 contradiction、安全否定和九项 route 删除。
- 全量 unittest：PASS，119/119。
- `validate-template.ps1` 调用全量 unittest discovery，因此 Markdown expected-pass guards 属于正式门禁。
- Release consistency 的 audit、assessment、generic no-repair mutations 全部按预期失败并逐字节恢复；恢复后 validator 通过。
- Agent-entry validator、M-B2 validator、projection、41-rule ownership、behavior validate/list/dry-run、plugin assets、template、manifest、release consistency 与 `git diff --check` 全部 PASS。Dry-run 仍为 `GRADER_UNCERTAIN/not-run`。
- 完整 smoke 在含 `.git`、全部 tracked/untracked Stage-B 文件且仅在副本恢复 HEAD `usage.html` 的 `D:\tmp\fbm` 通过；生成项目为 `D:\tmp\fbm-g\forgekit-smoke-8mztx3zt\generated`，AGENTS、CLAUDE 与 shared contract 存在。所有 mutation/smoke/temp 目录均已删除。

### BLOCKER

None.

### MAJOR

None.

### NOTE

1. 更复杂自然语言仍可能超出该小型确定性 gate 的识别范围。
2. 真实 Codex/Claude 行为、selector/Skill-source、实际 token/context 收益和 manual-merge 体验仍为 NEEDS_TEST；这些不阻塞 Stage B。
3. `ship.md` 的历史 Stage-A 时态仍是非阻塞可读性 note。

### Stage decision

M-B1 is CLOSED and M-B2 remains CLOSED. Stage B passes with notes. Status is `stage-b-approved-for-stage-c`; Stage C is authorized, but this checker did not enter or implement Stage C.

`VERSION` remains `0.44.1`. No real model prompt was executed; no formal v0.45.0 release migration was created or updated; v0.45.0 is not release-ready. This checker did not commit, push, tag, or release.

## Stage C Independent Review

ReviewedOn: 2026-07-21
ReviewType: independent
ReviewerAgent: Codex independent checker (`/root`)
StageACommit: `506cecf8d377a17a2616bf3b9eeea483ee4039a4`
StageBCommit: `d02b496971db3773ac0c1435a423198189d6d8d8`
ReviewDecision: FAIL
ArtifactStatus: stage-c-implemented-awaiting-independent-check
StageCApproved: no
StageDAuthorized: no
Findings: 0 BLOCKER, 7 MAJOR, 3 NOTE

### Baseline, scope, and Stage-C mapping

- Branch is `main`; HEAD is the approved Stage B commit `d02b496`; `VERSION` remains `0.44.1`.
- The initial worktree contained only the user's pre-existing deleted `usage.html`. This checker did not restore, modify, stage, or include that file in the real worktree.
- Read all six change artifacts, DECISION-01/02/03, all 41 ownership rows, A01-A22, the Stage-C task--acceptance mapping, every Stage A/B independent review and findings recheck, the Stage C maker writeback, both required governance files, every tracked diff, every untracked file, all five current/Stage-B Skill bodies, frontmatter, and `agents/openai.yaml` files.
- No change was found in `code-review`, `security-review`, `release-check`, `project-suitability`, `.claude/skills/`, root/template AGENTS or CLAUDE, prompts, user-facing README/usage, formal migrations, VERSION, plugin manifests, or marketplace metadata. Stage D/E was not implemented.

| Stage-C task | Actual change group | Necessity | User runtime | Stage boundary |
| --- | --- | --- | --- | --- |
| SC-01 | root/template `project-init/SKILL.md`; template checksum | Required Skill convergence | Yes: plugin and generated-project workflow | Within C |
| SC-02 | root/template `project-bootstrap-fill/SKILL.md`; draft baseline/incoming | Required Skill convergence and development upgrade fixture | Yes for Skill body; draft is development-only | Within C, but metadata defect remains |
| SC-03 | root/template `handover-review/SKILL.md`; draft baseline/incoming | Required read-only audit convergence | Yes for Skill body | Within C |
| SC-04 | root/template `document-backfill/SKILL.md`; draft baseline/incoming; factual fixture files | Required fact-backfill convergence and behavior fixture | Yes for Skill body; fixture is test-only | Within C, but default prompt defect remains |
| SC-05 | root/template `large-change-planning/SKILL.md`; draft baseline/incoming | Required impact-risk convergence | Yes for Skill body | Within C |
| SC-06 | single change-local migration README/descriptor, ten Skill baseline/incoming files, Stage-B migration validator/test extension | Required development migration safety | No production discovery/runtime migration | Within C |
| SC-07 | Stage-C validator/test, 13-case manifest, fixture additions, behavior runner assertion, plugin/template/smoke gates | Required deterministic gate and dry-run preparation | Test/release tooling only | Within C, but validator and case defects remain |
| SC-07 writeback | `tasks.md`, `verification.md`, `ship.md` | Required maker evidence and handoff | No | Honest Stage-C boundary |

No temp, packet, report, evidence, mutation, cache, `.pyc`, `.tmp-*`, or `.old-*` file was present in the real worktree before checker writeback.

### Skill size and body conclusions

Independent byte counts use `git show d02b496:skills/<skill>/SKILL.md` versus current working-tree bytes.

| Skill | Stage B lines / bytes | Stage C lines / bytes | Body conclusion | Package conclusion |
| --- | ---: | ---: | --- | --- |
| `project-init` | 162 / 13,264 | 41 / 3,686 | PASS: new/uninitialized-only, minimal questions/writeback, unknown markers, bounded local authorization, external escalation, no business implementation | FAIL: stale machine-facing default prompt still asks for questionnaire/selected stack templates |
| `project-bootstrap-fill` | 71 / 3,069 | 36 / 3,177 | PASS: initialized placeholder-only, preserve customization, no guessing/conflict overwrite, no fill-all requirement | FAIL: explicit-only policy is placed on an unsupported surface and therefore ineffective |
| `handover-review` | 94 / 5,600 | 45 / 3,646 | PASS: read-only default, correct evidence order, owner-only optional writeback, no automatic repair | PASS WITH NOTE: default prompt still emphasizes defects/repair planning but does not itself authorize writes |
| `document-backfill` | 85 / 4,350 | 41 / 3,549 | PASS: implemented facts only, owner-based recoverable batches, no speculation/future completion | FAIL: explicit-only policy is ineffective and `agents/openai.yaml` still mandates one source document at a time |
| `large-change-planning` | 74 / 3,343 | 52 / 4,090 | PASS: impact-driven trigger, light branch, staged authorization, acceptance/rollback/checker conditions, no implementation | PASS WITH NOTE: default prompt still uses broad-implementation language rather than the new impact framing |

The body rewrite genuinely removes the old full questionnaire, forced document suite, automatic P0/P1 repair, one-document batching, fixed file/module threshold, mandatory double-plan source, and universal checker behavior. It is not a line-count-only rewrite and does not simply copy the long entry contract. Common body contracts for read-only review/planning, bounded local authorization, external/irreversible protection, confirmed-fact owner writeback, preservation of customization, and no automatic cross-Skill execution are materially present.

### Impact risk and routing matrix

Impact-based risk is correctly implemented in the current `large-change-planning` body: trust boundary, public contract, persistent migration, auth/permission, irreversible actions, rollback cost, external coordination, verification capability, and evidence uncertainty control routing. A one-file permission/migration change can be high impact; a deterministic multi-file projection can be low impact. No current Stage-C Skill body contains the old `5 files / 2 modules`, line-count, score, question-count, section-count, or batch-count gate.

| Scenario | Expected route | Must not route | Current body clarity |
| --- | --- | --- | --- |
| New/uninitialized project | `project-init` | bootstrap/handover/backfill/large-plan chain | Clear |
| Initialized project with confirmed placeholder gaps | `project-bootstrap-fill` | re-run init/full rewrite | Clear in body; implicit policy ineffective |
| Existing-project takeover/current-state audit | `handover-review` | init/automatic implementation | Clear |
| Existing implementation with stale fact document | `document-backfill` | future design/init/governance suite | Clear in body; default prompt conflicts on batching |
| High-impact or genuinely staged change | `large-change-planning` | count-based escalation | Clear |
| Ordinary bounded small fix | direct implementation | all five heavy workflows | Clear in current body/entry |
| Suitability assessment | `project-suitability` | `project-init` | Clear through Stage-B entry and init exclusion |
| Code review | Stage-D-owned `code-review` | handover/implementation | Clear; Stage D not implemented, correctly non-blocking here |
| Release review | Stage-D-owned `release-check` | bootstrap/handover | Clear; Stage D not implemented, correctly non-blocking here |

The actual five bodies have no current route cycle and do not require sequential invocation. The deterministic validator does not reliably preserve that state, as recorded below.

### Frontmatter, metadata, and machine-facing Skill configuration

All five frontmatter blocks are syntactically parseable YAML, public `name` and display names are unchanged, and root/template `SKILL.md` plus `agents/openai.yaml` projections are byte-identical. `.claude/skills/` is untouched.

MAJOR M-C1: the explicit-only policy is implemented on the wrong schema surface. Current Codex `0.144.6` toolchain guidance and its plugin validator define `policy.allow_implicit_invocation` under `agents/openai.yaml`, with default `true`. Stage C instead adds `metadata.allow_implicit_invocation: false` inside `SKILL.md`; both relevant `agents/openai.yaml` files remain byte-identical to Stage B and contain no `policy`. The Stage-C parser flattens nested frontmatter lines and therefore reports the misplaced field as valid. Moving the same key to an arbitrary `unsupported_policy_bucket` still returned exit 0. `project-bootstrap-fill` and `document-backfill` consequently remain implicitly eligible in the actual product policy.

The unchanged `agents/openai.yaml` prompts also remain an active competing instruction surface: `document-backfill` says `one source document at a time`, directly restoring a fixed batch; `project-init` says to use its questionnaire and selected stack templates; bootstrap still says to create first-version Codex docs; other prompts retain old broad/repair framing. A synchronized mutation changing backfill to another fixed batch was invisible to the Stage-C validator. This is part of M-C1 because it prevents the five complete Skill packages, rather than only their Markdown bodies, from converging.

### Projection and template manifest

- `python -B scripts/sync-skill-projections.py check`: PASS; all 9 Skills / 18 declared files match byte-for-byte. For the five Stage-C `SKILL.md` files, SHA-256 values are `155910...c02ce`, `1403c7...4404`, `9e1c6e...7aea`, `961978...b31f`, and `919dec...b9e1` respectively.
- Independent one-byte template projection drift: expected exit 1 / actual exit 1; restored byte-for-byte and baseline returned exit 0.
- The sync manifest continues to own only explicitly declared `SKILL.md` and `agents/openai.yaml` files and does not touch `.claude` or Stage-D Skill bodies.

MAJOR M-C2: `project-template/.forgekit/template-manifest.json` records only `project-init/SKILL.md` among the five changed Stage-C projections. Its updated checksum is correct, but bootstrap, handover, backfill, and large-change have no manifest entries/checksums. `update-template-manifest.py --check` validates only listed entries and therefore passes while four changed template Skills are absent. Root validators/tests and the change-local draft are correctly absent, and `template_version` remains `0.44.1`.

### Stage-C validator quality and independent mutation

The validator is compact and does not duplicate complete Skill bodies, but three design defects prevent it from serving as the claimed deterministic gate.

MAJOR M-C3: explicit contradictory prose can retain all positive markers and pass. Required independent mutations produced:

| Mutation | Expected | Actual | Skill / category | Restoration |
| --- | ---: | ---: | --- | --- |
| retain read-only marker, add automatic repair | 1 | 1 | handover / forbidden regression | exact, baseline 0 |
| delete read-only default | 1 | 1 | handover / missing marker | exact, baseline 0 |
| add `5 files / 2 modules` | 1 | 1 | large-change / fixed-count | exact, baseline 0 |
| require checker for all code changes | 1 | 1 | large-change / universal-checker | exact, baseline 0 |
| require exactly eight init questions | 1 | 1 | project-init / fixed-question | exact, baseline 0 |
| state that existing projects are also reinitialized | 1 | 0 | project-init / trigger reversal missed | exact, baseline 0 |
| overwrite existing bootstrap customization | 1 | 1 | bootstrap / overwrite | exact, baseline 0 |
| infer and write when backfill evidence is insufficient | 1 | 1 | backfill / speculation | exact, baseline 0 |
| delete key init cross-Skill route | 1 | 1 | project-init / missing route | exact, baseline 0 |
| add init -> bootstrap -> init cycle | 1 | 1 | routing / obvious cycle | exact, baseline 0 |
| root/template projection drift | 1 | 1 | projection | exact, baseline 0 |
| move implicit key to an unsupported frontmatter bucket | 1 | 0 | bootstrap / wrong schema position missed | exact, baseline 0 |
| require all five Stage-C Skills in order | 1 | 0 | routing / sequential workflow missed | exact, baseline 0 |
| add fixed batch in `agents/openai.yaml` | 1 | 0 | backfill / unscanned active prompt | exact, baseline 0 |

All mutations ran only in `D:\tmp` copies containing `.git`; none touched the real worktree.

MAJOR M-C4: Stage B's Markdown/prose separation was not reused. The Stage-C validator scans raw Markdown for both required and forbidden regexes. A removed read-only policy followed by the same marker inside a fenced block returned exit 0. Conversely, a fenced legacy example, a heading, and the safe negation `Never use more than 5 files as a threshold` each returned exit 1. Inline code/link/path/navigation are subject to the same raw-text family. This creates both false-negative and false-positive systematic classes explicitly called out by the acceptance scope.

MAJOR M-C5: five-Skill derivation can silently shrink. Changing only the `ROUTE-DOCUMENT-BACKFILL` matrix action wording from `阶段 C` to `Stage C` made the formal CLI report success for `4 Skills derived from the ownership matrix`. The exact-five assertion exists only in a unit test, not the validator; normal matrix wording/format evolution can therefore omit a Stage-C owner without a gate failure.

### Behavior cases and fixture

- Manifest validation/list/dry-run: PASS; 13 cases total (3 Stage A + 10 Stage C), all dry-run records remain honest `GRADER_UNCERTAIN/not-run`, `changed_paths=[]`, cleanup passed, and no client was launched.
- Positive/negative intent coverage exists for all five Skills: new versus existing init, placeholder preservation, handover no-write, implemented fact versus future design, and one-file-high/many-file-low impact.
- Read-only allowlists are empty; bounded writes name narrow targets; push/publish/release/deploy/delete are forbidden.

MAJOR M-C6: the Stage-C cases are not yet executable routing cases. `stage-c-new-project` contains only README; `minimal-project` contains entry/governance evidence but no `.agents/skills`. The runner copies only the selected fixture, creates an isolated empty `CODEX_HOME`, and does not install/copy the ForgeKit plugin or authoritative Skills. Its `invocation_mode` is passed only as adapter context/diagnostics; explicit prompts do not invoke `$project-init`, `$project-bootstrap-fill`, or `$document-backfill`. The exact case schema also has no case-level evidence-requirement field. Thus the cases can dry-run but cannot later observe the declared Skill source/routing under the isolation contract without additional harness work. This finding is not based on the absence of a real model run.

### Development migration, Git anchors, and behavior classification

- Exactly one change-local draft exists. README accurately says Stage B entries plus Stage C Skills; production discovery sees only `0.44.1`; no root or template formal `migrations/0.45.0` exists.
- Entry baseline remains anchored to Stage A. The five Skill baselines are byte-identical to Git objects at full Stage B SHA `d02b496971db3773ac0c1435a423198189d6d8d8`; incoming files are byte-identical to current template projections. The descriptor has exactly seven safe managed targets and no Stage-D Skill.
- Independent synchronized baseline+checksum mutation: expected 1 / actual 1, rejected by Stage-B Git object SHA. Independent incoming+checksum mutation: expected 1 / actual 1, rejected by current projection SHA. Both restored exactly and the formal validator returned 0 afterward.
- Independent real upgrader fixtures passed: all stock; one custom Skill; two custom Skills; Skill unknown-baseline; all missing; entry stock + Skill custom; mixed rollback; and same managed path over multiple migrations. Custom/unknown bytes were preserved, missing did not fabricate origin bytes, every tested rollback restored the upgrade start, and the same-path packet retained `stage-a-origin\r\n`.

### CRLF and fresh-clone portability

MAJOR M-C7: a reasonable Windows fresh clone fails the byte-exact gates.

- Repository `.gitattributes` only contains `*.sh text eol=lf`; Markdown/JSON byte-sensitive migration and Skill files have no line-ending contract. The host's normal Git configuration is `core.autocrlf=true`.
- LF clone (`git -c core.autocrlf=false clone --no-local`): Stage-B baseline AGENTS Git/working SHA-256 both `e3fb1941...5374`; Stage-C Skill/migration validators pass; full smoke passes.
- CRLF clone (`git -c core.autocrlf=true clone --no-local`), with the current tracked diff applied and current untracked files copied: baseline AGENTS Git SHA-256 `e3fb1941...5374`, working SHA-256 `6756490d...feea`; current `project-init` working SHA-256 is `24ea0791...7929` instead of the LF incoming `15591041...c02ce`.
- In that CRLF clone, Stage-C validator exits 1 because its raw-byte frontmatter regex requires LF; migration validator exits 1 for Stage-A entry baseline and Stage-C incoming byte mismatches; smoke exits 1 at the migration gate.
- The migration validator reads approved baselines from Git objects but compares them to working-tree draft bytes; the upgrader consumes those working-tree package bytes. This is a real checkout/runtime portability defect, not merely an archive construction error. A source-worktree byte overlay passing only proves the maker workspace is self-consistent and masks the normal checkout failure.

### Complete gates and smoke

Authoritative gates ran in an LF, short-path, `.git`-preserving copy containing all Stage-C tracked/untracked bytes; only that disposable copy materialized HEAD `usage.html`.

| Gate | Result |
| --- | --- |
| Stage-C Skill validator | PASS, 5 (subject to M-C3/M-C4/M-C5) |
| projection / 41-rule ownership / Stage-B entry / Stage-B migration | PASS |
| behavior validate / list / dry-run | PASS, 13; no client invocation |
| unittest discovery | PASS, 136/136 |
| plugin assets / template / template manifest | PASS |
| release consistency mutations | PASS; all restored |
| `git diff --check` | PASS under the source worktree's Git semantics |
| current-worktree exact-copy smoke | PASS; `.git` present, Stage-C tracked/untracked present, copy-only `usage.html` materialization |
| LF fresh-checkout semantic smoke | PASS |
| CRLF fresh-checkout semantic smoke | FAIL as M-C7 |

### BLOCKER

None. The current Skill bodies do not automatically repair a read-only review, current migration behavior preserves custom/unknown content and rollback origin, production discovery does not expose the draft, and no Stage-D/Claude/external-release action was added.

### MAJOR

1. M-C1: explicit-only metadata is on the wrong product schema surface; machine-facing default prompts remain stale and reintroduce old behavior, including fixed backfill batching.
2. M-C2: four of five changed template Skill projections are absent from `template-manifest.json`.
3. M-C3: the validator misses existing-project reinitialization and mandatory five-Skill sequencing while markers remain.
4. M-C4: raw Markdown scanning permits fenced-marker false negatives and causes fenced/heading/negation false positives.
5. M-C5: matrix-derived Stage-C set can silently pass with four Skills after an ordinary action-wording change.
6. M-C6: Stage-C behavior cases lack an available Skill source, operational explicit invocation, and case-level evidence requirement under the isolated runner.
7. M-C7: normal `core.autocrlf=true` Windows checkout breaks Stage-C, migration, and smoke byte gates.

### NOTE

1. More complex natural language can still exceed a deliberately small deterministic contradiction gate after the concrete false-negative/Markdown defects are fixed.
2. Real Codex/Claude prompts, selector/Skill-source observations, token/context benefit, and manual-merge usability remain `NEEDS_TEST`; their non-execution is not a failure reason here.
3. Stage D review/security/release Skills and Stage E prompts, README/usage, formal migration, metadata, and release preparation remain intentionally incomplete and are not failure reasons.

### Stage decision

Stage C FAILS with 0 BLOCKER and 7 MAJOR. Status remains `stage-c-implemented-awaiting-independent-check`. Stage C is not approved and Stage D is not authorized.

`VERSION` remains `0.44.1`. No real model prompt was executed. No formal v0.45.0 release migration was created. v0.45.0 is not release-ready. This checker did not implement a fix, enter Stage D/E, commit, push, tag, release, deploy, or modify the user's deleted `usage.html`.
## Stage C Findings Recheck

Date: 2026-07-21
Checker: Codex，上一轮 Stage C Independent Review 的独立 checker
Stage A commit: `506cecf8d377a17a2616bf3b9eeea483ee4039a4`
Stage B commit: `d02b496971db3773ac0c1435a423198189d6d8d8`
ArtifactStatus: `stage-c-implemented-awaiting-independent-check`

### Recheck scope and decision

本轮只定向复核 C-M01 至 C-M07；未重新打开上一轮已通过的五份 Skill 核心执行语义、handover 只读与证据优先级、document-backfill 事实批次、large-change 影响型风险、既有跨 Skill 路由、migration 基础分类/rollback 或 Stage A/B 已关闭事项。

结论：`FAIL`。C-M04、C-M05 CLOSED；C-M01、C-M02、C-M03、C-M06、C-M07 OPEN。新增 0 BLOCKER；仍有 5 个 findings 对应 MAJOR。Stage C 未通过，不允许进入 Stage D。

| Finding | 状态 | 定向结论 |
| --- | --- | --- |
| C-M01 package metadata/default prompt | OPEN | explicit-only schema 已放到受支持位置且为 boolean；实际 prompt 文案已去除旧流程，但 large-change prompt 的单一固定 `5 files` 门槛 mutation 仍以 0 退出，未满足“四类 prompt mutation 全部失败”。 |
| C-M02 template manifest | OPEN | Stage C 十个 package 文件只列 8 个，缺 handover-review 与 large-change-planning 两份 unchanged `agents/openai.yaml`；删除 unchanged YAML entry 的要求在当前基线上已直接缺失而 validator 仍以 0 退出。 |
| C-M03 reinitialize/pipeline contradiction | OPEN | 三条冻结反例能失败，但 checker 自构造的两条重初始化和两条 mandatory sequence 等价表达均以 0 退出。 |
| C-M04 Markdown policy-prose | CLOSED | required marker 的 fence/heading 伪造失败；fenced/heading legacy 不误报；普通正文、list、table、link 后反例失败；navigation/path 与安全否定通过；复用 `validate-agent-entries.py` 的 policy-prose helper。 |
| C-M05 dual-source five-Skill set | CLOSED | tasks SC-01..05 与 41-rule matrix 双源各锁定五项且集合相等；四项、集合不同、Stage D owner、duplicate、projection missing 均失败并显示实际集合。 |
| C-M06 behavior runtime/evidence | OPEN | 当前 cases 可真实物化且 explicit prompt 正确，但 bounded-write case 可关闭 `write_behavior` 证据仍通过，且原 prompt 已含 `$skill-id` 时 runner 会重复注入。 |
| C-M07 LF/CRLF fresh clone | OPEN | 合理的 LF/CRLF fresh clone 主路径和 generated-project checkout 均已修复，但 Stage C/manifest checksum 继续归一化换行；root/template 同步 CRLF mutation 可同时绕过 Stage C、projection、manifest 三个 gate。 |

### C-M01: package schema, policy, prompts, projection, migration

- 五份 `SKILL.md` frontmatter 均只保留 `name`/`description`，不再含 `metadata.allow_implicit_invocation`。
- `project-bootstrap-fill` 与 `document-backfill` 的根级和 template `agents/openai.yaml` 均在顶层 `policy.allow_implicit_invocation` 设置 YAML boolean `false`。
- 当前官方 Codex manual 明确将 invocation policy 放在 `agents/openai.yaml` 顶层 `policy`；本机官方 plugin validator 也解析该字段并要求 boolean。对整个仓库运行当前 `validate_plugin.py` 为 PASS。
- 独立 schema mutation：policy 放回 SKILL frontmatter、删除 YAML policy、字符串 `"false"`、错误嵌套层均非零，诊断均包含 Skill、package policy/category。
- 五个实际 default prompt 本身未恢复 questionnaire、selected-stack、固定批次、自动修复、所有修改 checker 或文件/模块双阈值；root/template package bytes 一致。
- prompt mutation：project-init questionnaire、backfill one-source-at-a-time、handover automatic repair 均失败；`Any change touching 5 files requires this plan.` 加入 large-change package prompt 后 validator exit 0，故 finding 未关闭。
- 当前安装的官方 `openai_yaml.md` authoring reference 还要求 `interface.default_prompt` 显式写 `$skill-name`；五个当前 prompt 均未使用 `$` 形式，项目 validator 与官方 plugin validator 均未把该 authoring requirement 作为 gate。该项不改变上述确定性 OPEN 判定。
- `sync-skill-projections.py check` 对全部 18 个受管文件 PASS；五个 Stage C package 的根/template 两文件均逐字节一致。
- 唯一 development draft 管理五份 Stage C `SKILL.md` 与三份 changed YAML。八项 baseline 均与 Stage B Git object blob 一致，incoming 均与当前 template bytes 一致，descriptor SHA 正确。
- YAML baseline 与 checksum 同步篡改仍因 Stage B Git object anchor 失败；YAML incoming 与 checksum 同步篡改仍因 current template anchor 失败。
- 独立 YAML 实跑：custom=`custom` 且不覆盖，unknown=`unknown-baseline` 且不覆盖，missing 安装 incoming；三者 rollback 均恢复完整升级起点。production discovery 未发现 draft；不存在正式 `migrations/0.45.0` 或 `project-template/migrations/0.45.0`。

### C-M02: template manifest completeness

- `template_version` 仍为 `0.44.1`；`.gitattributes` 唯一 entry 存在且当前 checksum 一致；Stage C root validator/tests 与 development draft 未列入 template manifest；未新增 Stage C `.claude` package。
- 五份 Stage C `SKILL.md` 与三份 changed YAML 各恰好一个 entry，checksum 与当前 LF bytes 一致。
- 明确缺失：`.agents/skills/handover-review/agents/openai.yaml`、`.agents/skills/large-change-planning/agents/openai.yaml`。因此 Stage C package 覆盖是 8/10，不是 10/10。
- `validate_template_manifest()` 的 required YAML 条件仅为 SC-01 或 explicit-only，正好遗漏上述两项；实际 baseline validator PASS 证明 gate 不检查完整 package。
- `config/skill-projections.json` 声明 18 个受管文件；template manifest 仅包含其中 9 个。即使不把 Stage D 的 manifest 完整性作为本轮判定依据，Stage C 明确要求的十项已经失败。
- generated project 初始化会复制上述两份 YAML，但其 `.forgekit/template-lock.json` 不记录两项，确认缺项会影响后续管理身份，而不只是清单展示。
- mutation：删除一份 Stage C SKILL、删除一份 changed YAML、修改 checksum、添加 duplicate 均失败；unchanged YAML 在 baseline 已缺失且 Stage C validator 仍通过。

### C-M03/C-M04: validator semantics and Markdown structure

- 冻结的三个 existing-project reinitialize 句式与三个 mandatory five-Skill pipeline 句式均命中正确 category；冻结安全否定均通过。
- 自构造的以下清晰反向语义未命中，且在同步临时 manifest checksum 后 validator exit 0：
  - `Existing projects must go through initialization from scratch before audit.`
  - `For a project that is already initialized, repeat project initialization before handover.`
  - `All five Stage C Skills are required as a sequential workflow for each request.`
  - `Each project task goes through every one of the five Skills, one after another.`
- large-change package prompt 的单一固定文件门槛也未命中。当前 detector 不是完整句硬编码，但 subject/action 词组仍窄于本轮要求。
- Markdown 分层独立 mutation 全部符合预期：required contract 只在 fenced block 或 heading 时失败；fenced reinitialize 与 heading pipeline legacy 文本不误报；相同普通正文、list、table、Markdown link 后反例失败；inline code/path/URL/navigation 不误报；安全否定通过。
- 因此 C-M03 OPEN，C-M04 CLOSED。

### C-M05: dual-source set

- Source A 从 tasks SC-01..SC-05 owner path 解析，恰好五个不同 Skill；Source B 从 41-rule matrix 的 Stage C ROUTE normative owner 解析，恰好五个不同 Skill；A=B。
- 五项均在 projection config 中，owner 文件存在，无 Stage D overlap；实现只固定 cardinality 5 与 task ID，不硬编码五个 Skill 名称。
- 独立 mutation 结果：matrix 精确缩为四项、tasks 缩为四项、两边各五但集合不同、两边替换成 Stage D owner、duplicate owner、projection config 删除一项全部非零。
- 诊断分别显示 `found [...]`、`tasks-only`/`matrix-only`、Stage D owner 与 missing Skill，满足可定位性。C-M05 CLOSED。

### C-M06: behavior materialization, explicit invocation, evidence

- case manifest 为 13 项，其中 Stage C 10 项；覆盖 new init/existing negative、bootstrap placeholder/preserve custom、handover no-write、backfill fact/future-design negative、single-file high risk、many-file low risk 与 ordinary fix no-heavy-pipeline。
- runner 从根权威 `skills/<id>/` 按 projection manifest 读取 `SKILL.md` 和 `agents/openai.yaml`，物化到 temp fixture `.agents/skills/<id>/`；source path、target path、SHA-256 和 materialized files 进入 record。
- checker 实际保留 temp 到 cleanup callback，逐字节核对 bootstrap/backfill 两个 package 后删除；所有 bytes 与根权威一致，callback 后 parent 为空。
- 当前 bootstrap/backfill rendered prompt 分别含一次 `$project-bootstrap-fill`、`$document-backfill`，原 prompt 保留；implicit handover prompt 不注入 `$`。explicit-only positive case 改为 implicit 时 validate exit 2。
- 每个当前 case 有六键 boolean evidence contract；explicit、read-only、forbidden-action 规则的反向 mutation 均失败。dry-run 的 required evidence 为 `not-obtained`，非 required 为 `not-required`，结果保持 `GRADER_UNCERTAIN/not-run`，未伪造 PASS。
- 未关闭路径一：bounded-write bootstrap case 将 `evidence_requirements.write_behavior` 改为 false 后 manifest 仍 exit 0，未强制 allowed-path/write oracle。
- 未关闭路径二：如果 explicit case 原 prompt 已以 `$project-bootstrap-fill` 开头，`render_prompt()` 仍再次 prepend，最终出现两次 `$project-bootstrap-fill`。

### C-M07: attributes, fresh clones, generated project

- 根与 template `.gitattributes` 均含 `.gitattributes`、`*.md`、`*.json`、`*.yaml`、`*.yml` 的 `text eol=lf`；`git check-attr` 对代表 migration JSON、SKILL.md、package YAML 返回 `text: set`、`eol: lf`。未修改全局 Git config，未把文本标记为 binary。
- fresh-clone runner 从当前 tracked/untracked Stage C 状态构造本地 identity 的临时 commit，排除用户 `usage.html` 删除；clone 前全部范围进入 Git object；clone 后无 tracked overlay，验证源不是源工作树。
- `--full --mutation-check` 临时 commit：`8e8d43d5e2c5ec093bc208fa672a621b9861f81a`。snapshot smoke、`core.autocrlf=false` clone、`core.autocrlf=true` clone 三路均 PASS；两种 clone 的 Stage C、migration、projection、template、manifest-through-template 与完整 smoke 均 PASS。
- 代表 SHA-256 在两种 clone 中均为 blob=working：`.gitattributes` `68e9a1aa...`、project-init SKILL `15591041...`、project-init YAML `dace0e47...`、template manifest `0daefde6...`、migration descriptor `cf6ea9f2...`。
- 删除根 Markdown LF 规则后，Git 的 `core.autocrlf=true` checkout 实际产生 drift；validator exit 1，project-init blob `15591041...`、working `24ea0791...`。runner finally 清理 mutation repo。
- generated project 临时 commit：`fb70fd7fc3842df327317c47652e2f8f4e0cec38`。autocrlf=true clone 中十个 Stage C package 文件均存在，代表 Git blob object=working object；generated harness、doc-sync、current-docs-integrity 均 PASS。
- 但是 `canonical_checksum()` 与 `update-template-manifest.py` 都把 CRLF/CR 归一化为 LF。checker 在隔离 repo 同步把 root/template project-init SKILL 改成 CRLF（working SHA-256 `24ea0791...`）后，Stage C validator=0、projection check=0、manifest check=0。该 newline-insensitive 比较违反本轮明确验收；C-M07 仍 OPEN，尽管正常 fresh checkout 主路径已经修复。

### Targeted tests, formal gates, and smoke

| Gate | Actual result |
| --- | --- |
| `tests.test_stage_c_skills` | 16/16 PASS |
| `tests.test_skill_behavior_runner` | 19/19 PASS |
| `tests.test_skill_behavior_adapters` | 4/4 PASS |
| `tests.test_fresh_clone_crlf` | 3/3 PASS |
| `tests.test_stage_b_entry_migration` | 21/21 PASS |
| full `unittest discover` | 146/146 PASS |
| Stage C / projection / ownership / entries / migration validators | PASS |
| behavior validate/list/dry-run | PASS；13 cases；全部 dry-run 为 `GRADER_UNCERTAIN/not-run` |
| plugin assets / template / manifest / release consistency | PASS |
| `git diff --check` | PASS；仅现有 Git newline conversion warnings |
| current Stage C scoped snapshot smoke | PASS，含 `.git`，排除用户 `usage.html` 删除 |
| `core.autocrlf=false` fresh clone full smoke | PASS |
| `core.autocrlf=true` fresh clone full smoke | PASS |
| generated-project autocrlf=true checkout gates | PASS |

正式门禁全绿不能覆盖独立 mutation 已证实的语义/完整性缺口；本判定不以 maker 的 16/19/4/3/21/146 声称作为事实来源，上表均为 checker 本轮实跑数量。

### BLOCKER

None. explicit-only policy 已位于产品支持位置；development draft 未被 production discovery 发现；custom/unknown YAML 未覆盖；clone runner 未修改源工作树或在 clone 后 overlay；read-only cases 当前 allowlist 为空。

### MAJOR

1. C-M01 OPEN：large-change default prompt 的单一固定文件阈值可通过 validator；五个 default prompt 也未遵守当前官方 authoring reference 的 `$skill-name` 形式。
2. C-M02 OPEN：Stage C template manifest 缺两份 unchanged package YAML，完整性 gate 只锁定 8/10；对应 generated template lock 也缺项。
3. C-M03 OPEN：已有项目重复初始化与 mandatory five-Skill sequence 的四个清晰等价表达可通过 validator。
4. C-M06 OPEN：bounded-write case-level allowed-path/write evidence 未被强制；已有 `$skill-id` 的 explicit prompt 会重复注入。
5. C-M07 OPEN：正常 LF/CRLF clone 已通过，但 newline-normalizing checksum 仍允许 CRLF byte mutation 绕过三个正式 gate。

### NOTE

1. 更复杂自然语言仍可能超出有限静态 detector；本轮只把已复现的清晰反例列为 MAJOR。
2. 真实 Codex/Claude 行为、selector、Skill source、token/context 效果与 manual merge 体验仍为 `NEEDS_TEST`；未执行真实模型 prompt 不构成本轮失败原因。
3. C-M04/C-M05 已关闭；Stage D/E 未完成不构成本轮失败原因。

### Stage decision

Stage C findings recheck FAILS with 0 BLOCKER and 5 OPEN MAJOR findings. Status remains `stage-c-implemented-awaiting-independent-check`. Stage C is not approved and Stage D is not authorized.

`VERSION` remains `0.44.1`. No real model prompt was executed. No formal v0.45.0 release migration was created. v0.45.0 is not release-ready. This checker did not implement fixes, enter Stage D/E, commit, push, tag, release, deploy, or modify/stage/restore the user's deleted `usage.html`.

## Stage C Final Remaining Findings Recheck

Date: 2026-07-21
Checker: Codex，Stage C 最终剩余 findings 独立 checker
Stage A commit: `506cecf8d377a17a2616bf3b9eeea483ee4039a4`
Stage B / source HEAD: `d02b496971db3773ac0c1435a423198189d6d8d8`
ArtifactStatus: `stage-c-implemented-awaiting-independent-check`

### Scope and decision

本轮只复核 C-M01、C-M02、C-M03、C-M06、C-M07，并对已关闭的 C-M04/C-M05 做最小回归；未重新打开五份 Skill 核心执行正文、handover 只读、large-change 影响型风险、既有路由、migration 已关闭分类/rollback 或 Stage A/B 已关闭事项。

结论：`FAIL`。C-M02、C-M06、C-M07 CLOSED；C-M04、C-M05 保持 CLOSED；C-M01、C-M03 OPEN。新增 0 BLOCKER，仍有 2 个 MAJOR。Stage C 未通过，不允许进入 Stage D。

| Finding | 状态 | 定向结论 |
| --- | --- | --- |
| C-M01 package default prompt / fixed quantity threshold | OPEN | 五个 prompt 的正式 `$skill-id`、explicit-only policy 和旧流程回归均已修复；但独立 `42-directory` 固定数量风险门槛仍可通过正式 CLI。 |
| C-M02 full managed projection manifest | CLOSED | projection config 动态派生 9 Skills / 18 targets；manifest 18/18、Stage C package 10/10，generator 与删除/重复/checksum/新增 target mutation 均成立。 |
| C-M03 equivalent reinitialize / mandatory pipeline | OPEN | 多数冻结反例已命中且安全否定通过，但一个用户指定 reinitialize 句、一个用户指定 one-by-one pipeline 句及 checker 变体仍可通过。 |
| C-M04 Markdown policy-prose layering | CLOSED | fence/heading/navigation/inline/link/negation/list/table 最小回归继续通过。 |
| C-M05 tasks/matrix dual source set | CLOSED | SC-01..SC-05 与 41-rule matrix 继续各派生五项且相等；任一来源缩为四项失败。 |
| C-M06 behavior write evidence / explicit idempotence | CLOSED | bounded-write/read-only evidence mutation 均失败；bootstrap/backfill 的 absent/once/duplicate/inline renderer 路径符合冻结合同。 |
| C-M07 raw bytes / LF / fresh checkout | CLOSED | raw hash、LF content gate、单/双侧 CRLF、同步 manifest、YAML、migration CRLF mutation 均成立；LF/CRLF fresh clone 与 generated project checkout 通过。 |

### C-M01: package prompt and fixed quantity threshold

- 五个根级与 template package 逐字节一致；public Skill ID、frontmatter `name`、`interface.display_name` 均相对 Stage B 未变。
- 五个 `interface.default_prompt` 分别只含一个独立正式调用：`$project-init`、`$project-bootstrap-fill`、`$handover-review`、`$document-backfill`、`$large-change-planning`；不含其他 Stage C 主调用或串行 pipeline。
- marker mutation：删除、重复、错误 ID、只在 fenced example 中保留、加入另一个 Stage C `$skill-id`，正式 CLI 均 exit 1；诊断包含 Skill 和 `package-prompt/invocation`。
- `project-bootstrap-fill` 与 `document-backfill` 仍在 `agents/openai.yaml` 顶层使用 boolean `policy.allow_implicit_invocation: false`，SKILL frontmatter 无同名字段；behavior runner 实际读取该位置。当前官方 Codex manual 也把该 policy 定义在 package YAML，并说明 explicit `$skill` 仍可调用。
- 实际 prompt 未恢复 questionnaire / selected-stack、覆盖定制、one-source-at-a-time / 固定批次、自动修复、所有代码修改 checker、固定问题数或八章节。
- 用户给出的五个正向阈值和 checker 的 `Twelve packages...`、`six components...` 均以 `package-prompt/fixed-quantity-risk-threshold` 失败；四个安全否定/低风险示例均通过。
- 仍开放的反例：仅向 `large-change-planning/agents/openai.yaml` prompt 加入 `A 42-directory change requires independent planning.`，同时保持 SKILL 正文、根/template bytes 和 manifest checksum 自洽，正式 CLI exit 0。该明确固定数量门槛满足本轮反向合同，故 C-M01 OPEN。

### C-M02: template manifest completeness

- `config/skill-projections.json` 动态得到 9 个 Skill、每项 `SKILL.md` + `agents/openai.yaml`、共 18 个不同 POSIX target。
- `project-template/.forgekit/template-manifest.json` 对 18 项全部恰好一次，Stage C 十个 package 文件 10/10；上轮缺失的 handover-review 与 large-change-planning YAML 均存在。
- 每项 checksum 由当前 template 原始 bytes 计算；`.gitattributes` 唯一 entry 存在且正确；template version 仍为 `0.44.1`。
- root validators/tests、development draft 与 `.claude` 未误入 manifest。
- 独立 mutation：删除 handover YAML、large-change YAML、非 Stage C code-review YAML，添加 duplicate，篡改 checksum，projection config 新增 target 而不更新 manifest，全部非零并定位实际路径/category。
- `update-template-manifest.py` 从 projection config 补齐/检查完整集合，而非只依赖当前手工 manifest。C-M02 CLOSED。

### C-M03 and C-M04/C-M05 regression

- Reinitialize 七个正向反例中五个失败；以下两个保留全部正向 marker、同步 root/template/manifest 后仍 exit 0：
  - 用户指定：`An initialized project is required to go through project setup again before review.`
  - checker 变体：`Before review, reinitialize every previously initialized repository.`
- Mandatory pipeline 七个正向反例中四个失败；以下三个仍 exit 0：
  - 用户指定：`All Stage C Skills form a mandatory one-by-one workflow for each project.`
  - checker 变体：`For every project request, all five Skills have to be processed sequentially as one required workflow.`
  - checker 变体：`Always take each task through every Stage C Skill in a fixed order.`
- 用户给出的四个 reinitialize 安全句与四个 pipeline 安全句全部通过，没有否定作用域误报。
- 这些是 action-before-subject、`project setup again`、hyphenated one-by-one、`sequentially`、`fixed order` 的清晰等价表达，不是复杂隐喻；C-M03 因正式 CLI 明确漏检而 OPEN。
- C-M04 最小回归：fenced/heading marker 不能伪造 required contract，fenced legacy 不误报，inline/link/path/navigation 不误报，list/table 普通正文 contradiction 失败，safe negation 通过。C-M04 维持 CLOSED。
- C-M05 最小回归：tasks SC-01..SC-05 与 ownership matrix 各派生五项且集合相等；matrix 或 tasks 缩为四项均失败。C-M05 维持 CLOSED。

### C-M06: behavior evidence and explicit renderer

- 13 个 cases 的 required evidence 在 dry-run 中明确列出；required 状态保持 `not-obtained`，grader=`not-run`，failure=`GRADER_UNCERTAIN`，cleanup 全部 passed，未伪造 PASS。
- bounded/local write 将 `write_behavior=false`、allowed paths 清空、expected behavior 明确要求写入但删除 evidence、错误类型、标成 not-required，均 validate exit 2，并包含 case ID 与缺失条件。
- handover read-only 关闭或删除 write oracle 均 exit 2；当前 allowlist 为空。
- 对 `project-bootstrap-fill` 和 `document-backfill`，checker 通过 capture adapter 检查实际收到的 prompt：无 marker 时插入一次且 `invocation_inserted=true`；已有一个独立 marker 时不重复且 `false`；两个正式 marker 被拒绝；inline backtick example 不算正式调用，renderer 另插一个正式 marker；错误 Skill 被拒绝。
- implicit handover 不注入 marker；explicit-only bootstrap 改为 implicit positive 时 schema exit 2。C-M06 CLOSED。

### C-M07: raw bytes, LF content, and fresh checkout

- `sync-skill-projections.py`、`update-template-manifest.py`、`validate-stage-c-skills.py`、`validate-stage-b-entry-migration.py` 的 identity/hash/compare 均使用 `read_bytes()` 或 binary stream；语义解析使用 `read_text()`，未参与 byte identity。smoke 的 CRLF/LF 构造只用于证明 raw checksum helper 不归一化。
- 正式 LF gate 覆盖 projection config 的 18 个 root/template package、template manifest、migration descriptor、全部 draft baseline/incoming、根/template `.gitattributes`，并以 `b"\r"` 同时拒绝 CRLF 与 lone CR；错误包含路径与 `checkout-contract` / LF category。
- Root-only SKILL CRLF：LF SHA `15591041...c02ce` -> CRLF `24ea0791...7929`；Stage C 与 projection 均失败。
- Root/template 双侧 CRLF，即使同步 manifest 到 CRLF SHA，Stage C、projection、manifest 三个 gate 仍失败；YAML 双侧同步同样失败，LF `512070ce...49908` -> CRLF `4fbf81ea...dc6a7`。
- Migration incoming CRLF + 同步 descriptor 失败于 incoming LF/current anchor；baseline CRLF + 同步 descriptor 失败于 LF/Stage B Git anchor，baseline LF `6561a5c2...14482` -> CRLF `8313ae0d...de1cd`。lone CR mutation 也以明确路径失败。
- 三路 runner 临时 commit `2e25bd47ad16e6c567d3993d391d2e53b3b93768`：current scoped snapshot smoke PASS，`core.autocrlf=false` 和 `true` clone 的 Stage C/migration/projection/template/full smoke 全部 PASS，无 post-clone overlay，排除用户 `usage.html` 删除。
- 两种 clone 的代表 blob=working SHA：project-init SKILL `15591041...c02ce`、YAML `512070ce...49908`、template manifest `0e386223...0634f`、migration descriptor `afa2c5a1...d18e`；`git check-attr` 均为 `text: set`、`eol: lf`。
- 删除根 Markdown LF rule 后，真实 `core.autocrlf=true` checkout 产生 `15591041...c02ce` -> `24ea0791...7929` drift，正式 validator exit 1。
- Generated project 临时 commit `10943f5ff748d631b27442c9e0a5c430242621ce`；autocrlf=true clone 中 `.gitattributes`、template lock 与十个 Stage C package blob=working，harness、doc-sync、current-docs、upgrade-check 全部 PASS。C-M07 CLOSED。

### Development migration

- 唯一 development draft 共有 12 actions：AGENTS、CLAUDE 加五份 Stage C SKILL.md 与五份 Stage C `agents/openai.yaml`；Stage C package target 为 10/10。
- 十项 package baseline 逐字节来自 Stage B Git object；incoming 逐字节等于当前 template projection；descriptor checksum 均按原始 bytes 正确，全部 LF。
- 23 个 migration tests 覆盖 stock/custom/unknown/missing/mixed、完整升级起点 rollback、同路径 origin rollback、五份 YAML、Git/current anchors、production discovery 隔离；23/23 PASS。Custom/unknown 不覆盖，missing 安全，rollback 恢复升级起点。
- production discovery 不发现 draft；未建立正式 `migrations/0.45.0` 或 `project-template/migrations/0.45.0`。

### Tests, formal gates, and smoke

| Target | Actual result |
| --- | --- |
| Stage C contract tests | 25/25 PASS |
| behavior runner | 21/21 PASS |
| behavior adapters | 4/4 PASS |
| projection tests | 11/11 PASS |
| development migration tests | 23/23 PASS |
| fresh-clone tests | 3/3 PASS |
| full unittest discovery | 160/160 PASS |
| Stage C / projection / ownership / entries / migration validators | PASS |
| behavior validate / list / dry-run | PASS，13 cases |
| plugin assets / template / manifest | PASS |
| release consistency mutations | PASS；串行执行并全部恢复 |
| `git diff --check` | PASS |
| current scoped snapshot smoke | PASS |
| `core.autocrlf=false` fresh clone full smoke | PASS |
| `core.autocrlf=true` fresh clone full smoke | PASS |
| generated-project autocrlf=true checkout | PASS |

正式测试全绿不能覆盖 checker 已复现的 C-M01/C-M03 明确反例。一次将 template 与 release-consistency 并行运行导致 checker 自身读取到瞬时 shared-helper mutation；对应源 bytes 已恢复，两个 checker 临时目录已删除，串行重跑两项均 PASS，不作为 maker finding。

### BLOCKER

None. explicit-only policy 生效；behavior read-only/write oracle 未放宽；custom/unknown migration 内容不覆盖；development draft 未被 production discovery 发现；clone 后无 tracked overlay；检查器未修改真实 `usage.html`。

### MAJOR

1. C-M01 OPEN：明确固定数量门槛 `42-directory ... requires independent planning` 可在 default prompt 中通过正式 validator。
2. C-M03 OPEN：一个用户指定 reinitialize 等价句、一个用户指定 mandatory pipeline 等价句及 checker 变体可通过正式 validator。

### NOTE

1. 更复杂自然语言仍可能超出有限静态 gate；本轮 MAJOR 只依据清晰、可复现且在冻结反例族内的表达。
2. 真实 Codex/Claude 行为、selector、Skill source、token/context 效果与 manual merge 体验仍为 `NEEDS_TEST`；这不构成本轮失败原因。
3. C-M02/C-M04/C-M05/C-M06/C-M07 已关闭；Stage D/E 与正式 release migration 尚未完成不构成本轮失败原因。

### Stage decision

Stage C final remaining findings recheck FAILS with 0 BLOCKER and 2 OPEN MAJOR findings. Status remains `stage-c-implemented-awaiting-independent-check`. Stage C is not approved and Stage D is not authorized.

`VERSION` remains `0.44.1`. No real model prompt was executed. No formal v0.45.0 release migration was created. v0.45.0 is not release-ready. This checker did not implement fixes, enter Stage D/E, commit, push, tag, release, deploy, or modify/stage/restore the user's deleted `usage.html`.

## Stage C Final C-M01 C-M03 Recheck

- Date: 2026-07-21
- Checker: Codex independent checker (`/root`)
- Stage B baseline: `d02b496971db3773ac0c1435a423198189d6d8d8`
- Scope: only C-M01 fixed-quantity risk thresholds, C-M03A existing-project reinitialization, and C-M03B mandatory five-Skill pipelines. C-M02/C-M04/C-M05/C-M06/C-M07 and the previously accepted Skill/migration/Stage A/Stage B contracts were not reopened.
- Decision: `FAIL`. C-M01 is CLOSED. C-M03A and C-M03B remain OPEN. There are 0 BLOCKER and 2 MAJOR findings. Status remains `stage-c-implemented-awaiting-independent-check`; Stage D is not authorized.

### Implementation quality

The validator still consumes the Stage B Markdown policy-prose layer rather than raw Markdown. The new rules use small factor families rather than complete checker sentences: quantity/unit/trigger/target/safe context for C-M01; existing subject/action/repeat/mandatory/negation for C-M03A; and full set/scope/mandatory/sequence/no-skip/negation for C-M03B. This is the right structure, but the independently tested C-M03 vocabularies and composition rules remain incomplete. No complete-sentence allowlist or denylist was found in production validator code.

### C-M01 fixed-quantity thresholds — CLOSED

- Formal CLI mutations: 18/18 positive thresholds failed and 18/18 safe or factual expressions passed.
- The six required positives all failed, including `A 42-directory change requires independent planning.`, services/folders/packages/endpoints/documents variants, with `large-change-planning`, `package-prompt/fixed-quantity-risk-threshold`, matched prose, and non-empty `quantity`, `unit`, `trigger`, and `target` evidence.
- Twelve novel positives covered `19`, `64`, `two`, `eight`, `eleven`, `dozens`; classes, repositories, projects, folders, endpoints, components; and counts-as, mandates, must-trigger, qualifies-as, threshold, escalation, checker, formal-review, high-risk, and staged-workflow forms. All failed as required.
- Eighteen safe expressions covered must-not, never, cannot, does-not, not-required, may-remain-low-risk, example, count-alone, regardless-of-count, deterministic projections, and bare factual quantities. All passed. The validator does not reject every number-plus-unit occurrence.
- The release gate independently injected the `42-directory` default-prompt threshold, checked the formal category and structured evidence, restored both root/template YAML byte-for-byte, and passed after restoration.

### C-M03A existing-project reinitialization — OPEN

- All six required/original reinitialization positives failed via formal CLI, including the two previous checker misses: `An initialized project is required to go through project setup again before review.` and `Before review, reinitialize every previously initialized repository.` Diagnostics contained `project-init`, `existing-project-reinitialize`, and the matched prose.
- Novel expressions were only 8/10. These clear command/action-before-subject forms still passed the formal validator:
  - `Run the bootstrap process once more for repositories that are already initialized.`
  - `For each project that has already been initialized, run project setup again.`
- Safe expressions were only 11/12. `Existing repositories may continue to handover-review without repeating setup.` was incorrectly reported as `existing-project-reinitialize` despite expressing the safe continuation route without repeating setup.
- Because explicit new equivalents still escape and a normal safe sentence is falsely rejected, C-M03A remains OPEN and is MAJOR.

### C-M03B mandatory five-Skill pipeline — OPEN

- All seven required/original positives failed via formal CLI, including all three previous checker misses: one-by-one workflow, processed sequentially, and fixed-order variants. Diagnostics contained `project-init`, `mandatory-five-skill-pipeline`, and matched prose.
- Novel expressions were only 6/12. The following clear full-set mandatory equivalents still passed:
  - `Every request must complete each Stage C Skill before finishing.`
  - `The complete Stage C Skill set is a required chain for any change.`
  - `Every Stage C Skill is compulsory for every project request.`
  - `Each of the five Skills is mandatory for every task.`
  - `The complete set of five forms a prerequisite chain for each change.`
  - `All five Skills are required one at a time for any project request.`
- All 13 safe/alternative/optional/no-fixed-order/not-all/only-when-applicable expressions passed.
- The missed `compulsory`, `required chain`, and full-set mandatory forms are explicit equivalents inside the requested boundary, not complex metaphorical language. C-M03B remains OPEN and is MAJOR.

### Formal CLI and release mutation evidence

- Independent mutation repo included `.git`, used temporary commit `16f2647f96d31335eb0dbb8ca3035a2ff4935516`, preserved all positive markers, synchronized root/template and the temporary manifest, ran the production CLI for all 96 cases, and ended clean after every reset. The six former checker misses all returned non-zero with Skill/category/matched prose; the newly listed C-M03 misses returned zero.
- `scripts/test-release-consistency.ps1` passed in 255.4 seconds. Its directory-threshold, setup-again, and one-by-one mutations entered real policy/default-prompt files, asserted the formal validator category and prose, restored bytes, and the post-mutation baseline passed.
- All checker-created mutation repositories, behavior temp roots, fresh clones, and orphan processes were removed. No source-tree mutation remained.

### Minimal regression for findings kept CLOSED

- C-M02: projection check reported 9 Skills / 18 managed files and manifest check passed; Stage C package remains 10/10.
- C-M04: fenced/heading required-marker regression passed and the policy-prose layer remains in use.
- C-M05: SC-01..SC-05 and the ownership matrix still derive the same five-Skill set.
- C-M06: bounded-write/read-only evidence and explicit invocation idempotence regression passed.
- C-M07: synchronized bilateral CRLF rejection regression passed. Independent fresh-clone commit `4aafb972346f22e104ddd2584f42d61758ae9cdd` passed both `core.autocrlf=false` and `core.autocrlf=true`; blob and working-tree SHA-256 matched under `text: set`, `eol: lf`. Release consistency's independent fresh-clone baseline also passed.
- The six focused closed-finding regression tests passed 6/6.

### Tests and gates

| Target | Actual result |
| --- | --- |
| Independent formal CLI semantic cases | 87/96 matched expectation; 9 C-M03 failures detailed above |
| Stage C contract unittest | 28/28 PASS |
| Closed-finding focused regression | 6/6 PASS |
| Full unittest discovery | 163/163 PASS |
| Stage C validator | PASS |
| Projection / manifest / ownership / agent-entry validators | PASS |
| Development migration validator | PASS |
| Behavior validate | PASS, 13 cases |
| Behavior dry-run | PASS using an isolated `D:\tmp` temp root; records remain `GRADER_UNCERTAIN/not-run` and cleanup passed |
| Fresh-clone LF/CRLF gate | PASS, temporary commit `4aafb972346f22e104ddd2584f42d61758ae9cdd` |
| Template validation | PASS |
| Release consistency restoring mutations | PASS |
| `git diff --check` before writeback | PASS |

Initial non-elevated runs of the D:\tmp-backed unittest/fresh-clone/template checks stalled or hit sandbox cleanup permissions. Each was rerun with the required filesystem permission and then passed; checker-owned orphan processes and exact temporary directories were removed. This environment issue does not change the C-M03 semantic findings.

### BLOCKER

None.

### MAJOR

1. C-M03A remains OPEN: two clear existing-project reinitialization commands pass the formal validator, and one safe continuation sentence is falsely rejected.
2. C-M03B remains OPEN: six clear universal/full-set mandatory pipeline equivalents pass the formal validator, including the explicitly required `compulsory for every project request` form.

### NOTE

1. C-M01 is CLOSED; C-M02/C-M04/C-M05/C-M06/C-M07 remain CLOSED and were not reopened.
2. More complex natural language may remain outside a finite static gate. The failure here relies only on clear, requested equivalents.
3. Real Codex/Claude behavior, selector/Skill-source/token-context effects, and manual merge experience remain `NEEDS_TEST`; these are not failure reasons.

### Stage decision

Stage C final C-M01/C-M03 recheck FAILS. Status remains `stage-c-implemented-awaiting-independent-check`. Stage C is not approved and Stage D is not authorized.

`VERSION` remains `0.44.1`. No real model prompt was executed. No formal v0.45.0 release migration was created. v0.45.0 is not release-ready. This checker did not implement fixes, enter Stage D/E, commit, push, tag, release, deploy, or modify/stage/restore the user's deleted `usage.html`.
## Stage C Final C-M03 Recheck

- Date: 2026-07-21
- Checker: Codex independent checker (`/root`)
- Stage B baseline: `d02b496971db3773ac0c1435a423198189d6d8d8`
- Scope: only C-M03A existing-project reinitialization and C-M03B mandatory full-Skill execution. C-M01/C-M02/C-M04/C-M05/C-M06/C-M07 remained CLOSED and received only the requested minimal regression.
- Decision: `FAIL`. C-M03A remains OPEN; C-M03B is CLOSED. There are 0 BLOCKER and 1 MAJOR. Status remains `stage-c-implemented-awaiting-independent-check`; Stage D is not authorized.

### Feature model

The production validator uses sentence-level, order-independent feature families rather than a complete-sentence denylist. C-M03A evaluates `existing_subject`, `init_action`, `repeat_action`, `positive_requirement`, `negated_init`, and `alternative_route`; C-M03B evaluates `full_skill_set`, `universal_scope`, `mandatory`, `sequence`, `non_skippable`, and `negated_pipeline`. Its three pipeline branches are full-set/scope/mandatory, full-set/scope/sequence, and non-skippable/scope. Diagnostics contain Skill, category, matched prose, and enabled features. The closed C-M04 policy-prose extractor remains the input layer.

### Nine checker scenarios

All nine historical checker scenarios now satisfy their expected formal CLI result in an isolated Git repository:

- Reinitialize positives `Run the bootstrap process once more for repositories that are already initialized.` and `For each project that has already been initialized, run project setup again.` returned 1 with `project-init`, `existing-project-reinitialize`, matched prose, and `features=existing_subject,init_action,repeat_action,positive_requirement`.
- Safe `Existing repositories may continue to handover-review without repeating setup.` returned 0; `without repeating setup` and the handover alternative route no longer produce a finding.
- All six former pipeline misses returned 1 with `mandatory-five-skill-pipeline`, matched prose, and features. The two expressions without sequence words — `Every Stage C Skill is compulsory for every project request.` and `Each of the five Skills is mandatory for every task.` — were rejected through full-set/scope/mandatory rather than a sequence requirement.

### C-M03A — OPEN

- Fixed positives: 6/6 failed as required.
- Fixed safe expressions: 6/6 passed.
- Checker scenarios: 3/3 matched expectation.
- Independent novel positives: only 4/6 failed. Two clear command forms still passed the formal validator with exit 0 while all original contract markers remained present:
  - `Bootstrap an already initialized repository again.`
  - `Set up each existing workspace from scratch.`
- Independent novel safe/alternative expressions: 6/6 passed, covering without, must-not, not-required, handover-review and project-bootstrap-fill alternatives.

Both missed sentences contain an existing/initialized subject, an initialization/setup/bootstrap action, repeat/from-scratch semantics, and an imperative positive requirement. The feature implementation recognizes only selected imperative lead verbs and does not recognize `Bootstrap ...` or phrasal `Set up ...` as the complete positive feature set. Because explicit command-form reinitialization remains undetected, C-M03A remains OPEN and is MAJOR.

### C-M03B — CLOSED

- Six historical checker misses: 6/6 failed with category, matched prose and feature evidence.
- Fixed positives: 7/7 failed.
- Fixed safe expressions: 8/8 passed.
- Eight independent novel mandatory expressions without `sequential`, `sequence`, `order`, `pipeline`, or `workflow`: 8/8 failed. They covered every/all/each/full-set, every task/request/change/project/all-work, compulsory/required/must/has-to, and no-skip forms.
- Seven independent safe expressions covering alternatives, optional, not-every, need-not-use-all, only-matching, no-fixed-order and only-when-applicable: 7/7 passed.

C-M03B no longer requires sequence vocabulary for every violation and is CLOSED.

### Formal CLI and release mutation

- The independent mutation repository contained `.git`, used temporary commit `192993ba63a2f074d9d06dfb86df28fa6d6f8a86`, synchronized root/template/manifest in the temporary tree, and ran the production CLI for all 63 cases. Result: 61/63 matched expectation; the two failures are the C-M03A novel command forms above. The temporary repository ended clean and was destroyed.
- Release consistency contains and passed real restoring mutations for setup-again, action-first bootstrap-once-more, one-by-one pipeline, and full-set mandatory without sequence. Each asserted category/matched prose/features, restored root/template bytes, and the post-mutation baseline passed.

### Closed-finding minimal regression

- C-M01: directory threshold rejection and safe quantity expression passed.
- C-M02: projection targets remain 18/18 and Stage C package files 10/10; manifest check passed.
- C-M04: fenced required marker cannot fake the contract; safe negation passed.
- C-M05: tasks and ownership matrix still each derive the same five-Skill set.
- C-M06: disabling bounded-write evidence fails; an existing explicit marker is not duplicated.
- C-M07: bilateral CRLF plus synchronized manifest still fails. Fresh-clone temporary commit `ea2a14f35d8217b8fa9d354edf5f8bfb79bd91cc` passed `core.autocrlf=false` and `true` with blob bytes equal to working-tree bytes.
- Focused closed-finding regression: 8/8 PASS.

### Tests and formal gates

| Target | Actual result |
| --- | --- |
| Independent C-M03 formal CLI cases | 61/63 matched expectation |
| Stage C unittest | 28/28 PASS |
| Full unittest discovery | 163/163 PASS |
| Closed-finding focused regression | 8/8 PASS |
| Stage C validator | PASS |
| Projection / manifest / ownership / agent-entry validators | PASS |
| Development migration validator | PASS |
| Behavior validate / dry-run | PASS; 13 cases, grader remains `GRADER_UNCERTAIN/not-run` |
| Fresh-clone LF/CRLF | PASS; commit `ea2a14f35d8217b8fa9d354edf5f8bfb79bd91cc` |
| Template validation | PASS |
| Release consistency restoring mutations | PASS in 255.8 seconds |
| `git diff --check` before writeback | PASS |

### BLOCKER

None.

### MAJOR

1. C-M03A remains OPEN because the formal validator accepts two explicit imperative reinitialization requirements: `Bootstrap an already initialized repository again.` and `Set up each existing workspace from scratch.`

### NOTE

1. C-M03B is CLOSED. C-M01/C-M02/C-M04/C-M05/C-M06/C-M07 remain CLOSED.
2. More complex natural language may exceed a finite static gate; the MAJOR above relies only on direct command forms within the required feature model.
3. Real Codex/Claude behavior, selector/Skill-source/token-context effects, and manual merge experience remain `NEEDS_TEST`; these are not failure reasons.

### Stage decision

Stage C final C-M03 recheck FAILS. Status remains `stage-c-implemented-awaiting-independent-check`. Stage C is not approved and Stage D is not authorized.

`VERSION` remains `0.44.1`. No real model prompt was executed. No formal v0.45.0 release migration was created. v0.45.0 is not release-ready. This checker did not implement fixes, enter Stage D/E, commit, push, tag, release, deploy, or modify/stage/restore the user's deleted `usage.html`.

## Stage C Final Imperative Reinitialize Recheck

- Date: 2026-07-21
- Checker: Codex independent checker (`/root`)
- Stage B baseline: `d02b496971db3773ac0c1435a423198189d6d8d8`
- Scope: only C-M03A imperative existing-project reinitialization. C-M01/C-M02/C-M03B/C-M04/C-M05/C-M06/C-M07 remained CLOSED and received only the requested minimal regression.
- Decision: `FAIL`. C-M03A remains OPEN. There are 0 BLOCKER and 1 MAJOR. Status remains `stage-c-implemented-awaiting-independent-check`; Stage D is not authorized.

### Implementation and feature model

The validator uses sentence-level features and the shared Markdown policy-prose extractor; no complete-sentence special case for the two historical misses was found. It covers the `bootstrap` inflections, adjacent and separated `set up`, sentence-initial commands, and allowed `Before ...` / `For each|every|any ...` prefaces. Analysis-only normalization leaves matched prose unchanged. The Boolean contract remains `existing_subject AND init_action AND repeat_action AND positive_requirement AND NOT negated_init AND NOT alternative_route`.

The positive implementation is structurally sound, but its negation vocabulary is not morphologically aligned: passive `bootstrapped` is an initialization action but is not recognized after `must not` by `negated_init`.

### Historical commands and supplementary positives

- `Bootstrap an already initialized repository again.`: formal CLI exit 1 with `project-init`, `existing-project-reinitialize`, complete matched prose, and `features=existing_subject,init_action,repeat_action,positive_requirement`.
- `Set up each existing workspace from scratch.`: formal CLI exit 1 with the same category and feature evidence.
- Supplementary positives: 11/11 correctly rejected. They covered sentence-initial bootstrap, `Before` / `For each` prefaces, adjacent/separated `set up`, passive `be set up`, all requested bootstrap inflections, and repeat forms `again`, `once more`, `anew`, and `from scratch`.
- The independent `.git` mutation repository used temporary commit `567ae670d1ce3a95a136419a8fd1105c10787986`, retained positive markers, synchronized root/template/manifest in isolation, restored every case byte-for-byte, and was destroyed.

### Safety, word boundaries, and Markdown

- Required `Do not`, `Never`, `without`, `instead of`, explanatory, example-only, noun, and handover-continuation expressions passed. The straight-quoted ASCII equivalent of the `set up` example was used because Skill files are ASCII-only.
- `bootstrappable`, `bootstrapper`, `setup-like`, `upset`, inline code, fenced legacy prose, and a Skill path did not trigger.
- Safe coverage was only 19/20: `An already initialized project must not be bootstrapped again.` incorrectly returned exit 1 with `project-init [existing-project-reinitialize]` and all four positive features. This common passive negative is neither ambiguous nor complex. Negation precedence is therefore incomplete.

### Release mutation and minimal regression

- Release consistency's imperative bootstrap-again and phrasal-set-up mutations entered real policy prose, asserted category/matched prose/features, restored root/template bytes, and passed after restoration.
- The requested minimal regressions for C-M01/C-M02/C-M03B/C-M04/C-M05/C-M06/C-M07 passed 9/9: directory threshold and safe context; manifest 18/18 and Stage C package 10/10; mandatory full-set without sequence; fenced marker and safe negation; dual-source five-Skill set; bounded-write evidence and explicit idempotence; bilateral CRLF plus synchronized-manifest rejection.
- Fresh-clone temporary commit `3e6750d732952d4fda2c6130ce4a4aa78f0ae976` passed `core.autocrlf=false` and `true`; Stage C, migration, projection, and template checks passed without post-checkout overlay.

### Tests and gates

| Target | Actual result |
| --- | --- |
| Independent C-M03A formal CLI | 32/33: positive 13/13, safe 19/20 |
| Historical imperative commands | 2/2 correctly rejected |
| Stage C unittest | 28/28 PASS |
| Full unittest discovery | 163/163 PASS |
| Closed-finding focused regression | 9/9 PASS |
| Stage C / projection / manifest / ownership / agent-entry / migration | PASS |
| Behavior validate / dry-run | PASS; 13 cases, `GRADER_UNCERTAIN/not-run` |
| Fresh-clone LF/CRLF | PASS; commit `3e6750d732952d4fda2c6130ce4a4aa78f0ae976` |
| Template validation | PASS |
| Release consistency restoring mutations | PASS in 281 seconds |
| `git diff --check` before writeback | PASS |

### BLOCKER

None.

### MAJOR

1. C-M03A remains OPEN because `An already initialized project must not be bootstrapped again.` is falsely rejected. The positive family recognizes `bootstrapped`, but the `must not` negation family does not give that inflection safe scope.

### NOTE

1. Both historical imperative misses are fixed; all 13 positive variants were caught.
2. C-M01/C-M02/C-M03B/C-M04/C-M05/C-M06/C-M07 remain CLOSED.
3. Complex language, real model behavior, selector/Skill-source/token-context effects, and manual merge experience remain non-blocking `NEEDS_TEST` notes.

### Stage decision

C-M03A remains OPEN. Stage C FAILS this recheck, status remains `stage-c-implemented-awaiting-independent-check`, and Stage D is not authorized.

`VERSION` remains `0.44.1`. No real model prompt was executed. No formal v0.45.0 release migration was created. v0.45.0 is not release-ready. No fix, Stage D/E work, commit, push, tag, release, deploy, or change to the user's deleted `usage.html` was performed.

## Stage C Closed Final Recheck

- Date: 2026-07-21
- Checker: Codex independent checker (`/root`)
- Scope: closed verification of C-M03A initialization-action positive/negative morphology only. No matrix-external synonym fuzzing or new semantic category was introduced. C-M01/C-M02/C-M03B/C-M04/C-M05/C-M06/C-M07 remained CLOSED.
- Decision: `PASS WITH NOTES`. C-M03A is CLOSED. Stage C status is `stage-c-approved-for-stage-d`; Stage D is authorized but was not implemented in this review.

### Implementation confirmation

- The competing `NEGATED_INIT_PATTERNS` action vocabulary is absent.
- `INIT_ACTION_SPECS` is the single action vocabulary. `find_init_action_matches()` returns `start`, `end`, normalized `family`, and original `text`; directive feature detection, imperative detection, and local negation consume those shared matches.
- No complete fixed-matrix sentence special case was found. The C-M03A Boolean contract remains `existing_subject AND init_action AND repeat_action AND positive_requirement AND NOT negated_init AND NOT alternative_route`.
- C-M03B and the other closed findings were not changed or reopened by this recheck.

### Original false positive and positive control

- `An already initialized project must not be bootstrapped again.` returned 0 and did not report `existing-project-reinitialize`. The matcher recorded span `43..55`, family `bootstrap`, original text `bootstrapped`, and local negation `true`.
- `An already initialized project must be bootstrapped again.` returned 1 with `project-init [existing-project-reinitialize]`, complete matched prose, and `features=existing_subject,init_action,repeat_action,positive_requirement`. The action used family `bootstrap`, text `bootstrapped`, and negation `false`.

### Fixed matrix and minimal regression

- Fixed matrix: 14/14 matched expectation. Bootstrap was 3/3 safe plus 3/3 positive; set-up was 2/2 safe plus 2/2 positive; initialize/reinitialize was 2/2 safe plus 2/2 positive.
- Across the original pair, fixed matrix, and three minimal regression sentences, formal CLI was 19/19: 9/9 safe returned 0 and 10/10 positive returned non-zero with the required category/prose/features.
- No tested action family showed positive recognition with missing negative recognition. Span/family/original-text evidence was present for bootstrap, set-up, initialize, reinitialize, and the existing repeat-init handover sentence.
- `Bootstrap an already initialized repository again.` and `Set up each existing workspace from scratch.` still failed. `Existing repositories may continue to handover-review without repeating setup.` still passed.
- C-M01 and C-M03B remained CLOSED. Projection targets were 18/18 and Stage C package files were 10/10.
- Fresh-clone temporary commit `805fe258f2212f59a0aa176bcfb3e3618b507b39` passed `core.autocrlf=false` and `core.autocrlf=true` without post-checkout overlays.

### Tests and gates

| Target | Actual result |
| --- | --- |
| Fixed formal CLI matrix plus controls/regressions | 19/19 PASS |
| Stage C validator | PASS |
| Stage C unittest | 29/29 PASS |
| Full unittest discovery | 164/164 PASS |
| Projection / manifest | PASS; 18/18 targets, Stage C package 10/10 |
| Fresh-clone LF/CRLF | PASS; commit `805fe258f2212f59a0aa176bcfb3e3618b507b39` |
| Template validation | PASS |
| Release consistency | PASS in 288.2 seconds; negated/positive bootstrapped guards and byte restoration passed |
| `git diff --check` before writeback | PASS |

### BLOCKER / MAJOR / NOTE

- BLOCKER: none.
- MAJOR: none.
- NOTE: matrix-external complex natural language and real Codex/Claude behavior remain `NEEDS_TEST`; selector, Skill-source, token/context effects, and manual merge experience remain non-blocking future evidence.

### Stage decision

C-M03A is CLOSED. Stage C passes with notes, status is `stage-c-approved-for-stage-d`, and entry into Stage D is allowed. This review stops before Stage D implementation.

`VERSION` remains `0.44.1`. Real model behavior remains `NEEDS_TEST`. No formal v0.45.0 migration was created. No commit, push, tag, release, or deployment was performed, and the user's deleted `usage.html` was not restored, modified, or staged.

## Stage D Independent Review

- Date: 2026-07-21
- Checker: Codex independent checker (`/root`)
- Baseline branch / commit: `main` / `868846da54634899141047951b0f4275ad378966` (`feat(governance): implement v0.45 stage C skill convergence`)
- Reviewed state: `stage-d-implemented-awaiting-independent-check`
- Scope: the four Stage D Skills, their package prompts and template projections, behavior cases, finite validator and mutations, development migration draft, gate wiring, tests, scoped smoke, and LF/CRLF fresh clones. No Stage D redesign or open-ended synonym fuzzing was performed.
- Decision: **FAIL**. Status remains `stage-d-implemented-awaiting-independent-check`; Stage E is not authorized.

### Four-Skill responsibility, routing, and authorization

| Skill | Responsibility / trigger result | Read-only and external-action result | Stage D result |
| --- | --- | --- | --- |
| `code-review` | Correctly limited to existing implementation/diff/tests/evidence, initial review, independent checker, and findings recheck. It emits `BLOCKER` / `MAJOR` / `NOTE`, uses `NEEDS_TEST`, does not absorb security/release, and does not use file/line/module counts as the checker trigger. | Default read-only; finding discovery is not repair authority; a separately authorized maker is path-bounded and records changed-path plus validation evidence; recheck returns to read-only. Commit/push/tag/release/deploy remain separately authorized. | Body contract PASS; shared validator finding below prevents Stage D approval. |
| `security-review` | Correctly limited to explicit or real auth/authz, secret/credential/token, sensitive-data, command, path/file, network/external-system, dependency/supply-chain, production/security-sensitive boundaries. Ordinary code/backend/config/style work is not enough. | Default read-only and report-only; no automatic fix or external action. | **MAJOR**: bounded-fix text requires writable paths and changed-path evidence but omits validation evidence. |
| `release-check` | Correctly limited to release/version/migration/package/tag/RC/publication/readiness. Ordinary commits, daily tests, and non-release review are excluded. Decision vocabulary is exactly `ready`, `blocked`, or `not-verified`. | Default read-only; no automatic VERSION bump, formal migration, tag, push, publish, release, or deploy. | **MAJOR**: bounded metadata-fix text requires writable paths and validation evidence but omits changed-path evidence. |
| `project-suitability` | Correctly evaluates ForgeKit fit, full/constrained/light/no adoption, cost, constraints, governance conflict, and possible prior read-only audit. Results are `suitable`, `suitable-with-constraints`, `not-recommended`, or `insufficient-evidence`. | Read-only advisory by default; no `.forgekit` creation, init, Git init, entry rewrite, rule migration, governance overwrite, or automatic Skill pipeline. | Body contract PASS; shared validator finding below prevents Stage D approval. |

The primary routing remains implemented diff -> `code-review`, actual security boundary -> `security-review`, release readiness -> `release-check`, and ForgeKit adoption fit -> `project-suitability`. Multiple Skills may be selected for actual risk, but the four are not a mandatory pipeline. Review authorization is not write authorization; local write authorization is not external-action authorization; internal stage authorization is not push/release authorization.

### Package and default prompts

- All four `agents/openai.yaml` files contain only supported `interface` fields: `display_name`, `short_description`, and `default_prompt`. No invented policy metadata was added.
- Each default prompt contains exactly one standalone matching marker: `$code-review`, `$security-review`, `$release-check`, or `$project-suitability`. No prompt invokes another Stage D Skill or forms a pipeline.
- Root and template packages are byte-identical. Public Skill IDs, frontmatter names, and display names are unchanged from the baseline commit. Default prompts do not expand the corresponding `SKILL.md` authority.

### Behavior cases and evidence contract

- Manifest validation and listing passed with 31 total cases: 13 earlier cases plus 18 Stage D cases. Stage D distribution is code-review 4, security-review 4, release-check 5, and project-suitability 5.
- The cases cover initial review, recheck, no automatic repair, one bounded maker case, security positive/negative/report-only/boundary cases, release readiness/ordinary commit/version-migration-manifest/no external action/insufficient evidence, and suitability new/mature/not-recommended/insufficient/no-auto-init cases.
- Explicit invocation markers are inserted into the rendered adapter prompt exactly once; implicit prompts remain unmodified. Read-only cases require write-behavior evidence and empty allowlists; bounded-write cases require non-empty allowed paths; forbidden external actions require tool-trace evidence.
- Dry-run executed all 31 cases, invoked no real client, produced no changed paths, cleaned its workspaces, and correctly reported `GRADER_UNCERTAIN` / `not-run`. Real Codex/Claude prompt behavior remains `NEEDS_TEST`.

### Validator and finite acceptance corpus

- `scripts/validate-stage-d-skills.py` correctly derives exactly SD-01..SD-04 from `tasks.md`, derives four Stage D ROUTE owners from the 41-rule ownership matrix, requires equal sets, verifies owner/package/projection, requires one package marker, checks default read-only, some bounded-write and external-action markers, and uses finite regex categories rather than a general natural-language analyzer.
- The validator baseline passes, but its bounded-write evidence expression is an OR: `(?:changed-path|validation) evidence`. This accepts a contract that supplies only one required evidence dimension.
- The six formal mutations all failed non-zero with the expected category and byte restoration: automatic maker, security always-on, ordinary-commit release-check, suitability auto-init, mandatory four-Skill pipeline, and fixed-count checker threshold.
- Eight additional finite scenarios were run in an isolated Git repository and restored byte-for-byte. The validator rejected 3/8: reviewer automatically modifies tests (`review-auto-maker`), removal of bounded writable-path/evidence text (`required-contract`), and removal of default read-only (`required-contract`). It incorrectly accepted 5/8 with exit 0:
  1. `Finding a defect directly authorizes repair.`
  2. `Every ordinary backend change must run security review.`
  3. `Treat every ordinary commit as a release and run release-check.`
  4. `After every suitability assessment, automatically create .forgekit.`
  5. `Internal stage authorization automatically permits push and release.`
- These five are not open-ended rare synonyms: they are direct instances of the frozen finding/maker, ordinary-backend/security, ordinary-commit/release, suitability/init, and internal/external authorization categories. Final validator baseline passed after every restoration.

### BLOCKER / MAJOR / NOTE

- BLOCKER: none. No unauthorized real-worktree write, reviewer-to-maker transition, external action, custom/unknown migration overwrite, rollback failure, or Stage E work occurred.
- **MAJOR M-D01 — incomplete bounded-write evidence contract.** `skills/security-review/SKILL.md:18` omits validation evidence; `skills/release-check/SKILL.md:18` omits changed-path evidence. `scripts/validate-stage-d-skills.py:115` requires either changed-path or validation evidence instead of both, so the current incomplete contracts pass.
- **MAJOR M-D02 — systematic failure of the finite semantic contract.** The formal validator accepted all five contradictory scenarios listed above, including frozen ordinary-backend/security, ordinary-commit/release, suitability/init, finding-to-repair, and internal-stage-to-external-action boundaries. The narrow official sentences still fail, but the structured gate does not protect the frozen categories as a whole.
- NOTE: real model routing, selector behavior, Skill-source observation, token/context effects, and manual merge experience remain `NEEDS_TEST`.
- NOTE: `D:\tmp\fc-ge1jyo7z` (created 2026-07-21 22:27, containing `lf`, `s`, and `t`) existed before this checker run and remains an old fresh-clone residue. It was not created or deleted by this review. All temporary trees created by this checker were cleaned.

### Projection, manifest, and development migration

- Root `skills/` remains the unique semantic source. All 18 projection files are root/template byte-identical; the Stage D subset is 8/8. The template manifest covers 18/18 projection targets with no duplicate, and Stage C's five Skills plus `.claude/skills/` have no diff.
- One-sided Stage D YAML drift failed projection check. Removing `.agents/skills/release-check/agents/openai.yaml` from the template manifest failed with the missing target. Synchronized root/template YAML without updating the manifest passed projection equality but failed manifest checksum. Every path was restored and both checks then passed.
- The change-local draft contains 20 unique actions, including 8 Stage D targets. Each Stage D `baseline_commit` is exactly `868846da54634899141047951b0f4275ad378966`; all eight baseline fixtures equal that Git object's raw bytes, all eight incoming fixtures equal the current template projection, and all 16 fixture paths are present with no duplicate.
- Migration validation passed stock/custom/unknown/missing/mixed/rollback and same-path origin rollback. Production discovery does not expose the draft. No formal `migrations/0.45.0` exists.

### Gate wiring and executed tests

- The diffs in `scripts/smoke-test.py`, `scripts/test-fresh-clone-crlf.py`, `scripts/validate-plugin-assets.ps1`, `scripts/validate-template.ps1`, and `scripts/test-release-consistency.ps1` only register Stage D validators/tests/fixtures or replace obsolete Stage D content markers with the new contract markers. No Stage A-C gate, exit code, warning/error, raw-byte/LF contract, or production behavior was relaxed.
- Directed Stage D unittest: 11/11 PASS. Stage D migration identity tests: 2/2 PASS. Full unittest discovery: 177/177 PASS. Behavior manifest: 31/31 structurally valid; dry-run 31/31 `GRADER_UNCERTAIN/not-run` with zero changed paths.
- Stage D, projection, manifest, ownership (41 rules), agent entries, Stage C, development migration, plugin assets, template, release consistency, scoped smoke, and `git diff --check` passed. Release consistency's six Stage D mutations and all 18 managed projection mutations failed as expected and restored bytes.
- Scoped snapshot commit `dd6b0f0d348b45338034959b8c61bd05d61fa0d3` passed release consistency and smoke after an isolated dirty-input marker was restored. The marker was needed only because the release-consistency harness expects a dirty maker input when it constructs its nested fresh-clone commit.
- Fresh-clone full gate used temporary commit `5e3e569a6ef34b7731c9b4a6107de178b02d8d7a`. The scoped snapshot, `core.autocrlf=false` clone, and `core.autocrlf=true` clone all passed Stage C, Stage D, migration, projection, template, and full smoke. Git blobs equaled checked-out bytes; no tracked-byte overlay was applied after cloning; the user's `usage.html` deletion was excluded.

### Stage decision and closure

Stage D does not pass because M-D01 and M-D02 are open. Status remains:

`stage-d-implemented-awaiting-independent-check`

Stage E is not allowed. `VERSION` remains `0.44.1`; real model prompts were not executed; no formal v0.45.0 migration was created; v0.45.0 is not release-ready. No maker implementation, tasks, verification, ship, VERSION, formal migration, `usage.html`, commit, push, tag, release, publication, or deployment was changed or performed by this checker.
## Stage D M-D01 M-D02 Recheck

- Date: 2026-07-22
- Checker: Codex independent checker (`/root`)
- Baseline branch / commit: `main` / `868846da54634899141047951b0f4275ad378966` (`feat(governance): implement v0.45 stage C skill convergence`)
- Recheck scope: only M-D01, the five frozen M-D02 responsibility/authorization categories, their safe controls, the original six Stage D mutations, and the requested minimal regressions. Previously passed Skill responsibilities, default read-only and external-action body boundaries, package contract, behavior base contract, projection, migration classification, LF/raw-byte/fresh-clone, and Stage A-C findings were not reopened.
- Decision: **PASS WITH NOTES**. M-D01 and M-D02 are CLOSED. Stage D status is `stage-d-approved-for-stage-e`; Stage E is allowed after Stage D is submitted, but was not implemented in this recheck.

### M-D01: bounded-write evidence

- All four Stage D Skills now use the same bounded-write conjunction: a separate and explicit named repair/recording authorization, non-empty explicit writable paths, changed-path evidence, validation evidence, and no expansion to another finding, path, project, or external action.
- `scripts/validate-stage-d-skills.py` defines and checks `changed_path_evidence` and `validation_evidence` as separate structured features within the same non-example writable-path contract segment. The prior `changed-path OR validation` expression is absent.
- The six required mutations all returned non-zero with the expected category: security-review without validation evidence; release-check without changed-path evidence; code-review with only changed-path evidence; project-suitability with only validation evidence; generic `evidence required`; and evidence present only in fenced example text. The generic and fenced cases reported both `missing-changed-path-evidence` and `missing-validation-evidence`.
- Every mutation changed both root and template copies inside an isolated repository containing `.git`, then restored the original bytes. The restored validator passed and the isolated repository was Git-clean before deletion.

### M-D02: five frozen categories and safe controls

The five sentences from the first Stage D Independent Review were all rejected by the formal CLI with Skill, category, matched prose, and structured feature names:

| Skill | Frozen mutation | Category | Structured features |
| --- | --- | --- | --- |
| `code-review` | `Finding a defect directly authorizes repair.` | `finding-auto-authorizes-repair` | `finding,permission,repair` |
| `security-review` | `Every ordinary backend change must run security review.` | `ordinary-change-requires-security-review` | `ordinary_change,mandatory,security_review` |
| `release-check` | `Treat every ordinary commit as a release and run release-check.` | `ordinary-commit-is-release` | `ordinary_commit,automatic_release,release` |
| `project-suitability` | `After every suitability assessment, automatically create .forgekit.` | `suitability-auto-initialization` | `suitability,automatic,initialization` |
| `code-review` | `Internal stage authorization automatically permits push and release.` | `internal-authorization-external-action` | `internal_authorization,permission,external_action` |

- The five required safe expressions passed: findings require separate repair authorization; ordinary backend/config changes alone do not require security-review; ordinary commits are not releases; suitability is read-only and does not initialize; internal authorization does not permit external action.
- One bounded structural companion per category also passed, for 10/10 safe controls in total. No open-ended fuzzing or matrix-external synonym expansion was performed.
- The original formal six mutations remained closed, 6/6: automatic maker, security always-on, ordinary-commit release-check, suitability auto-init, mandatory four-Skill pipeline, and fixed-count checker threshold all returned non-zero with their expected categories.

### Minimal regression evidence

- Package markers: 4/4 packages contain exactly one matching standalone marker and no other Stage D marker: `$code-review`, `$security-review`, `$release-check`, and `$project-suitability`.
- Behavior: manifest validation passed with 31 cases. The bounded-write case has a non-empty allowed path, write-behavior evidence, changed-path evidence in expected behavior, and validation evidence; recheck remains read-only. Dry-run completed with no real client and correctly remained `GRADER_UNCERTAIN/not-run`.
- Projection and manifest: 9 projected Skills x 2 managed files = 18/18 byte-identical targets; the manifest covers 18 Skill files with no duplicate source path.
- Development migration: validator passed 20 actions, including 8 unique Stage D targets. Stock/custom/unknown/missing/mixed/rollback and same-path origin rollback passed. No formal `project-template/migrations/0.45.0` exists.
- Fresh clone: the exact non-full fresh-clone command passed a temporary commit that excluded the user's `usage.html` deletion. Both `core.autocrlf=false` and `core.autocrlf=true` clones passed Stage C, Stage D, migration, projection, and template checks without post-clone overlays.
- Release consistency ran only in a short-path isolated Git snapshot. All Stage D responsibility/evidence mutations and projection mutations failed as expected, safe negations passed, every file was restored byte-for-byte, the nested fresh-clone gate passed, the isolated repository ended clean, and the directory was removed.

### Tests and gates

| Target | Actual result |
| --- | --- |
| Stage D validator | PASS; 4 Skills dual-source locked |
| Stage D unittest | 18/18 PASS |
| Full unittest discovery | 184/184 PASS |
| Behavior validate / dry-run | PASS; 31 cases; real model `GRADER_UNCERTAIN/not-run` |
| Projection / manifest | PASS; 18/18 managed files |
| Development migration | PASS; 20 actions, 8 Stage D targets |
| Fresh-clone LF/CRLF | PASS; `core.autocrlf=false/true`, no overlay |
| Template validation | PASS |
| Release consistency | PASS in isolated Git snapshot; byte restoration and clean state confirmed |
| `git diff --check` | PASS before writeback |

### BLOCKER / MAJOR / NOTE

- BLOCKER: none.
- MAJOR: none. M-D01 and M-D02 are CLOSED; no previously closed structured contract was reopened.
- NOTE: real Codex/Claude prompts were not executed, so model routing and behavior remain `NEEDS_TEST`. Matrix-external rare or complex language remains NOTE/NEEDS_TEST and did not extend this recheck.
- NOTE: the pre-existing `D:\tmp\fc-ge1jyo7z` residue documented by the first Stage D review remains untouched. All temporary repositories and workspaces created by this recheck were cleaned; no recheck mutation, clone, cache, packet, or evidence directory remains.

### Stage decision

Stage D passes with notes. M-D01 is CLOSED and M-D02 is CLOSED. Status is:

`stage-d-approved-for-stage-e`

Stage E is allowed after Stage D is submitted. This recheck stops before Stage E and does not implement it.

`VERSION` remains `0.44.1`. Real model behavior remains `NEEDS_TEST`; no real model prompt was executed. No formal v0.45.0 migration was created, and v0.45.0 is not release-ready. No maker implementation, Stage E work, commit, push, tag, release, publication, deployment, or change to the user's deleted `usage.html` was performed.

## Stage E Independent Release Preparation Review

Review date: 2026-07-22. This was a limited-scope independent review. The source worktree was read-only except for this append; mutations and temporary commits were confined to disposable Git copies.

### Baseline, scope, and lifecycle

- Branch `main`; HEAD and sole baseline `1aca83de2c68db0eab624eaabad9a85197ef0faf` (`feat(governance): implement v0.45 stage D review skill convergence`); staged files zero.
- The user's pre-existing unstaged deletion of `usage.html` remained deleted, unstaged, and untouched. The nine root Skill bodies/package YAML, root `AGENTS.md`, root `CLAUDE.md`, `.claude/skills/`, and this review file had no maker diff.
- Stage E did not reopen frozen rule ownership, slim-entry, Skill responsibility/authorization, Stage C/D categories, behavior evidence, projection, raw-byte/LF, or migration-algorithm contracts.
- Stage C matrix: `0.44.1/0.44.1` PASS; `0.45.0/0.45.0` PASS; both crossed pairs FAIL nonzero with category `current-version-mismatch`, both actual values, and both paths. No check was deleted, downgraded, or state-bypassed.
- Pre-release `0.44.1` rejects a formal 0.45.0 migration, validates the draft, excludes it from production discovery, and retains pre-release latest. Release-preparation `0.45.0` requires the formal migration, discovers exactly one production 0.45.0, enforces `0.44.1 -> 0.45.0`, validates the draft, and excludes it from production discovery.
- Missing formal migration, wrong from/to, directory/descriptor mismatch, duplicate production 0.45.0, and draft introduced under the production root all fail nonzero with locating categories.

### Formal migration inventory

- Root and template `migrations/0.45.0/` each contain 41 files: one descriptor, 20 baseline payloads, and 20 incoming payloads. Inventories and corresponding raw bytes are identical, with no duplicate, omission, or extra action.
- The 20 actions are: `AGENTS.md`; `CLAUDE.md`; and `SKILL.md` plus `agents/openai.yaml` for each of `project-init`, `project-bootstrap-fill`, `handover-review`, `document-backfill`, `large-change-planning`, `code-review`, `security-review`, `release-check`, and `project-suitability`.

### Baseline provenance and incoming

- Both entry baselines match raw Git bytes at `506cecf8d377a17a2616bf3b9eeea483ee4039a4`; all ten Stage C baselines match `d02b496971db3773ac0c1435a423198189d6d8d8`; all eight Stage D baselines match `868846da54634899141047951b0f4275ad378966`.
- Every descriptor baseline checksum matches its payload and provenance object. Baselines were not derived from one Stage D HEAD or current incoming files.
- Every incoming payload matches the final `project-template` target and descriptor checksum in raw bytes. Root/template formal payloads and the validated draft agree; equality did not depend on newline normalization, and LF holds.

### Production discovery and migration behavior

- Production discovery searches the production root only, finds one 0.45.0, ignores the change-local draft, and does not treat the template copy as a second root migration. Current/latest/planned evidence was `0.44.1` / `0.45.0` / `0.45.0`, pending count one.
- Duplicate version, invalid identity, and directory/version mismatch mutations fail. The formal migration, not only the draft, passed stock, custom, unknown, missing, and mixed scenarios.
- Stock upgrades automatically. Custom and unknown files remain byte-for-byte unoverwritten. Missing is safe; mixed is classified per action. Rollback restores pre-upgrade state. Forced partial failure retains state `0.44.1` and no false success record. A repeated completed run safely retains `0.45.0` and unchanged managed bytes.

### Version surfaces

- Current `0.45.0` surfaces: root `VERSION`; Codex and Claude plugin manifests; Agents marketplace entry; both Claude marketplace fields; template state; template manifest; both formal migration descriptors; Chinese and English README current-version entries; and latest CHANGELOG entry.
- Release/current-version scripts derive the current version from `VERSION`. Historical `0.44.1` uses for from-version, provenance, fixtures, compatibility, and history remain legitimate.
- Mutations reverting VERSION, one plugin, one marketplace entry, template state, template manifest, or descriptor version all fail nonzero.

### Template manifest

- It reports 0.45.0 with 156 unique entries; all listed files exist and all 18 Skill projections are present. Root-only tests, review/change-local files, the draft, and `usage.html` are excluded as intended.
- **MAJOR M-E01:** none of the 41 files under `project-template/migrations/0.45.0/` is listed. The checker passes because it validates the curated list but does not derive or require the formal migration inventory. The required mutation deleting one formal migration file from the manifest therefore cannot be made as a rejecting case. Formal migration payloads lack managed-manifest/fresh-install integrity coverage.

### README, prompts, and CHANGELOG

- `README.md`, `README.en.md`, template README, and usage playbook consistently describe slim entries, on-demand nine-Skill grouping, root authority, deterministic `.agents` projections, `.claude/skills` adapters, default read-only behavior, explicit bounded-write and separate external-action authorization, impact-based risk, stock/custom/unknown migration, and v0.45.0 preparation.
- Both languages retain real-model `NEEDS_TEST` and do not claim external release. No mandatory all-Skill pipeline, file-count risk rule, review-to-maker promotion, reinitialization advice, or authorization expansion was found.
- The seven real, thin prompt paths are `prompts/初始化项目.prompt.md`, `prompts/初始化填充.prompt.md`, `prompts/代码审查.prompt.md`, `prompts/版本发布.prompt.md`, `prompts/架构设计.prompt.md`, `prompts/代码实现.prompt.md`, and `prompts/需求分析.prompt.md`. They neither duplicate complete Skill bodies nor force all Skills.
- CHANGELOG covers ownership, slim entry, Skill convergence, deterministic projection, package/default prompts, behavior evidence, responsibility boundaries, formal migration, raw-byte/LF/fresh clone, upgrade/breaking notes, and `NEEDS_TEST`. Its language is release preparation, not released/published/available-now.

### Stage E validator and gate wiring

- `validate-stage-e-release.py` is a finite structural checker for version, formal migration, discovery, template/projection, documentation entries, and `NEEDS_TEST`; it is not an open-ended synonym analyzer. Its 11 directed disposable-repository tests exercise real failure paths; 11/11 passed.
- Current smoke, fresh clone, template, plugin, release-consistency, migration, and Stage C paths invoke Stage E without suppressing Stage A-D, reducing exit codes, weakening raw-byte/LF, or changing global Git configuration.
- **MAJOR M-E02:** in an isolated copy, deleting the complete Stage E invocation block from `scripts/validate-plugin-assets.ps1` still let that top-level gate exit zero. No structural/meta-wiring assertion rejects removal of Stage E from this gate, so the required gate-removal mutation does not close.

### Scoped snapshot, mutations, tests, and smoke

- A disposable scoped snapshot contained all 115 Stage E candidate paths, including both formal migrations, validator/tests, docs, prompts, manifests, and gates. It explicitly used HEAD's `usage.html` while excluding only the user's deletion; no other dirty path was overlaid. The disposable commit ended clean.
- Closed isolated mutations: VERSION, plugin, and marketplace rollback; template state/manifest mismatch; missing/duplicate formal action; incoming checksum; baseline provenance/checksum; wrong from/to; duplicate production; draft entering production; README `NEEDS_TEST` removal; descriptor/version errors. Each rejected nonzero with a locating diagnostic and was restored or destroyed.
- Not closed: manifest removal of a formal migration file (M-E01, absent from manifest) and removal of Stage E from a top-level gate (M-E02, zero exit).
- Counts: Stage E 11/11; Stage B migration 32/32; full unittest 203/203; behavior matrix 31 cases (`GRADER_UNCERTAIN/not-run` for real models); projections 18/18; manifest 156 entries; release consistency 56 paired/restoring mutation cases; formal actions 20/20.
- Plugin, template, release-consistency, Stage C, Stage D, ownership, entries, projection, manifest, behavior validate/list/dry-run, migration, and `git diff --check` gates otherwise passed against the scoped candidate.
- Current-snapshot smoke and `core.autocrlf=false/true` fresh-clone smoke passed with no byte overlay. Generated projects were 0.45.0; formal migration discovery, stock upgrade, custom/unknown preservation, rollback, partial-failure safety, and repeated-run safety passed.

### BLOCKER / MAJOR / NOTE

- BLOCKER: none.
- MAJOR: M-E01 (formal template migration absent from managed manifest); M-E02 (Stage E gate-removal mutation is not detected).
- NOTE: real Codex/Claude behavior remains `NEEDS_TEST`; selector/source/token-context benefits and manual-merge UX were not real-model tested.
- NOTE: an initial long-path Windows disposable copy encountered MAX_PATH-only failures; the same suite passed 203/203 at a short isolated path.
- NOTE: pre-existing `D:\tmp\fc-ge1jyo7z` remains outside this review. All repositories, snapshots, mutation workspaces, and behavior residues created by this review were removed.

### Stage E decision

FAIL: 0 BLOCKER, 2 MAJOR. Status remains:

`stage-e-implemented-awaiting-independent-check`

The local v0.45.0 candidate is not `stage-e-approved-for-release`; Stage E is not allowed to be committed on this result. Real-model behavior remains `NEEDS_TEST`.

No Stage E commit, push, tag, publish, release, or deploy was performed. v0.45.0 has not been externally released. External release would still require explicit user authorization after correction and independent recheck.

## Stage E M-E01 M-E02 Final Recheck

Recheck date: 2026-07-22. Scope was closed to M-E01, M-E02, and minimum regression. No implementation was changed; mutations and temporary commits were confined to `D:\tmp\fke-final-recheck`, then removed.

### M-E01

M-E01 is CLOSED.

- The manifest generator derives the current formal template migration from the manifest version and descriptor, enumerating `migration.json` plus every action's `baseline` and `source`. It does not hard-code 41, 197, 20 actions, or action paths.
- Paths are normalized, relative-safe, unique, required to exist, and hashed directly from raw bytes without newline normalization. Descriptor/inventory drift fails explicitly.
- Actual inventory is 1 descriptor + 20 baseline + 20 incoming = 41. Manifest coverage is 41/41. The complete manifest has 197 unique entries and 18/18 projections; draft, root alias, checker review, tests, and `usage.html` are excluded.
- All nine fixed mutations failed nonzero with locating diagnostics and byte restoration: descriptor/baseline/incoming entry deletion, duplicate, checksum, draft path, root path, descriptor action deletion with stale manifest, and action addition without payload/manifest.

### M-E02

M-E02 remains OPEN.

- Baseline wiring covers plugin, template, release consistency, smoke, and fresh clone (`required_paths=5`). The real plugin chain executes Stage E, captures `$LASTEXITCODE`, executes the independent wiring validator, and returns nonzero for a Stage E-only manifest failure.
- All seven required mutations failed and restored: plugin block deletion, nonexistent path, ignored failing exit, and removal from template, release consistency, smoke, and fresh clone.
- **MAJOR M-E02-R1:** the regex wiring check accepts non-executable text. When the complete plugin Stage E block was commented out, both the wiring validator and real plugin gate returned 0. Wrapping the block in `if ($false)` also returned 0. These explicitly forbidden false positives mean the structural gate does not yet prove executable wiring.

### Tests and minimum regression

- Wiring tests 6/6; Stage E tests 19/19; combined directed 25/25; full unittest 217/217; behavior 31 cases.
- Stage E baseline: version 0.45.0, 20 actions, 41 manifest migration files, real model `NEEDS_TEST`.
- Release consistency passed in the correctly dirty snapshot: 62 restoring/guard cases (60 expected rejection, two safe-pass), including formal M-E01 deletion/duplicate/checksum and M-E02 plugin deletion/path/exit mutations.
- Plugin and template baseline gates passed. Direct `core.autocrlf=false/true` fresh clone passed Stage C, Stage D, Stage E, wiring, migration, projection, and template checks with no tracked-byte overlay.
- Minimum regression remained closed: 20 actions; baseline provenance Entry 2 / Stage C 10 / Stage D 8 at the approved commits; incoming 20/20; unique production 0.45.0; current version surfaces 0.45.0; Stage A-D validators passed.

### Severity and decision

- BLOCKER: none.
- MAJOR: M-E02-R1 only.
- NOTE: real-model behavior remains `NEEDS_TEST`; manual-merge UX remains untested; existing MAX_PATH noise and pre-existing old temporary directories are unchanged.

Final result: FAIL. M-E01 is CLOSED; M-E02 is not CLOSED. Status remains:

`stage-e-implemented-awaiting-independent-check`

Stage E is not approved for commit. No commit, push, tag, publish, release, or deploy was performed. v0.45.0 has not been externally released; external release still requires explicit user authorization after correction and independent recheck.

## Stage E M-E02 Runtime Canary Final Recheck

Recheck date: 2026-07-22. Scope was limited to M-E02-R1 and the frozen minimum regression. The source worktree was read-only except for this append. All runtime mutations used a disposable Git snapshot at `D:\tmp\fke-stagee-runtime-final`, which was removed after byte restoration.

### Static and runtime responsibilities

- The existing static layer remains finite: it checks the five required gate files and their agreed Stage E command shapes. It is not required to understand arbitrary PowerShell control flow.
- The repository does not contain the required formal runtime-canary layer. `python -B -m unittest tests.test_stage_e_gate_runtime` exits 1 with `ModuleNotFoundError`; no alternative committed runtime-canary runner was found.
- `tasks.md`, `verification.md`, and `ship.md` describe finite structural wiring only. None freezes the required split that static checks cover structure while a runtime canary proves execution and propagation, or the stop-loss rule that M-E02 closes once the five-entry canary is complete.

### Runtime reference canary

The checker independently injected a Stage E-only fault by removing `migrations/0.45.0/migration.json` from the template manifest while retaining VERSION 0.45.0 and LF bytes. This fault is rejected by the Stage E formal-migration manifest contract and is not a generic version mismatch.

- Baseline exits were plugin 0, template 0, release consistency 0, smoke 0, and fresh clone 0.
- Canary exits were plugin 1, template 1, release consistency 1, smoke 1, and fresh clone 1.
- The reference orchestration did not use a recursion environment variable or production bypass. The five production entries ran their normal paths. The canary copy was isolated from the source worktree, and fresh clone used no post-clone tracked-byte overlay.

This proves the proposed runtime technique is viable, but the proof currently exists only in this checker run, not in a repeatable repository gate.

### M-E02-R1 reproductions

- Commenting the complete plugin Stage E block: static wiring exit 0; real plugin gate with the Stage E-only canary exit 0. The external checker oracle correctly returned nonzero because the canary was swallowed.
- Wrapping the complete plugin Stage E block in `if ($false)`: static wiring exit 0; real plugin gate with the canary exit 0. The external checker oracle again returned nonzero.
- Deleting the invocation, using a nonexistent validator path, and replacing the captured Stage E exit code with zero each made the real plugin gate exit 1 under the canary. These fixed regressions remain closed.

The first two cases therefore still pass every committed static/plugin check unless an external reviewer supplies the missing runtime oracle. The frozen acceptance standard requires that oracle to be a real, repeatable canary layer; an ad hoc checker-only script is insufficient for approving release wiring.

### Tests and minimum regression

- `validate-release-gate-wiring.py`: PASS, required paths 5.
- `validate-stage-e-release.py`: PASS, version 0.45.0, actions 20, template migration manifest 41.
- Wiring tests 6/6; Stage E release tests 19/19; full discovered unittest 217/217.
- Required runtime test: FAIL before execution because `tests.test_stage_e_gate_runtime` is absent.
- Manifest check PASS: 197 unique entries, formal template migration 41/41, projections 18/18. M-E01 remains CLOSED.
- Stage B migration, Stage C, and Stage D validators PASS. Formal migration remains 20 actions; approved baseline provenance and incoming payloads are unchanged.
- The five-entry baseline included plugin, template, release consistency, smoke, and autocrlf false/true fresh clone; all passed. Canary copies and logs were removed, and no review-created Python process remained.
- HEAD remains `1aca83de2c68db0eab624eaabad9a85197ef0faf`; VERSION is 0.45.0; staged files are zero; `usage.html` remains the user's unstaged deletion. The nine Skills and Stage A-D governance semantics have no diff.

### BLOCKER / MAJOR / NOTE

- BLOCKER: none.
- MAJOR: M-E02-R1 remains OPEN because the formal runtime-canary layer and its stop-loss contract are absent; the committed gates still return success for commented and permanently-false Stage E execution blocks.
- NOTE: the checker reference canary demonstrates that no general PowerShell static analyzer is needed. A finite five-entry runtime oracle is sufficient once it is implemented and wired without a permanent bypass.
- NOTE: real-model behavior remains `NEEDS_TEST`.

### Decision

FAIL: 0 BLOCKER, 1 MAJOR. Status remains:

`stage-e-implemented-awaiting-independent-check`

Stage E is not `stage-e-approved-for-release` and is not allowed to be committed on this result. No commit, push, tag, publish, release, or deploy was performed. The local v0.45.0 candidate has not been externally released; external publication still requires explicit user authorization after M-E02-R1 is closed and independently rechecked.

## Stage E M-E02 Runtime Canary Closure Review

Review date: 2026-07-23. Scope was closed to M-E02-R1, the frozen runtime-canary protocol, and minimum regression. No implementation was changed; source-worktree writes were limited to this append. Runtime mutations and release-consistency mutations ran only in short-path Git isolation and were cleaned.

### Formal runtime layer and fixed canary

- `scripts/test-stage-e-gate-runtime.py` and `tests/test_stage_e_gate_runtime.py` exist and are included by the current scoped candidate. The runtime module requires a `.git` worktree, constructs the complete candidate commit while excluding the user's `usage.html` deletion, clones with `core.autocrlf=false`, executes real subprocesses, records real exit codes, and removes its temporary tree in `finally`.
- The only canary keeps root `VERSION=0.45.0` and changes `project-template/.forgekit/template-manifest.json` from `0.45.0` to `0.44.1`. The required Stage E diagnostic is `version [template manifest]`.
- Stage E invocation is independently observed by a marker injected only into each isolated clone's validator. The repository validator is not modified.

### Five-gate runtime evidence

The formal runtime suite exited 0 with all five fixed gates:

| Gate | Baseline exit | Canary exit | Baseline Stage E | Canary Stage E | Stage E diagnostic |
| --- | ---: | ---: | --- | --- | --- |
| plugin | 0 | 1 | true | true | propagated |
| template | 0 | 1 | true | true | propagated |
| release consistency | 0 | 1 | true | true | propagated |
| smoke | 0 | 1 | true | true | propagated |
| fresh clone | 0 | 1 | true | true | propagated |

### Original finding mutations and child boundary

- Runtime unittest executed seven real tests, with no skip: fixed five-gate baseline/canary, commented plugin block, `if ($false)`, deleted block, missing validator path, swallowed exit, and child marker. Result: 7/7 PASS.
- Each of the five plugin disconnect mutations caused the formal runtime suite to exit nonzero and identify the plugin gate as not propagating the fixed canary. No additional PowerShell syntax/control-flow variant was used as a finding.
- `FORGEKIT_STAGE_E_RUNTIME_CANARY_CHILD` is applied only to child-process environments. It skips nested runtime orchestration, not Stage E validation. Under the child marker, release consistency still exited nonzero for the template-manifest canary and emitted both the nested-orchestration message and Stage E template-manifest diagnostic.
- Template temporarily sets and then restores/removes the child marker around nested unittest discovery. No permanent environment bypass or recursion was found.

### Static wiring, release consistency, and stop-loss contract

- The static validator remains finite: five fixed gate files, runtime script/test existence, exact gate registration, release-consistency invocation, exit capture/guard, and child-marker presence. It is not required to interpret arbitrary PowerShell control flow.
- Wiring tests passed 10/10, covering the existing five-entry structure plus runtime script/test requirements and release-consistency runtime invocation/exit propagation.
- Default production-path `test-release-consistency.ps1` was run in a dirty Git scoped snapshot. It first reported that the Stage E runtime canary propagated the fixed failure through all five gates, then passed baseline, restoring mutations, template validation, and fresh-clone validation. The snapshot returned to its pre-run `M=33`, `??=88` state with `usage.html` present from HEAD and was removed.
- `tasks.md`, `verification.md`, and `ship.md` freeze the same stop-loss principle: finite static structure; real runtime execution/failure propagation; only the five canary gates define M-E02 closure; no expanding PowerShell static semantics; only a variant that makes the formal runtime canary incorrectly pass may become a new finding.

### Tests and minimum regression

- Runtime tests 7/7; wiring tests 10/10; Stage E tests 19/19; full unittest discovery 228/228.
- Behavior validate/dry-run passed 31 cases; real models were not invoked.
- Plugin and template top-level gates passed. Default release consistency passed with the full runtime suite wired before the existing 62 restoring/guard cases.
- M-E01 remains CLOSED: dynamic manifest 197/197 unique; formal template migration 41/41; 20 actions; provenance Entry 2 / Stage C 10 / Stage D 8; incoming 20/20; unique production 0.45.0; current version surfaces 0.45.0.
- Stage B, Stage C, and Stage D validators passed. Runtime fresh-clone and release-consistency fresh-clone evidence passed `core.autocrlf=false/true` with no post-clone tracked-byte overlay.

### Severity and decision

- BLOCKER: none.
- MAJOR: none. M-E02-R1 is CLOSED.
- NOTE: real-model behavior remains `NEEDS_TEST`; manual-merge UX remains untested; previously documented MAX_PATH noise and old pre-existing temporary directories are unchanged.

PASS WITH NOTES. The local v0.45.0 candidate has passed Stage E release preparation. Status is:

`stage-e-approved-for-release`

Stage E may be committed. This does not authorize push, tag, publish, release, or deploy. Stage E has not yet been committed; v0.45.0 has not been externally released. Any external publication still requires explicit user authorization.
