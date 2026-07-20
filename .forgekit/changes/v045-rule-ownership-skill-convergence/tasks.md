DesignStatus: design-approved-for-stage-a
ImplementationStatus: stage-a-implemented-awaiting-independent-check

# v0.45.0 分阶段实施计划

本计划冻结阶段 A-E 的实施切片。阶段 A 已按审批设计完成 maker 实施和确定性自验，正等待独立 checker；阶段 B-E 未进入。

## 设计阶段工作记录

| ID | 工作 | 状态 | 证据 |
| --- | --- | --- | --- |
| D-001 | 确认分支、版本、工作树和 v0.44 提交 | Done | `proposal.md` 当前状态；本轮命令记录 |
| D-002 | 盘点入口、Skills、Claude adapters、governance、references、prompts、脚本和元数据 | Done | `design.md` 第 2 节 |
| D-003 | 冻结四层所有权、分发方案、Skill 职责和风险模型 | Done | `design.md` 第 4-9 节 |
| D-004 | 设计兼容、测试、分阶段实施和回滚 | Done | `verification.md` 与本文件 |
| D-005 | 独立 blocker-recheck 关闭当前 OPEN 的 M-02 与 M-04 | Done | `review.md` 的 Second Blocker Recheck 为 PASS；历史记录保持不变 |
| D-006 | 冻结 DECISION-01/02/03 | Done | `proposal.md` / `design.md` 的已冻结决策 |

## 阶段 A task—acceptance 实施映射

| Stage-A task | 验收 ID | 实现文件 | 确定性验证 | 本阶段仅骨架 | 明确非范围 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| SA-01 共享入口与规则所有权 | A04；A11 的影响型风险静态合同 | `project-template/governance/agent-entry-contract.md`、`project-template/governance/ai-engineering-loop.md`、`scripts/validate-rule-ownership.py`、`tests/test_rule_ownership.py` | 41 条 ID/owner/application-site/anchor 检查；风险文本断言；模板校验 | 否 | 不改 AGENTS/CLAUDE，不提前实施入口瘦身或 Skill 触发语义 | Done |
| SA-02 九个通用 Skill 投影 | A05、A06 | `config/skill-projections.json`、`scripts/sync-skill-projections.py`、`tests/test_skill_projections.py` | check/apply、双方 SHA-256、缺失/漂移、unmanaged、Claude 排除、escape/reparse、全计划预检 | 否 | 不管理 `.claude/skills`、附属目录或真实用户项目 | Done |
| SA-03 升级 review/manual-merge 合同 | A07 | `scripts/upgrade_review_packets.py`、`scripts/forgekit-upgrade.py`、对应 template 镜像、`tests/test_upgrade_review_packets.py` | 四分类 fixture、稳定 packet ID、固定树、rollback 原始字节、相对 JSON 路径、既有 CLI smoke | 否 | 不创建第二套 baseline、顶层 rollback root、release migration 或新升级入口 | Done |
| SA-04 行为测试基础设施 | A01-A03、A08-A16、A19-A22 的 runner/fixture 接口 | `scripts/test-skill-behavior.py`、两个 adapter、`tests/skill-behavior/cases.json`、最小 fixture、`tests/test_skill_behavior_runner.py` | schema、授权模式、changed-path oracle、隔离、清理、脱敏、failure class、dry-run | 是；只建立安全 runner 和代表性案例 | 不声称真实路由/语义通过，不把真实客户端单次结果设为自动 blocker，不据此改 Skill | Done |
| SA-05 现有门禁与 mutation 接入 | A04-A07、A18 的确定性部分 | `scripts/validate-plugin-assets.ps1`、`scripts/validate-template.ps1`、`scripts/test-release-consistency.ps1`、`scripts/smoke-test.py`、四组单元测试 | plugin/template/release/smoke；18 个受管文件逐项 mutation 并逐字节恢复 | 否 | 不修改版本号、README、usage playbook 或发布元数据 | Done |
| SA-06 阶段记录与交接 | A04-A07、A18 的实施证据 | 本文件、`verification.md`、`ship.md` | 状态、命令、结果、未验证项和非范围复核 | 否 | 不改写 `review.md` 历史，不宣称 v0.45.0 完成或 release-ready | Done |

A17 属于后续 prompts 兼容阶段；A01-A03、A08-A16、A19-A22 的真实模型行为仍为 `NEEDS_TEST`。A17 及其余真实语义验证不得因阶段 A 基础设施通过而被视为完成。

## Stage A Independent Review finding 修复映射

本节只覆盖独立 checker 指定的 2 个 BLOCKER 和 10 个 MAJOR。修复不改变 `stage-a-implemented-awaiting-independent-check`，不进入阶段 B。

