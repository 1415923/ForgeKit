DesignStatus: design-approved-for-stage-a
ImplementationStatus: stage-e-implemented-awaiting-independent-check

# v0.45.0 分阶段实施计划

本计划冻结阶段 A-E 的实施切片。阶段 A、阶段 B、阶段 C、阶段 D 已通过独立 checker；阶段 E 已完成 maker 实施并等待独立 checker。

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

## 阶段 B task—acceptance 实施映射

| Stage-B task | 验收 ID | 修改文件 | 确定性验证 | 真实模型验证 | 阶段 C-E 非范围 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| SB-01 模板入口内容迁移 | A01-A04、A11 的入口静态部分、A19、A20、A22 | `project-template/AGENTS.md`、`project-template/CLAUDE.md`、template manifest、generated-project harness | 七个共享 anchor、最小路由、平台差异、禁用完整条件协议和固定门槛；fixture 与目标逐字节一致 | A01-A03、A19-A20、A22 仍为 `NEEDS_TEST` | 不改任何 Skill 正文/metadata/trigger，不迁 prompts、README 或 usage | Done / awaiting checker |
| SB-02 stock/custom 安全升级 | A07、A18 | change-local `stage-b-migration-draft/`、根/template `forgekit-upgrade.py` 的精确 root-entry allowlist | stock AGENTS/CLAUDE 更新；custom/unknown 不覆盖；missing；原始 rollback；packet/summary；同路径多 migration；Windows 路径 | manual merge 可理解性仍为 `NEEDS_TEST` | 不创建正式 `migrations/0.45.0`，不更新 VERSION/plugin/marketplace 版本 | Done / awaiting checker |
| SB-03 入口 validator、fixture 与 mutation | A01-A04、A11、A12-A13 的“不复制 review convergence”静态部分、A16 的“不固定八章节”静态部分、A19-A20 | 两个 Stage B validator、两组单测、behavior fixture/cases、template/release/smoke 门禁 | 必要 marker 缺失、review convergence 回流、固定阈值、universal review、baseline 漂移、custom 错误覆盖 mutation 均失败并恢复 | 行为 cases 只更新入口 fixture；真实客户端结果不伪造 | 不调整 code-review/security/release/first-principles 工作流 | Done / awaiting checker |
| SB-04 回归与交接 | A04-A07、A18；A01-A03/A19-A22 的 runner 骨架 | 本文件、`verification.md`、`ship.md` | 41-rule ownership、18-file projection、56 单测、upgrade packets、plugin/template/release/manifest/smoke、`git diff --check` | dry-run 为 `GRADER_UNCERTAIN/not-run`；真实 Codex/Claude 继续 `NEEDS_TEST` | 不宣称 A01-A22 全过，不授权阶段 C | Done / awaiting checker |

阶段 B 必须完成的内容是 SB-01 的入口迁移和 SB-02 的 stock/custom upgrade migration；SB-03/SB-04 给出可确定性复核的静态合同与回归证据。A08-A10 与 A11 的具体 Skill 分支属于阶段 C；A12-A16 的 Skill 工作流属于阶段 D；A17、A21 的 prompts 与 plugin/project-local 职责拆分属于阶段 E。阶段 B 不执行真实 prompt，相关项保持 `NEEDS_TEST`。

### Stage B validator MAJOR 定向修复映射

本轮只关闭独立审查的两个 validator 覆盖缺口，不重新设计入口、migration draft 或 upgrader 产品行为。

| Finding | 根因 | 修改文件 | 新增反例 | 验收方式 |
| --- | --- | --- | --- | --- |
| M-B1 | marker 和有限正则无法识别矛盾正文、未逐项校验九个 Skill 路由 | `scripts/validate-agent-entries.py`、`tests/test_agent_entries.py`、正式门禁接入脚本 | audit contradiction；外部动作/证据等明确反向声明；从 `config/skill-projections.json` 派生并逐个删除 Skill route | 每个反例调用正式 validator，必须返回错误或 CLI 非零；正常安全措辞和 fenced 反例保持通过 |
| M-B2 | baseline checksum 仅内部自洽而无独立 Git 锚点；未验证 production discovery；validator 未执行实际分类行为 | `scripts/validate-stage-b-entry-migration.py`、`tests/test_stage_b_entry_migration.py`、正式门禁接入脚本 | baseline+checksum 同步篡改；descriptor source commit 篡改；incoming+checksum 同步漂移；discovery 重定向；stock/custom/unknown/missing/mixed/rollback | baseline 必须逐字节锚定已审批 Stage A commit；production `check` 与完整真实 upgrader fixture gate 必须由 validator 默认执行，任一不符均非零 |

范围外保持不变：Stage C/D 的具体 Skill 工作流、Stage E 的 prompts 与分发职责拆分、真实模型 prompt、入口正文、draft migration 语义、正式 migration、VERSION 和发布元数据。

