Status: design-revised-awaiting-blocker-recheck
DesignStatus: design-revised-awaiting-blocker-recheck
Risk: high
Created: 2026-07-20
Owner: ForgeKit Maintainers
Reason: 冻结 v0.45.0 的规则所有权、Skill 职责、分发兼容和行为测试设计。
AuthorizedStage: design-revised-awaiting-blocker-recheck

# v0.45.0 规则所有权与 Skill 收敛提案

## 当前状态

- 当前分支为 `main`，基线版本为 `0.44.1`，HEAD 为 `9e6c407`。
- 本轮开始时工作树仅有与本设计无关的 `D usage.html`；本 change 不恢复、不覆盖也不解释该删除。
- 仓库尚无 v0.45.0 change artifact；本目录是该版本的首个专用设计工件。
- 根级 `skills/` 与 `project-template/.agents/skills/` 有九组同名 Skill；当前 `SKILL.md` 与 `agents/openai.yaml` 内容相同，但由人工双副本维护。
- `project-template/.claude/skills/` 是 Claude 平台适配层，不是上述九组文件的逐字投影。
- v0.44.1 的发布校验仅将 `code-review` 声明为共享副本并检查哈希，尚未表达完整权威源关系。
- 初始化脚本复制整个 `project-template/`；升级脚本已支持 baseline 匹配、`REVIEW-NEEDED` 和手工合并，能够保护项目本地定制。

## 问题

1. 常驻入口、Skills、governance、references、README、usage playbook 和 prompts 重复表达同类规则，部分授权语义不一致。
2. 根级插件 Skill 与项目模板 Skill 当前内容一致，但权威源、同步动作和平台适配边界未正式定义。
3. `project-init`、`handover-review` 等 Skill 同时承担判断、访谈、规划、写回、执行和审批，容易把只读任务升级为修改流程。
4. 文件数、模块数、问题数量和固定输出章节等硬规则不能稳定表达真实影响。
5. 当前测试以结构和脚本 smoke 为主，缺少 Skill 的触发、冲突、授权和轻量化行为合同。
6. `prompts/` 仍复制旧路径、固定文件清单和流程；Codex 当前官方机制已将 reusable workflow 的首选入口转向 Skills。

## 目标

- 为重要规则指定唯一权威层，其他位置只保留短引用、生成投影或明确的平台适配。
- 保留无 Skill 触发时仍不可丢失的安全、事实和授权边界，同时降低 AGENTS/CLAUDE 常驻上下文负担。
- 将核心 Skill 收敛为清晰任务、条件加载和风险相称的流程，不把“是否隐式触发”当作写入授权。
- 用定性影响模型替换固定文件数或模块数门槛。
- 冻结根级共享 Skill、项目本地投影和 Claude 适配的分发与升级策略。
- 为 v0.45.0 定义可自动化的最小行为测试集及后续扩展集。
- 保持单命令升级、`REVIEW-NEEDED`、本地定制保护、maker-checker 和版本字段语义分离。

## 非目标

- 本轮不修改 AGENTS.md、CLAUDE.md、任何 Skill、governance、references、README、usage playbook、prompts 或脚本。
- 本轮不修改模板、插件元数据、marketplace、manifest、版本号或 migration。
- 本轮不删除、迁移或弃用任何实际 prompt 文件。
- 本轮不建立 Skill 生成器、同步器或测试运行器。
- 本轮不重新处理 v0.44.1，不修复审计发现的其他问题。
- 本轮不执行 commit、push、tag、release 或外部系统动作。

## 范围

设计范围覆盖：

- 根级与模板 AGENTS/CLAUDE 的常驻规则边界。
- 根级九个共享 Skill、模板 `.agents` 投影及六个 Claude 平台 Skill。
- governance、references、managed docs、usage playbook、README 和旧 prompts 的规则职责。
- 初始化、升级、Skill 分发、模板 manifest 和发布校验脚本的未来职责。
- 新安装、新生成、v0.44.1 升级、本地定制、插件与本地同名 Skill 并存、单平台使用等兼容场景。

## 信任边界

- 防止审计类请求未获授权就写文件，或修复请求被同义确认反复阻断。
- 防止不可逆、破坏性、外部和越界动作因 Skill 路由而失去明确授权保护。
- 防止不确定内容被写成项目事实，或业务事实被写入 governance 模板。
- 防止共享 Skill 投影漂移、平台专属内容被通用同步覆盖、升级静默覆盖项目定制。
- 不承诺控制第三方客户端内部的同名 Skill 选择优先级；该行为需要真实客户端测试。
- 不把用户绕过正式 ForgeKit 入口直接运行内部 helper 的故意误用纳入本次保护合同，除非该 helper 自身会造成高影响外部或不可逆后果。

## 阶段授权

- 当前状态为 `design-revised-awaiting-blocker-recheck`：只允许完成 M-02、M-04 的定向设计修订和 blocker recheck。
- 不允许进入任何实施阶段。
- M-01、M-03 和 A21 已由上一轮 blocker-recheck 关闭，本轮不重新讨论；三个维护者决策继续冻结。进入阶段 A 仍需独立 checker 关闭 M-02、M-04，并由维护者另行授权。
- 阶段 A 通过独立 checker 后，后续每个阶段仍按本 change 的阶段边界单独授权。

## 冻结原则

