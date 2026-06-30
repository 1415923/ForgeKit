# Changelog

本文件记录 ForgeKit 的用户可感知变化。

写法参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 和语义化版本风格，但 ForgeKit 的版本历史不只记录“做了什么”，也记录每个版本当时面对的问题、形成的设计结论，以及解决的真实痛点。

README 只保留当前定位、快速开始和常用入口；完整版本历史、设计取舍和演进脉络放在这里维护。

## 阅读方式

每个版本尽量按以下结构记录：

- **问题背景**：当时真实使用中遇到什么问题。
- **设计结论**：从第一性原则出发，最终决定如何收敛。
- **用户可感知变化**：用户实际会看到什么不同。
- **边界**：明确没有做什么，避免误解 ForgeKit 的能力范围。

## [Unreleased]

### Added

- 暂无。

### Changed

- 暂无。

### Fixed

- 暂无。

---

## [0.38.0] - Context Continuity Protocol

### 问题背景

v0.31 到 v0.37 逐步补齐了 bounded-auto、workflow-router、managed docs writeback、handoff、independent review 和 versioned migration。问题也随之暴露出来：ForgeKit 已经能规划、执行、审查和交付，但长会话里的关键结论仍可能只停留在聊天上下文中。

真实使用里，这会表现为几类问题：

- 长会话推进一段时间后，前面确认过的范围、技术结论、bug 根因或失败路线被后续会话遗忘。
- 子 agent 处理大输出或独立任务后，只把很粗的摘要带回主会话，关键证据没有进入 ForgeKit 文档。
- bounded-auto 多轮推进后，阶段性结论没有及时 checkpoint，后续 handoff 才发现缺证据。
- ForgeKit 升级后，磁盘上的 `AGENTS.md`、`CLAUDE.md`、rules、skills、agents 已更新，但旧会话仍可能沿用旧上下文继续工作。
- v0.37.1 在 macOS 初始化时暴露出 `AGENTS.md` checksum mismatch，说明模板完整性校验必须跨平台稳定，不能只在 Windows 验证通过。

这些问题的共同根因是：聊天上下文、旧会话上下文和工具输出都不是可靠的工程状态存储。关键工程事实如果没有落盘，就不能指望后续会话、compact 后的上下文、子 agent 或 handoff 自动记住。

### 设计结论

v0.38.0 将“上下文连续性”明确为 ForgeKit 的一等协议：关键工程事实必须在阶段边界、上下文切换、子 agent 返回、review / verification 阻断、handoff / commit / tag 前做最小 checkpoint。

这版的核心结论是：

- **聊天上下文不是 durable state**：需求确认、bug 根因、验证结论、风险和阻断不能只存在于对话里。
- **checkpoint 要写到职责最窄的位置**：任务状态写 `task-board.md`，过程摘要写 `work-log.md`，验证证据写 `verification.md`，风险写 `risk-register.md`，不要把所有东西塞进 `CLAUDE.md` / `AGENTS.md`。
- **长输出只保留摘要和证据路径**：完整日志、文件全文和临时推理不进入常驻 managed docs。
- **升级后旧会话不等于新规则已加载**：ForgeKit 升级后，旧会话默认只用于 checkpoint、最小写回和收口；新任务应新开会话或重启工具。
- **模板完整性校验必须跨平台稳定**：UTF-8 文本 checksum 统一按 LF 归一化，避免 CRLF/LF 导致 Mac / Windows 初始化结果不一致。

### Added

- 新增 `.forgekit/docs/context-continuity.md`，定义 Context Continuity Protocol。
- 新增 Critical Facts 列表，明确哪些信息必须 checkpoint：
  - 用户确认过的需求和范围；
  - 关键技术决策；
  - bug 根因和已验证修复结论；
  - 不应重复尝试的失败路线；
  - 风险、阻塞和 `TODO_REVIEW`；
  - 任务状态和版本可见变化；
  - reviewer / verifier 的阻断结论。
- 新增 Context Checkpoint Triggers：
  - 长会话进入阶段边界；
  - 准备 compact / clear / resume 前后；
  - bounded-auto checkpoint；
  - 子 agent 返回关键结论后；
  - 大工具输出或长日志处理后；
  - review / verification 产生 blocking、needs-fix 或 `TODO_REVIEW` 后；
  - handoff / commit / tag 前。
- 新增 Context Survival Map，定义不同信息应该写入哪个 ForgeKit 文档或 change artifact。
- 新增 Post-Upgrade Session Refresh 规则：ForgeKit 升级后，旧会话只用于收口，新任务应新开会话以加载新版规则、skills 和 agents。
- 新增 v0.37.0 -> v0.38.0 safe migration，用于安装缺失的 context continuity 协议文档并登记 feature。

### Changed