定向修复结果：M-B1 与 M-B2 均为 `Fixed / self-verified / awaiting checker`。M-B1 的九项路由从 `config/skill-projections.json` 动态派生，AGENTS/CLAUDE 各 9 项删除反例均失败；明确 audit/external/evidence 矛盾失败，正常措辞与 fenced 反例通过。M-B2 使用 `506cecf8d377a17a2616bf3b9eeea483ee4039a4` 的 Git blob 和当前模板双锚点，production 默认 discovery 与重定向反例、stock/custom/unknown/missing/mixed/rollback 和同路径多 migration origin rollback 均由正式 validator 默认执行。定向单测 32/32、全量单测 76/76、release mutation 和完整隔离 smoke 通过；所有 mutation 和临时目录已恢复/清理。状态继续为 `stage-b-implemented-awaiting-independent-check`。

### M-B1 剩余 contradiction 漏检定向修复映射

| Finding | 剩余根因 | 修改文件 | 新增反例 / 防误报 | 验收方式 |
| --- | --- | --- | --- | --- |
| M-B1 contradiction family | `audit-auto-write` 仍由少量 audit/review 单句正则组成，没有统一组合只读 subject、自动写入 action、无 repair request 写入和否定作用域 | `scripts/validate-agent-entries.py`、`tests/test_agent_entries.py`、`scripts/test-release-consistency.ps1`、本轮三份 maker 工件 | checker 五例分别独立测试；subject/action/modal/大小写组合；must not/never/cannot/no audit/propose-but-not-apply/recommend-but-do-not-modify；fenced/Skill route | 五例正式 validator 均非零且报告 `audit-default` category 与命中正文；安全否定、routing 和 fenced 全部通过；既有 route/anchor/convergence/threshold 测试保持通过；release 至少两个非 audit 原句 mutation 逐字节恢复 |

M-B2 保持 CLOSED。本轮不修改入口、manifest、migration、upgrader、Stage A 基础设施、Skills、prompts、VERSION、正式 migration、`review.md` 或 `usage.html`，也不进入 Stage C。

定向修复结果：M-B1 已完成 maker 实施与自验，等待原 checker 复核。`audit-auto-write` 已改为 subject/action/no-repair/negation 四组小型组合规则；五个 checker 漏检反例各自以正式 validator 返回 1，并报告 `audit-auto-write [audit-default]` 与命中正文。7 个安全否定/只读措辞、fenced 反例及 routing/path 内容通过；AGENTS/CLAUDE 的 manifest-derived 9+9 route deletion 回归继续失败关闭。`tests.test_agent_entries` 31/31、全量单测 92/92、两个新增 release contradiction mutation、完整门禁和含 `.git` 的短路径 smoke 均通过，mutation 与临时目录已恢复/清理。状态保持 `stage-b-implemented-awaiting-independent-check`。

### M-B1 Markdown 导航误报定向修复映射

| Finding | 根因 | 修改文件 | 新增反例 / 防逃逸 | 验收方式 |
| --- | --- | --- | --- | --- |
| M-B1 Markdown/prose separation | contradiction family 直接扫描仅剔除 fenced block 的原始 Markdown，导致 heading、inline-code Skill、link/path 导航 token 与普通 `auto-edit` 术语被错误组合 | `scripts/validate-agent-entries.py`、`tests/test_agent_entries.py`、必要的正式 gate、三份 maker 工件 | checker 四个误报分别通过；ATX/Setext、inline code、多 delimiter、link/image/reference/autolink、manifest/Claude 动态 Skill ID、Windows/POSIX/文件路径；heading/link/inline/list/table 后的真实 contradiction 继续失败 | 正式 CLI 验证 exit code；失败项同时断言 `audit-default` category 和 matched text；提取器边界测试确认只移除 Markdown/navigation 结构；原五例、五个独立组合、否定句和 9+9 route deletion 全部回归 |

M-B2 保持 CLOSED。本轮不缩小 subject/action/no-repair family，不增加 checker 示例白名单或第二份 Skill 清单，不修改入口、manifest、migration、upgrader、Stage A 基础设施、Skills、prompts、VERSION、`review.md` 或 `usage.html`。

定向修复结果：Markdown/prose separation 已完成 maker 实施与自验，等待原 checker 复核。正式 CLI 中四个 checker 误报均为 exit 0；原五个 contradiction 与五个独立 subject/action 组合均为 exit 1，并报告 `audit-default` 与准确 matched text；十类安全否定均为 exit 0；heading/link/inline 后的真实正文均为 exit 1；AGENTS/CLAUDE 各 9 项 route deletion 继续失败关闭。focused tests 58/58、全量 119/119、现有 release mutations、完整门禁和含 `.git` 的短路径 smoke 全部通过；状态保持 `stage-b-implemented-awaiting-independent-check`。

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

### Stage-C task—acceptance 实施映射

