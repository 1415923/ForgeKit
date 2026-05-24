# 用户级规则：命令白名单

用于把常见命令按权限风险分级。具体项目如果有 `.codex/commands.md`，项目规则优先；本文件作为用户级默认策略。

## 分级说明

| 等级 | 含义 | 执行策略 |
| --- | --- | --- |
| A | 只读或低风险 | 可直接执行 |
| B | 写入当前工作区或运行项目验证 | 可执行，但应确认命令与当前任务相关 |
| C | 需要用户确认 | 执行前说明目的、影响范围和替代方案 |
| D | 需要升级权限或正常本机权限 | 先尝试常规方式；若因沙盒、网络、权限失败，再请求升级权限 |
| X | 默认禁止 | 除非用户明确要求且风险已说明，否则不执行 |

## Shell 与文件读取

| 命令或模式 | 等级 | 说明 |
| --- | --- | --- |
| `Get-ChildItem`、`ls` | A | 查看当前工作区或用户明确给出的目录 |
| `Get-Content` | A | 读取文本文件；中文 Markdown 优先用 PowerShell 7 |
| `Select-String`、`rg` | A | 搜索文本 |
| `Get-Command` | A | 检查命令是否存在 |
| `Get-Item`、`Resolve-Path` | A | 检查路径 |
| `New-Item -ItemType Directory` | B | 仅限当前工作区或用户指定项目目录 |
| `Set-Content`、`Out-File`、重定向写文件 | B | 手工编辑优先用 apply_patch；脚本生成文件需限定在工作区 |
| `Remove-Item` | C/X | 删除单个明确临时文件为 C；递归删除、大范围删除为 X，除非明确要求 |
| `Move-Item`、`Rename-Item` | C | 可能影响项目结构，先确认 |

## Git

| 命令或模式 | 等级 | 说明 |
| --- | --- | --- |
| `git status` | A | 可直接执行 |
| `git diff` | A | 可直接执行 |
| `git log`、`git show` | A | 可直接执行 |
| `git branch --show-current` | A | 可直接执行 |
| `git add` | C | 暂存会影响提交内容，执行前确认范围 |
| `git commit` | C | 需要用户确认提交信息和内容 |
| `git tag` | C | 需要用户确认版本号和影响 |
| `git push` | D | 通常需要升级权限或正常本机权限；执行前必须确认 |
| `git pull`、`git fetch` | C/D | 涉及网络；执行前确认，网络失败再请求升级权限 |
| `git merge`、`git rebase` | C | 会改变历史或工作区，先确认 |
| `git reset --hard` | X | 默认禁止 |
| `git checkout -- <path>`、`git restore <path>` | X | 默认禁止，避免回滚用户改动 |
| `git clean -fdx` | X | 默认禁止 |
| `git push --force` | X | 默认禁止 |

## 工具版本与环境检查

| 命令或模式 | 等级 | 说明 |
| --- | --- | --- |
| `java -version`、`javac -version` | A | 可直接执行 |
| `mvn -version`、`gradle --version` | A | 可直接执行 |
| `node --version`、`npm --version`、`pnpm --version` | A | 可直接执行 |
| `python --version`、`py --version` | A | 可直接执行 |
| `pwsh -Version`、`$PSVersionTable` | A | 可直接执行 |
| `Get-ChildItem Env:` | A | 可读取非敏感环境变量；不要输出 API key 全值 |
| 修改环境变量 | C | 仅限当前进程可按任务需要设置；系统级修改必须确认 |

## Java / Maven / Gradle

| 命令或模式 | 等级 | 说明 |
| --- | --- | --- |
| `mvn test`、`mvn -q test` | B | 项目测试命令 |
| `mvn package`、`mvn verify` | B | 构建验证，可能耗时 |
| `mvn spring-boot:run` | C/D | 长期运行服务，默认先确认 |
| `mvn dependency:*` | C/D | 可能联网下载依赖，先确认 |
| `gradle test`、`gradle build` | B | 项目验证命令 |
| `gradle bootRun` | C/D | 长期运行服务，默认先确认 |
| 修改 Maven/Gradle 全局配置 | C | 例如 settings.xml、全局仓库、代理 |

## 前端 / Node

| 命令或模式 | 等级 | 说明 |
| --- | --- | --- |
| `npm run lint`、`npm run typecheck`、`npm test` | B | 项目验证命令 |
| `npm run build` | B | 构建验证 |
| `npm run dev`、`pnpm dev`、`vite --host` | C/D | 长期运行 dev server，Vite 在沙盒中可能 `spawn EPERM` |
| `npm install`、`pnpm install`、`yarn install` | C/D | 会下载依赖并改 lockfile |
| `npm update`、`pnpm update` | C/D | 会改变依赖版本 |
| `npm publish` | X | 默认禁止，除非明确发布任务 |
| 全局安装 `npm install -g` | C/D | 修改用户或系统环境，先确认 |

## Python / Conda