- workflow-router 增加“保存关键结论 / compact 或 clear 前 checkpoint / 子 agent 返回结论 / 长会话续接 / 升级后开新会话”的路由。
- bounded-auto-loop-policy 要求每个 checkpoint 先检查 Critical Facts 是否已落盘，再执行最小 managed docs writeback。
- handoff package 增加 Context Continuity Check：如果来源、验证、风险或 reviewer 结论缺证据，必须标记 `TODO_REVIEW`。
- AGENTS、CLAUDE 和 Codex rules 增加短规则：
  - 关键结论不能只留在聊天里；
  - 阶段边界、compact / clear 前、handoff / commit 前要 checkpoint；
  - 长输出只摘要，不写全文；
  - 不确定项标记 `TODO_REVIEW`；
  - 不把所有项目事实塞进 `CLAUDE.md` / `AGENTS.md`；
  - 磁盘文件更新不等于当前旧会话已加载新规则。
- 模板 manifest checksum 逻辑改为：UTF-8 文本文件按 LF 归一化后计算 checksum，二进制文件仍按原始字节计算。

### Fixed

- 修复 v0.37.1 在 macOS 初始化时可能出现的 `AGENTS.md` checksum mismatch。
- 刷新 stale manifest checksum。
- 增加回归验证，确保 `AGENTS.md` / `CLAUDE.md` / `.codex/rules.md` 在 LF/CRLF 下 checksum 稳定。
- 确认初始化后 `AGENTS.md` checksum 与 manifest 一致。
- 确认运行时 `.forgekit/state.json` 不进入 template manifest。

### 用户可感知变化

- 长任务中确认过的关键结论更容易在新会话、handoff 和后续版本中恢复。
- AI 不再把“我刚才说过”当成可靠状态，而会在阶段边界主动做最小 checkpoint。
- 子 agent、reviewer、verifier 产生的阻断结论会被视为 Critical Fact，而不是只留在子会话输出里。
- ForgeKit 升级后，用户会被明确提醒：旧会话只适合收口，新任务应新开会话。
- Mac / Unix 初始化路径下的模板 checksum 校验更稳定，避免 Windows 验证通过但 macOS 初始化失败。

### 边界

- 不做 Claude auto-compact 教程，也不依赖某个工具的内部压缩实现。
- 不自动执行 compact、clear、resume 或 token 监控。
- 不新增 hook、daemon、runner、scheduler 或后台调度。
- 不自动读取全量 managed docs。
- 不把完整聊天、长日志、临时推理或所有项目事实写进 `CLAUDE.md` / `AGENTS.md`。
- 不自动修改未经用户确认的 `requirements.md` 或 `task-intake.md` 原文。
- 不把 checksum 修复扩展成复杂 merge、自动 PR 或旧项目自动升级。

---
## [0.37.0] - Independent Code Review Protocol

### 问题背景

在实际使用 Claude Code / Codex 做代码实现时，如果让同一个会话里的 maker 自己审查自己的代码，很容易出现“有问题也默认通过”的倾向。原因不是模型是否认真，而是审查上下文已经被实现过程污染：maker 知道自己为什么这么改，于是容易相信自己的意图，而不是像独立 reviewer 一样只看 diff、证据和风险。

### 设计结论

代码审查不能只做 self-review。ForgeKit 需要引入独立审查上下文：maker 负责请求审查，reviewer 只读审查 diff、changed files、验证输出和风险，不接收 maker 的完整会话历史，也不替 maker 修代码。

v0.37.0 参考了多个已验证的 code-review skills / subagents 做法：独立 reviewer、最小上下文、结构化 findings、按需 references、read-only 审查和 gate verdict。最终没有照搬大型语言专项规则库，而是落成 ForgeKit 的最小通用审查协议。

### Added

- 新增 Independent Code Review Protocol。
- 新增 `forgekit-code-reviewer` 独立只读 code reviewer agent。
- 新增 `forgekit-request-code-review` skill：maker 用于构造最小 review packet 并请求独立审查。
- 新增 `forgekit-code-review` skill：reviewer 用于 read-only diff review。
- 新增通用、安全、测试三个按需 reference，避免巨型 checklist。
- 新增最小上下文包，用于向独立 reviewer 传递任务摘要、diff/stat、changed files、验证输出和已知风险。
- 新增 `pass` / `needs-fix` / `manual-review` review gate。

### Changed

- 明确 self-review 不能冒充 independent review。
- reviewer 不可用时必须记录为 `manual-review`，不得伪造通过。
- `needs-fix` 会阻断后续 handoff / commit，除非用户明确接受风险。
- bounded-auto 收口、发版/tag 前、核心逻辑/API/数据/权限/脚本改动默认需要 independent review。

### 边界

- 不接 GitHub PR API。
- 不自动评论 PR。
- 不自动修代码。
- 不默认加载大型语言专项规则库。
- 不新增 runner、daemon、auto PR 或 worktree orchestration。

---

## [0.36.0] - Versioned Migration Upgrade Model

### 问题背景

早期 ForgeKit 的升级体系基于模板文件 diff、candidates、upgrade-export、lock、report 等多层机制。工程上安全，但用户体验很差：用户不知道应该看哪个文件，也不知道哪些可以自动应用、哪些必须人工合并。AI 在处理升级时也容易读入大量候选模板，浪费 token，并增加误改风险。

真实痛点是：用户想知道“我当前版本是什么、最新版本会做几件事、哪些安全可应用、哪些需要人工确认”，而不是面对一堆模板文件差异。

### 设计结论

ForgeKit 的升级模型从“模板文件对比”切换为“版本迁移计划”。