| Stage-C task | Skill owner path | Invocation policy | Acceptance IDs | 确定性验证 | 真实行为状态 | 后续阶段 |
| --- | --- | --- | --- | --- | --- | --- |
| SC-01 新项目轻量初始化 | `skills/project-init/SKILL.md` | implicit eligible | A01-A03、A08、A19 | owner/trigger/route/TODO/授权与外部动作 marker；正负路由及 fixed-question mutation；投影逐字节检查 | 2 个行为 case 已 validate/list/dry-run；真实 Codex/Claude 为 `GRADER_UNCERTAIN/not-run`、`NEEDS_TEST` | A22 的真实单平台证据留待 release evidence |
| SC-02 已初始化项目 bootstrap 补缺 | `skills/project-bootstrap-fill/SKILL.md` | explicit-only | A02-A03、A10、A19 | placeholder-only、保留定制、冲突不覆盖、无关文档禁止、explicit-only；覆盖定制 mutation | 2 个行为 case 已声明；真实模型 `NEEDS_TEST` | A22 同上 |
| SC-03 只读接手审计 | `skills/handover-review/SKILL.md` | implicit eligible | A01、A03、A09、A20 | read-only、证据优先、无自动修复、owner-only writeback；read-only/auto-repair mutation | 2 个行为 case 已声明；真实模型 `NEEDS_TEST` | A12-A16 的 review/release convergence 属 Stage D；A22 留待真实证据 |
| SC-04 已实现事实回填 | `skills/document-backfill/SKILL.md` | explicit-only | A01-A03、A10、A19 | owner/fact/conflict/batch/保留定制合同；推测补全 mutation | 2 个行为 case 已声明；真实模型 `NEEDS_TEST` | A22 留待真实证据 |
| SC-05 高影响变更规划 | `skills/large-change-planning/SKILL.md` | implicit eligible | A01-A03、A11、A19-A20 | scope/trust boundary/non-goals/stage authorization/acceptance/rollback；单文件高风险与多文件低风险；数量门槛/universal-checker mutation | 2 个行为 case 已声明；真实模型 `NEEDS_TEST` | 独立 checker 的具体 review workflow 属 Stage D；A22 留待真实证据 |
| SC-06 投影与开发期升级兼容 | 由 SC-01 至 SC-05 owner path 派生 | package policy follows owner | A05-A07 | tasks mapping 与 41-rule matrix 双源锁定；root→`.agents` 字节一致；Stage B commit baseline、当前 projection incoming、stock/custom/unknown/missing/rollback | 不需要模型 | 正式 `migrations/0.45.0` 与发布迁移留 Stage E |
| SC-07 Stage C validator、mutation 与 runner cases | 由 SC-01 至 SC-05 owner path 派生 | case-specific | A01-A03、A08-A11、A19-A20 | 正式 validator、package/Markdown/集合/behavior/CRLF mutation；13-case manifest validate/list/dry-run | dry-run 不伪造结果；真实客户端继续 `NEEDS_TEST` | A17/A21 属 Stage E；A18 仅作为最终 release consistency gate；A22 为最终真实客户端证据 |

A12-A16 明确属于 Stage D；A17、A21 属于 Stage E；A18 只是最终 release/version consistency gate；A22 必须由真实 Codex/Claude 单平台运行证据完成。本阶段不为填满映射而实施这些后续项。

### Stage C independent-review findings 修复映射

| Finding | 根因 | 修改文件 | 新增失败路径 | 验收命令 |
| --- | --- | --- | --- | --- |
| C-M01 | implicit policy 误放在 SKILL frontmatter，且三个 active default prompt 与已通过正文冲突 | bootstrap/backfill `SKILL.md` frontmatter；project-init/bootstrap/backfill 根与投影 `agents/openai.yaml`；Stage C validator/tests；development migration | frontmatter policy、YAML policy 缺失/字符串/错层；questionnaire/selected-stack；one-source/fixed batch；YAML projection drift | Stage C package tests；projection check；migration validator |
| C-M02 | template manifest refresh 只更新已列 checksum，不发现漏项；缺少 Stage C package completeness gate | template manifest；Stage C validator/tests；template validator | 任一五项 SKILL 或变更 YAML 缺失、checksum 错误、duplicate | Stage C manifest tests；manifest `--check`；template gate |
| C-M03 | marker/有限 regex 未识别保留正向 marker 的直接反向语义 | Stage C validator/tests | existing-project reinitialize 三类；mandatory five-Skill sequence 三类；安全否定必须通过 | Stage C semantic tests；正式 validator CLI |
| C-M04 | Stage C 直接扫描 raw Markdown，未复用 Stage B policy-prose 层 | Stage C validator/tests；复用 Stage B extractor（仅必要时最小公共化） | fenced/heading required marker 伪造；fenced/heading legacy；safe negation；navigation；list/table/link 后真实反例 | Stage C Markdown tests；Stage B entry tests 回归 |
| C-M05 | 只从 matrix 的单一文案筛选 owner，且正式 CLI 未锁定 cardinality | tasks SC-01..05 mapping；Stage C validator/tests | matrix/tasks 缩为四项、集合不同、Stage D owner、duplicate | Stage C skill-set tests；ownership validator |
| C-M06 | runtime fixture 无权威 Skill package，explicit prompt 未渲染 `$skill-id`，case 无 evidence contract | behavior runner/cases/fixtures/tests；adapter context | 缺 materialized source；explicit 未渲染；implicit 被注入；explicit-only implicit positive；evidence 缺失/类型错误 | behavior runner tests；validate/list/dry-run |
| C-M07 | byte-sensitive文本无 LF checkout contract，maker smoke 用 overlay 掩盖 fresh clone | 根/模板 `.gitattributes`；fresh-clone gate/tests；migration/smoke/release/template 接入 | autocrlf true/false fresh checkout；删 LF rule 后失败；generated-project contract | fresh-clone tests；release consistency；三类 smoke |

