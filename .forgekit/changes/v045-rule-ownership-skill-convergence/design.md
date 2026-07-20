DesignStatus: design-revised-awaiting-blocker-recheck

# v0.45.0 规则所有权、Skill 职责与轻量化设计

## 1. 设计状态

本文件是设计和范围冻结材料，不是实施记录。凡涉及未来文件、脚本或行为的表述均表示目标合同；只有当前仓库证据可表述为已确认事实。

## 2. 当前状态与证据

### 2.1 仓库基线

| 事实 | 证据 | 结论 |
| --- | --- | --- |
| 当前版本为 0.44.1 | `VERSION`、plugin/marketplace/state/template manifest 的当前版本字段 | v0.45.0 尚未实施 |
| 现有 v0.44.1 发布修复已独立提交 | `9e6c407 fix(release): align v0.44.1 assets and validation` | 本 change 不重新处理补丁 |
| v0.44.0 已冻结 maker-checker 收敛合同 | `710153d (tag: v0.44.0) feat: converge Maker-Checker review workflow for v0.44.0` | v0.45.0 必须保留 blocker recheck 语义 |
| 初始工作树仅有 `D usage.html` | 本轮基线 `git status --short` | 属于本 change 范围外，保持原状 |
| 现有 change 使用 proposal/design/tasks/verification/review/ship | `.forgekit/changes/maker-checker-review-convergence/` 与 `project-template/changes/_template/` | 本设计沿用高风险工件集合 |
| `work-log` 只记录近期推进窗口 | `project-template/docs/work-log.md` | 不用全局 work-log 代替本 change 的设计、计划或历史源 |

### 2.2 规则载体

| 载体 | 当前事实 | 主要问题 |
| --- | --- | --- |
| 根 `AGENTS.md` | 55 行，ForgeKit 仓库维护入口 | 已较短，但仍混入若干只在维护任务触发的细则 |
| 模板 `AGENTS.md` | 181 行，约 25 KB | 16 项上下文顺序、长路由、文档写回、archive、checkpoint、maker-checker 等常驻加载 |
| 模板 `CLAUDE.md` | 166 行，约 23 KB | 与模板 AGENTS 大量共享语义，另含 Claude 平台路由 |
| 根 `skills/` | 九个通用 Skill | 有的职责宽、硬编码提问/文件数/输出格式 |
| 模板 `.agents/skills/` | 与根九个 Skill 的 `SKILL.md`、`agents/openai.yaml` 当前逐个哈希一致 | 人工双副本，权威源未声明；发布检查只覆盖 `code-review` |
| 模板 `.claude/skills/` | 六个 Claude 专属 Skill，code review 另有按需 references | 是平台适配而非通用投影，应保留差异 |
| governance / managed docs | 已有风险、变更、review、文档职责、路由等完整规范 | 多个文档对风险、确认、写回有重叠；入口又复制摘要和清单 |
| `prompts/` | 七个旧 prompt，含固定文件清单和输出章节 | 多处仍写 `docs/`，与当前 `.forgekit/docs/` 责任模型脱节 |
| scripts / validators | 初始化复制模板；升级支持 baseline guard；版本一致性和 code-review 漂移有检查 | 尚无全量共享 Skill 权威关系和行为测试 |

### 2.3 与新模型机制相关的外部事实

- Codex 官方建议 AGENTS 保持短、准确、实用；较大的任务特定说明应下沉到引用文档：<https://learn.chatgpt.com/docs/agent-configuration/agents-md>。
- Skills 使用逐层加载；触发主要依赖 frontmatter `description`，可以显式或隐式触发：<https://learn.chatgpt.com/docs/build-skills>。
- 同名 Skill 不会合并，多个来源可能同时出现在选择器中，因此插件与项目本地同名 Skill 的重复是真实兼容问题，而不是目录命名问题。
- `allow_implicit_invocation` 只控制自动触发；它不表达文件写入授权。
- Codex custom prompts 已标记为 deprecated，reusable workflow 推荐使用 Skills：<https://learn.chatgpt.com/docs/custom-prompts>。
- 官方提示词建议按需要提供目标、上下文、输出和边界，不要求固定完整格式：<https://learn.chatgpt.com/docs/prompting>。

### 2.4 主要重叠与冲突证据

1. 根 AGENTS 已要求“details belong in skills/docs/governance”和“不要在 HTML、prompts、skills、AGENTS 重复长规则”，但模板 AGENTS/CLAUDE 仍常驻复制 document routing、archive、checkpoint、worktree、maker-checker 和 risk artifact 细则。
2. `.forgekit/docs/document-responsibility.md` 明确把 AGENTS/CLAUDE 定义为“简短启动顺序、边界规则、任务路由”，并明确排除长清单；当前模板入口超过 20 KB，与该职责不一致。
3. `project-init` 同时包含入口判断、访谈、技术选型、路线图、document-backfill、large-change、文档填充和执行确认，覆盖 `project-bootstrap-fill`、`document-backfill`、`large-change-planning` 的职责。
4. `handover-review` 的描述包含 repair defects，流程又要求修 P0/P1；“接手审计”因此可能从只读自动进入修改。
5. `document-backfill` 默认一次一个源文件并直接写目标；它还允许 governance 作为目标，存在把项目业务事实写入规范模板的风险。
6. `large-change-planning` 用“超过 5 个文件或 2 个模块”作为触发门槛；这会漏掉单文件权限/迁移改动，也会把多文件机械投影误判为大变更。
7. `release-check` 默认读取近二十类材料，与“按发布类型和实际变更渐进加载”不符。
8. `security-review` 没有明确只读默认、证据等级、无法验证时的降级和人工复核边界。
9. `forgekit-first-principles` 强制恰好八个章节，格式要求压过了思考原则。
10. `prompts/初始化项目`、`初始化填充`、`版本发布` 复制固定文档清单；`需求分析`、`架构设计` 等默认写 `docs/`，而当前边界将业务 `docs/**` 视为默认只读证据，将 ForgeKit 当前态写回放在 `.forgekit/docs/`。
11. `project-template/README.md`、`workflow-router.md`、`document-responsibility.md`、usage playbook 和两个入口对路由/写回有多份解释，虽然多数方向一致，但维护时没有唯一规范位置。
12. 初始化按目录递归复制模板；升级已有 `replace_file_if_baseline_matches`、`REVIEW-NEEDED` 和 `manual-merge`。这证明项目本地副本是分发产物，并且现有兼容机制可复用，无需静默覆盖。

## 3. 问题定义、目标和非目标

问题不是单纯“文档太长”，而是规范性所有权和运行时职责没有收敛。设计目标是在 Skill 未触发时仍保住安全边界，在 Skill 触发时只加载当前任务所需流程，并把可机器判断的合同交给 validator。完整目标和非目标见 `proposal.md`，本文件不重复扩写。

### 3.1 已冻结决策

- `DECISION-01`: 根 `skills/` 是九个通用 Skill 的唯一共享语义维护源；`project-template/.agents/skills/` 是同构确定性投影；`.claude/skills/` 是排除在机械投影外的平台适配层。新项目保留本地 Skills，已有项目仅在命中已知来源 baseline 时自动升级，custom/unknown-baseline 进入 `REVIEW-NEEDED/manual-merge`。sync check 可用于 CI/release，apply 仅由维护者显式运行。
- `DECISION-02`: 阶段 A 不增加来源 display name、不修改公共 Skill `name`；selector、显式/隐式优先级继续 `NEEDS_TEST`。阶段 E 优先研究插件入口型能力与项目本地操作型能力的职责拆分；双命名空间/双来源显示名仅为实测后的备选。
- `DECISION-03`: 阶段 A 采用仓库原生、跨平台、数据驱动 Python runner 和 Codex/Claude adapters。确定性检查是自动 blocker；代表性模型行为证据由独立 checker 复核，单次非确定结果不是无条件自动 CI blocker。

