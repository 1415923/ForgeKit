# v0.45.0 发布 / 交接设计

Status: stage-c-implemented-awaiting-independent-check
DesignStatus: design-approved-for-stage-a
AuthorizedStage: stage-c

## 发布 / 交接步骤

当前不得发布。阶段 A、阶段 B 已通过独立 checker；阶段 C maker 已完成实施和确定性自验，等待独立 checker；阶段 D-E 未进入。后续交接条件为：

1. DECISION-01 至 DECISION-03 已冻结，不再作为未决项退回。
2. M-01、M-03、A21 保持上一轮已关闭；`review.md` 的两次 blocker-recheck 已关闭 M-02、M-04，设计状态为 `design-approved-for-stage-a`。
3. 阶段 C 的独立 checker 必须以新鲜只读上下文复核五个 Skill、development migration、mutation、回归和残留证据；阶段 D-E 仍需逐段授权、实现、验证和独立复查。
4. 完成新安装、新项目、v0.44.1 stock/custom 升级、plugin+local、Codex-only 和 Claude-only 验收。
5. 执行完整 template/plugin/release smoke 与 mutation，确认自动恢复。
6. 最后才更新正式版本元数据、changelog 和发布说明。

阶段 A 的冻结合同为：`config/skill-projections.json` 仅显式管理九个通用 Skill 的 `SKILL.md` 与 `agents/openai.yaml`，sync apply 仅供维护者显式调用；行为测试使用 `scripts/test-skill-behavior.py`、`tests/skill-behavior/cases.json`、`scripts/skill_behavior_adapters/codex.py` 与 `scripts/skill_behavior_adapters/claude.py`。确定性合同是自动 blocker；Codex/Claude 各一组代表性行为证据须由独立 checker 复核，单次非确定模型结果不直接成为无条件自动 blocker。

M-02 已按冻结合同沿用 `.forgekit/reports/upgrade-review-needed.md`、`.forgekit/reports/upgrade-review-needed.json` 和 `.forgekit/reports/review-needed/`；rollback 只位于对应 packet 的 `rollback/` 内，不新增顶层 root。M-04 已由 `project-template/governance/agent-entry-contract.md` 落地共享入口规则权威，AGENTS/CLAUDE 本阶段未改，仍只是未来 application sites；通用与 Claude Skill 的具体规则继续使用设计矩阵中的实际单文件 owner。

阶段 A 未修改版本号、AGENTS、CLAUDE、Skills、prompts、README 或 usage playbook；未执行 commit、push、tag、release，也未进入阶段 B。

## Stage A finding 修复交接

独立审查的 B-01、B-02 与 M-01 至 M-10 已由 maker 完成限定修复和确定性自验；当前仍为 `stage-a-implemented-awaiting-independent-check`，不得自行视为 approved。origin snapshot、packet 两阶段发布/可恢复交换、portable path、projection 全计划预检、helper 双副本门禁、目录 oracle、公共脱敏、稳定退出码、adapter 隔离/能力合同和 42 项单测均已落地。真实 Codex/Claude 只做 version/help probe；由于无法证明 fixture-only 读取边界和网络/外部动作禁用，adapter 失败关闭且没有运行 prompt。

保留 NOTE：upgrade review JSON schema 2 的外部兼容说明须在最终 release 前完成；当前未发现仓库内消费者回归，但该事项未完成。极端 I/O 中断下 projection 的完整事务性与本地 reparse 检查的合理 TOCTOU 残余仍不属于本轮 blocker 修复。

### Findings recheck 最后修复交接

M-02、M-06、M-10 已完成最后一次定向修复和 maker 自验。packet 的提交点现在位于 canonical packet、Markdown、JSON 全部发布并完成身份/classification/checksum/artifact 交叉验证之后；提交后的 `.old-*` 清理失败只记录 cleanup-pending warning，不得回滚已一致提交的新状态。behavior record 在 evidence/stdout 序列化前经过最终整对象递归脱敏，嵌套 environment/auth 敏感键的任意类型值均替换为稳定占位符。全量单测为 44/44，正式门禁和隔离 smoke 通过。

checker 报告的主机 TEMP 三个外部 fixture 仍诚实记录为环境噪声；本轮未终止未知进程或删除被外部进程使用的目录。真实模型行为矩阵仍未执行。状态继续为 `stage-a-implemented-awaiting-independent-check`，只等待 checker 对 M-02、M-06、M-10 复核。

## 阶段 B maker 交接