实现结果：C-M01 至 C-M07 均为 `Fixed / self-verified / awaiting original checker recheck`。这只表示 maker 已关闭确定性失败路径；不表示 Stage C 已获独立批准。双 fresh-clone gate 从临时 Stage C commit 直接 checkout，clone 后不覆盖 tracked bytes；真实模型证据仍为 `NEEDS_TEST`。

本映射只授权关闭 C-M01 至 C-M07。状态继续为 `stage-c-implemented-awaiting-independent-check`；不得修改 `review.md`，不得进入 Stage D/E。

### Stage C findings recheck 剩余五项修复映射

| Finding | 剩余根因 | 修改文件 | 独立反例 | 正式门禁 |
| --- | --- | --- | --- | --- |
| C-M01 | package prompt 未执行 `$skill-id` authoring 合同，且 fixed-count risk threshold 未覆盖 default prompt | 五个根/投影 `agents/openai.yaml`；Stage C package validator/tests；development migration | 缺失/重复/错误/inline-only `$skill-id`；`5 files` 与通用数值阈值；安全否定 | Stage C package validator；projection；migration |
| C-M02 | template manifest 只覆盖 changed files，未锁定 projection manifest 的完整 18-file target 集合 | manifest generator/checker；template manifest；Stage C/manifest tests | handover/large-change unchanged YAML 缺失；非 Stage C target 缺失；duplicate/checksum；projection 新 target 未同步 | manifest `--check`；Stage C validator；template gate |
| C-M03 | reinitialize 与 mandatory pipeline detector 仍过度贴近冻结句式 | Stage C semantic validator/tests | checker 四条等价表达；额外 subject/action/order 变体；安全否定 | Stage C semantic CLI；Stage C tests；C-M04/C-M05 回归 |
| C-M06 | bounded-write authorization 未绑定 write evidence/allowed paths，explicit renderer 对已有 marker 非幂等 | behavior schema/runner/cases/tests | bounded-write evidence false/空 allowlist；handover write oracle false；已有/重复/inline/错误 marker；implicit case | behavior validate/list/dry-run；behavior tests |
| C-M07 | projection、manifest 或 migration checksum/comparison 仍可能在 text decode 后规范化换行，且无完整 LF content gate | raw-byte/checksum helpers；projection/manifest/Stage C/migration validators；release/smoke tests | root 单侧 CRLF；root/template 双侧 CRLF；同步 manifest checksum；YAML CRLF；migration CRLF+descriptor | byte-exact projection/manifest/migration；LF content gate；fresh-clone/smoke |

本映射只授权修复仍 OPEN 的 C-M01、C-M02、C-M03、C-M06、C-M07。C-M04、C-M05 保持 CLOSED，仅运行回归；状态继续为 `stage-c-implemented-awaiting-independent-check`。

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

### Maker 实施结果

- 五个根级权威 `SKILL.md` 已按影响型风险、只读审计、局部授权、外部动作保护和最小写回合同收敛；没有要求五项串行执行。
- `config/skill-projections.json` 未另建竞争清单；`.agents` 投影由既有同步器确定性生成。
- change-local 单一 development migration draft 已扩展五个 Skill；baseline 锚定阶段 B 提交，incoming 锚定当前 projection；未创建正式 migration。
- Stage C 当前状态为 `stage-c-implemented-awaiting-independent-check`；不得视为 `stage-c-approved`，不得授权 Stage D。

## 阶段 D：审查和发布 Skills

### Stage-D task—acceptance 实施映射

本阶段按维护者当前授权只收敛四个通用 Skill；设计中 A16 的 Claude first-principles 输出行为继续为 `NEEDS_TEST`，不在本阶段修改 `.claude/skills/` 或扩大为第五个实现 owner。

