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