v0.36.0 以后只认新的 state + migrations 模型。v0.35.x 及更早项目不再假装支持自动升级，而是按“ForgeKit 接手既有项目”处理。这样可以明确断代，避免在旧模板历史上继续堆复杂兼容逻辑。

### Added

- 新增 Versioned Migration Upgrade Model。
- 新增 `.forgekit/state.json` 驱动的新项目升级模型。
- 新增 `forgekit-upgrade.py check` / `plan` / `apply --safe` 三步升级流程。
- 新增 `migrations/0.36.0/migration.json` 作为新模型基线。

### Changed

- v0.36.0 及以后初始化的新项目使用 state + migrations 进行安全升级。
- v0.35.x 及更早项目不再视为可自动升级项目，而是按既有项目 adoption 流程处理。
- 明确 `plan` 默认不写文件，只输出一屏升级计划。
- 明确 `apply --safe` 只执行 migration 中标记为 safe 的动作。
- 旧 `upgrade-forgekit.*` 保留但降级为 legacy guided upgrade，不再作为推荐路径。
- 不再把 candidates / upgrade-export 作为主路径暴露给用户。

### 边界

- 不支持 v0.35.x 及更早项目自动升级。
- 不做复杂三方 merge。
- 不自动迁移旧 docs。
- 不自动改 business docs。
- 不默认导出全量 candidates。
- 不新增 daemon、runner、auto PR 或 worktree orchestration。

---

## [0.35.2] - Managed Docs Writeback Policy

### 问题背景

v0.31 到 v0.35 强化了 report-only、Do Not Write、review-only 等安全边界，解决了“AI 乱写 managed docs”的问题。但真实项目中又出现了反向问题：任务和版本已经推进，ForgeKit 文档却不再自然更新。例如业务代码已经做到多个版本，`work-log.md`、`task-board.md`、`changelog.md` 没有同步，用户反而失去交接和回溯能力。

根因是提示词里的“只改某几个业务文件”被 agent 理解成“连 ForgeKit 治理文档也不能更新”。

### 设计结论

业务实现范围和治理文档写回范围必须分离：

- **Implementation Scope**：限制业务实现可以改哪些代码/配置。
- **Governance Writeback Scope**：允许在阶段结束时对 ForgeKit managed docs 做最小必要写回。

默认恢复 `ManagedDocsWriteback: minimal`，但不退回到乱写文档。

### Changed

- 新增 Managed Docs Writeback Policy。
- 默认 `ManagedDocsWriteback: minimal`。
- 区分业务实现范围与 ForgeKit 治理写回范围。
- 恢复任务完成后的最小治理写回：`work-log.md`、状态确实变化的 `task-board.md`、用户/版本可见变化的 `changelog.md` 和当前 change artifacts。
- 明确用户只有显式禁止文档写入时，才关闭治理写回。
- 保持 `review-only` 与 report-only 工具的不写入、不自动修复边界。
- `task-intake.md`、`requirements.md`、business docs 仍需明确授权才可修改。

### 边界

- 不新增脚本。
- 不新增 runner、daemon、自动 PR 或 worktree 自动化。
- report-only 报告不会因为 writeback policy 自动触发修复。

---

## [0.35.1] - Codex Agent Schema Hotfix

### 问题背景

在 Codex v0.142.x 中启动项目时，`.codex/agents/forgekit-*.toml` 被 Codex 找到，但解析失败，报错类似：`invalid type: map, expected a string`。这说明 agent 文件结构存在 schema 问题：某些字段被写成 TOML table/map，但 Codex custom agent 需要字符串。

### 设计结论

这是启动级兼容 bug，不能等到后续大版本处理。ForgeKit 必须严格校验 Codex custom agent TOML schema，特别是 `name`、`description`、`developer_instructions` 的类型。

### Fixed

- 修复 Codex custom agent TOML schema 问题。
- 确保 `name`、`description`、`developer_instructions` 均为字符串。
- `developer_instructions` 使用 TOML multiline string，避免 table/map schema 报错。
- 增强 `check-codex-native-agents.py` 类型校验。
- smoke-test 增加 malformed schema 回归测试。

---

## [0.35.0] - Review-Ready Handoff Package

### 问题背景

当一个阶段或任务完成后，ForgeKit 已经能生成很多有用信息：任务来源、任务状态、工作日志、验证记录、风险、doc-health 报告、source-trace 报告等。但这些信息分散在多个文件里，用户要交给领导、reviewer 或测试人员时，仍然需要手工翻文档和整理。

真实痛点是：阶段完成后，用户需要的是“一份能给人看的交付包”，而不是让对方读完整 ForgeKit 工作区。

### 设计结论

handoff 不应该是新的检查器，也不应该自动修复问题。它只应该汇总已有信息，把证据、范围、风险、验证和 TODO_REVIEW 整理成一份可审查报告。

### Added

- 新增 Review-Ready Handoff Package。
- 新增 report-only 交付包，用于汇总来源、需求、任务、变更、验证、风险和 `TODO_REVIEW`。
- 支持生成 `.forgekit/handoff-package.md` 或 `.forgekit/changes/<id>/handoff.md`。

### Changed