| Stage-D task | Skill owner path | Acceptance IDs | 确定性验证 | 行为状态 | 后续阶段 |
| --- | --- | --- | --- | --- | --- |
| SD-01 实现审查与 findings recheck | `skills/code-review/SKILL.md` | A01-A03、A12-A13、A20 | package/只读/证据/严重度/initial-recheck/非自动 maker/影响型 checker/外部动作合同；正负路由与 mutation | cases 只做 validate/list/dry-run；真实模型 `GRADER_UNCERTAIN/not-run` | A22 真实客户端证据留最终 release evidence |
| SD-02 安全边界审查 | `skills/security-review/SKILL.md` | A01-A03、A14、A20 | 实际安全影响触发、只读、证据等级、人工复核、非普通必经、非自动 maker、外部动作合同 | 同上 | A22 同上 |
| SD-03 发布准备审查 | `skills/release-check/SKILL.md` | A01-A03、A15、A18、A20 | release-only trigger、渐进加载、ready/blocked/not-verified、无自动 bump/tag/push/release、普通 commit 负路由 | 同上 | 正式 migration、VERSION 与 release metadata 留 Stage E |
| SD-04 ForgeKit 适配评估 | `skills/project-suitability/SKILL.md` | A01-A03、A19、A22 | 只读建议、四类结论、采用成本/约束、无自动初始化/迁移/全 Skill pipeline | 同上 | 初始化或治理改造只能由后续明确请求另行路由 |
| SD-05 投影与开发期升级兼容 | 由 SD-01 至 SD-04 owner path 派生 | A05-A07、A18 | root→template raw-byte 投影；18/18 manifest；Stage C commit baseline、当前 projection incoming；stock/custom/unknown/missing/rollback | 不需要模型 | 正式 `migrations/0.45.0` 留 Stage E |
| SD-06 validator、behavior 与正式门禁 | 由 SD-01 至 SD-04 owner path 派生 | A01-A03、A12-A15、A19-A20 | 双源四项集合、有限语料、package prompt、只读/授权/外部动作、路由/非 mandatory pipeline、mutation、dry-run | 不伪造真实结果 | A16 与真实 A22 证据保持 `NEEDS_TEST` |

Stage D 的静态 gate 只覆盖本映射和 `verification.md` 冻结的有限语料类别；矩阵外罕见同义词默认记为 NOTE / `NEEDS_TEST`，除非揭示未授权写入、外部发布、安全边界或真实常见路由的系统性破坏。

### Stage D maker 实施结果

- SD-01 至 SD-04 的四个权威 Skill 已完成：默认只读；finding 不产生 maker 权限；明确本地修复授权必须限定 writable paths 和 changed-path/validation evidence；commit/push/tag/release/deploy 等外部动作仍要求用户明确授权。
- 四个 package default prompt 各包含唯一独立 `$skill-id`，未调用其他 Stage D Skill；public ID、name 和 display name 未变。
- SD-05 development draft 在既有唯一 package 中新增 8 个 Stage D target；baseline 均锚定 Stage C commit `868846da54634899141047951b0f4275ad378966`，incoming 与当前 template projection 逐字节一致。
- SD-06 新增双源四项 validator、11 项 Stage D 定向单测和 18 个 behavior cases；release consistency 保留六类有限 mutation。真实模型未运行，behavior 仍为 `GRADER_UNCERTAIN/not-run`。
- Maker 状态为 `stage-d-implemented-awaiting-independent-check`；A16 和真实 A22 证据继续 `NEEDS_TEST`，正式 migration、VERSION 与 release metadata 留 Stage E。

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

### Stage E maker 实施记录

| Task | 实施结果 | 确定性验收 | 真实行为状态 |
| --- | --- | --- | --- |
| SE-01 正式 migration | 从唯一 development draft 提升 root/template `migrations/0.45.0`，保留 20 个 action、逐 action baseline 与 payload | Stage E validator、migration behavior、production discovery | manual merge 体验 `NEEDS_TEST` |
| SE-02 版本表面 | VERSION、plugin、marketplace、template state/manifest 统一为 0.45.0 | plugin/template/release consistency | N/A |
| SE-03 文档与 prompts | README 中英文、CHANGELOG、usage playbook 和七个旧 prompt 路径收敛；prompt 保留 v0.45-v0.46 弃用窗口 | Stage E validator、template manifest | 真实 selector/source `NEEDS_TEST` |
| SE-04 发布门禁 | 新增结构化 Stage E validator/tests，并接入 template/plugin/release/smoke/fresh clone | unit、mutation、LF/CRLF、smoke | 不执行真实模型 prompt |
| SE-05 状态收口 | 写回本 change 的 tasks/verification/ship，保持 review 历史不变 | status/content audit | 等待独立 checker |
| SE-06 validator 生命周期兼容 | Stage C current-version gate 改为 VERSION/template manifest 动态一致；Stage B draft gate按当前 VERSION区分 pre-release 与 release-preparation，同时始终完整验证 development draft | 四组版本一致性 mutation；0.44.1/0.45.0 两阶段 migration lifecycle tests；production discovery | 不改变 Stage A-D 语义、分类或 rollback |
| SE-07 三路发布候选 smoke | 当前 scoped snapshot、autocrlf=false fresh clone、autocrlf=true fresh clone均运行完整 smoke；临时提交排除用户删除的 `usage.html` | `test-fresh-clone-crlf.py --full`；clone 后无 tracked-byte overlay | 真实模型继续 not-run |
| SE-08 M-E01 template migration manifest | manifest generator 从当前 template migration descriptor 动态派生 descriptor、baseline 与 incoming 的完整文件集合，不硬编码 41/197 | Stage E validator、manifest check、8 项定向反例、3 项 release mutation | N/A |
| SE-09 M-E02 release gate wiring | 五个冻结顶层入口由独立结构化 wiring validator 复核；plugin gate 同时真实执行 Stage E 与独立 wiring gate并传播退出码 | wiring validator、6 项定向反例、3 项真实 plugin-gate mutation | N/A |