模板 `AGENTS.md` 和 `CLAUDE.md` 已收敛为共享合同应用、最小 startup/routing 和 upgrade 入口。七项 always-on 规则均指向 `governance/agent-entry-contract.md` 的唯一 anchor；完整 archive/checkpoint/worktree/loop/maker-checker/code-review convergence、固定数量门槛和重复本地授权确认不再常驻。CLAUDE 仅额外保留可定位的平台 adapter/agent 路由和“不扩大共享授权”的边界。

change-local `stage-b-migration-draft/` 冻结 v0.44.1 baseline 和阶段 B incoming；它只是开发 fixture，不是已发布的 0.45.0 migration。现有 upgrader 的安全 root-file allowlist 只增加 AGENTS/CLAUDE：stock 精确匹配才更新，custom/unknown 不覆盖，missing 不伪造原始字节，rollback/packet/summary 沿用阶段 A 合同。VERSION、plugin/marketplace 版本和正式 migration 均未更新。

两个 Stage B validator、12 个定向单测、56 个全量单测、41-rule ownership、18-file projection、behavior dry-run、template/plugin/release/manifest、可恢复 mutation 和隔离 smoke 已通过。真实 Codex/Claude prompt 未执行，相关行为保持 `NEEDS_TEST`，不能由 dry-run 或行数/bytes 推断通过。

阶段 B 未修改任何通用或 Claude Skill 正文/metadata，未修改 prompts、README 或用户原有 `usage.html` 删除，未执行 commit、push、tag、release。当前只能交给新鲜只读独立 checker，不得写成 `stage-b-approved` 或授权阶段 C。

### Stage B validator MAJOR 修复交接

独立 checker 的 M-B1、M-B2 已由 maker 做封闭定向修复和自验，产品入口正文、迁移动作语义与 upgrader运行行为未重新设计。入口 validator 从唯一 `config/skill-projections.json` 派生全部通用 route，并新增明确反向语义 gate；migration validator 以完整 Stage A commit `506cecf8d377a17a2616bf3b9eeea483ee4039a4` 的 Git blob 和当前模板分别锚定 baseline/incoming，默认执行 production discovery 及 stock/custom/unknown/missing/mixed/rollback 真实 gate。

两个定向测试模块 32/32、全量单测 76/76、18-file projection、41-rule ownership、behavior dry-run、plugin/template/manifest、release mutation 和含 Git 锚点的短路径完整 smoke 已通过。audit contradiction、manifest-derived 单 route 删除、baseline+checksum 同步篡改和 production discovery 重定向均失败后逐字节恢复。真实模型 prompt、selector/Skill source、context/token 收益和 manual merge 体验仍为 NOTE / `NEEDS_TEST`。

状态仍是 `stage-b-implemented-awaiting-independent-check`；maker 不宣布 Stage B 通过，不授权 Stage C。VERSION 仍为 `0.44.1`，未 commit、push、tag、release。

### M-B1 contradiction family 最后修复交接

原 checker 已关闭九个通用 route 完整性和 M-B2；本轮只修复 audit-default 对明确反向写入声明的剩余漏检。入口 validator 现在由小型数据表组合 audit/review/assessment/diagnosis/planning subject、automatic/direct/default write/fix action、无 repair request 写入短语与明确否定词；错误包含 rule ID、`audit-default` category、文件和命中正文。它继续剔除 fenced code block，不把 Skill route、路径、heading、link 或正常否定安全措辞当成矛盾，也没有修改产品入口正文。

checker 五个漏检反例均由正式 CLI 以退出码 1 拒绝；must not、never、cannot、no audit、propose-but-not-apply、recommend-but-do-not-modify 等安全措辞通过。入口定向单测 31/31、全量单测 92/92；AGENTS/CLAUDE 的 9+9 route deletion 回归继续失败关闭。release consistency 新增 assessment 与 generic no-repair-write 两个 mutation，均验证 category/命中正文并逐字节恢复。M-B2 回归、projection、41-rule ownership、behavior dry-run、plugin/template/manifest、release consistency 和含 `.git` 的短路径 smoke 全部通过，所有本轮临时目录已清理。

真实 Codex/Claude prompt 未执行，selector/Skill source、context/token 收益和 manual merge 体验仍为 NOTE / `NEEDS_TEST`。M-B2 保持 CLOSED；状态仍是 `stage-b-implemented-awaiting-independent-check`，只等待原 checker 复核 M-B1。VERSION 仍为 `0.44.1`，未进入 Stage C，未 commit、push、tag 或 release。

### M-B1 Markdown/prose separation 最后修复交接