这三个决定已经关闭，不再返回为未决。当前状态为 `design-revised-awaiting-blocker-recheck`，尚未授权或实施阶段 A。

## 4. 四层规则所有权模型

### 4.1 第一层：常驻入口

载体为 AGENTS.md / CLAUDE.md。只保留不加载就可能导致越界、错误授权、事实污染或不可恢复操作的内容：

- ProjectRoot、ForgeKitRoot、managed docs root 与写入边界的最小解释；具体路径值引用 machine-readable boundary 配置。
- 证据优先、禁止编造、未知值的标记方式。
- 审计/评估默认只读；明确修复请求授权对应范围内本地可回滚写入；已经清晰给出的局部授权不得同义重复确认。
- 外部、不可逆、破坏性和越界动作必须明确授权。
- 最小风险路由、项目本地 Skill 优先提示和最小验证入口。
- 升级改变入口/Skill 后新开会话的最短提醒。

### 4.2 第二层：Skills

每个 Skill 只承载一个清晰任务的触发、输入、条件流程、写入边界、输出和验收：

- 通过短 description 进行语义路由；详细“何时使用”不在正文重复。
- 默认行为和用户明确修改后的行为分开写。
- 按影响条件加载 governance/references，不复制全局授权协议。
- 不用固定问题数、文件数或章节数代替判断；仅在脆弱格式需要时保留精确结构。

### 4.3 第三层：governance / references

承载完整规范、背景、模板、例外、清单和平台适配说明：

- 风险影响模型、maker-checker、文档责任、archive/checkpoint/worktree 等详细协议；code-review convergence 的唯一规范例外地保留在 `skills/code-review/SKILL.md`，本层不重复定义。
- Skill 通过路径引用所需章节；入口只保留安全摘要。
- current project facts 不写入 governance 模板；业务 `docs/**` 默认是证据，除非用户明确授权更新。

### 4.4 第四层：确定性配置、scripts / validators

承载机器可验证或可安全生成的内容：

- 当前版本、schema、模板创建版本各自的一致性和语义边界。
- manifest、required paths、frontmatter、ASCII、链接和投影清单。
- 共享 Skill 从权威源到模板副本的显式同步和 `--check`。
- 初始化、baseline-guarded upgrade、`REVIEW-NEEDED`、mutation 和 fixture 测试。
- 具体项目边界值仍由 `.forgekit/project-boundary.yml` 表达；入口拥有“必须遵守边界”的规范性规则，validator 检查配置结构。

### 4.5 原子化规则所有权矩阵

`normative_owner` 是唯一规范来源；`application_sites` 只能引用或应用，不能重新定义；`deterministic_enforcement` 只检查可确定部分。阶段 A 将创建 `project-template/governance/agent-entry-contract.md`，作为 AGENTS 与 CLAUDE 共享常驻规则的唯一规范来源；本轮只冻结路径，不创建文件。`project-template/AGENTS.md` 与 `project-template/CLAUDE.md` 只是 application sites，并在阶段 B 迁移为该合同的平台入口投影。

owner 格式合同：每个 `normative_owner` 必须是一个实际存在、或已冻结在阶段 A 创建的仓库相对文件路径，可选带一个 heading anchor。owner 不得是目录、角色名或文件集合，不得使用通配符、参数化占位符、“对应文件”“共享合同”“各 Skill”等自然语言，也不得用 `/` 表达自然语言二选一。`application_sites` 和 `deterministic_enforcement` 可以列多个位置，但不取得规范所有权。