Stage E 不修改九个 Skill 语义、AGENTS/CLAUDE 治理合同、Stage C/D 自然语言规则或 behavior 合同；不包含用户删除的 `usage.html`。最终 maker 状态只能是 `stage-e-implemented-awaiting-independent-check`。

Stage E maker 最终确定性结果：Stage E 定向测试 25/25、全量 unittest 217/217、behavior 31 cases、projection 18/18；template manifest 由实际集合动态得到197项，其中正式0.45.0 template migration为41/41。plugin/template/release consistency、当前 scoped snapshot smoke 与 autocrlf=false/true fresh clone均 PASS。正式 migration action 仍为20项，production discovery只发现唯一正式0.45.0并忽略change-local draft。

### Stage E independent review：M-E01 / M-E02 修复映射

| Finding | 根因 | 修改文件 | 新增失败路径 | 正式门禁 |
| --- | --- | --- | --- | --- |
| M-E01 | manifest generator未把正式template migration inventory视为受管集合 | manifest generator/manifest、Stage E validator/tests、release mutation | 缺descriptor/baseline/incoming、duplicate、checksum、draft/root误入 | manifest check；Stage E CLI；template/release gates |
| M-E02 | 顶层gate只执行Stage E，没有独立结构化接线合同；删除plugin调用仍可绿灯 | wiring validator/tests、plugin/template/release/smoke/fresh-clone接线 | plugin调用删除、忽略退出码、无效路径、template/release接线删除 | 独立wiring CLI；真实plugin gate；release consistency |

两项修复只增加结构化发布集合和有限接线检查；未修改正式migration descriptor/baseline/incoming、action集合、九个Skill、Stage A-D治理语义或版本表面。状态继续为 `stage-e-implemented-awaiting-independent-check`。

### Stage E M-E02-R1 runtime-canary 止损合同

- 静态 `validate-release-gate-wiring.py` 只检查五个固定入口、runtime-canary脚本/测试、登记集合和正式release-consistency接线等有限结构，不证明任意PowerShell控制流。
- `test-stage-e-gate-runtime.py` 在含`.git`的隔离候选中，以template manifest版本错配作为固定Stage E故障，真实执行plugin、template、release consistency、smoke和fresh clone，证明Stage E调用及失败传播。
- M-E02最终验收只看上述五入口runtime canary；不再因新的PowerShell文本、注释或控制流变体扩展静态解析。
- 注释块、`if ($false)`、删除调用、错误路径和吞退出码由runtime mutation自动覆盖；只要固定canary能捕获真实断链，M-E02即结束。
- 新变体只有在能使正式runtime canary错误通过时，才可能成为新finding。
- `FORGEKIT_STAGE_E_RUNTIME_CANARY_CHILD`仅阻止子进程再次启动完整编排，不跳过Stage E validator；正式入口默认路径仍执行Stage E。

## 实施顺序规则

- 阶段严格按 A -> B -> C -> D -> E 推进；任何阶段的行为合同变化先更新 acceptance matrix，再实现。
- 每个阶段只授权自身范围，不因前一阶段通过而自动授权下一阶段。
- 阶段内可以拆更小提交，但不得跨阶段混合入口、Skill 语义、prompts 和发布元数据。

### Stage C recheck 剩余五项 maker 实施结果

- C-M01：五个 package default prompt 分别以唯一独立的 $project-init、$project-bootstrap-fill、$handover-review、$document-backfill、$large-change-planning 开头。validator 同时扫描 Skill policy prose 和 package prompt；缺失、重复、错误/其他 Skill invocation、fenced-only invocation、任意正向固定文件/模块/行数门槛均失败，安全否定通过。
- C-M02：manifest generator 从 config/skill-projections.json 派生完整 target 集合，正式合同为 18/18、每项恰好一次、raw-byte SHA-256；Stage C 五个 package 为 10/10。handover、large-change 的 unchanged YAML 与其余通用 Skill projection 不再遗漏。
- C-M03：existing-project subject、repeat/restart/from-scratch action、mandatory/universal/scope/sequence family 已扩展。checker 四个漏检句和额外变体由真实 CLI 非零拒绝并定位 Skill/category/matched prose；安全否定通过。C-M04 Markdown 分层与 C-M05 tasks/matrix 双源集合保持 CLOSED。
- C-M06：bounded_local_write 必须同时有非空 allowed paths 与 write_behavior=true；handover read-only 仍要求 write oracle。renderer 对已有独立 $skill-id 保持幂等，无 marker 插入一次，多 marker/错误 marker 失败，inline 示例不算正式调用，implicit 不注入。
- C-M07：projection、manifest、Stage C 与 migration checksum 全部使用原始 bytes；LF content gate 独立拒绝 CRLF/lone CR。根与 generated-project checkout contract 覆盖 manifest 实际管理的 Markdown/JSON/YAML/YML/TOML/Python/PowerShell/Shell 文本。单侧 CRLF、双侧 CRLF、双侧加 manifest checksum、YAML CRLF、migration CRLF 加 descriptor checksum mutation 均非零。
- 唯一 development migration 现管理五份 Stage C SKILL.md 与五份 agents/openai.yaml；baseline 来自 Stage B commit，incoming 与当前 template projection 一致，stock/custom/unknown/missing/rollback 回归通过。没有建立正式 migration。
- 定向 83/83、全量 unittest 160/160；正式快速门禁、release consistency 通过。临时 commit 477e041183602ca9cc1ddc006404ca98084a7441 的 scoped snapshot、autocrlf=false、autocrlf=true 三路完整 smoke 均 PASS；clone 后无 byte overlay，删除 Markdown LF rule 后 validator exit 1。

