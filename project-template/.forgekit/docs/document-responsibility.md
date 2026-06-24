# Managed Docs 职责矩阵 v2

编辑 `.forgekit/docs/**` 前先看本文。它的作用是减少默认读取、避免重复写入，并让给用户确认的文档保持短、自然、可读。

## 文档分类

- `core`：初始化、接手项目或日常工作通常会用到。
- `current`：当前项目事实；只有稳定事实变化时才更新。
- `working`：当前工作状态、任务来源、近期交接信息。
- `triggered`：只有对应事件发生时才更新。
- `reference`：任务需要该主题时才读取。
- `generated`：脚本生成物；不要当作当前事实手改。
- `archive`：历史材料；默认不读取。

## 默认读取

- `yes`：初始化、广义交接或启动时可以读取。
- `as-needed`：任务指向该主题时读取。
- `no`：默认不读取。

| 文档 | 文档分类 | 读者 | 默认读取 | 写什么 | 不写什么 | 更新触发 | 相关文档 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `README.md` | core | 用户 | yes | 项目是什么、快速开始、基础用法 | 内部过程、长历史、任务流水 | 用户入口或启动方式变化 | `AGENTS.md`, `CLAUDE.md` |
| `AGENTS.md` / `CLAUDE.md` | core | AI 工具 | yes | 简短启动顺序、边界规则、任务路由 | 长清单、模板正文、技术栈手册 | 启动顺序、写入边界或路由变化 | `.codex/rules.md`, skills |
| `.forgekit/project-boundary.yml` | core | AI 工具、维护者 | yes | ForgeKitRoot、ProjectRoot、managed docs root、change root、写入策略 | 产品计划、架构、任务状态 | 目录布局或写入策略变化 | `AGENTS.md`, `CLAUDE.md` |
| `.forgekit/docs/document-responsibility.md` | core | 用户、AI 工具 | yes | 文档职责、更新触发、事实归属 | 项目事实、任务日志、发布说明 | managed docs 职责变化 | `document-lifecycle.md` |
| `.forgekit/docs/codebase-map.md` | core | AI 工具、维护者 | yes | 代码搜索入口、模块入口、关键命令、谨慎读取路径 | 完整架构、API 百科、长扫描历史 | 模块入口、命令或归属变化 | `architecture.md`, `api.md`, `local-toolchain.md` |
| `.forgekit/docs/task-intake.md` | working | 用户、AI 工具 | as-needed | 工作来源原文或原始想法、Source ID、Update Notes、Task Decision、Derived Task IDs、人工确认状态 | 执行状态总表、工作流水、changelog、长分析 | 领导任务、微信任务、计划表格子、会议任务、个人规划、用户反馈、bug、技术债、测试失败；小补充默认更新已有 Source | `requirements.md`, `task-board.md`, `work-log.md` |
| `.forgekit/docs/requirements.md` | current | 用户、产品、AI 工具 | as-needed | 已确认的需求事实、验收标准、范围边界、Source ID 引用 | 任务派发原文、长推理、执行状态 | 需求被确认、修正、拒绝或定界 | `task-intake.md`, `traceability.md` |
| `.forgekit/docs/task-board.md` | working | 用户、AI 工具 | as-needed | 通过准入的可执行任务、状态、owner、下一步、验证方式、Source ID、Superseded/Dropped 结论 | 任务原文、聊天补充、纯确认、工作流水、长计划 | Task Gate ready、任务阻塞、复查、完成、取消或被替代 | `task-intake.md`, `work-log.md`, `changes/<id>/tasks.md` |
| `.forgekit/docs/work-log.md` | working | 用户、AI 工具 | as-needed | 近期工作窗口、Task ID / Source ID 引用、验证/提交/推送/阻塞/确认摘要 | 任务原文、任务总表、全量历史、正式发布说明、敏感信息 | 阶段收口、验证完成、提交/推送、阻塞变化、领导确认、日报、中断恢复 | `task-board.md`, `testing.md`, `changelog.md` |
| `.forgekit/docs/changelog.md` | current | 用户、发布复查者 | as-needed | 用户可见变化、兼容性、迁移提示 | 内部工作顺序、每次提交、原始验证日志 | 用户可见变化完成或发布说明更新 | `work-log.md`, `ship.md` |
| `.forgekit/docs/testing.md` | current | 开发者、测试、AI 工具 | as-needed | 当前验证命令、测试范围、人工验证清单、已知缺口 | 每次测试运行日志、长失败历史、截图堆积 | 测试策略或可运行验证命令变化 | `work-log.md`, `changes/<id>/verification.md` |
| `.forgekit/docs/risk-register.md` | current | 用户、维护者 | as-needed | 仍影响交付、安全、兼容性、成本或排期的开放风险 | 已关闭风险长历史、所有 bug、泛泛担忧 | 新风险、概率/影响变化、缓解或关闭 | `technical-debt.md`, `incident-review.md` |
| `.forgekit/docs/project-plan.md` | current | 用户、维护者 | as-needed | 当前项目目标、非目标、范围、落地条件 | 日常进展、版本历史、任务原文 | 产品方向或范围变化 | `requirements.md`, `version-roadmap.md` |
| `.forgekit/docs/architecture.md` | current | 开发者、维护者 | as-needed | 当前架构、模块职责、数据流、边界 | 旧设计、实现日记、API 细节 | 架构、边界或主要依赖变化 | `api.md`, `database-design.md`, ADR |
| `.forgekit/docs/local-toolchain.md` | reference | AI 工具、开发者 | as-needed | 本地构建/测试/lint/运行事实 | 安装许可、凭据、无关环境记录 | 工具链探测或验证命令变化 | `.codex/commands.md` |
| `.forgekit/docs/codex-next-work-order.md` | working | 用户、AI 工具 | as-needed | 初始化或交接后的下一步 AI 工作单 | 长路线图、工作日志、任务看板替代品 | 初始化、交接或用户方向变化 | `project-plan.md`, `task-board.md` |
| `.forgekit/docs/implementation-plan.md` | triggered | 开发者、AI 工具 | no | 大型或跨模块工作的实施计划 | 小任务状态、当前需求 | 大型/跨模块/高风险任务确认后 | `changes/<id>/tasks.md`, `exploration-report.md` |
| `.forgekit/docs/exploration-report.md` | triggered | 开发者、AI 工具 | no | 大型工作前的只读调研发现 | 最终架构、任务状态、发布说明 | 大型/跨模块/高风险调研 | `implementation-plan.md` |
| `.forgekit/docs/defect-fix-plan.md` | triggered | 开发者、维护者 | no | 已确认缺陷的修复计划 | 通用任务看板、无关风险历史 | 缺陷需要单独修复计划 | `defect-review.md`, `task-board.md` |
| `.forgekit/docs/defect-review.md` | triggered | 开发者、维护者 | no | 严重或重复缺陷的根因和预防 | 普通 bug 状态 | 严重/重复缺陷复查 | `incident-review.md`, `risk-register.md` |
| `.forgekit/docs/incident-review.md` | triggered | 维护者 | no | 事故时间线、影响、根因、后续动作 | 普通 bug、日常日志 | 事故或生产影响故障 | `risk-register.md`, `work-log.md` |
| `.forgekit/docs/dependency-review.md` | triggered | 开发者、安全 | no | 依赖变更原因、风险、许可证/安全说明 | 所有包版本、安装日志 | 新增/删除/大版本升级依赖 | `threat-model.md`, `.codex/security.md` |
| `.forgekit/docs/threat-model.md` | triggered | 安全、维护者 | no | 安全敏感数据流、信任边界、威胁、缓解 | 泛质量风险、凭据 | 鉴权、权限、数据暴露、密钥、外部集成变化 | `risk-register.md`, `.codex/security.md` |
| `.forgekit/docs/release-pipeline.md` | triggered | 发布负责人 | no | 当前发布路径、回滚、部署检查 | changelog、任务历史 | 发布流程或部署路径变化 | `changelog.md`, `environment-matrix.md` |
| `.forgekit/docs/quality-metrics.md` | triggered | 维护者 | no | 选定质量指标和复查门槛 | 每次测试结果、每个缺陷 | 质量指标或复查门槛变化 | `testing.md`, `risk-register.md` |
| `.forgekit/docs/technical-debt.md` | triggered | 维护者 | no | 已接受的技术债、负责人、复查条件 | 所有 TODO、已关闭风险 | 技术债被接受或退休 | `risk-register.md`, `task-board.md` |
| `.forgekit/docs/traceability.md` | triggered | 测试、维护者 | no | 需要时的需求-任务-测试-缺陷映射 | 任务原文、长证据 | 受监管、高风险或用户要求追踪 | `requirements.md`, `testing.md`, `task-board.md` |
| `.forgekit/docs/loop-readiness.md` | triggered | 用户、AI 工具 | no | 是否具备安全运行 loop 的条件 | loop runner 配置、daemon 设置 | loop 设计或操作前 | `loop-blueprint.md`, `loop-operations.md` |
| `.forgekit/docs/loop-blueprint.md` | triggered | 用户、AI 工具 | no | 可审查的 loop 设计 | 自动执行授权 | 用户要求类似循环的重复工作 | `loop-readiness.md`, `work-log.md` |
| `.forgekit/docs/loop-operations.md` | triggered | 用户、AI 工具 | no | 明确触发的 dry-run、one-step、continue、stop/handoff 协议 | 后台 runner、调度器、自动化代码 | 用户明确操作 loop | `loop-blueprint.md` |
| `.forgekit/docs/maker-checker-protocol.md` | triggered | 用户、AI 工具 | no | Maker/Checker 复查协议 | 多 agent 调度器或最终人工批准 | 中高风险复查分离 | `changes/<id>/review.md` |
| `.forgekit/docs/worktree-playbook.md` | triggered | 用户、AI 工具 | no | 手动 worktree 隔离指南 | 自动 worktree 编排 | 用户要求并行隔离工作 | `work-log.md` |
| `.forgekit/changes/<id>/*` | triggered | 开发者、复查者 | no | 单次中高风险变更过程 | 当前态事实、无关历史 | 中高风险变更开始或收口 | `document-lifecycle.md` |
| `.forgekit/archive/*` | archive | 审计者、维护者 | no | 历史证据和旧变更材料 | 当前事实、活跃变更上下文 | 用户要求历史、审计、回归、复盘 | `document-lifecycle.md` |
| `.forgekit/*-report.md` | generated | 用户、AI 工具 | no | 脚本生成的报告 | 当前事实或可编辑项目文档 | 脚本运行生成或覆盖 | 对应脚本文档 |
| `docs/**` 业务文档 | reference | 用户、AI 工具 | as-needed | 用户允许或要求时读取的业务证据 | 默认写入 ForgeKit 治理模板 | 用户明确要求更新业务文档 | `.forgekit/project-boundary.yml` |

写入前先做 5 步判断：

1. 判断内容类型：任务来源、需求事实、任务状态、验证方式、工作顺序、发布变化、风险、设计决策还是历史。
2. 只把事实写入一个负责文档。
3. 相关文档只放链接或 Source ID，不复制同一段内容。
4. 给用户看的文档先写结论，再写必要证据，避免模板腔和长过程自述。
5. 触发式文档只有事件真的发生时才读取或更新。

## Source-to-Task 链路

任务和个人开发工作按以下顺序处理：

1. `task-intake.md`：记录工作来源原文或原始想法、补充、人工确认和 Task Decision。
2. `task-board.md`：只接收满足准入条件的可执行任务，并保留 `Source ID`。
3. `work-log.md`：记录推进过程、验证、提交/推送、阻塞和确认，并引用 `Task ID` / `Source ID`。

公司派发、个人规划、用户反馈、bug 发现、技术债、测试失败和调研发现都使用同一条 Source-to-Task 链路，只是 `Source Type` 不同。小补充、小确认、改期或责任修正默认写到已有 Source 的 `Update Notes`，不要直接变成新任务。过时任务必须进入 `Closed / Dropped / Superseded`，不要继续出现在当前重点。