原 checker 已确认五个漏检、subject/action family、generic no-repair、否定句、fenced code、九项 route 和 M-B2；本轮只关闭 Markdown/navigation 系统性误报。validator 现在先由 `extract_policy_prose` 排除 heading/fence/reference definition，并中性化 inline code、link/image destination、URL、path/file 与动态 Skill navigation token，再由独立 `detect_policy_contradictions` 执行既有 family。通用 Skill 名仍由 manifest 派生，Claude 专属名由实际目录发现；未建立白名单、第二份 Skill 清单或 Markdown 第三方依赖。

四个 checker 误报均由真实 CLI 以 exit 0 通过；原五例和五个独立组合均以 exit 1 返回 `audit-default` category 与准确 matched text；十类否定以 exit 0 通过；heading/link/inline 后真实矛盾继续以 exit 1 失败关闭。AGENTS/CLAUDE 各 9 项 route deletion 回归继续通过。focused tests 58/58、全量 119/119，M-B2、projection、41-rule ownership、behavior dry-run、plugin/template/manifest、release consistency 与含 `.git` 的短路径 smoke 全部通过。原三个 release contradiction mutation 均逐字节恢复；expected-pass Markdown guard 由 template gate 的正式 unittest suite 执行并清理临时仓库。

状态仍是 `stage-b-implemented-awaiting-independent-check`，只等待原 checker 复核 Markdown 误报修复。M-B2 保持 CLOSED；VERSION 仍为 `0.44.1`；未修改入口、migration、upgrader、Skills、prompts、`review.md` 或 `usage.html`，未进入 Stage C，未执行真实模型 prompt，未 commit、push、tag 或 release。

## Stage C maker 交接

五个 Stage C Skill 已在根级权威源收敛，并经 manifest/sync 确定性投影到 template `.agents`。`project-init` 只处理未初始化新项目并在覆盖、跨项目、删除、远程或不可逆动作前升级风险；`project-bootstrap-fill` 只补已初始化项目中有证据的 placeholder；`handover-review` 默认只读且代码/可重复运行证据优先；`document-backfill` 只回填已有实现事实并按事实域、owner、风险和上下文容量分批；`large-change-planning` 按信任边界、公共接口、migration、安全、回滚和证据不确定性触发，并冻结阶段授权与 acceptance IDs。

Stage C validator 从 41-rule matrix 派生五项 owner，检查触发、授权、外部保护、事实边界、旧固定门槛回流、路由循环和 projection 漂移。13 项定向测试覆盖 9 个要求的 mutation：mutation 正式 CLI 均 exit 1，逐字节恢复后 exit 0。behavior manifest 为 13 cases，Stage C 新增 10 个正/负场景；只运行 validate/list/dry-run，真实 Codex/Claude 仍为 `NEEDS_TEST`。

既有单一 development migration draft 已扩展五项 Skill；baseline 锚定已审批 Stage B commit，incoming 锚定当前 projection，stock/custom/unknown/missing/rollback 和 production-discovery gate 通过。未建立正式 `migrations/0.45.0`。完整 136 项单测、plugin/template/manifest、release mutation 和含 `.git` 的短路径 smoke 通过；隔离目录和 mutation 均已恢复/清理。

当前只允许交给新鲜只读独立 checker。状态是 `stage-c-implemented-awaiting-independent-check`，不是 `stage-c-approved`；不得进入 Stage D/E。VERSION 保持 `0.44.1`，用户原有 `D usage.html` 未恢复、未修改、未暂存；未 commit、push、tag、release。

### Stage C 七项 MAJOR 修复交接

C-M01 至 C-M07 已完成 maker 限定修复与确定性自验，等待原 checker recheck。公开 Skill ID、name、display name 和已通过的五份核心执行语义保持不变；错误 frontmatter implicit policy 已删除，bootstrap/backfill 在 package YAML 顶层 `policy.allow_implicit_invocation` 设置 boolean false，三个冲突 default prompt 已收敛。根/template package 逐字节投影，唯一 development migration 同时覆盖五份 SKILL 和三份 changed YAML。

Template manifest 现完整覆盖五份 Stage C SKILL、三份 changed YAML 与 generated-project `.gitattributes`。Stage C validator 使用 tasks SC-01..05 与 41-rule matrix 双源五项锁定，并复用 Stage B Markdown policy-prose 层；reinitialize-existing-project、mandatory-five-Skill-pipeline、fence/heading fake、安全否定、matrix/tasks 缩减和 package/manifest mutation 均失败关闭。

Behavior fixture 运行时从根级权威 package 物化到 `.agents/skills`，explicit prompt 实际包含 `$skill-id`，case-level evidence requirement 在 dry-run 中保持未取得状态。根和 generated project 均发布 LF checkout 合同；双 `--no-local` fresh clone 在 autocrlf=false/true 下不做 post-clone overlay，byte-exact、migration、projection、template 门禁通过，删除 LF rule mutation 失败。真实模型 prompt 未执行。