以上只构成 maker 自验。状态保持 stage-c-implemented-awaiting-independent-check，等待原 checker 只复核 C-M01、C-M02、C-M03、C-M06、C-M07。

### Stage C 最后两个 OPEN finding 修复映射

| Finding | 剩余根因 | 修改文件 | 独立反例 | 正式门禁 |
| --- | --- | --- | --- | --- |
| C-M01 | 固定数量检测的 workload unit 词形不完整，且 trigger/target 组合未覆盖 directory、service、package、endpoint 等等价风险流程表达 | `scripts/validate-stage-c-skills.py`、`tests/test_stage_c_skills.py`、release consistency mutation | `A 42-directory change requires independent planning.`；quantity × unit × trigger/target 表驱动变体；安全否定 | Stage C validator；Stage C tests；template gate；release consistency directory mutation |
| C-M03 | reinitialize 与 mandatory pipeline 规则仍依赖有限句式，未完整组合已有状态主体、初始化/再次语义、全量集合、普遍范围和顺序/不可跳过语义 | `scripts/validate-stage-c-skills.py`、`tests/test_stage_c_skills.py`、release consistency mutation | setup-again、action-first reinitialize、one-by-one、processed sequentially、take-through-fixed-order；安全否定 | Stage C semantic CLI；Stage C tests；template gate；release consistency setup/pipeline mutations |

本映射只授权关闭 C-M01 与 C-M03。C-M02/C-M04/C-M05/C-M06/C-M07 保持 CLOSED，仅做最小回归；状态继续为 `stage-c-implemented-awaiting-independent-check`。

### Stage C 最后两个 OPEN finding maker 结果

- C-M01：fixed-count detector 已改为 `quantity expression + workload unit + mandatory trigger + risk/process target` 的数据驱动组合。数量覆盖任意阿拉伯数字、one 至 twelve 与 dozens；unit 使用词根式单复数 family，覆盖 file/directory/folder/module/line/component/package/service/endpoint/document/class/repository/project；安全否定、example-only 和 may/can-remain-low-risk 上下文不报错。错误包含 Skill/package、`fixed-quantity-risk-threshold`、matched prose 以及 quantity/unit/trigger/target。
- C-M03：reinitialize detector 组合 existing/initialized subject、initialization/setup/bootstrap action、again/from-scratch/anew/repeat/rerun/restart/reinitialize 语义与 modal/命令式；mandatory pipeline detector 组合 full Skill set、universal scope、mandatory 与 sequence/workflow，另行拒绝 no-Skill-may-be-skipped 语义。安全否定、alternatives、rather-than、no-fixed-order 与 not-required 继续通过。
- checker 六句均在保留正向合同的隔离 package 副本中运行真实 Stage C CLI，逐项 exit 1，并回显 Skill/package、category 与 matched prose。Stage C 定向模块 28/28；完整 unittest 163/163。
- release consistency 新增 directory threshold、setup again、one-by-one pipeline 三项正式 mutation，均非零失败并逐字节恢复。Stage C、projection、18/18 manifest、ownership、entry、migration、behavior validate/dry-run、template、fresh-clone 与 release consistency 全部 PASS。
- C-M02/C-M04/C-M05/C-M06/C-M07 保持 CLOSED；未修改五个 Skill 正文/package YAML、projection、manifest、behavior、migration、`.gitattributes`、fresh-clone runner或 Stage B validator。

以上仍只构成 maker 自验。当前状态保持 `stage-c-implemented-awaiting-independent-check`，等待原 checker 只复核 C-M01 与 C-M03。

### Stage C 最后一个 OPEN finding（C-M03）修复映射与结果

| Finding | 剩余根因 | 修改文件 | 独立反例 | 正式门禁 |
| --- | --- | --- | --- | --- |
| C-M03 | reinitialize 检测仍受 subject/action 词序影响，且 mandatory full-Skill 检测错误地把 sequence/order 词作为必要条件 | `scripts/validate-stage-c-skills.py`、`tests/test_stage_c_skills.py`、`scripts/test-release-consistency.ps1`；本节同步 `tasks.md`、`verification.md`、`ship.md` | action-first bootstrap once more、relative-clause setup again、局部 `without repeating`；full set + universal scope + mandatory、full set + scope + chain、non-skippable + scope | Stage C validator CLI；Stage C 28 项定向测试；template gate；release consistency 四项 C-M03 mutation |

