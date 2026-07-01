# 代码库地图

本文只做代码搜索入口，不做项目百科。目标是帮助 AI 和接手人员快速知道：从哪里开始看、哪些目录谨慎碰、怎么验证。

定位：代码搜索入口，不是项目百科。

维护原则：

- 只记录当前稳定入口，不写长扫描历史。
- 模块细节放到 `architecture.md`、`api.md`、`database-design.md`。
- 任务来源放到 `task-intake.md`，任务状态放到 `task-board.md`。
- 如果本文超过日常可读范围，优先删旧细节并改成链接。

## 搜索入口

| 区域 | 路径 | 用途 | 默认处理 |
| --- | --- | --- | --- |
| 后端入口 | 待补充 | 应用启动、接口、业务逻辑 | 任务相关时读取 |
| 前端入口 | 待补充 | 页面、路由、组件、状态管理 | 任务相关时读取 |
| 数据库 | 待补充 | schema、migration、数据访问 | 改动前确认 |
| 部署配置 | 待补充 | 环境变量、容器、脚本、发布配置 | 默认只读 |
| 测试 | 待补充 | 单元测试、集成测试、端到端测试 | 修改后验证 |
| 业务文档 | `docs/` | 业务说明、既有方案、验收资料 | 默认只读 |
| ForgeKit 管理文档 | `.forgekit/docs/` | 当前项目事实和工作状态 | 按职责矩阵读取 |

用户意图类问题先看 `.forgekit/docs/workflow-router.md`。本文只指向入口，不复制路由表。

Multi-project scoped docs 启用后，先从 `.forgekit/workspace-map.json` 确认 WorkspaceRoot、ProjectScope、RepoRoot 和 ArtifactRoot，再只读取命中的 project capsule。详细边界见 `.forgekit/docs/scoped-docs.md`。

## 当前主要模块

| 模块 | 路径 | 关键文件 | 什么时候读 | 验证方式 |
| --- | --- | --- | --- | --- |
| 待补充 | 待补充 | 待补充 | 待补充 | 待补充 |

## 常用搜索关键词

| 场景 | 关键词 |
| --- | --- |
| 接口入口 | controller、route、handler、endpoint、api |
| 业务逻辑 | service、usecase、domain、manager |
| 数据访问 | repository、mapper、dao、entity、model、schema、migration |
| 前端页面 | routes、pages、views、components、store、api |
| 配置 | config、application、env、docker、vite、webpack、pom、gradle、package |
| 测试 | test、spec、mock、fixture、e2e |

## 局部验证命令

| 区域 | 命令 | 何时运行 |
| --- | --- | --- |
| 后端 | 待补充 | 修改后端代码后 |
| 前端 | 待补充 | 修改页面、组件或前端接口后 |
| 测试 | 待补充 | 修改业务逻辑或修复缺陷后 |
| 构建 | 待补充 | 发布前或跨模块变更后 |

详细工具链状态记录在 `.forgekit/docs/local-toolchain.md`。如果该文档未填写，先询问或用只读命令探测，不要默认安装依赖或启动服务。

## ForgeKit 文档入口

| 需要了解 | 读取 |
| --- | --- |
| 文档该写到哪里 | `.forgekit/docs/document-responsibility.md` |
| 用户一句话该读/写哪些文档 | `.forgekit/docs/workflow-router.md` |
| 长会话、compact/clear、子 agent 结果如何存活 | `.forgekit/docs/context-continuity.md` |
| 当前项目目标和范围 | `.forgekit/docs/project-plan.md` |
| 工作来源原文、补充记录和 Task Decision | `.forgekit/docs/task-intake.md` |
| 可执行任务、Task ID、状态和 Source ID 反链 | `.forgekit/docs/task-board.md` |
| 最近工作顺序、验证、提交/推送和阻塞确认 | `.forgekit/docs/work-log.md` |
| 验证命令和测试策略 | `.forgekit/docs/testing.md` |
| 用户可见版本变化 | `.forgekit/docs/changelog.md` |
| 文档健康检查 | `scripts/doc-health-report.py`，输出 `.forgekit/doc-health-report.md` |
| 来源追溯检查 | `scripts/source-trace-report.py`，输出 `.forgekit/source-trace-report.md` |
| 独立代码审查 | `.claude/skills/forgekit-request-code-review/SKILL.md` 请求；`forgekit-code-reviewer` 只读审查；结果写当前 change `review.md` |
| 根因推导 / 失败路径审查 | `.forgekit/docs/reasoning-review.md`；按需使用 `forgekit-first-principles` 或 `forgekit-adversarial-review`，结果写当前 change 或 checkpoint 摘要 |
| 阶段交付包 / reviewer handoff | `scripts/handoff-package.py`，汇总独立审查证据并输出 `.forgekit/handoff-package.md` 或 `.forgekit/changes/<change-id>/handoff.md` |
| 项目维护意图 | `.forgekit/docs/project-maintenance.md`；先识别 `MaintenanceIntent`，再 plan / confirm / summary |
| 阶段归档 capsule | `.forgekit/docs/archive-capsule.md`、`scripts/archive-capsule.py`；历史检索先看 `.forgekit/archive/index.md` |
| 当前任务断链 / 归档后无法继续 | `.forgekit/docs/current-docs-integrity.md`、`scripts/check-current-docs-integrity.py`；先检查，再决定是否做 Current State Restoration Pass |
| 多项目 / 多仓库边界和 scoped docs | `.forgekit/workspace-map.json`、`.forgekit/docs/scoped-docs.md`、`scripts/check-workspace-integrity.py`；未启用时保持 single-project |
| 中高风险变更过程 | `.forgekit/changes/<change-id>/` |
| 有限授权连续推进规则 | `.forgekit/docs/bounded-auto-loop-policy.md` |
| 原生 agent 配置适配 | `.forgekit/docs/native-agent-adapter.md` |
| ForgeKit 版本迁移 | `scripts/forgekit-upgrade.py check -> plan -> apply --safe`；状态见 `.forgekit/state.json` |

不要默认读取 `.forgekit/docs/**` 全量内容。先按本文件、`document-responsibility.md` 和 `workflow-router.md` 判断需要哪些文档。

任务链路按 `task-intake.md -> task-board.md -> work-log.md` 处理：先归并工作来源，再进入看板，最后记录推进过程。公司派发、个人规划、用户反馈、bug、技术债、测试失败都走同一条链路。补充和确认默认更新已有 Source 或 Task，不默认创建新任务。

## 忽略和谨慎读取

| 路径或类型 | 处理方式 | 原因 |
| --- | --- | --- |
| 构建产物、依赖目录、缓存 | 默认忽略 | 噪音大，通常不应手改 |
| `.DS_Store`、`Thumbs.db`、`__pycache__`、`.pytest_cache`、`*.tmp` | 不记录进管理文档，不纳入模板 | 系统或临时产物 |
| 大型二进制文件 | 先询问 | 不适合直接读入上下文 |
| 凭据、私钥、token、证书、真实环境地址 | 不输出完整值 | 安全风险 |

## 维护触发

- 新增或删除主要模块。
- 入口文件、验证命令、谨慎读取路径变化。
- 接手项目时发现本文和代码不一致。
- 大版本 review/refactor gate 要求复查入口。