1. 审核、审计、检查、诊断、评估和规划默认只读。
2. 修复、修改、实现和更新允许在用户明确范围内进行本地、可回滚写入；不得重复确认同一局部授权。
3. 不可逆、破坏性、外部和越界动作仍需明确授权；局部写入授权不能扩张为这些动作。
4. AGENTS/CLAUDE 保留无 Skill 触发时仍不可丢失的最小安全、事实、授权和路由合同。
5. Skills 只承载按需任务流程；governance/references 承载细则；scripts/validators 承载可确定性检查。
6. 重要规则只有一个规范性权威位置；其他位置必须是短引用、生成投影或有记录的平台适配。
7. 风险由影响、回滚、验证和不确定性决定，文件数只作辅助信号。
8. maker-checker 和独立 code review 由中高影响或明确 gate 触发，不默认覆盖所有代码改动。
9. 新生成项目继续自包含本地 Skills；插件与本地同名 Skill 的重复必须通过同语义投影，以及能记录实际加载来源路径、Skill 名和客户端观察结果的行为测试与诊断降低风险。
10. 现有项目升级只自动替换已知未定制 baseline；定制文件进入 `REVIEW-NEEDED` 或人工合并。
11. Claude 平台 Skill 是适配层，不纳入通用 Skill 的机械覆盖。
12. prompts 在 v0.45.0 采用兼容迁移，不直接删除。

## 已冻结的维护者决策

### DECISION-01：共享 Skill 权威源

- 根 `skills/` 是 `project-init`、`project-bootstrap-fill`、`handover-review`、`document-backfill`、`large-change-planning`、`release-check`、`code-review`、`project-suitability`、`security-review` 的唯一共享语义维护源。
- `project-template/.agents/skills/` 是上述九个 Skill 的确定性同构投影；新项目继续包含该本地投影。
- `project-template/.claude/skills/` 是 Claude 平台适配层，不属于通用机械投影目标。
- stock 文件仅在匹配项目记录来源版本所对应的已知 baseline 时自动更新；custom 或 baseline 无法唯一确定的文件进入 `REVIEW-NEEDED/manual-merge`，不得静默覆盖。
- sync `check` 可进入 CI/release；sync `apply` 只允许维护者显式调用，release 不得隐式执行 apply。

### DECISION-02：同名 Skill 与 display name

- 阶段 A 不添加 Plugin/Project 等来源 display name，不修改公共 Skill `name`，通用源和 `.agents` 投影保持同构。
- selector、显式调用和隐式路由优先级继续标记为 `NEEDS_TEST`。
- 阶段 E 长期优先研究插件承担跨项目入口型能力、项目本地 Skills 承担依赖项目上下文的操作型流程。
- 为同一工作流永久设置两个命名空间或两个来源显示名只作为实测后的备选，不是首选方案。

### DECISION-03：行为测试 runner 与发布门禁

- 使用仓库原生、跨平台、数据驱动的 Python runner，通过 Codex/Claude adapters 执行行为案例。
- 确定性结构、投影、升级 fixture 和静态授权合同是自动 CI/release blocker。
- v0.45.0 发布前必须分别具有一个当前稳定 Codex 和一个当前稳定 Claude Code 的代表性行为证据，并由独立 checker 复核。
- 单次非确定模型结果不直接成为无条件自动 CI blocker；真实越权写入、安全边界丢失或重复稳定失败仍可由独立 checker 判为发布 blocker。
- 只有经多版本、多次运行证明稳定的少量行为案例，后续才可提升为自动 blocker。

## M-02 与 M-04 最终冻结合同

- M-02：升级人工审查继续且仅使用 `.forgekit/reports/upgrade-review-needed.md`、`.forgekit/reports/upgrade-review-needed.json` 和 `.forgekit/reports/review-needed/`。packet ID 固定为 `<target-version>--<managed-path-sha256-prefix>`；packet 内固定使用 `packet.json`、`local/<managed-relative-path>`、`incoming/<managed-relative-path>`、`rollback/<managed-relative-path>` 和 `diff.patch`。rollback 与 packet 同根，保存升级前原始字节；不得新增 `.forgekit/rollback/`、`.forgekit/backups/` 或其他顶层 review/merge/rollback root。
- M-02 兼容性：上述合同直接扩展 `scripts/forgekit-upgrade.py` 的现有 review 输出和 migration `replace_file_if_baseline_matches`，不建立平行系统。stock 写前准备同 packet rollback 身份但不必标为未解决 review；custom/unknown-baseline 必须生成 packet 且不覆盖；missing 不伪造不存在的 local/rollback 文件。
- M-04：阶段 A 将创建唯一共享入口规范 `project-template/governance/agent-entry-contract.md`；本轮不创建。AGENTS 与 CLAUDE 只应用该规范，并在阶段 B 迁移。矩阵 owner 必须是一个实际或已冻结创建的仓库相对文件路径，可带 anchor；不得使用通配符、参数化占位符、目录、角色名或多文件共同 owner。
- M-04 路由：通用 SKILL-ROUTING 由 `project-template/governance/agent-entry-contract.md#skill-routing` 拥有；九个根 Skill 的具体触发和六个 Claude Skill 的平台行为分别由矩阵中列出的实际 `SKILL.md` 文件拥有。Claude 常驻入口适配仅由 `project-template/CLAUDE.md` 拥有，不取得共享安全规则所有权。

## 保留的未决项

- `OPEN`: Claude Code 对同名/相邻 Skill 的实际选择和 metadata 能力需要按目标客户端版本验证。
- `OPEN`: 旧 prompts 的弃用周期建议为两个 minor 版本，但最终删除版本由使用反馈决定。

## 生命周期说明

- 本 change 当前为 `design-revised-awaiting-blocker-recheck`；设计修订不等于实现完成。
- 独立 checker 关闭当前仍待复核的 M-02、M-04 且维护者另行授权后，才可进入阶段 A 并改为 `active`。
- 所有阶段实现、验证、升级兼容和独立审查完成后才可改为 `done`。
- 只有 v0.45.0 已成为历史材料且不再是活跃上下文时才可归档。
