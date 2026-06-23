# 代码库地图

本文只做代码搜索入口，不做项目百科。目标是帮助 AI 和接手人员快速知道：从哪里开始看、哪些目录谨慎碰、怎么验证。

Role: code search entry, not project encyclopedia.

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
| 业务文档 | `docs/` | 业务说明、既有方案、验收资料 | read-mostly |
| ForgeKit managed docs | `.forgekit/docs/` | 当前项目事实和工作状态 | 按职责矩阵读取 |

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
| 当前项目目标和范围 | `.forgekit/docs/project-plan.md` |
| 任务派发原文和 Source ID | `.forgekit/docs/task-intake.md` |
| 当前任务状态 | `.forgekit/docs/task-board.md` |
| 最近工作顺序和交接 | `.forgekit/docs/work-log.md` |
| 验证命令和测试策略 | `.forgekit/docs/testing.md` |
| 用户可见版本变化 | `.forgekit/docs/changelog.md` |
| 中高风险变更过程 | `.forgekit/changes/<change-id>/` |

不要默认读取 `.forgekit/docs/**` 全量内容。先按本文件和 `document-responsibility.md` 判断需要哪些文档。

## 忽略和谨慎读取

| 路径或类型 | 处理方式 | 原因 |
| --- | --- | --- |
| 构建产物、依赖目录、缓存 | 默认忽略 | 噪音大，通常不应手改 |
| `.DS_Store`、`Thumbs.db`、`__pycache__`、`.pytest_cache`、`*.tmp` | 不记录进 managed docs，不纳入模板 | 系统或临时产物 |
| 大型二进制文件 | 先询问 | 不适合直接读入上下文 |
| 凭据、私钥、token、证书、真实环境地址 | 不输出完整值 | 安全风险 |

## 维护触发

- 新增或删除主要模块。
- 入口文件、验证命令、谨慎读取路径变化。
- 接手项目时发现本文和代码不一致。
- 大版本 review/refactor gate 要求复查入口。