| rule_id | rule | normative_owner | application_sites | deterministic_enforcement | migration_action |
| --- | --- | --- | --- | --- | --- |
| ENTRY-BOUNDARY | 必须服从 ProjectRoot/ForgeKitRoot 与写入边界 | `project-template/governance/agent-entry-contract.md#project-and-write-boundary` | `project-template/AGENTS.md`、`project-template/CLAUDE.md`、所有 Skills | boundary config 结构与解析检查 | 阶段 A 创建合同；阶段 B 入口只应用 |
| BOUNDARY-VALUES | 项目边界具体路径和值 | `project-template/.forgekit/project-boundary.yml` | `project-template/AGENTS.md`、`project-template/CLAUDE.md`、统一 CLI | schema、路径存在和根范围检查 | 保留 machine-readable 配置 |
| ENTRY-EVIDENCE | 证据优先、未知不得编造 | `project-template/governance/agent-entry-contract.md#evidence-and-no-fabrication` | `project-template/AGENTS.md`、`project-template/CLAUDE.md`、Skills、事实文档 | 只检查最小 marker，不校验自然语言全文 | 阶段 A 创建合同；删除 Skill 完整重复协议 |
| ENTRY-AUDIT | audit/evaluate/plan 默认只读 | `project-template/governance/agent-entry-contract.md#audit-default` | `project-template/AGENTS.md`、`project-template/CLAUDE.md`、审计类 Skills | 行为 runner 的 write trace | 阶段 A 创建合同；Skill 只声明应用模式 |
| ENTRY-AUTH | 明确修复授权允许范围内本地可回滚写入且不重复确认 | `project-template/governance/agent-entry-contract.md#bounded-local-authorization` | `project-template/AGENTS.md`、`project-template/CLAUDE.md`、写入型 Skills | bounded-write fixture | 阶段 A 创建合同；删除否定既有局部授权的规则 |
| ENTRY-EXTERNAL | 外部、不可逆、破坏性和越界操作需明确授权 | `project-template/governance/agent-entry-contract.md#external-and-irreversible-actions` | `project-template/AGENTS.md`、`project-template/CLAUDE.md`、release/maintenance/init Skills | forbidden-action trace | 阶段 A 创建合同；不由 implicit policy 代替 |
| RISK-IMPACT | 低中高风险按客观影响、回滚、验证和不确定性判断 | `project-template/governance/ai-engineering-loop.md` | planning/review/release Skills | 固定反例 fixture 只检查可观察分类 | 用影响模型替换数量门槛 |
| MAKER-CHECKER | maker、独立 checker、gate 与人工升级协议 | `project-template/docs/maker-checker-protocol.md` | request-review、code-review、change `review.md` | reviewer identity 与结构检查 | 中高风险或明确 gate 才触发 |
| REVIEW-CONVERGENCE | initial、blocker-recheck、blocker 收敛和阶段授权 | `skills/code-review/SKILL.md` | `.agents` 投影、Claude reviewer adapter、AGENTS/CLAUDE 路由 | 投影一致性、必需结构和 paired fixture | 保留 v0.44 收敛语义 |
| ARCHIVE-PROTOCOL | archive 判定、capsule、索引和非删除语义 | `project-template/docs/archive-capsule.md` | maintenance Skill、入口最小路由 | archive script plan/apply 不变量 | 从入口移除完整 capsule 清单 |
| CHECKPOINT-PROTOCOL | checkpoint 触发、内容和最小写回 | `project-template/.forgekit/docs/work-session-checkpoint.md` | 入口最小路由、maintenance/context Skills | checkpoint 结构检查 | Skill 不复制完整协议 |
| WORKTREE-PROTOCOL | worktree 隔离、验证和清理 | `project-template/docs/worktree-playbook.md` | implementation/maintenance 路由 | worktree helper 的路径检查 | 从入口移除操作细节 |
| WRITEBACK-BASE | 只做完成当前授权任务所需的最小持久化写回 | `project-template/governance/agent-entry-contract.md#minimum-evidence-based-writeback` | `project-template/AGENTS.md`、`project-template/CLAUDE.md`、所有写入型 Skills | changed-path allowlist + behavior fixture | 阶段 A 创建合同；入口只应用 |
| WRITEBACK-OWNERSHIP | 文档职责、事实归属和可写目标 | `project-template/.forgekit/docs/document-responsibility.md` | workflow-router、所有写入型 Skills | 路径/required-doc 检查 | workflow-router 不重新定义职责 |
| BACKFILL-FLOW | 历史来源到 managed docs 的具体回填流程 | `skills/document-backfill/SKILL.md` | handover/project-init handoff | source trace 和 allowed-path fixture | 改为授权后小批次 |
| INIT-ORCHESTRATION | 初始化状态判断后的对话与任务编排 | `skills/project-init/SKILL.md` | Claude project-workflow adapter | behavior fixture | 收敛为轻量编排器 |
| INIT-STATE | init/current/upgrade/adoption 的确定性状态识别 | `scripts/forgekit-project.py` | project-init、maintenance Skill | CLI smoke fixture | 不在 Skill 复制算法 |
| LARGE-PLAN | 中高影响任务的计划流程 | `skills/large-change-planning/SKILL.md` | project-init handoff、change artifacts | acceptance/phase fixture | 删除文件数门槛和第二计划源 |
| RELEASE-FLOW | 发布准备的渐进式检查流程 | `skills/release-check/SKILL.md` | AGENTS/CLAUDE 路由 | release validator 与 release-type fixture | 按 release type/diff 加载 |
| VERSION-GATE | 版本推进与 review/refactor gate 规范 | `project-template/governance/version-governance.md` | release-check | 版本一致性 checker | 不在 release Skill 复制完整规则 |
| SKILL-ROUTING | 通用 Skill 发现、显式/隐式路由与冲突处理原则 | `project-template/governance/agent-entry-contract.md#skill-routing` | `project-template/AGENTS.md`、`project-template/CLAUDE.md`、下列九个根 Skill frontmatter | frontmatter 与行为 runner | 阶段 A 创建通用路由合同；具体触发仍由各 Skill 拥有 |
| ROUTE-PROJECT-INIT | project-init 的具体触发与不触发语义 | `skills/project-init/SKILL.md` | `.agents` 投影、入口路由 | frontmatter 与行为 runner | 阶段 C 收敛具体触发 |
| ROUTE-PROJECT-BOOTSTRAP-FILL | project-bootstrap-fill 的具体触发与不触发语义 | `skills/project-bootstrap-fill/SKILL.md` | `.agents` 投影、入口路由 | frontmatter 与行为 runner | 阶段 C 收敛具体触发 |
| ROUTE-HANDOVER-REVIEW | handover-review 的具体触发与不触发语义 | `skills/handover-review/SKILL.md` | `.agents` 投影、入口路由 | frontmatter 与行为 runner | 阶段 C 收敛具体触发 |
| ROUTE-DOCUMENT-BACKFILL | document-backfill 的具体触发与不触发语义 | `skills/document-backfill/SKILL.md` | `.agents` 投影、入口路由 | frontmatter 与行为 runner | 阶段 C 收敛具体触发 |
| ROUTE-LARGE-CHANGE-PLANNING | large-change-planning 的具体触发与不触发语义 | `skills/large-change-planning/SKILL.md` | `.agents` 投影、入口路由 | frontmatter 与行为 runner | 阶段 C 收敛具体触发 |
| ROUTE-RELEASE-CHECK | release-check 的具体触发与不触发语义 | `skills/release-check/SKILL.md` | `.agents` 投影、入口路由 | frontmatter 与行为 runner | 阶段 D 收敛具体触发 |
| ROUTE-CODE-REVIEW | code-review 的具体触发与不触发语义 | `skills/code-review/SKILL.md` | `.agents` 投影、入口路由 | frontmatter 与行为 runner | 阶段 D 保留 convergence 并收敛触发 |
| ROUTE-PROJECT-SUITABILITY | project-suitability 的具体触发与不触发语义 | `skills/project-suitability/SKILL.md` | `.agents` 投影、入口路由 | frontmatter 与行为 runner | 阶段 D 收敛具体触发 |
| ROUTE-SECURITY-REVIEW | security-review 的具体触发与不触发语义 | `skills/security-review/SKILL.md` | `.agents` 投影、入口路由 | frontmatter 与行为 runner | 阶段 D 收敛具体触发 |
| SKILL-PROJECTION | 九个共享 Skill 的源、目标和受管文件 | `config/skill-projections.json` | sync check/apply、release validator | schema/path/hash 检查 | 阶段 A 创建 schema v1 manifest |
| CLAUDE-ENTRY-ADAPTER | Claude 常驻入口专属调用语法、agent wiring 与 permission mode | `project-template/CLAUDE.md` | Claude Code 启动与路由；共享安全规则引用 agent-entry-contract | Claude adapter behavior fixture | 阶段 B 仅保留平台适配语义 |
| CLAUDE-MAINTENANCE-ADAPTER | Claude maintenance 的具体路由与平台行为 | `project-template/.claude/skills/forgekit-maintenance/SKILL.md` | `project-template/CLAUDE.md` | Claude adapter behavior fixture | 排除通用机械投影 |
| CLAUDE-PROJECT-WORKFLOW-ADAPTER | Claude project workflow 的具体路由与平台行为 | `project-template/.claude/skills/forgekit-project-workflow/SKILL.md` | `project-template/CLAUDE.md` | Claude adapter behavior fixture | 排除通用机械投影 |
| CLAUDE-CODE-REVIEW-ADAPTER | Claude 独立 code review 的平台行为 | `project-template/.claude/skills/forgekit-code-review/SKILL.md` | `project-template/CLAUDE.md`、code-review convergence | Claude adapter paired-review fixture | 共享 convergence 仍引用根 code-review owner |
| CLAUDE-REQUEST-CODE-REVIEW-ADAPTER | Claude 请求独立 review 的平台行为 | `project-template/.claude/skills/forgekit-request-code-review/SKILL.md` | `project-template/CLAUDE.md`、maker-checker | Claude reviewer-identity fixture | 不取得 maker-checker 规范所有权 |
| CLAUDE-ADVERSARIAL-REVIEW-ADAPTER | Claude adversarial review 的平台行为 | `project-template/.claude/skills/forgekit-adversarial-review/SKILL.md` | `project-template/CLAUDE.md`、高风险 review | Claude adapter behavior fixture | 排除通用机械投影 |
| CLAUDE-FIRST-PRINCIPLES-ADAPTER | Claude first-principles 的平台行为 | `project-template/.claude/skills/forgekit-first-principles/SKILL.md` | `project-template/CLAUDE.md`、高风险推理路由 | Claude adapter behavior fixture | 阶段 D 收敛固定输出结构 |
| UPGRADE-CUSTOM | stock/custom/missing/unknown-baseline 与 manual merge | `project-template/docs/project-maintenance.md` | maintenance Skill、migration descriptors | baseline checksum 与 upgrade fixtures | 复用现有 REVIEW-NEEDED 框架 |
| VERSION-METADATA | 当前 ForgeKit 发布版本的唯一值 | `VERSION` | plugin/marketplace/state/template metadata | release consistency checker | 保持 schema、创建和历史版本独立 |
| SOURCE-TASK | source-first intake 与任务派生 | `project-template/docs/task-intake.md` | workflow-router、task-board、相关 Skills | source integrity checker | 从常驻入口移除长链路 |

宽泛规则已经按语义、应用和确定性执行拆开。任何 application site 若需要新增规范，必须先修改对应 `normative_owner`，不得在引用处形成第二权威。九个通用 Skill 与六个 Claude Skill 均使用实际完整文件路径逐条拥有其具体触发或平台行为；没有参数化 owner。

## 5. Skill 权威源与分发策略

### 5.1 使用场景

