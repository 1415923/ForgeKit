DesignStatus: design-revised-awaiting-blocker-recheck

# v0.45.0 分阶段实施计划

本计划只冻结未来实施切片。本轮没有执行任何阶段 A-E 的产品修改。

## 设计阶段工作记录

| ID | 工作 | 状态 | 证据 |
| --- | --- | --- | --- |
| D-001 | 确认分支、版本、工作树和 v0.44 提交 | Done | `proposal.md` 当前状态；本轮命令记录 |
| D-002 | 盘点入口、Skills、Claude adapters、governance、references、prompts、脚本和元数据 | Done | `design.md` 第 2 节 |
| D-003 | 冻结四层所有权、分发方案、Skill 职责和风险模型 | Done | `design.md` 第 4-9 节 |
| D-004 | 设计兼容、测试、分阶段实施和回滚 | Done | `verification.md` 与本文件 |
| D-005 | 独立 blocker-recheck 关闭当前 OPEN 的 M-02 与 M-04 | Todo | M-01、M-03、A21 不重开；原始 `review.md` 保持不变 |
| D-006 | 冻结 DECISION-01/02/03 | Done | `proposal.md` / `design.md` 的已冻结决策 |

## 阶段 A：规则所有权和基础测试设施

### 修改范围

- 创建 `project-template/governance/agent-entry-contract.md`，落地共享入口唯一规范和原子化 owner 合同；AGENTS/CLAUDE 本阶段不改，阶段 B 才迁移为 application sites。
- 在 governance/reference 中落地其余原子化规则权威矩阵和影响型风险模型，不改变普通用户工作流语义。
- 创建 `config/skill-projections.json` schema v1，精确列出九个通用 Skill 的 `SKILL.md` 与 `agents/openai.yaml`。
- 建立显式 sync check/apply 基础；check 可供 CI/release，apply 仅维护者显式调用且只维护 ForgeKit template projection。
- 建立 `scripts/test-skill-behavior.py`、`tests/skill-behavior/cases.json`、`scripts/skill_behavior_adapters/codex.py` 和 `scripts/skill_behavior_adapters/claude.py` 的接口与最小安全 fixture。
- 扩展并测试现有 migration baseline 身份、stock/custom/missing/unknown-baseline 和 manual-merge packet 合同；输出只使用 `.forgekit/reports/upgrade-review-needed.md`、`.forgekit/reports/upgrade-review-needed.json` 与 `.forgekit/reports/review-needed/`。

### 不修改范围

- 不瘦身 AGENTS/CLAUDE。
- 不重写核心 Skill 正文。
- 不修改 prompts 用户入口。
- 不改变现有用户工作流语义。
- 不增加来源 display name，不修改公共 Skill `name`，不实施入口型/操作型职责拆分。
- 不在真实用户项目运行 sync apply 或可写行为案例。
- 不创建 `.forgekit/rollback/`、`.forgekit/backups/` 或其他顶层 review/merge/rollback root。

### 前置条件

- DECISION-01/02/03 已冻结。
- 独立 blocker-recheck 关闭 M-02 与 M-04，并由维护者另行授权阶段 A；M-01、M-03、A21 保持已关闭，不重新设计。
- 阶段 A 实现必须遵守 `design.md` 中 manifest、safe-target、baseline、runner、隔离和门禁合同。

### 验收标准