最终临时 Stage C snapshot smoke、autocrlf=false fresh-clone full smoke、autocrlf=true fresh-clone full smoke 三路均通过；两种 clone 的 Stage C、migration、projection、template、完整 smoke 全部 PASS，代表性 Git blob 与 working-tree SHA-256 相等。release consistency 的既有 mutation 和新增 fresh-clone gate 通过并恢复，临时 repo/clone/TEMP 均清理。

当前仍只允许原 checker 做七项 findings recheck。状态保持 `stage-c-implemented-awaiting-independent-check`；VERSION 仍为 `0.44.1`；未进入 Stage D/E，未建立正式 release migration，未 commit、push、tag 或 release。

## 回滚

- 每阶段使用独立提交候选和 baseline-guarded migration。
- 用户定制入口/Skills 不自动覆盖；使用 keep-local/manual-merge/replace-template 决策。
- 若入口轻量化造成基础边界回归，恢复 v0.44.1 入口，同时保留阶段 A 测试。
- 若投影 sync 不稳定，退回 check-only + 人工双副本校验，不影响用户项目运行。
- v0.45.0 不删除 prompt 路径，因此 prompt 兼容层可单独回滚。

## 用户可见变化

以下仅是设计目标，尚未生效：

- 更短但仍有实质安全边界的 AGENTS/CLAUDE。
- 更聚焦、按影响分支的 Skills。
- 审计默认只读，明确修复不重复确认局部授权。
- 共享 Skill 单一语义权威源与可定位漂移检查。
- 旧 prompts 继续可用，但变为兼容包装。

## 当前态文档同步

- 尚无已实施的稳定结果，不更新 changelog、README 或版本路线图。
- 只有阶段 E 完成并验证后，才能把用户可见变化同步到发布文档。

### Stage C recheck 剩余五项交接

原 checker 已关闭 C-M04 Markdown/policy-prose 分层与 C-M05 tasks/matrix 双源五项锁定；本轮只修复仍 OPEN 的 C-M01、C-M02、C-M03、C-M06、C-M07。五个 package default prompt 现各含唯一独立 $skill-id，fixed-count 风险门槛同时受正文与 package prompt gate；template manifest 覆盖 projection config 的完整 18/18 target 与 Stage C 10/10 package 文件。

reinitialize 与 mandatory-pipeline detector 已扩展为 subject/action/mandatory/sequence/scope 组合 family，checker 等价句及额外变体由正式 CLI 失败关闭，安全否定和 C-M04/C-M05 回归通过。Behavior bounded-write/read-only case 必须提供相称 write evidence；explicit renderer 对已有 marker 幂等，对缺失 marker 只插入一次，重复/错误 marker 失败，implicit 不注入。

所有 checksum/projection 比较均使用 raw bytes；独立 LF content gate 阻止双侧 CRLF 与同步 manifest/descriptor checksum 绕过。根和 generated project checkout contract 覆盖完整 manifest 文本扩展。唯一 development migration 管理五份 Stage C YAML，仍保持 Stage B Git baseline、current template incoming 与 stock/custom/unknown/missing/rollback 合同。

定向 83/83、全量 160/160、正式快速门禁、release consistency、scoped snapshot 与两种 autocrlf fresh-clone full smoke 均通过；临时 commit 477e041183602ca9cc1ddc006404ca98084a7441，clone 后无 tracked-byte overlay，删除 LF rule mutation exit 1。真实模型 prompt 未执行。

当前只等待原 checker 复核剩余五项。状态继续为 stage-c-implemented-awaiting-independent-check，不是 Stage C approved；VERSION 保持 0.44.1，未进入 Stage D/E，未建立正式 migration，未 commit、push、tag、release 或 deploy。

### Stage C 最后两个 OPEN finding 交接

本轮只修复 C-M01 与 C-M03。fixed-count gate 现按 quantity/workload-unit/mandatory-trigger/risk-target 要素组合，覆盖 directory/folder/service/package/endpoint 等词根式单复数与数字词；reinitialize 和 mandatory pipeline 分别按 subject/action/repeat/command 与 full-set/scope/mandatory/sequence 组合，未维护完整 checker 句库。安全否定作用域继续通过。

checker 六句由真实 Stage C CLI 在隔离 package 副本中逐项 exit 1 并定位 Skill/category/matched prose。Stage C tests 28/28、全量 unittest 163/163；release consistency 的 directory threshold、setup again、one-by-one pipeline mutation 均非零并逐字节恢复。fresh-clone 临时提交 `a4debe204d2ade609a83950fb49bb2bd987b722d` 的 autocrlf=false/true checkout 均通过 byte/LF/attribute 快速门禁。