- 明确 handoff package 不自动修复、不提交、不创建 PR。
- 缺少验证证据、来源不清、风险不明时标记 `TODO_REVIEW`，不编造结论。
- handoff 可以摘要 doc-health / source-trace 结果，但不能自动修复这些报告中的问题。

### 边界

- 不修改 `task-board.md`、`work-log.md`、`changelog.md`、`requirements.md`。
- 不自动补 Source ID。
- 不自动提交 Git 或创建 PR。

---

## [0.34.0] - Source Trace Report v2

### 问题背景

v0.28.1 已经引入 Source-First Task Intake，解决“任务原文要保留，AI 推导不能混进原文”的问题。但真实项目继续推进后，又出现了新的问题：任务从来源到需求、拆解、实现、验证、完成状态之间的链路可能断掉。比如任务标记完成了，但找不到验证证据；changelog 写了变化，但找不到对应 task/change；work-log 说完成，但 task-board 仍是 pending。

### 设计结论

v0.34 不重做 source intake，不重写 Source ID 规则，而是新增 report-only 的追溯链路检查。v0.33 看“文档有没有写乱”，v0.34 看“事实链路有没有断”。

### Added

- 新增 Source Trace Report v2。
- 新增 report-only 来源追溯报告，用于检查 `Source ID -> requirement -> task -> change -> verification -> work-log/changelog` 链路断点。
- 检查 orphan source、orphan task、verification without task、changelog without task/change 等问题。
- 检查 pending / completed / blocked 状态冲突。

### Changed

- 明确来源追溯报告只报告问题，不自动补链或修复文档。
- workflow-router 新增“检查任务来源追溯 / 任务从哪来 / 完成状态有没有证据”意图。

### 边界

- 不自动补 Source ID。
- 不移动或改写 `task-intake.md`、`requirements.md`、`task-board.md`、`work-log.md`、`changelog.md`。
- 不做 v0.35 handoff。

---

## [0.33.0] - Doc Health Report v2

### 问题背景

ForgeKit 早期已经有 Current Docs Sync Check 和 responsibility matrix，但它们主要解决“模板/当前文档是否同步、职责是否存在”的问题。真实项目使用后，又出现了更具体的文档健康问题：`task-board.md` 写成长篇过程日志，`changelog.md` 写成每日流水账，`requirements.md` 混入未确认原文，同一事实在多个 managed docs 里重复出现。

### 设计结论

v0.33 不重复做 `check-doc-sync`，而是在已有同步检查、职责矩阵和 workflow-router 基础上，新增 report-only 的文档健康汇总报告。它检查真实项目文档是否可读、职责是否错位、是否违反 router 边界。

### Added

- 新增 Doc Health Report v2。
- 新增 report-only managed-docs 健康汇总，用于检查文档过长、重复事实、职责错位和 workflow-router 边界风险。
- 新增 `.forgekit/doc-health-report.md` 生成报告。

### Changed

- 明确文档健康报告只报告问题，不自动修复。
- workflow-router 新增“检查文档健康 / 文档太乱了 / 哪些文档该瘦身”意图。
- bounded-auto 最多生成 doc health report 并停下，不能自动修复文档。

### 边界

- 不自动瘦身文档。
- 不自动归档。
- 不自动改真实项目内容。
- 不重复替代 `check-doc-sync`。

---

## [0.32.0] - Workflow Router / User Intent Router

### 问题背景

随着 ForgeKit managed docs 增多，用户和 AI 都会迷茫：看任务原文该读哪个文件？看当前状态读哪个文件？验证结果写在哪里？changelog、work-log、task-board 有什么区别？如果让 AI 默认全量读取 `.forgekit/docs/**`，既浪费 token，也容易把同一事实重复写进多个文档。

### 设计结论

ForgeKit 需要一个“用户意图 -> 应读文档 / 应写文档 / 不应写文档 / 输出格式”的路由层。它不做自动执行，只让 AI 在回答或写入前先判断意图和文档边界。

### Added

- 新增 `.forgekit/docs/workflow-router.md`。
- 新增用户意图路由机制，用于把请求路由到正确的 Read / Write / Do Not Write 文档。

### Changed

- 减少 AI 默认全量读取 docs 的倾向。
- 减少同一事实在多个 managed docs 中重复写入的问题。
- 入口规则要求写入前先判断 Read Targets / Write Targets / Do Not Write。
- 没有写入触发条件时，不修改 managed docs。

### 边界

- 不做 UI。
- 不做自动 runner。
- 不改变既有文档事实源职责。

---

## [0.31.0] - Bounded Auto Loop Policy

### 问题背景

真实使用 PaiCLI / ForgeKit loop 时，用户不希望每一小步都反复说“继续”，但也不希望 AI 完全无人值守地乱跑。需要一种中间状态：用户一次授权，AI 可以在明确边界内推进多个阶段；遇到风险、越界、验证失败或 agent mode 不满足时必须停。

### 设计结论

ForgeKit 不应该直接实现后台 runner，而应该先定义安全策略：loop mode、授权范围、预算、stop conditions、agent mode gate、checkpoint writeback 和 final handoff。自动执行是后续问题，v0.31 只定义“什么时候可以继续，什么时候必须停”。

### Added