- C-M03A 现按句子计算 `existing_subject + init_action + repeat_action + positive_requirement`，feature 顺序不影响判断；`negated_init` 与 `alternative_route` 阻止局部否定和 handover/bootstrap-fill 替代路由误报。
- C-M03B 现分别拒绝 `full_skill_set + universal_scope + mandatory`、`full_skill_set + universal_scope + sequence`、`non_skippable + universal_scope`，不再要求每条违规句都出现 sequence、pipeline 或 order。
- 错误输出包含 Skill/package、category、matched prose 和 feature 集合。checker 的两个 reinitialize 漏检与六个 pipeline 漏检均由正式 CLI exit 1；`Existing repositories may continue to handover-review without repeating setup.` exit 0。
- C-M01 与 C-M02/C-M04/C-M05/C-M06/C-M07 只做回归；其已关闭实现未修改。状态继续为 `stage-c-implemented-awaiting-independent-check`，只等待原 checker 复核 C-M03。

### Stage C C-M03A 最后两个命令式漏检

| Finding | 剩余根因 | 修改文件 | 独立反例 | 正式门禁 |
| --- | --- | --- | --- | --- |
| C-M03A | `bootstrap` 句首命令未满足 positive requirement；`set up` 短语动词未归一化为初始化动作 | `scripts/validate-stage-c-skills.py`、`tests/test_stage_c_skills.py`、`scripts/test-release-consistency.ps1`；同步本 change 的 `tasks.md`、`verification.md`、`ship.md` | `Bootstrap an already initialized repository again.`；`Set up each existing workspace from scratch.`；否定、说明、inline/fence 安全句 | Stage C CLI/28 项定向测试；template gate；release consistency 两项 C-M03A mutation |

- 仅拆分初始化 noun/verb/phrasal-verb pattern，并在 feature 分析副本中将相邻 `set up/sets up/setting up` 规范化；原始文件和 matched prose 不变。
- 句首或允许的 `Before ...` / `For each ...` 前置状语后的 init command 满足既有 `positive_requirement` feature。C-M03A 布尔表达式和 C-M03B 实现未修改。
- 两个原漏检均由正式 CLI exit 1，返回 `existing-project-reinitialize` 与四项 feature；安全反例 exit 0。状态继续为 `stage-c-implemented-awaiting-independent-check`。

### Stage C C-M03A 正负词形对称修复

| Finding | 剩余根因 | 修改文件 | 独立反例 | 正式门禁 |
| --- | --- | --- | --- | --- |
| C-M03A | 正向 `init_action` 与 `negated_init` 使用不同动作词形来源，导致 passive `bootstrapped` 可正向命中却不能被局部否定 | `scripts/validate-stage-c-skills.py`、`tests/test_stage_c_skills.py`、`scripts/test-release-consistency.ps1`；同步 `tasks.md`、`verification.md`、`ship.md` | `must not be bootstrapped again` 对照 `must be bootstrapped again`；bootstrap/set-up/initialize/reinitialize 七组正负对称 | Stage C CLI；29 项定向测试；release expected-pass + positive guard；完整 template/fresh-clone/release gate |

- 删除竞争的 `NEGATED_INIT_PATTERNS` 动作词表。`find_init_action_matches()` 从唯一 `INIT_ACTION_SPECS` 返回 span、family、原始 text；`init_action`、imperative 和局部否定共同消费这些 match。
- 已初始化主体中的描述性 `initialized` match 从 directive action 中剔除；否定只检查每个实际 directive action 前后局部上下文。C-M03A A+B+C+D 合同和 C-M03B 未修改。
- 原误报正式 CLI exit 0；对应正向句 exit 1 并返回原句、category 和 feature。状态继续为 `stage-c-implemented-awaiting-independent-check`。

### Stage D independent review：M-D01 / M-D02 修复映射

| Finding | 根因 | 修改文件 | 新增失败路径 | 验收命令 |
| --- | --- | --- | --- | --- |
| M-D01 | 四份有限写入合同措辞不一致，validator 将 changed-path evidence 与 validation evidence 作为 OR | 四个 Stage D `SKILL.md`、template projection、Stage D validator/tests、development draft incoming/descriptor、manifest、release mutation | 各 Skill 分别删除任一证据；只保留笼统 evidence；只在 fence/example 出现 | Stage D CLI；18 项定向测试；migration/template/release gates |
| M-D02 | 既有 regex 只覆盖六条冻结句式，未覆盖 checker 暴露的五个系统性权限/路由类别 | Stage D validator/tests、release mutation | finding 自动授权 repair；普通 backend 强制 security；普通 commit 自动 release；suitability 自动初始化；内部授权允许外部动作 | Stage D CLI；安全 expected-pass guard；release consistency |

- 四项有限写入现统一要求：独立明确授权、非空 explicit writable paths、changed-path evidence、validation evidence，以及不得扩张到其他 finding、路径、项目或外部动作。
- M-D02 只增加五个有限的数据驱动 category；未构建通用自然语言分析器，未修改 Stage A-C validator。
- 正式 Stage D failure mutation 共 14 项：原六项、checker 五条原句、M-D01 三项；另有一组五类安全否定 expected-pass guard。所有 mutation 逐字节恢复。
- Maker 状态继续为 `stage-d-implemented-awaiting-independent-check`；不得据此进入 Stage E。