- 根 `skills/`：随 ForgeKit plugin 安装，服务于尚未初始化的目录、ForgeKit 仓库本身和跨项目可复用任务。
- `project-template/.agents/skills/`：随新项目复制，提供项目自包含、版本锁定、离线可读的 repo-level workflow。
- `project-template/.claude/skills/`：Claude Code 的薄入口、独立 reviewer 和平台能力适配；它们与通用 Skill 共享行为合同，但不要求逐字一致。

新生成项目应继续包含本地 Skills。否则项目会依赖机器是否已安装 plugin，破坏可移植性、团队共享和现有 README/升级合同。

### 5.2 方案比较

| 方案 | 用户体验 | 兼容性 | 实现复杂度 | 漂移风险 | 升级风险 | 同名冲突 | v0.45 适配性 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A. 保留人工双副本，发布时全量哈希校验 | 编辑需改两处；失败晚 | 最高，目录不变 | 低 | 中，直到校验才发现 | 低 | 不解决 | 可做，但未解决所有权 |
| B. 根 `skills/` 为权威源，显式 sync `--check/--apply` 投影到模板 | 维护者改单处；用户目录不变 | 高 | 中 | 低 | 中，可复用 baseline guard | 语义冲突降低，UI 重复仍需测试 | 推荐，可分阶段完成 |
| C. 新建中立 `skill-sources/`，同时生成 plugin 与项目副本 | 所有产物清晰 | 中，改变作者路径 | 高 | 最低 | 高，迁移面广 | 仍需解决 UI | 不适合一次完成 |
| D. 新项目不再分发本地 Skills，只依赖 plugin | 安装过 plugin 的用户简单 | 低，破坏自包含与单平台/离线场景 | 中 | 低 | 高 | 消除重复 | 不接受 |

### 5.3 推荐方案

采用方案 B：

1. 根 `skills/` 是九个通用 Skill 的唯一共享语义维护源。
2. 模板 `.agents/skills/` 是同构确定性投影；维护者显式运行 sync apply，CI/release 只运行 sync check，release 不得隐式 apply。
3. 唯一投影配置固定为 `config/skill-projections.json`，不用“所有同名目录都必须一致”的隐式规则。
4. `.claude/skills/` 不在通用投影清单中；它保留 Claude 命名、agent wiring、permission mode 和 references。
5. Claude 适配通过共享行为 fixture 和关键合同 marker 校验，而不是哈希覆盖。
6. 发布前先生成或检查 ForgeKit 仓库内的 template projection；初始化脚本只复制已发布投影，不在真实用户项目中运行 sync apply。
7. 升级现有项目时，只有命中项目记录来源版本对应 baseline 的 stock 文件才自动替换；custom/unknown-baseline 生成 `REVIEW-NEEDED` 与 manual-merge packet。

### 5.4 同名 Skill 并存

Codex 不会合并同名 Skill，因此插件和项目本地副本可能都出现在选择器中。v0.45.0 的最小处理是：

- 让两份通用 Skill 来自同一语义权威源，使无论哪份被选中都遵守相同行为合同。
- 项目入口短规则明确项目任务优先使用项目本地 Skill；plugin 负责项目外/bootstrap 场景。
- 阶段 A 不增加 Plugin/Project 等来源 display name，也不修改公共 Skill `name`。
- 不假定客户端存在未记录的优先级。
- `NEEDS_TEST`: 通过行为 run record 记录实际加载来源路径、Skill 名、selector 观察、隐式触发和显式 `$skill` 结果；阶段 A 不把 UI 标签作为验收条件。

阶段 E 的长期首选研究方向是：插件保留初始化、适用性判断、升级等跨项目入口型能力，依赖项目上下文的操作型流程保留在项目本地。只有实测仍不可接受时，才把双命名空间或双来源显示名作为备选，不在阶段 A 实施。

### 5.5 `config/skill-projections.json` schema v1

阶段 A 只创建一个投影配置：`config/skill-projections.json`。最小逻辑结构固定为：

```json
{
  "schema_version": 1,
  "source_root": "skills",
  "target_root": "project-template/.agents/skills",
  "entries": [
    {
      "skill": "code-review",
      "managed_files": [
        "SKILL.md",
        "agents/openai.yaml"
      ]
    }
  ]
}
```

实际 manifest 必须为九个通用 Skill 各建立一个 entry：`project-init`、`project-bootstrap-fill`、`handover-review`、`document-backfill`、`large-change-planning`、`release-check`、`code-review`、`project-suitability`、`security-review`。

schema v1 合同：

- `skill` 是单层相对目录名，不得为空、包含分隔符、`.` 或 `..`。
- `managed_files` 是 Skill 目录内的相对 POSIX 路径。
- 只管理逐项显式声明的文件，不支持隐式递归或通配符。
- 当前每个 entry 精确管理 `SKILL.md` 与 `agents/openai.yaml`。
- 未来 `references/`、`scripts/`、`assets/` 只有把具体文件路径加入对应 `managed_files` 后才 opt-in；目录存在本身不产生管理关系。
- `.claude/skills/` 永远不属于该 manifest 的 source、target 或 managed_files。

### 5.6 sync check、apply 与 safe-target

sync check：

- 按 manifest 验证 source/target 文件存在并逐字节比较。
- 对每项报告 Skill、source、target、source SHA-256 和 target SHA-256。
- 任一文件缺失、manifest schema/entry/path 非法或内容漂移均返回非零。
- 不检查 `.claude/skills/` 和 manifest 未声明文件，不修改任何文件。

sync apply：

- 必须显式选择 apply；默认先输出计划。
- 只把 manifest 声明的 source 文件复制到对应 target。
- 不删除 target 中未受管文件，不扫描或复制未声明目录，不修改 `.claude/skills/`。
- 完成后自动执行 check；check 失败则整体返回失败。
- 只维护 ForgeKit 仓库内 `project-template/.agents/skills/` 投影，不承担用户项目升级。

safe-target 在任何复制前验证：

- `source_root`、`target_root` 和相对路径不得为绝对路径或包含 `..` 逃逸。
- source 解析后必须位于仓库 `skills/`；target 解析后必须位于 `project-template/.agents/skills/`。
- 拒绝 symlink、junction 或 reparse point 穿越受管根。
- apply 写集合必须等于 manifest 计算出的目标文件集合；不允许删除，也不允许写入 template 之外的用户工作区。
- 任一非法路径使整个 apply 在第一次复制前失败。

### 5.7 现有项目 baseline 身份与 manual merge

不建立平行 baseline 系统。复用以下实际机制：

- 项目来源版本：目标项目 `.forgekit/state.json` 的 `forgekit_version`。
- migration 选择：`migrations/<target-version>/migration.json` 及项目模板镜像 `project-template/migrations/<target-version>/migration.json` 的 `from`、`to`、`actions`。
- 替换动作：`type: replace_file_if_baseline_matches`，使用 `source`、`baseline`、`target` 字段；来源/基线文件位于对应 migration package 的 `files/`、`baseline/`。
- 当前分类实现位于 `scripts/forgekit-upgrade.py` 的 `action_status`；review 输出由同一脚本的 `REVIEW_REPORT_MD`、`REVIEW_REPORT_JSON`、`REVIEW_EXPORT_ROOT`、`write_review_reports` 和 `export_manual_merge` 维护。现有固定出口分别是 `.forgekit/reports/upgrade-review-needed.md`、`.forgekit/reports/upgrade-review-needed.json` 和 `.forgekit/reports/review-needed/`。
- 现有 review 字段包括 `source_migration`、`migration_to`、`expected_baseline_checksum`、`actual_checksum`、`incoming_template_checksum`、`target_path`、`status`、`export_path`、`exported_files` 和报告级 `target_version`。v0.45.0 只在这些字段和既有出口上兼容扩展，不建立平行 review、merge 或 rollback 系统。

