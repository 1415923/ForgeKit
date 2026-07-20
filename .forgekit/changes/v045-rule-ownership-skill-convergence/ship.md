# v0.45.0 发布 / 交接设计

Status: stage-a-implemented-awaiting-independent-check
DesignStatus: design-approved-for-stage-a
AuthorizedStage: stage-a

## 发布 / 交接步骤

当前不得发布。阶段 A maker 已完成实施和确定性自验，等待独立 checker；后续交接条件为：

1. DECISION-01 至 DECISION-03 已冻结，不再作为未决项退回。
2. M-01、M-03、A21 保持上一轮已关闭；`review.md` 的两次 blocker-recheck 已关闭 M-02、M-04，设计状态为 `design-approved-for-stage-a`。
3. 阶段 A 的独立 checker 必须复核 maker 结果；阶段 B-E 仍需逐段授权、实现、验证和独立复查。
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