- 新增 Bounded Auto Loop Policy。
- 新增 `one-step`、`bounded-auto`、`review-only` 三种授权边界。
- 新增 scope、stages、budget、stop conditions、agent mode gate 和 handoff 规则。

### Changed

- 明确 bounded-auto 必须用户显式授权。
- 明确 AgentModeRequired=native 时，如果 native 不可用必须停止。
- fallback-allowed 可以降级，但必须记录 fallback reason，不能冒充 native。
- one-step 每轮后必须停。
- review-only 绝不能写文件。

### 边界

- ForgeKit 不提供 runner、daemon、scheduler、自动 PR 或 worktree 编排。
- bounded-auto 是有限授权策略，不是自动执行器。

---

## [0.30.1] - Native Agent Adapter Verification

### 问题背景

v0.30.0 引入 native agent adapter 后，真实验证发现一个关键问题：生成了 agent 配置，不代表 Claude Code / Codex runtime 已经真正注册或能调用这些 agents。Codex 当时也可能只暴露 default / explorer / worker，而没有 ForgeKit 自定义 agent。如果把“配置已生成”误说成“native 可用”，会误导用户。

### 设计结论

必须区分 native agent 生命周期：generated、installed、registered、invoked。只有实际 invoked 才能说 native available。配置检查和运行时调用证据不能混为一谈。

### Changed

- 强化 Native Agent Adapter Verification。
- 明确 generated config 不等于 runtime registered。
- 新增 native / fallback / simulated 状态字段和验证清单。
- native-only verification 默认只读，不自动写 `task-intake.md`、`work-log.md` 或 loop state。
- fallback 必须用户允许或 workflow 明确允许。

### 边界

- 不承诺所有 runtime 都能识别 ForgeKit agents。
- 不把 default / worker / explorer fallback 说成 native。

---

## [0.30.0] - Native Agent Adapter

### 问题背景

ForgeKit 已经有 loop、maker-checker、verification 等协议，但它们还只是文档层规则。Claude Code 和 Codex 逐步支持 subagent/custom agent 后，ForgeKit 需要把这些协议导出成对应工具能识别的原生 agent 配置，以减少纯提示词约束的不稳定性。

### 设计结论

先做 adapter，不做自动调度器。ForgeKit 只生成 Claude Code / Codex 可审查的 agent 配置模板，把 planner、reviewer、verifier 等角色显式化。运行时是否真的注册和调用，由后续验证来确认。

### Added

- 新增 Native Agent Adapter。
- 支持将 ForgeKit loop / maker-checker / verification 协议导出为 Claude Code / Codex 可审查的原生 agent 配置模板。

### Changed

- 明确 Native Agent Adapter 只生成配置，不提供自动执行、runner、dispatcher、worktree 自动化、merge、commit、push 或 PR。

### 边界

- 配置生成不等于 runtime registered。
- 不自动启动 agent team。

---

## [0.29.0] - Guided Upgrade Workflow

### 问题背景

早期 template manifest / lock 已经能识别模板版本，但旧项目升级时仍然需要大量人工判断。AI 会面对很多模板差异、候选文件和 report，token 消耗高，用户也不清楚哪些该合并、哪些该忽略。

### 设计结论

在当时阶段，先做 guided upgrade：生成 upgrade-plan、upgrade-actions 和候选模板，降低人工判断成本。但这个模型后来在真实使用中被证明仍然太复杂，因此 v0.36 将其降级为 legacy。

### Added

- 新增 Guided Upgrade Workflow。
- 新增独立升级脚本，用于生成 upgrade-plan、upgrade-actions 和候选模板。

### Changed

- 降低旧项目升级时的人工判断成本和 token 消耗。
- 为后续 v0.36 的 versioned migration model 暴露了旧模型的复杂性和用户体验问题。

### 边界

- 仍然基于模板文件 diff。
- 不做真正版本迁移包。
- 不自动覆盖项目文件。

---

## [0.28.5] - Work Source Unification

### 问题背景

真实工作来源并不只有“需求文档”。公司派发、微信消息、个人规划、用户反馈、bug、技术债都会变成任务。如果这些来源分别散落，后续 task-board、work-log、changelog 很难串起来。

### 设计结论

把各种工作来源统一纳入 `Source ID -> Task ID -> Work Log` 链路。来源类型可以不同，但进入 ForgeKit 后都应该有统一的可追溯结构。

### Changed

- 新增 Work Source Unification。
- 将公司派发、个人规划、用户反馈、bug、技术债等统一纳入 `Source ID -> Task ID -> Work Log` 链路。

### 边界

- 不把所有来源都自动转成任务。
- 未确认来源仍需人工确认后才能派生可执行任务。

---

## [0.28.4] - Source-to-Task Alignment

### 问题背景

Source-First Task Intake 引入后，新的问题是：source、task-board、work-log 之间仍可能不一致。AI 可能把补充说明当成新 Source，也可能把未确认信息直接写成任务。

### 设计结论

收紧 source-to-task 对齐规则：补充说明默认归并到已有 Source；`task-board.md` 只接收可执行任务；source、task、work-log 之间必须保持反链。

### Changed

- 强化 Source-to-Task Alignment。
- 收紧 `task-intake`、`task-board`、`work-log` 的对应关系。
- 补充和确认默认归并到已有 Source。
- `task-board.md` 只接收可执行任务。