v0.45.0 baseline 身份至少由 `source ForgeKit version + managed relative path + expected source SHA-256` 组成。只能依据项目记录的来源版本和 migration `from -> to` 链选择 baseline；不得用“最接近”、最新版本或内容猜测来源版本。`.forgekit/template-lock.json[installed_version]` 可做一致性诊断，但不替代 `.forgekit/state.json[forgekit_version]` 的升级来源身份。

分类冻结为：

- `stock`: local SHA-256 与选定来源 baseline 完全一致；可按 migration 进入 safe replace。
- `custom`: 文件存在但不等于来源 baseline；必须 `REVIEW-NEEDED`。
- `missing`: 文件不存在；沿用 migration 当前缺失文件语义处理。
- `unknown-baseline`: 来源版本或对应 baseline 无法唯一确定；不得自动覆盖，必须 `REVIEW-NEEDED`。

manual-merge metadata 必须把现有字段扩展/映射为：managed relative path=`target_path`；source ForgeKit version=选定 migration 的 `from`；source baseline SHA-256=`expected_baseline_checksum`；local SHA-256=`actual_checksum`；target ForgeKit version=`migration_to`/报告 `target_version`；incoming SHA-256=`incoming_template_checksum`；classification；packet artifacts；rollback 原始字节路径与 SHA-256；resolution status；用户下一步动作。固定位置、packet ID、目录结构和分类行为见 5.8。

### 5.8 现有 review/export 出口与 rollback packet

阶段 A 必须保留并兼容扩展现有三个出口，不得选择其他顶层 review、merge、backup 或 rollback root：

- `.forgekit/reports/upgrade-review-needed.md`：面向用户的人工审查汇总；每个 packet 列出 managed path、classification、source ForgeKit version、target ForgeKit version 和用户动作。
- `.forgekit/reports/upgrade-review-needed.json`：机器可读汇总；每项包含 packet ID、managed path、classification、baseline/local/incoming/rollback checksum 和 artifact 路径。所有 artifact 路径必须相对于 `.forgekit/reports/`，不得存储机器绝对路径。
- `.forgekit/reports/review-needed/`：唯一 packet root。每个需要人工处理或写前 rollback 留证的 managed file 使用 `.forgekit/reports/review-needed/<packet-id>/`。

这是对 `scripts/forgekit-upgrade.py` 当前 `REVIEW_REPORT_MD`、`REVIEW_REPORT_JSON`、`REVIEW_EXPORT_ROOT` 和 export 逻辑的兼容结构扩展，不是平行 baseline、manual-merge 或 rollback 系统。不得创建 `.forgekit/rollback/`、`.forgekit/backups/` 或其他顶层存储。

packet ID 固定为 `<target-version>--<managed-path-sha256-prefix>`。managed path 的规范形式是已通过 safe-target 验证的相对 POSIX 路径：使用 `/` 分隔，不带开头 `/` 或 `./`，不含空、`.` 或 `..` segment，大小写保持不变；对该字符串的 UTF-8 字节计算 SHA-256，取小写十六进制前 16 字符。target version 必须通过安全文件名字符校验，完整 packet ID 仅允许 `[A-Za-z0-9._-]`。相同 target version 与规范 managed path 必须稳定生成相同 ID，绝对路径和未经处理的 path segment 不得进入 ID。

每个 packet 固定为：

```text
.forgekit/reports/review-needed/<packet-id>/
├── packet.json
├── local/
│   └── <managed-relative-path>
├── incoming/
│   └── <managed-relative-path>
├── rollback/
│   └── <managed-relative-path>
└── diff.patch
```

- `packet.json` 保存 packet ID、managed path、source/target version、classification、baseline/local/incoming/rollback SHA-256、文件原先是否存在、artifact 相对路径、resolution status 和用户动作。
- `local/` 保存升级前用户本地版本的审查副本；`incoming/` 保存目标 ForgeKit 候选字节；`diff.patch` 是 local 与 incoming 的可读差异。
- `rollback/` 保存升级写入前的原始本地字节，不得格式化、重编码或重新生成；rollback SHA-256 必须对应该原始字节。rollback artifact 必须位于同一 packet，且其路径进入 `packet.json` 和 JSON 汇总。
- 文件原本不存在时，`local/` 与 `rollback/` 不伪造空文件；`packet.json` 记录 `local_existed: false`，rollback action 记录为删除本次升级新建的 managed file。
- packet artifact 路径均相对于 `.forgekit/reports/`。Markdown 汇总引用 packet 目录，JSON 汇总引用 `packet.json`、local、incoming、rollback 和 diff；两份汇总不得引用另一套根。

classification 与 packet 行为冻结为：

- `stock`：可按 migration 自动更新。实际覆盖前必须创建并验证包含原始字节及 SHA-256 的同目录 rollback packet；该 packet 可标为自动升级留证而非未解决的 `REVIEW-NEEDED`，无需用户动作。packet 未完成或 rollback 身份不一致时不得覆盖。
- `custom`：必须生成 packet 和 `REVIEW-NEEDED` 汇总项，只保存 local/incoming/diff/rollback 审查材料，不覆盖本地文件。
- `unknown-baseline`：必须生成 packet 和 `REVIEW-NEEDED` 汇总项，不覆盖本地文件。
- `missing`：遵循 migration 的缺失文件策略；需要用户判断时生成 packet。若原文件不存在，不伪造 local/rollback，rollback action 是删除升级中新建文件。

manual merge 完成前，custom、unknown-baseline 或需要判断的 missing 文件不得标为已自动升级。阶段 A 只扩展现有 review/export 合同并保留单命令 check/plan/apply 体验；不得把 packet 输出分流到真实用户工作区之外或新顶层目录。

## 6. AGENTS.md / CLAUDE.md 瘦身设计

### 6.1 建议保留

1. 项目身份、ProjectRoot/ForgeKitRoot 和 boundary 配置入口。
2. 证据优先、未知不得编造。
3. audit/evaluate/plan 默认只读；fix/implement/update 的明确局部授权允许范围内本地可回滚写入且不重复确认。
4. 外部、不可逆、破坏性和越界动作明确授权。
5. 最小启动顺序：入口 -> boundary/codebase map -> 命中的本地 Skill -> 必要 reference -> 验证命令。
6. 低风险保持轻量；中高风险读取 active change 和 maker-checker。
7. 关键结论在换会话/compact/handoff 前做最小 checkpoint。
8. 升级入口或 Skills 后新开会话。

### 6.2 建议下沉

| 当前内容 | 目标位置 | 原因 |
| --- | --- | --- |
| 16 项完整上下文加载顺序 | codebase-map / agent-harness | 属于搜索策略，不是每任务安全合同 |
| 长用户意图路由表 | workflow-router + Skill descriptions | 可按需加载，frontmatter 是触发入口 |
| 完整 managed docs 读写矩阵 | document-responsibility | 已有专门权威文档 |
| source/task/work-log 长链路 | task-intake + document-responsibility | 仅相关工作触发 |
| archive/current-doc integrity/scoped docs 细则 | maintenance Skill + 对应 references | 特定维护任务 |
| worktree、native agent、loop 细则 | 对应 references/Skills | 平台或任务特定 |
| maker-checker packet 与复审状态机 | maker-checker protocol + review Skills | 中高风险才加载 |
| 风险文件清单和 change artifact 模板 | ai-engineering-loop + validators | 入口只保留何时路由 |
| 固定输出章节和提问数量 | Skill 内条件化或删除 | 不是常驻保护 |

### 6.3 防止保护能力丢失

- 安全不是依赖 Skill 触发：只读默认、局部授权、外部/不可逆保护、事实边界始终保留在入口。
- validator 检查入口必须含这些语义 marker，但不强制逐字模板。
- 行为测试包含“Skill 未触发”fixture，验证基础边界仍成立。
- 项目边界具体值由机器配置提供，避免入口缩短后丢失实际路径。