C-M02/C-M04/C-M05/C-M06/C-M07 保持 CLOSED，相关实现未修改且回归通过。当前只等待原 checker 复核 C-M01 与 C-M03；状态仍为 `stage-c-implemented-awaiting-independent-check`。VERSION 为 `0.44.1`；未进入 Stage D/E，未执行真实模型 prompt，未建立正式 migration，未 commit、push、tag、release 或 deploy。

### Stage C 最后一个 OPEN finding（C-M03）交接

C-M03 已完成 maker 限定修复。reinitialize 使用同句 `existing_subject + init_action + repeat_action + positive_requirement` 不变量，并以动作局部否定和 handover/bootstrap-fill 替代路由排除安全句；mandatory full-Skill execution 分别拒绝 `S+U+M`、`S+U+Q` 与 `non-skippable+U`，不再把 sequence/order/pipeline 词作为所有违规表达的必要条件。未新增完整 forbidden-sentence 清单，也未修改 Markdown policy-prose helper。

checker 的两个 reinitialize 漏检、一个安全误报与六个 pipeline 漏检已逐项通过正式 CLI 预期/实际退出码、category、matched prose 和 feature 集合断言。Stage C 定向测试 28/28、全量 unittest 163/163；template、projection、18/18 manifest、ownership、entry、migration、behavior、LF/CRLF fresh clone 与 release consistency 全部 PASS。Release mutation 覆盖 setup-again、action-first bootstrap-once-more、one-by-one 及无 sequence 的 full-set compulsory，并逐字节恢复。

C-M01/C-M02/C-M04/C-M05/C-M06/C-M07 保持 CLOSED；五个 Skill 正文、package YAML、projection、manifest、behavior、migration、`.gitattributes` 和 fresh-clone runner 均未修改。当前只等待原 checker 复核 C-M03，状态继续为 `stage-c-implemented-awaiting-independent-check`。VERSION 仍为 `0.44.1`；未进入 Stage D/E，未执行真实模型 prompt，未建立正式 migration，未 commit、push、tag、release 或 deploy。

### Stage C C-M03A 最后两个命令式表达交接

C-M03A 已完成 maker 限定修复：bootstrap 完整动词词形与 `set up` 短语动词在分析副本中归一化，句首及允许前置状语后的 init command 满足既有 positive-requirement feature。原始 matched prose、A+B+C+D 布尔判定、C-M03B 和 Markdown policy-prose helper 均未改变。

`Bootstrap an already initialized repository again.` 与 `Set up each existing workspace from scratch.` 均由正式 CLI exit 1，并回显正确 category、原句和四项 feature。安全否定/说明/示例/alternative/inline/fence 回归通过。Stage C 28/28、全量 163/163、template、18/18 manifest、behavior、migration、autocrlf=false/true fresh clone 与 release consistency 全部 PASS；两项新 mutation 均逐字节恢复。

当前只等待原 checker 复核这两个命令式表达及安全回归。状态继续为 `stage-c-implemented-awaiting-independent-check`；VERSION 仍为 `0.44.1`，未进入 Stage D/E，未执行真实模型 prompt，未建立正式 migration，未 commit、push、tag、release 或 deploy。

### Stage C C-M03A 正负词形对称交接

C-M03A 最后一个 maker bug 已定向修复。初始化动作现在只由 `find_init_action_matches` 从唯一词法源产出带 span/family/original-text 的 match；`init_action`、imperative 和 `negated_init` 共享这些 match。竞争的否定动作词表已删除，否定只在每个 directive action 的局部上下文判定；C-M03A A+B+C+D 和 C-M03B 未修改。

原误报 `An already initialized project must not be bootstrapped again.` 正式 CLI exit 0；对应正向句 exit 1 并返回正确 Skill/category/matched prose/features。bootstrap、bootstrapped、bootstrapping、set-up、split set-up、initialized、reinitialize 七组正负对称测试通过。Release expected-pass guard 先验证安全句通过，再验证正向句失败，三份受管文件逐字节恢复。

Stage C 29/29、全量 164/164、template、manifest 18/18、behavior、migration、LF/CRLF fresh clone 与 release consistency 全部 PASS。当前只等待原 checker 复核正负词形对称性；状态继续为 `stage-c-implemented-awaiting-independent-check`。VERSION 仍为 `0.44.1`，未进入 Stage D/E，未执行真实模型 prompt，未建立正式 migration，未 commit、push、tag、release 或 deploy。