---

## [0.28.3] - Chinese User-Facing Docs

### 问题背景

ForgeKit 的文档逐步增多后，很多内容是给 AI 和脚本看的，机器字段稳定，但用户读起来像模板说明，不像自然工作文档。真实使用时，用户需要中文、简短、接近工作语境的文案。

### 设计结论

把 loop、maker-checker、worktree 和 change 模板改为中文用户可读文案，同时保留机器字段稳定，避免影响自动检查和脚本处理。

### Changed

- 将 loop、maker-checker、worktree 和 change 模板改为中文用户可读文案。
- 保留机器字段稳定，避免影响自动检查和脚本处理。

---

## [0.28.2] - Managed Docs Responsibility Matrix v2

### 问题背景

真实公司项目试用后发现，ForgeKit 文档开始变得“看起来都有用，但每个都太长、职责重叠、用户不知道该看哪个”。`requirements.md`、`task-board.md`、`work-log.md`、`changelog.md` 容易互相写同一事实。AI 也倾向默认全量读取 `.forgekit/docs/**`，导致 token 浪费和写入错位。

### 设计结论

必须先把 managed docs 的职责收紧，建立责任矩阵：哪些是 core/current/working/triggered/reference/generated/archive，不同文档负责不同事实。默认不全量读取 docs，同一事实只写一个负责文档。

### Changed

- 新增 Managed Docs Responsibility Matrix v2。
- 收紧 managed docs 的职责、默认读取策略和重复写入边界。
- 让用户可读文档更短、更自然。
- 明确默认先读 document-responsibility 和 codebase-map，再按任务读取必要文档。

### 边界

- 不删除所有文档。
- 不把所有事实集中到一个大文档。
- 不让触发式文档被默认更新。

---

## [0.28.1] - Source-First Task Intake

### 问题背景

在公司真实任务交接中，用户收到的是领导计划表、微信群消息、接口 JSON、旧表格和人工口头说明混合的信息。之前 ForgeKit 更关注“任务拆解”，容易把 AI 分析后的内容直接写成任务，而没有保存原始来源。这样后续如果有人问“这个任务到底从哪来”，就难以解释。

### 设计结论

第一性原则是：先保留来源，再做分析。任务派发原文、AI 分析、任务反链和人工确认状态应该分离。只有确认后的来源才进入 task-board 变成可执行任务。

### Added

- 新增 `.forgekit/docs/task-intake.md`。

### Changed

- 建立任务来源优先流程：保留任务派发原文、AI 分析、任务反链和人工确认状态，再判断是否生成可执行任务。
- `task-intake.md` 承担来源记录职责，`task-board.md` 只承担可执行任务管理职责。

### 边界

- 不把 AI 推导内容混入原始任务文本。
- 不把未确认来源直接转成 done/pending 任务。

---

## [0.28.0] - Worktree Playbook

### 问题背景

多个并行任务或多 agent 协作时，单工作区容易互相污染。但直接做自动 worktree 调度会引入复杂性和风险，尤其是 merge、冲突、分支清理、用户确认等问题。

### 设计结论

先提供手动 worktree playbook，明确何时适合使用 worktree、如何命名、如何隔离、如何收口。不做自动调度。

### Added

- 新增 Worktree Playbook。
- 新增手动 worktree 并行隔离指南和入口短规则。

### Changed

- 明确 ForgeKit 不提供自动 worktree 调度。

---

## [0.27.0] - Optional Loop Operation Mode

### 问题背景

v0.25/v0.26 已经有 loop 和 maker/checker 设计，但用户需要更具体的“怎么操作”：什么时候 dry-run、什么时候 one-step、什么时候 continue、什么时候 stop-handoff。

### 设计结论

提供显式触发的 loop operation mode。它是操作协议，不是自动 runner。用户明确说进入 loop 后，AI 才按该协议推进。

### Added

- 新增 Optional Loop Operation Mode。
- 新增显式触发的 loop dry-run / one-step / continue / stop-handoff 操作协议。

### Changed

- 明确该模式不提供自动 runner。

---

## [0.26.0] - Maker / Checker Protocol

### 问题背景

让同一个 AI 一边实现、一边确认自己做得对，容易漏掉范围偏移、验证缺失和文档不同步。即便还没有真正多 agent 调度，也需要在流程上区分“做的人”和“查的人”。

### 设计结论

先建立 maker / checker protocol，把实现摘要、检查证据、风险和 review 结论拆开。它不等于真正独立代码审查，但为后续 v0.37 的 independent code review 打基础。

### Added

- 新增 Maker / Checker Protocol。
- 新增 managed docs 模板和 review 证据字段，用于分离实现和复核。

### Changed

- 明确 ForgeKit 不提供自动多 agent 调度。

---

## [0.25.0] - Loop Readiness / Loop Blueprint

### 问题背景

用户希望 ForgeKit 支持 AI 工程 loop，但如果直接做 runner，很容易变成黑盒自动化。第一步应该先判断一个项目是否适合 loop、loop 应该读写哪些文档、有哪些阶段和停止条件。

### 设计结论