### 6.4 共享与平台差异

AGENTS 与 CLAUDE 必须共享：边界、证据、授权、不可逆/外部保护、风险路由、项目本地事实源和最小验证语义。

允许平台适配：Skill 搜索路径、显式调用语法、原生 reviewer/agent wiring、permission mode、客户端特有配置。平台差异只能改变“如何调用”，不能改变“何时可写、何时须停、何为证据”。

## 7. 核心 Skills 目标职责

下列“写入权限”均不包含 commit/push/tag/release、外部系统或破坏性操作；这些动作始终受第一层保护。

### 7.1 project-init

- 当前职责/触发：新建、接手和变更分类；扫描、访谈、选型、路线图、文档填充、backfill、大变更计划及编码确认。
- 当前写入：可更新大批 `.codex/` 和 managed docs；不默认改业务代码。
- 重叠：project-bootstrap-fill、handover-review、document-backfill、large-change-planning、project-suitability。
- 重复/硬编码：重复全局授权和文档责任；固定 3-5 问、2-4 方案、v0.1/v0.2/v0.3/v1.0、完整文件清单。
- 保留：识别 init/current/upgrade/adoption、确认最小事实、选择下一个专门工作流、给出 readiness。
- 删除/下沉：访谈模板和文档映射下沉 bootstrap governance；风险和升级细则引用治理/脚本。
- 条件分支：信息足够直接给 plan；不足时只问会改变方案的少量问题；已有项目路由 handover；已确认问答路由 bootstrap-fill。
- 拆分/合并：不再拆微型 Skill；保留轻量编排器，不合并相邻执行 Skill。
- 隐式调用：允许语义匹配；隐式触发只读发现。只有用户明确要求初始化/更新时才可在项目根内执行可回滚写入。
- 审计默认：只输出状态、缺口和建议路由。
- 验收：简单项目不被强制完整访谈；明确 init 请求不重复确认本地写入；越界/外部动作仍停下。

### 7.2 project-bootstrap-fill

- 当前职责/触发：把初始化问答转换为首版规则和文档，提出下一轮问题。
- 当前写入：多份 `.codex/` 与 managed docs。
- 重叠：project-init 的文档填充、document-backfill。
- 重复/硬编码：固定 18 类目标文档、3-5 个问题和固定输出。
- 保留：仅从已确认输入提取事实、保留未知、写入职责对应文档。
- 删除/下沉：完整映射下沉 `governance/project-bootstrap-fill.md`；不重复授权协议。
- 条件分支：按项目模式、已确认事实和受影响职责选择最小目标集合。
- 拆分/合并：不拆分；由 project-init 显式委派。
- 隐式调用：建议关闭。具体原因是它与 project-init/document-backfill 的语言高度重叠且会改变多份项目权威事实；应由明确用户请求或编排器 handoff 选择，而不是模糊匹配。
- 写入边界：明确要求“填充/更新项目文档”后，可写 project boundary 内的 `.codex/` 与 `.forgekit/docs/`；不写业务代码或 governance 模板。
- 审计默认：只生成映射预览和缺口。
- 验收：每条写入可追溯到用户输入；未确认项保持 OPEN；只改职责命中的小集合。

### 7.3 handover-review

- 当前职责/触发：接手审计、缺陷发现/修复、兼容边界、文档回填和路线图。
- 当前写入：handover、defect、risk、roadmap 等多类文档；流程含“Fix P0/P1”。
- 重叠：project-suitability、document-backfill、security-review、code-review。
- 重复/硬编码：近二十类材料、one-file backfill、默认修 P0/P1。
- 保留：只读建立系统边界、可运行性、测试能力、风险、事实置信度和接手建议。
- 删除/下沉：自动修复和完整 backfill；缺陷修复转交实现请求，文档迁移转交 document-backfill。
- 条件分支：按证据可用性和风险加载 security/ownership/deployment references。
- 拆分/合并：不拆；收敛为 handover audit，输出可路由的后续动作。
- 隐式调用：允许在“接手/交接/审计既有项目”语义下触发，始终默认只读。
- 写入边界：只有用户明确要求记录审计结果时，写当前 change 或 handover-audit；明确要求修复后仅在指定代码/文档范围内实施，不能把 audit findings 当授权。
- 验收：审计请求零写入；修复请求不重复确认；每个结论有路径/命令证据和置信度。

### 7.4 document-backfill

- 当前职责/触发：从旧文档迁移事实到 managed docs，当前固定一次一个源文件。
- 当前写入：可写 `.codex/`、`.forgekit/docs/`、governance、CHANGELOG。
- 重叠：project-init、bootstrap-fill、handover-review。
- 重复/硬编码：固定单文件批次；重复事实分类和全局写入边界。
- 保留：来源追溯、事实/假设/历史/冲突分类、职责映射和最小写回。
- 删除/下沉：governance 作为业务事实目标；固定 one-file 限制。
- 条件分支：默认选择一个可审查的小批次，批次大小由同一事实域、来源一致性和回滚能力决定；冲突或跨域时缩小。
- 拆分/合并：不拆；不与 bootstrap-fill 合并，因为一个处理历史来源，一个处理初始化问答。
- 隐式调用：建议关闭。原因是“整理/补文档”容易与 handover、maintenance、checkpoint 冲突，并且该 Skill 会重新分配事实所有权；需要用户明确 backfill 意图或上游编排器 handoff。
- 写入边界：先只读给 source set、目标职责和计划；用户已明确授权 backfill 后可写 `.codex/`/`.forgekit/docs/` 的职责目标，不写 governance 模板。
- 验收：默认小批次、每项带来源、冲突不被覆盖、未授权零写入。

### 7.5 large-change-planning

- 当前职责/触发：为大范围任务生成 exploration/implementation plans，触发含固定文件/模块数。
- 当前写入：计划文档和 change artifacts，不改业务代码。
- 重叠：project-init、change governance、implementation planning。
- 重复/硬编码：`>5 files`、`>2 modules`；强制双计划文档。
- 保留：只读探索、影响边界、可验证切片、回滚、阶段授权和 acceptance matrix。
- 删除/下沉：数量门槛；计划格式归 change template，风险定义归 governance。
- 条件分支：按影响模型决定轻量口头计划、change artifacts 或高风险设计；若 active change 已是计划权威，不再创建第二套 implementation-plan。
- 拆分/合并：不拆；与 risk governance 保持“规则/执行”分离。
- 隐式调用：允许在中高影响或用户明确规划请求中触发；默认只读/设计文档写入仅限用户已授权的 change artifact。
- 写入边界：规划请求可写专用 change artifact，不授权实现。
- 验收：单文件安全改动可判高风险；多文件机械改动可判低风险；计划源唯一。

### 7.6 release-check

- 当前职责/触发：发布前检查，默认加载广泛文档和固定检查表。
- 当前写入：以报告为主；不自动 commit/tag/push/deploy。
- 重叠：version governance、deployment、security、code review、release validator。
- 重复/硬编码：近二十类文档、固定输出章节。
- 保留：branch/status/diff、release type、版本元数据、测试/构建、变更合同、阻塞项、回滚与外部动作边界。
- 删除/下沉：确定性版本/manifest 检查交给 validator；详细 release/deploy 清单放 reference。
- 条件分支：patch/plugin/template/migration/docs-only 等发布类型；只有 diff 命中数据、安全、部署、所有权时加载对应材料。
- 拆分/合并：不拆；调用现有 validator，汇总证据。
- 隐式调用：允许明确的“发布检查/能否发布”语义，默认只读。实际 tag/release/deploy 永不由隐式触发。
- 写入边界：明确要求修复 release metadata 时可做限定本地修改；发布外部动作仍单独授权。
- 验收：最小 patch 不读取无关文档；真实风险分支不会漏；结论区分 ready、blocked、not-verified。

