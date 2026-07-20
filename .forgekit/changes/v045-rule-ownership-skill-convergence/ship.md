# v0.45.0 发布 / 交接设计

Status: design-revised-awaiting-blocker-recheck
DesignStatus: design-revised-awaiting-blocker-recheck
AuthorizedStage: design-revised-awaiting-blocker-recheck

## 发布 / 交接步骤

当前不得发布。本工件只定义未来交接条件：

1. DECISION-01 至 DECISION-03 已冻结，不再作为未决项退回。
2. M-01、M-03、A21 保持上一轮已关闭；独立 checker 仅对当前 OPEN 的 M-02、M-04 执行 blocker recheck。通过后仍需维护者单独授权阶段 A。
3. A-E 阶段逐段授权、实现、验证并独立复查。
4. 完成新安装、新项目、v0.44.1 stock/custom 升级、plugin+local、Codex-only 和 Claude-only 验收。
5. 执行完整 template/plugin/release smoke 与 mutation，确认自动恢复。
6. 最后才更新正式版本元数据、changelog 和发布说明。

阶段 A 的冻结合同为：`config/skill-projections.json` 仅显式管理九个通用 Skill 的 `SKILL.md` 与 `agents/openai.yaml`，sync apply 仅供维护者显式调用；行为测试使用 `scripts/test-skill-behavior.py`、`tests/skill-behavior/cases.json`、`scripts/skill_behavior_adapters/codex.py` 与 `scripts/skill_behavior_adapters/claude.py`。确定性合同是自动 blocker；Codex/Claude 各一组代表性行为证据须由独立 checker 复核，单次非确定模型结果不直接成为无条件自动 blocker。

M-02 固定沿用 `.forgekit/reports/upgrade-review-needed.md`、`.forgekit/reports/upgrade-review-needed.json` 和 `.forgekit/reports/review-needed/`；rollback 只能位于对应 packet 的 `rollback/` 内，不新增顶层 root。M-04 固定由未来 `project-template/governance/agent-entry-contract.md` 拥有共享入口规则，AGENTS/CLAUDE 只应用；通用与 Claude Skill 的具体规则使用设计矩阵中的实际单文件 owner。上述两项仍等待独立 blocker-recheck，不得表述为 checker 已关闭。

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