先做 loop readiness 和 loop blueprint：评估和设计可审查 loop，不做自动执行。只有当项目、文档、边界和验证条件足够明确时，才适合进入后续 loop operation。

### Added

- 新增 Loop Readiness / Loop Blueprint。
- 新增 managed docs 模板和入口短规则，用于评估与设计可审查 loop。

### Changed

- 明确 ForgeKit 不提供自动 runner。

---

## [0.24.0] - Smart Archive Apply

### 问题背景

v0.23 能给出智能归档建议，但如果每次都让用户手动移动文件，长期会增加维护成本。需要在严格条件下执行归档，但不能误删或误移动活跃 change。

### 设计结论

只有在 Git clean、用户显式确认，并且 advisor 标记为 `auto_archive_candidate` 时，才允许 apply。归档动作必须生成 apply report。

### Added

- 新增 Smart Archive Apply。

### Changed

- 在 Git clean 且用户显式确认后，只归档 Smart Archive Advisor 标记为 `auto_archive_candidate` 的 change。
- 新增 apply report 输出。

---

## [0.23.0] - Smart Archive Advisor

### 问题背景

Archive Plan 和 Reference Check 分别告诉用户哪些 change 可能可归档、哪些引用还存在。但用户真正需要的是综合判断：哪些可以安全归档，哪些必须保留，哪些需要人工确认。

### 设计结论

新增智能归档建议报告，综合 archive plan、reference report 和 sync report，但保持 report-only，不自动移动文件。

### Added

- 新增 Smart Archive Advisor。
- 综合 archive plan、reference report 和 sync report 生成智能归档建议报告。

### Changed

- 明确 Smart Archive Advisor 仍为 report-only。

---

## [0.22.0] - Current Docs Sync Check

### 问题背景

随着 change artifacts 增多，已完成 change 的结果可能没有同步到 current docs。用户需要知道哪些 current docs 可能过期，但又不能让工具自动修改项目事实。

### 设计结论

生成同步证据报告，告诉用户哪些 current docs 需要检查。检查不等于修改。

### Added

- 新增 Current Docs Sync Check。
- 基于 archive plan candidates 生成 current docs 同步证据报告。

### Changed

- 明确该检查不修改项目事实文件。

---

## [0.21.1] - Work Log Managed Doc

### 问题背景

只靠 task-board 和 changelog 不足以记录“今天实际做了什么、被什么打断、下次从哪里接上”。个人项目和公司项目都需要一个轻量工作顺序记录。

### 设计结论

新增 work-log，承担个人工作顺序、交接上下文和中断恢复，不承担唯一需求源或版本历史职责。

### Added

- 新增 Work Log managed doc template。
- 新增 `.forgekit/docs/work-log.md`，用于个人工作顺序、交接上下文和中断恢复记录。

---

## [0.21.0] - Archive Reference Check

### 问题背景

有了 archive plan 后，还需要知道候选 change 是否仍被 current docs、活跃 change 或入口文档引用。否则直接归档可能断链。

### 设计结论

先做引用检查，确认候选归档项是否仍被引用。检查只输出 reference report，不移动文件。

### Added

- 新增 Archive Reference Check。
- 基于 archive plan candidates 生成引用报告。
- 检查 current docs、活跃 change 和入口文档中的字符串引用。

---

## [0.20.0] - Archive Apply

### 问题背景

v0.19 已经能生成 dry-run 归档计划，但用户仍然需要安全地把已完成 change 移到 archive。自动归档如果没有确认和 Git clean 保护，会有较高风险。

### 设计结论

归档 apply 必须满足 Git clean 和用户显式 `--confirm`。操作后输出 apply report，保证可追溯。

### Added

- 新增 Archive Apply。

### Changed

- 在 Git clean 且用户显式 `--confirm` 后，按 dry-run plan 移动候选 change。
- 新增 apply report 输出。

---

## [0.19.0] - Archive Plan

### 问题背景

`.forgekit/changes` 会随着迭代不断增长。如果所有 change 都留在活跃区，AI 和用户都会读到过时内容，浪费 token，也容易误判当前状态。

### 设计结论

先做 dry-run archive plan：只生成归档计划，不移动文件。归档从“建议”开始，不能一开始就自动执行。

### Added

- 新增 Archive Plan。
- 新增 dry-run 归档计划。

### Changed

- dry-run 只生成或覆盖 `.forgekit/archive-plan.md`，不移动文件。

---

## [0.18.0] - Document Lifecycle

### 问题背景

早期 ForgeKit 文档没有明确生命周期：哪些是当前事实，哪些是过程 change，哪些是历史 archive。所有内容都放在默认上下文，会让 AI 读到过时信息。

### 设计结论

建立 current docs / changes / archive 三层规则。当前事实、进行中变更和历史归档必须分开。archive 默认不进入 AI 默认上下文。

### Added

- 新增 Document Lifecycle。
- 新增 current docs / changes / archive 三层规则。

### Changed

- archive 默认不进入 AI 默认上下文。
- done change 只提示可归档，不自动归档。

---

## [0.17.0] - Template Versioning

### 问题背景

ForgeKit 作为模板工具，需要知道“模板版本是什么、项目安装的模板是什么、哪些文件来自模板”。否则后续升级和校验都没有依据。

