# 代码库地图

本文是 Codex 的代码搜索起点。新项目初始化时先保留模板；随着项目落地，逐步把真实目录、入口、验证命令补齐。

## 项目入口

| 区域 | 路径 | 用途 | 负责人 |
| --- | --- | --- | --- |
| 后端入口 | 待补充 | 应用启动、接口、业务逻辑 | 待补充 |
| 前端入口 | 待补充 | 页面、路由、组件、状态管理 | 待补充 |
| 数据库 | 待补充 | schema、migration、数据访问 | 待补充 |
| 部署配置 | 待补充 | 环境变量、容器、脚本、发布配置 | 待补充 |
| 测试 | 待补充 | 单元测试、集成测试、端到端测试 | 待补充 |
| 文档 | `docs/` | 方案、架构、版本、任务、风险 | 待补充 |
| ForgeKit 工作日志 | `.forgekit/docs/work-log.md` | 个人工作顺序、交接上下文、中断恢复、验证/提交/阻塞/确认摘要 | 待补充 |
| Loop Readiness | `.forgekit/docs/loop-readiness.md` | 判断项目是否具备安全运行 loop 的状态、验证、边界、停止和升级条件 | 待补充 |
| Loop Blueprint | `.forgekit/docs/loop-blueprint.md` | 定义可审查的 loop 设计图纸，不是自动执行授权 | 待补充 |

## 关键模块

| 模块 | 路径 | 关键文件 | 外部依赖 | 验证方式 |
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

## 推荐启动目录

| 技术栈 | 推荐启动目录 | 备注 |
| --- | --- | --- |
| Java Spring Boot | 后端模块根目录 | 优先找 `pom.xml`、`build.gradle`、`src/main` |
| Vue | 前端模块根目录 | 优先找 `package.json`、`vite.config.*`、`src/router` |
| React | 前端模块根目录 | 优先找 `package.json`、`src/`、路由配置 |
| Python FastAPI | API 模块根目录 | 优先找 `pyproject.toml`、`requirements.txt`、`app/` |
| Node Express | Node 服务根目录 | 优先找 `package.json`、`src/`、路由配置 |
| FPGA Vivado/Vitis | 硬件工程根目录 | 优先找 Vivado/Vitis 工程、HLS 工程、仿真脚本 |

## 局部验证命令

| 区域 | 命令 | 何时运行 |
| --- | --- | --- |
| 后端 | 待补充 | 修改后端代码后 |
| 前端 | 待补充 | 修改页面、组件或前端接口后 |
| 测试 | 待补充 | 修改业务逻辑或修复缺陷后 |
| 构建 | 待补充 | 发布前或跨模块变更后 |

详细工具链状态记录在 `.forgekit/docs/local-toolchain.md`。如果该文档未填写，Codex 应先询问或用只读命令探测，不要默认安装依赖或启动服务。

个人工作顺序记录在 `.forgekit/docs/work-log.md`。它用于阶段收口、验证、提交/推送、阻塞变化、领导/组长确认和中断恢复，不替代 `.forgekit/docs/changelog.md`、`.forgekit/docs/task-board.md`、`.forgekit/docs/testing.md` 或风险/追踪文档。

Loop 设计记录在 `.forgekit/docs/loop-readiness.md` 和 `.forgekit/docs/loop-blueprint.md`。它们用于判断项目是否适合安全运行 loop，并定义 Trigger、Input Sources、State File、Allowed Paths、Forbidden Paths、Validation Command、Stop Condition、Human Escalation、Token Budget、Comprehension Check 和 Output / Writeback；它们不是 daemon、cron、MCP、connector、自动 PR、多 agent 调度或 worktree 自动化配置。

## 忽略和谨慎读取

| 路径或类型 | 处理方式 | 原因 |
| --- | --- | --- |
| 构建产物 | 默认忽略 | 噪音大，通常不应手改 |
| 依赖目录 | 默认忽略 | 由包管理器维护 |
| 大型二进制文件 | 先询问 | 不适合直接读入上下文 |
| 凭据和私钥 | 不输出完整值 | 安全风险 |

## 维护规则

- 新增模块时，同步更新本文件。
- 接手既有项目时，先补齐真实目录和启动命令。
- 大版本 review/refactor gate 时，检查本文件是否过期。
- 如果本文件和代码不一致，以代码为准，并在本文件记录修正。