- `config/skill-projections.json` 只有九个 entry，每项仅显式管理 `SKILL.md` 与 `agents/openai.yaml`，无递归/通配符。
- sync check 能列出 Skill、source/target 路径和双方 SHA-256；缺失、非法或漂移返回非零且不写文件。
- sync apply 仅写 manifest 计算目标，不删除/递归/触碰 `.claude`，完成后 check；safe-target 在复制前拒绝绝对路径、`..`、symlink/junction/reparse escape。
- Claude 专属文件不会被通用 sync 修改。
- `project-template/governance/agent-entry-contract.md` 是 ENTRY-BOUNDARY、ENTRY-EVIDENCE、ENTRY-AUDIT、ENTRY-AUTH、ENTRY-EXTERNAL、WRITEBACK-BASE 和通用 SKILL-ROUTING 的唯一 owner；AGENTS/CLAUDE 仅为 application sites。
- owner validator 拒绝通配符、参数化占位符、目录、角色名、“对应文件”“共享合同”“各 Skill”和多文件 owner；九个根 Skill 与六个 Claude Skill 的具体规则 owner 路径均实际存在。
- baseline fixture 依据 `.forgekit/state.json[forgekit_version]` 和 migration `from/to/source/baseline/target` 唯一分类 stock/custom/missing/unknown-baseline；custom/unknown 不覆盖。
- review 汇总恰为 `.forgekit/reports/upgrade-review-needed.md` 与 `.forgekit/reports/upgrade-review-needed.json`，packet root 恰为 `.forgekit/reports/review-needed/`；JSON artifact 路径相对于 `.forgekit/reports/`。
- packet ID 为 `<target-version>--<规范 managed path 的 SHA-256 前 16 位>`，结构固定为 `packet.json`、`local/<managed-path>`、`incoming/<managed-path>`、`rollback/<managed-path>` 和 `diff.patch`。
- rollback 保存升级前原始字节并位于同一 packet；packet/checksum 未验证前不得覆盖 stock。custom/unknown 不覆盖；missing 不伪造 local/rollback，必要时记录删除新建文件的 rollback action。
- Python runner/manifest/adapters 在独立临时目录运行，保存统一 run record，并区分环境、adapter、routing、unauthorized-write、behavior 和 grader-uncertain。
- 确定性测试是自动 blocker；单次非确定行为结果只形成需独立 checker 复核的代表性证据。
- 所有现有 release/template 验证继续通过。

### 回滚

- 删除新增 checker/fixture，并恢复 governance/reference 的本阶段修改；不触及用户项目。

### Checker 与提交切分

- 必须独立 checker，因为这是后续阶段的规则与测试基座。
- 建议拆为两个提交候选：`rule ownership + risk model`、`sync/test skeleton`。

## 阶段 B：入口轻量化

### 修改范围

- 精简模板 AGENTS.md 与 CLAUDE.md。
- 对根 AGENTS.md 仅做与 ForgeKit 仓库自身职责相称的去重。
- 保留共同的安全/事实/授权合同，分别适配 Codex/Claude 路由。
- 更新对应入口 validator、migration baseline 和兼容说明。

### 不修改范围

- 不改核心 Skill 任务语义。
- 不改变升级入口、版本字段或发布动作。
- 不把入口变成只有链接的空壳。

### 前置条件

- 阶段 A 的权威矩阵、基础行为 fixture 和风险模型通过 checker。
- v0.44.1 入口 baseline 已纳入 migration fixture。

### 验收标准

- Skill 未触发时，审计只读、局部授权、外部/不可逆保护、证据边界测试均通过。
- 简单本地任务不被强制加载完整治理链路。
- AGENTS 与 CLAUDE 的共享语义一致，平台调用方式允许不同。
- 定制入口升级进入 REVIEW-NEEDED，未定制入口可安全更新。

### 回滚

- 恢复 v0.44.1 入口内容和对应 migration；保留阶段 A 测试作为回归证据。

### Checker 与提交切分

- 必须独立 checker。
- AGENTS/CLAUDE + validator/migration 可作为一个原子提交候选；若根入口也调整，建议单独提交。

## 阶段 C：高优先级 Skills 收敛

### 修改范围

- `project-init`、`project-bootstrap-fill`、`handover-review`、`document-backfill`、`large-change-planning`。
- 对应 frontmatter description、implicit policy、references、投影、migration 和行为 fixture。
- 删除固定文件/模块/提问数量门槛，落实 audit/implementation 分离。

### 不修改范围

- 不改 code/security/release review convergence。
- 不迁移旧 prompts。
- 不拆成大量微型 Skills。

### 前置条件