### 设计结论

新增 template manifest / lock。升级时先生成 report-only 分类和候选模板，不自动覆盖项目文件。

### Added

- 新增 Template Versioning。
- 新增 template manifest / lock。

### Changed

- 升级时只生成 report-only 分类和候选模板。
- 不自动覆盖项目文件。

---

## [0.16.0] - Boundary First

### 问题背景

ForgeKit 既是工具包，又会被安装到具体项目中。早期如果不区分 ForgeKitRoot 和 ProjectRoot，AI 容易把模板文件、项目文件、业务文件混在一起改。

### 设计结论

先定义边界，再做任何改动。明确 ForgeKitRoot、ProjectRoot、managed docs、change artifacts 的位置，避免把工具自身和目标项目混淆。

### Added

- 新增 Boundary First。
- 新增 `.forgekit/project-boundary.yml`。

### Changed

- 新项目默认把 ForgeKit managed docs 写入 `.forgekit/docs`。
- 新项目默认把 change artifacts 写入 `.forgekit/changes`。

---

## [0.15.0] - AI Engineering Loop / Change Workflow

### 问题背景

ForgeKit 在 v0.14 之前主要还是“项目模板 + 规则文档 + skills”的集合。它能帮助 AI 了解项目，也能约束一些常见行为，但还没有把 AI 编程从一次性 prompt 拉回到工程交付流程里。

当时讨论的核心问题不是“要不要集成 OpenSpec、Superpowers、gstack 这些工具”，而是它们背后共同指出了同一个痛点：AI 写代码容易快，但工程交付需要长期可追踪的规格、执行纪律和验证闭环。只靠 README、task-board 或几条 rules，无法回答一次中高风险变更的关键问题：为什么要改、改什么、不改什么、怎么验收、谁来 review、最后怎么沉淀。

### 参考结论

当时形成的判断是：ForgeKit 不应该复刻外部工具，也不应该变成多个工具名的拼装包，而应该吸收它们背后的三层模型：

- **规格层（Spec Layer）**：借鉴 OpenSpec 一类方法，把“系统当前状态”和“本次拟议变更”分开；重大变更不能只写在聊天里，应当有 proposal、design、tasks、verification 等可审查工件。
- **执行纪律层（Execution Layer）**：借鉴 Superpowers 一类方法，约束 agent 不要默认直接写代码，而是按风险等级决定是否需要澄清、设计、任务拆分、TDD、review 和验证。
- **交付闭环层（Delivery Layer）**：借鉴 gstack 一类流程化 delivery 思路，提醒实现完成不等于交付完成，还需要 review、QA、ship、retro 等闭环。

这个版本的关键结论是：ForgeKit 的价值不是“给 AI 更多提示词”，而是把 AI 编程从 ad-hoc prompting 拉回到 spec-guided、skill-disciplined、verification-first 的工程流程。

### 设计结论

v0.15.0 将 ForgeKit 的定位从“AI 项目工作流模板”升级为“轻量级 AI 工程交付工具包”。

设计上没有强制所有任务都走重流程，而是引入风险分级：

- **low risk**：允许轻流程，直接实现并做基本验证。
- **medium risk**：需要 proposal、tasks、verification、review 等最小 change workflow。
- **high risk**：需要更完整的 design、ship checklist 和更严格的验证闭环。

同时引入 `changes/<change-id>/` 作为持续变更治理的基本单元，让 ForgeKit 不只管理“项目总文档”，也能管理“这一次变更”的上下文、设计、任务、验证和复盘。

### Added

- 新增 AI Engineering Loop，定义 ForgeKit 自己的六步闭环：Discover、Specify、Plan、Build、Verify、Ship。
- 新增 `project-template/governance/ai-engineering-loop.md`，说明 ForgeKit 的规格层、执行纪律层和交付闭环层。
- 新增 `project-template/changes/_template/` 变更模板：`proposal.md`、`design.md`、`tasks.md`、`verification.md`、`review.md`、`ship.md`、`retro.md`。
- 新增基于 `Risk:` 的中高风险 change 必需文件检查。

### Changed

- 将 ForgeKit 定位升级为轻量级 AI 工程交付工具包。
- 将中高风险规则接入 `AGENTS.md`、`CLAUDE.md`、`.codex/rules.md` 和 project template 入口文档。
- README / README.en / usage.html 更新为“AI engineering delivery toolkit”定位。
- 现有 skills 只做最小同步，避免把 v0.15 做成外部工具复刻或大型命令系统。

### 解决的痛点

- 避免大改动只留在聊天记录里，后续无法追踪“为什么这么改”。
- 避免 AI 一上来直接改代码，缺少风险判断、任务拆解和验收标准。
- 避免“测试过了就结束”，把 review、ship、retro 纳入交付闭环。
- 让 ForgeKit 从初始化模板变成可以支撑持续变更治理的轻量工具包。

### 边界

- 不集成 OpenSpec、Superpowers 或 gstack，不复制它们的目录结构和工具实现。
- 不强制所有小改动都走完整 proposal / design / ship / retro。
- 不引入大量 slash commands 或重型流程引擎。
- 不做自动 runner、CI/CD 平台或项目管理系统。