### 7.7 code-review

- 当前职责/触发：审查当前 diff、风险、artifact 合同和复审 blocker。
- 当前写入：只读；可建议修复。
- 重叠：security-review、maker-checker、Claude independent reviewer。
- 重复/硬编码：默认加载多类项目文档；固定四章节输出。
- 保留：正确性、回归、证据路径和 v0.44 已冻结的 review convergence；复审既有 blocker，同时允许本轮修复引入的真实回归继续阻塞。
- 删除/下沉：全局安全/授权协议；universal/security/testing 详细清单保留 references。
- 条件分支：默认 diff 正确性；存在 active ForgeKit change 才检查冻结合同；中高风险或 gate 才检查 maker-checker；安全/测试按 diff 命中加载。
- 拆分/合并：保持一个通用 Skill；Claude independent reviewer 保留平台适配，不与 maker 请求器合并。
- 隐式调用：允许明确 review 语义，始终只读；不把每个代码改动都自动送入独立 review。
- 写入边界：无。用户另行明确要求 fix 时退出 review 模式，进入限定实现工作流。
- 验收：findings-first、行号/证据、风险相称加载；recheck 不扩张边界且阻止新回归。

### 7.8 project-suitability

- 当前职责/触发：评估项目是否适合 ForgeKit 与推荐模式。
- 当前写入：当前流程可更新 suitability 文档。
- 重叠：project-init/handover 的 readiness 判断。
- 重复/硬编码：固定模式和检查表可被误当强制流程。
- 保留：基于证据的适用性、缺口、最小采用建议和“不适合”结论。
- 删除/下沉：默认写 suitability 文档；模式详细定义放 governance/reference。
- 条件分支：只评估与当前项目相关的维度；高合规/无 Git/无验证分别降级。
- 拆分/合并：不拆；project-init 可调用其结论。
- 隐式调用：允许“适不适合/准备度”语义，默认只读。
- 写入边界：只有明确要求记录评估时写专用文档。
- 验收：不把采用 ForgeKit 当预设答案；缺证据时降低置信度。

### 7.9 security-review

- 当前职责/触发：检查安全敏感变更和常见风险。
- 当前写入：未清晰声明只读/修复转换边界。
- 重叠：code-review、threat model、dependency review、release-check。
- 重复/硬编码：简短检查表缺少证据层级和人工复核规则。
- 保留：信任边界、数据流、身份/权限、秘密、依赖、输入输出、外部集成的风险审查。
- 删除/下沉：完整安全清单和项目特定策略放 security governance/reference。
- 条件分支：按 diff/架构命中加载；证据分为 Verified、Supported、Unverified；无法运行验证时结论降级，不写“安全通过”。
- 拆分/合并：不拆；作为 code-review/release-check 的按需深查，也可独立调用。
- 隐式调用：允许安全敏感语义或 diff 自动建议触发，但始终默认只读。
- 写入边界：用户明确要求修复具体 finding 后才进入本地实现；凭据轮换、权限变更、生产配置和外部系统必须人工复核/明确授权。
- 验收：每项含证据等级、影响、验证缺口；身份授权、加密/密钥、生产数据、合规和不可逆权限迁移必须人工复核。

### 7.10 first-principles / Claude 同类 Skill

- 当前职责/触发：从事实、假设、约束和最小机制推导，当前强制八章节。
- 当前写入：只读推理。
- 重叠：adversarial-review、design/planning。
- 重复/硬编码：固定八章节与入口中的 first-principles 规则重复。
- 保留：确认事实、分离假设、识别约束、寻找最小可验证机制和反例。
- 删除/下沉：固定章节；详细写回协议放 reasoning-review reference。
- 条件分支：简单问题自然短答；复杂/高风险问题使用可追踪推导和 `TODO_REVIEW`。
- 拆分/合并：与 adversarial review 保持相邻但不合并；前者推导机制，后者攻击失败路径。
- 隐式调用：可在明确“第一性原理/根因推导”或复杂根因任务中触发，默认只读。
- 写入边界：只有用户明确要求记录设计，才写 current change 的摘要，不写完整思维日志。
- 验收：结构随任务复杂度变化，结论可追溯且不伪装未验证假设。

## 8. 影响型风险模型

### 8.1 判断维度

每次只用一段简短判断覆盖：不可逆性、公共合同、持久化数据/迁移、权限安全、外部动作、跨仓库/独立项目、回滚难度、部署影响、验证成本/可观察性、需求与证据不确定性。不采用加权分数。

### 8.2 分级原则

- 低风险：本地、可逆、无公共合同/持久状态/权限/外部影响，验证便宜且证据清楚。即使改很多文件，只要是确定性机械投影且可完整校验，仍可为低风险。
- 中风险：至少一个实质影响维度存在，但范围可界定、回滚直接、验证可信；或需求/证据存在会影响实现选择的不确定性。
- 高风险：不可逆或难回滚、生产/持久数据、身份权限/秘密、公共兼容合同、跨仓库协调部署、外部动作，或关键结论在当前环境无法可靠验证；多个中风险维度叠加也可升高。

### 8.3 与文件数量无关的强触发

- 单文件 schema migration、权限策略、release workflow、公共 API、模板升级规则都至少中风险。
- 数据破坏、生产权限、密钥/身份、跨项目迁移、不可回滚发布为高风险。
- 多文件格式化、版权头、由权威源生成的逐字投影，在无语义/合同变化且 validator 完整时可为低风险。

### 8.4 流程触发

| 流程 | 触发条件 |
| --- | --- |
| maker-checker | 中高风险实现；用户/发布 gate 明确要求；低风险不默认强制 |
| 独立 code review | 中高风险代码、脚本、模板、迁移、安全和发布合同变更；低风险或纯文档按需 |
| change artifact / 文档计划 | 中高风险、跨会话、公共合同或需冻结验收；低风险可轻量 |
| checkpoint | 关键结论、状态/风险/验证变化、长会话边界、handoff/commit/tag 前 |

用户授权会降低“是否允许做”的执行不确定性，但不会降低数据、权限、部署、兼容或回滚的客观风险。风险表达采用一句话：`Risk: <level> — <最主要影响>; rollback <难度>; verification <能力/缺口>.`

## 9. Skill 调用与授权策略

| Skill | 隐式策略 | 默认模式 | 明确修改后的行为 |
| --- | --- | --- | --- |
| project-init | 允许 | 只读发现/编排 | 项目根内初始化写入；外部安装另行授权 |
| project-bootstrap-fill | 关闭 | 显式 handoff 后预览 | 写职责命中的项目事实文档 |
| project-suitability | 允许 | 只读评估 | 明确要求时记录评估 |
| handover-review | 允许 | 只读审计 | 另行明确 fix 范围后本地修改 |
| document-backfill | 关闭 | 显式计划 | 已授权 source set/目标内小批次写回 |
| large-change-planning | 允许 | 只读/设计工件 | 不因规划授权实现 |
| code-review | 允许 | 只读 | 需要新 fix 请求切换工作流 |
| release-check | 允许明确发布语义 | 只读 gate | 可修限定本地元数据；不执行发布 |
| security-review | 允许 | 只读、证据分级 | 明确 finding 范围内修复；人工复核项仍停 |
| request-code-review | 关闭或由 gate 显式调用 | 组装最小 packet | 只请求独立 reviewer，不执行修复 |
| maintenance/archive apply | apply 路径关闭 | plan/read-only 可语义路由 | 明确 plan/目标授权后执行可回滚本地动作 |
| first-principles/adversarial | 允许明确语义或高风险 gate | 只读 | 仅在明确要求时写摘要 |

关闭隐式调用的原因是路由冲突、事实所有权或管理员型 gate，不是“它可能写文件”。写入权限始终由用户意图、入口合同和 Skill 内模式共同决定。