| 命令或模式 | 等级 | 说明 |
| --- | --- | --- |
| `python --version` | A | 可直接执行 |
| `python -m pytest`、`pytest` | B | 项目测试命令 |
| `python -m compileall` | B | 语法验证 |
| `pip install`、`conda install` | C/D | 下载依赖、修改环境，先确认 |
| `conda env create`、`conda env update` | C/D | 修改环境，先确认 |
| 执行未审查的远程脚本 | X | 默认禁止 |

## 服务与端口

| 命令或模式 | 等级 | 说明 |
| --- | --- | --- |
| `Get-Service` | A | 检查服务状态 |
| `Test-NetConnection -ComputerName localhost -Port <port>` | A | 检查本机端口 |
| `netstat`、`Get-NetTCPConnection` | A | 检查端口占用 |
| `Start-Service MySQL95` | C/D | 启动系统服务，先确认 |
| `Start-Service Redis` | C/D | 启动系统服务，先确认 |
| `Stop-Service` | C/X | 停止开发服务为 C；停止未知或系统关键服务为 X |
| `Start-Process cmd /k ...` | C/D | 长期服务或可见终端，先确认 |
| `Stop-Process -Name java` | X | 可能误杀多个服务，默认禁止 |

## 本机中间件

| 工具 | 推荐策略 |
| --- | --- |
| MySQL | 查询服务和端口可直接做；启动/停止服务先确认 |
| Redis | 查询服务和端口可直接做；启动服务端先确认；不要把 `redis-cli` 当服务端 |
| MinIO | 推荐正常本机权限启动；沙盒内可能写 `D:\minio\data` 失败 |
| Kafka | 推荐项目脚本启动；清理日志或 KRaft 数据属于破坏性操作，先确认 |
| Elasticsearch | 推荐正常本机权限启动；避免重复拉起节点导致锁冲突 |
| Ollama / DeepSeek | `ollama list` 可查询；已发现 `deepseek-r1:7b`；`ollama pull`、`ollama serve` 先确认 |

## 数据库与数据操作

| 命令或模式 | 等级 | 说明 |
| --- | --- | --- |
| 只读查询 | C | 连接数据库前确认连接目标和凭据来源 |
| 本地开发库迁移 | C | 说明影响表和回滚方式 |
| 清库、删表、truncate | X | 默认禁止 |
| 导入生产数据 | X | 默认禁止 |
| 导出含敏感信息的数据 | X | 默认禁止 |

## FPGA / Xilinx

| 命令或模式 | 等级 | 说明 |
| --- | --- | --- |
| 查看 Xilinx 目录 | A | 例如 `D:\Xilinx\Vivado\2023.2` |
| 读取 HLS/Vivado 项目文件 | A | 只读分析 |
| `vitis_hls -f <script>` | C/D | 可能长时间运行并生成大量文件 |
| `vivado -mode batch -source <script>` | C/D | 可能长时间运行并生成大量文件 |
| 打开 Vivado/Vitis GUI | D | GUI 操作需要用户确认 |
| 综合、实现、生成 bitstream | C/D | 长耗时、高资源消耗，先确认 |
| 连接或操作硬件板卡 | C/D | 可能影响设备状态，先确认 |

## 网络与外部服务

| 命令或模式 | 等级 | 说明 |
| --- | --- | --- |
| 浏览公开文档 | A/C | 使用浏览工具只读访问公开资料可行；命令行联网需确认 |
| `curl`、`Invoke-WebRequest` 下载文件 | C/D | 下载外部资源前确认 |
| 调用 API 读取公开信息 | C | 确认目标和是否需要凭据 |
| 调用会写入外部状态的 API | C/D | 必须确认 |
| 发送邮件、Webhook、消息 | C/D | 必须确认 |

## Agent 工具链

| 命令或模式 | 等级 | 说明 |
| --- | --- | --- |
| 阅读 AGENTS、skills、commands、hooks、MCP 示例 | A | 只读审查 |
| 新增或修改项目内 command 草稿 | B/C | 仅写文档为 B；涉及真实命令或外部动作前确认 |
| 启用 hook | C/D | 默认不启用；确认触发点、耗时、误阻断、跳过方式 |
| 启用 MCP | C/D | 需要确认网络、凭据、读写范围和审计方式 |
| MCP / GitHub / Jira / CI 只读查询 | C/D | 确认目标和凭据来源 |
| MCP / GitHub / Jira / CI 写操作 | C/D | 创建 issue、更新 PR、触发 CI 或部署前必须确认 |
| 安装 plugin 或第三方 skill | C/D | 审查来源、权限、写入范围和供应链风险 |

## 绝对禁止的默认行为

除非用户明确提出并确认风险，否则不要执行：

- `git reset --hard`
- `git clean -fdx`
- `git push --force`
- 递归删除不明确目录
- 清空数据库、删库、删表
- 删除 Kafka / Elasticsearch / MinIO / MySQL / Redis 数据目录
- 修改系统 PATH、全局代理、系统服务启动项
- 上传、发布、部署、推送到远程生产资源
- 输出完整 API key、密码、令牌、私钥