| Finding | 级别 | 根因 | 修改文件 | 新增或增强测试 | 验收命令 | 明确不修改范围 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B-01 | BLOCKER | 同一路径的后续 migration 从已更新工作树重新取得 rollback，固定 packet ID 因而把升级起点覆盖为中间版本 | 根/template `forgekit-upgrade.py`、根/template `upgrade_review_packets.py` | 真实双 migration A→B→C；rollback/恢复/重试保持 A；packet identity conflict | upgrade 集成单测、完整 smoke | 不改 packet ID 格式，不建第二套 baseline 或 rollback root | Fixed / self-verified |
| B-02 | BLOCKER | adapter 仅设置 cwd/sandbox，仍继承真实 HOME、配置、hooks/plugins/MCP、秘密环境，且没有可证明的 fixture 读取边界 | behavior runner、Codex/Claude adapters | fake executable 验证临时配置根、最小环境、prompt、cwd、无 shell；隔离能力不足时不启动 | adapter/runner 单测；真实客户端仅 probe | 不复制用户配置，不运行真实 prompt，不降低隔离标准 | Fixed / self-verified |
| M-01 | MAJOR | apply 只检查最终 target，未预检全部父组件，后续父路径文件冲突会发生在已有复制之后 | `scripts/sync-skill-projections.py` | 第二目标父组件为文件时零写入；target 目录；source 非普通文件；root/path escape | projection 定向单测、projection check | 不承诺极端 I/O 中断事务回滚 | Fixed / self-verified |
| M-02 | MAJOR | packet 在固定目录逐项覆盖，异常会混合新旧 artifact；汇总可引用半成品 | 两份 packet helper、upgrader | local/incoming/rollback/diff/JSON 前、交换、汇总故障注入；旧 packet/汇总不变且无临时残留 | upgrade 定向单测、smoke | 不新建顶层 review/backup/rollback 系统 | Fixed / self-verified |
| M-03 | MAJOR | 路径只按宽松字符正则检查，未实施所有平台可创建的版本、设备名、尾随点/空格和 Unicode 冲突策略 | 两份 packet helper | `..`、CON、NUL.txt、COM1、尾随点/空格、Unicode 合法/冲突 | path policy 单测 | 不大小写折叠或改变 POSIX UTF-8 哈希身份 | Fixed / self-verified |
| M-04 | MAJOR | 仅 upgrader 双副本有门禁，packet helper 根/template 漂移未检查 | `validate-template.ps1`、`test-release-consistency.ps1`、`smoke-test.py` | helper root-only mutation 失败，错误含双方路径/checksum，恢复精确字节 | template/release/smoke | 不创建大型同步框架 | Fixed / self-verified |
| M-05 | MAJOR | snapshot 只记录文件；`rmtree(ignore_errors=True)` 不验证清理结果 | behavior runner/tests | 空目录新增/删除、文件目录类型互换、重命名、模拟清理失败 | behavior 定向单测 | 不在真实仓库做清理故障测试 | Fixed / self-verified |
| M-06 | MAJOR | 脱敏正则只覆盖少量文本形式，command/diagnostics/home 未统一处理 | behavior runner、adapter tests | token/API key/password 的 `=` 与空格形式、Bearer、环境名、HOME 路径、maker 独立值 | redaction 定向单测 | 不声称识别任意自然语言秘密 | Fixed / self-verified |
| M-07 | MAJOR | `run` 打印 records 后固定返回 0 | behavior runner/tests | 七类 failure class 的 CLI 级退出码；validate/list/dry-run 仍为 0 | CLI 定向单测 | 不增加默认吞失败模式 | Fixed / self-verified |
| M-08 | MAJOR | adapter 统一结果缺少能力声明，model/tool trace/Skill 来源长期为空且无法区分不可观察 | adapters、runner/tests | 完整/缺 model/缺 trace/缺 source/结构化解析失败；证据不足为 uncertain | evidence capability 单测 | 不从自由文本猜测或伪造证据 | Fixed / self-verified |
| M-09 | MAJOR | `EXPECTED_SKILLS` 复制九项正式清单，形成第二机器权威 | sync 工具、ownership validator/tests | sync 无九项硬编码；从 41 条 ROUTE 规则派生并交叉验证 manifest | ownership/projection 单测 | 不把九项列表复制到发布脚本或测试 | Fixed / self-verified |
| M-10 | MAJOR | 原 27 项测试未覆盖 checker 的关键 mutation 与失败顺序 | 四组阶段 A tests、release/smoke gate | 汇总以上 projection/upgrade/behavior/adapter/helper 全部关键失败路径 | 完整 unittest、发布校验、隔离 smoke | 不削弱既有断言，不加入真实模型 CI blocker | Fixed / self-verified |

修复自验结果：12/12 finding 均已按上表边界实现并通过定向测试；状态仍为 `stage-a-implemented-awaiting-independent-check`。真实 Codex/Claude 仅执行 version/help capability probe，因两个客户端均无法证明 fixture-only 读取边界和网络/外部动作禁用而失败关闭，未执行 prompt。

### Findings recheck 最后定向修复

本节只处理 recheck 后仍 OPEN 的 M-02、M-06、M-10；其他 2 个 BLOCKER 和 7 个 MAJOR 只复跑回归，不重新设计。

| Finding | Recheck 根因 | 定向修改 | 新增测试 | 结果 |
| --- | --- | --- | --- | --- |
| M-02 | canonical packet 和两份 summary 已发布后，`.old-*` 删除失败仍进入提交前回滚，导致旧 packet 配新 summary | packet helper 双副本明确提交点；upgrader 双副本加强 packet/summary 交叉验证和同 packet-id summary 替换；提交后 cleanup 只 warning，不回滚 | `test_old_cleanup_failure_keeps_committed_packet_and_summaries_consistent`；复跑既有 staging/交换/summary 失败测试 | Fixed / self-verified |
| M-06 | 递归遍历嵌套字典时只处理字符串值，没有按规范化敏感键整体替换对应值 | runner 增加 `sanitize_record`、敏感键规范化/供应商前缀匹配、dict/list/tuple 递归和 `serialize_sanitized` 最终持久化边界 | `test_final_recursive_sanitization_redacts_nested_auth_values_and_evidence` | Fixed / self-verified |
| M-10 | 42 项测试没有覆盖 post-commit old cleanup failure 和嵌套 environment/auth secret | 增加上述两个真实文件状态/最终 JSON 扫描测试；全量增至 44 项 | 定向 5/5、upgrade 11/11、behavior+adapter 19/19、全量 44/44 | Fixed / self-verified |

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
