# v0.45.0 发布 / 交接设计

Status: stage-b-implemented-awaiting-independent-check
DesignStatus: design-approved-for-stage-a
AuthorizedStage: stage-b

## 发布 / 交接步骤

当前不得发布。阶段 A 已通过独立 checker；阶段 B maker 已完成实施和确定性自验，等待独立 checker；阶段 C-E 未进入。后续交接条件为：

1. DECISION-01 至 DECISION-03 已冻结，不再作为未决项退回。
2. M-01、M-03、A21 保持上一轮已关闭；`review.md` 的两次 blocker-recheck 已关闭 M-02、M-04，设计状态为 `design-approved-for-stage-a`。
3. 阶段 B 的独立 checker 必须复核入口、migration、mutation、回归和残留证据；阶段 C-E 仍需逐段授权、实现、验证和独立复查。
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