- 阶段 B 的入口安全合同通过。
- 每个 Skill 的正触发、负触发和相邻冲突 fixture 已冻结。

### 验收标准

- project-init 是轻量编排器；小项目不被完整访谈阻塞。
- handover audit 默认零写入，findings 不自动授权 fix。
- document-backfill 使用可审查小批次、有来源、不写 governance 业务事实。
- large-change 根据影响而非数量路由。
- 已有明确本地写入授权不被同义确认重复否定。

### 回滚

- 按 Skill 独立恢复权威源与投影；migration 仍保护项目定制。

### Checker 与提交切分

- 每个高优先级 Skill 至少一次独立 checker；可按 `init/bootstrap`、`handover/backfill`、`large-change` 三个提交候选切分。

## 阶段 D：审查和发布 Skills

### 修改范围

- `code-review`、`security-review`、`release-check`、`project-suitability`、first-principles 及 Claude review adapters。
- 实施渐进加载、证据等级、人工复核、review convergence 和风险触发。
- 更新独立 reviewer fixture，不强制所有低风险代码改动进入独立审查。

### 不修改范围

- 不执行真实发布、tag、push、deploy。
- 不改变 v0.44 冻结的 blocker recheck 收敛合同。
- 不把 self-review 算作 mandatory independent review。

### 前置条件

- 阶段 A 的测试骨架可表达风险分支和 reviewer 身份。
- 阶段 C 的影响路由不会与 review Skill 争抢写入任务。

### 验收标准

- code-review 默认检查正确性/回归，active artifact 和 maker-checker 仅条件加载。
- security-review 只读、证据分级，关键类别要求人工复核。
- release-check 按发布类型/diff 加载，确定性版本检查交给 validator。
- first-principles 不再强制八章节。
- blocker recheck 聚焦既有 blocker，同时阻止修复引入的真实回归。

### 回滚

- 可按单个 Skill 恢复；保留 v0.44 review convergence baseline。

### Checker 与提交切分

- code/security/release 必须独立 checker；suitability/first-principles 可合并为单独轻量提交候选。

## 阶段 E：prompts 兼容迁移与分发策略落地

### 修改范围

- 将旧 prompts 改为带弃用期的薄 Skill 包装。
- README/usage playbook 将 Skills/自然语言设为首选、prompts 为兼容入口。
- 完成显式 sync apply、发布 check、升级 migration 和用户定制保护。
- 对 plugin + local 同名 Skill 的已验证策略落地。

### 不修改范围

- v0.45.0 不删除 prompts。
- 不静默覆盖用户复制到项目外的 prompt 或本地定制 Skill。
- 不引入大型构建系统。

### 前置条件

- 阶段 C/D 的目标 Skills 稳定。
- Codex/Claude 真实客户端冲突测试完成。
- 弃用文案、周期和升级策略经维护者确认。

### 验收标准

- 旧 prompt 路径仍可用但不复制旧清单/旧 `docs/` 写回语义。
- 新用户文档以 Skills 为首选。
- 九个共享 Skill 投影在 release check 中一致。
- stock v0.44.1 项目可单命令升级；定制项目产生清晰 REVIEW-NEEDED/manual-merge。
- plugin-only、project-local-only、plugin+local、Codex-only、Claude-only fixture 均满足兼容合同。

### 回滚

- 恢复 prompt 原内容和 README 入口；保留 Skill 收敛成果。
- sync apply 可退回 check-only；不删除项目本地 Skills。

### Checker 与提交切分

- 必须独立 checker，并执行发布前完整 smoke。
- 建议分为 `prompt compatibility`、`distribution/upgrade`、`release docs/metadata` 三个提交候选。

## 实施顺序规则

- 阶段严格按 A -> B -> C -> D -> E 推进；任何阶段的行为合同变化先更新 acceptance matrix，再实现。
- 每个阶段只授权自身范围，不因前一阶段通过而自动授权下一阶段。
- 阶段内可以拆更小提交，但不得跨阶段混合入口、Skill 语义、prompts 和发布元数据。