### 9.1 阶段 A Python 行为 runner 合同

冻结未来路径：runner 为 `scripts/test-skill-behavior.py`，case manifest 为 `tests/skill-behavior/cases.json`，adapter package 为 `scripts/skill_behavior_adapters/`，客户端 adapters 为 `scripts/skill_behavior_adapters/codex.py` 和 `scripts/skill_behavior_adapters/claude.py`。阶段 A 只建立 runner、manifest、adapter 接口和最小安全 fixture，不一次实现全部 A01-A22 模型案例。

每个 case 至少包含：`id`、`title`、`client`、`fixture`、`prompt`、`invocation_mode`、`expected_skill`、`forbidden_skills`、`authorization`、`allowed_write_paths`、`forbidden_actions`、`expected_behavior`、`grader`、`tags`。`client` 仅为 `codex|claude`；`invocation_mode` 仅为 `implicit|explicit`；`authorization` 至少为 `read_only|bounded_local_write|external_or_irreversible_not_authorized`。manifest 不保存密钥或用户真实路径。

adapter 只负责检测客户端、取得版本、在明确临时工作区调用、传递 prompt、捕获 stdout/stderr/exit code、可用的 model/tool trace，并转换为统一 run record。adapter 不判定 ForgeKit 行为正确性，不在真实 ForgeKit 工作树运行可写案例，不使用用户当前会话，不访问未声明外部目录，也不执行发布、push、部署或其他外部动作。

隔离合同：

- 每个 case 复制 fixture 到独立临时目录；运行前后记录文件树和 SHA-256，所有 changed paths 必须可观察。
- 正常或异常结束都清理临时目录；只有显式指定且位于 fixture 外的 evidence 目录可保留证据。
- read-only case 的任何未允许变化为 `UNAUTHORIZED_WRITE`；bounded-write 只能修改 `allowed_write_paths`；外部动作只能观察拒绝/停下，不得真实执行。

统一 run record 至少记录：run ID、case ID、UTC 时间、ForgeKit version、Git commit 或工作树身份、OS、Python version、client、client executable、client version、可用的 model 标识、invocation mode、prompt 原文和 SHA-256、fixture 身份和 SHA-256、调用命令的安全化表示、stdout、stderr、exit code、可用的 tool trace、运行前后文件树摘要、changed paths、grader 结果/理由、failure class 和 independent review 状态。不得记录 token、秘密或认证信息。

失败分类固定为：

- `PASS`: 路由、授权和目标行为均满足且证据充分。
- `ENVIRONMENT_UNAVAILABLE`: 客户端、模型或必要环境不可用。
- `ADAPTER_ERROR`: runner 与客户端连接、解析或协议故障。
- `ROUTING_FAILURE`: 预期 Skill 未触发、禁止 Skill 触发或显式调用未解析。
- `UNAUTHORIZED_WRITE`: 违反 read-only 或 bounded-write 合同。
- `BEHAVIOR_FAILURE`: 已正确路由，但回答或动作违反目标行为。
- `GRADER_UNCERTAIN`: 证据不足，不能可靠判定。

环境/adapter 故障不得冒充 Skill 行为失败或通过。

门禁边界：manifest/schema、fixture 结构、adapter 接口静态检查、隔离保护、确定性投影/upgrade fixture 和 runner 单元测试是自动 CI/release blocker。Codex/Claude 各至少一组冻结案例的统一 run record 是 v0.45.0 代表性发布证据，必须由独立 checker 审查。单次 `ROUTING_FAILURE`、`BEHAVIOR_FAILURE` 或 `GRADER_UNCERTAIN` 不由 CI 无条件判整版失败；`UNAUTHORIZED_WRITE`、安全边界丢失或重复稳定失败可由独立 checker 升级为发布 blocker。只有多版本、多次运行稳定的少量案例后续才可提升为自动 blocker。

## 10. 旧 prompts 兼容迁移

### 10.1 v0.45.0 应做

- 保留七个文件和既有路径，文件顶部增加弃用提示、替代 Skill 和兼容周期。
- 把 prompt 收敛为薄包装：传递用户目标/边界，然后调用对应 Skill；不复制完整文档清单、固定问题数或输出章节。
- 把旧 `docs/` 写入语义改为：业务 `docs/**` 默认只读证据；ForgeKit 当前态按 `.forgekit/docs/document-responsibility.md` 选择目标。
- README/usage playbook 将 Skills 和自然语言意图作为首选入口；旧 prompts 只列兼容入口。
- 对仓库外复制的旧 prompt，文档说明其不会自动升级，并提供人工替换对照表。
- 建议弃用窗口至少覆盖 v0.45 和 v0.46 两个 minor 版本。

### 10.2 后续版本可做

- 根据遥测不可用情况下的 issue/反馈和仓库搜索，决定 v0.47 或更晚是否删除。
- 删除前提供一次 release note、migration note 和可复制 Skill 调用替代。
- 如果外部用户仍依赖路径，保留只含弃用说明的 stub，而不是直接 404。

### 10.3 本设计阶段明确不做

- 不编辑、删除、移动 prompts。
- 不更新 README 或 usage playbook。
- 不宣称 deprecated 已生效。

## 11. 兼容性与升级

| 用户类型 | 影响与保护 |
| --- | --- |
| 新安装 plugin | 获得收敛后的根级共享 Skills；项目外可用；外部动作不因安装自动授权 |
| 新生成项目 | 继续含项目本地 Skills、入口和 managed docs；本地投影与 plugin 同语义 |
| 从 v0.44.1 升级 | 单命令 check/plan/apply 保持；stock baseline 可安全替换，定制进入 REVIEW-NEEDED |
| 修改过 AGENTS/CLAUDE/Skills | 不静默覆盖；导出 incoming/diff，用户选择 keep-local/manual-merge/replace-template |
| plugin + 本地同名 Skills | 可能出现双 selector；保持同构语义，并在 run record 中记录实际加载路径、Skill 名和客户端观察，不假定自动合并 |
| 仅 Codex | 使用 AGENTS + `.agents/skills`；Claude 适配不成为依赖 |
| 仅 Claude | 使用 CLAUDE + `.claude/skills`，共享事实仍在 `.codex`/`.forgekit/docs`；不要求安装 Codex plugin |

必须保持：模板创建版本、当前 ForgeKit 版本和 schema 版本分别表达；升级只改变适用的当前版本字段，不机械重写历史记录。

## 12. 回滚原则

- 每阶段独立提交候选，可单独恢复对应文件集合；本设计不执行提交。
- 入口轻量化保留 v0.44.1 baseline，以便出现路由回归时恢复。
- Skill 投影脚本引入前先建立 `--check`，不得让生成动作成为唯一可见真相。
- 升级 migration 的每个 replacement 都带 baseline；定制文件只生成 review-needed material。
- prompts 兼容期内保留原路径，回滚只需恢复薄包装内容，不涉及用户业务文件。

## 13. 保留的 OPEN 与 NEEDS_TEST

- `NEEDS_TEST`: Codex plugin + repo-local 同名 Skill 的隐式/显式路由、selector 和优先级。
- `NEEDS_TEST`: Claude Skill metadata/implicit policy 的可表达能力和实际路由行为。
- `NEEDS_TEST`: 精简入口在 Skill 不触发时仍能阻止只读任务写入和外部动作。
- `NEEDS_TEST`: 已有 v0.44.1 定制入口/Skills 的 manual-merge 差异是否足够易读。
- `NEEDS_TEST`: plugin 入口型能力与项目本地操作型能力在阶段 E 拆分后的用户体验和冲突改善。
- `OPEN`: prompt stub 的最终删除版本；建议不早于 v0.47.0。
- `OPEN`: 真实客户端测试后是否需要备用命名空间策略；双公开名称不是首选，阶段 A 不改 `name` 或 display name。
