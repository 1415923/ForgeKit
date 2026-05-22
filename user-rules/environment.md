# 用户级规则：本机环境

用于记录当前电脑上的固定开发环境。不同项目可以引用这里的信息，但不应把这些内容复制到项目文档中。

## 基础环境

- 操作系统：Windows
- 默认 Shell：PowerShell
- 常用工作目录：
  - `D:\JAVA-code`
  - `D:\tmp`
- 默认输出语言：中文
- 当前模板目录：`D:\JAVA-code\项目开发流程`
- Java 全栈环境参考文档：`D:\JAVA-code\simple-auth\项目环境启动指南.md`

## 常用工具

| 工具 | 路径或命令 | 备注 |
| --- | --- | --- |
| Git | `D:\Git\cmd\git.exe` | 版本：2.53.0.windows.1；统一使用本机安装的 Git |
| Windows PowerShell | `C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe` | 原生 PowerShell；部分中文输出可能乱码 |
| PowerShell 7 | `C:\Program Files\PowerShell\7\pwsh.exe` | 版本：7.6.1；读写中文文档优先使用，但执行部分命令可能遇到权限或兼容问题 |
| JDK | `D:\JAVA\jdk-17` | JAVA_HOME；Java 17.0.17 |
| Java 命令 | `C:\Program Files\Common Files\Oracle\Java\javapath\java.exe` | PATH 中的 shim；实际 Maven 使用 `D:\JAVA\jdk-17` |
| Maven | `D:\JetBrains\IntelliJ IDEA 2025.2\plugins\maven\lib\maven3\bin\mvn.cmd` | Maven 3.9.9；来自 IDEA 内置 Maven |
| Gradle | `D:\gradle\gradle-9.5.1\bin\gradle.bat` | Gradle 9.5.1 |
| Node.js | `D:\nodejs\node.exe` | Node v24.15.0 |
| npm | `D:\nodejs\npm.ps1` | npm 11.12.1 |
| pnpm | `C:\Users\32390\AppData\Roaming\npm\pnpm.ps1` | pnpm 10.28.2 |
| Python | `D:\anaconda3\python.exe` | Anaconda Python 3.12.7 |
| Python Launcher | `C:\WINDOWS\py.exe` | Windows Python Launcher |
| IntelliJ IDEA | `D:\JetBrains\IntelliJ IDEA 2025.2` | Java IDE；CLI 通常不直接调用 IDEA |
| VS Code | `D:\Microsoft VS Code\bin\code.cmd` | 编辑器命令 |
| Redis | `D:\Redis\redis-server.exe`、`D:\Redis\redis-cli.exe` | Windows 服务 `Redis` 当前可用 |
| MySQL | Windows 服务 `MySQL95` | 当前服务已存在，启动项目时优先检查服务状态和端口 |
| MinIO | `D:\minio_server_data\bin` | 数据目录涉及 `D:\minio\data`，沙盒内启动可能权限失败 |
| Kafka | `D:\kafka\kafka_2.13-3.9.1` | simple-auth 推荐 KRaft 脚本启动 |
| Elasticsearch | `D:\elasticsearch-8.10.0` | 版本目录为 8.10.0 |
| Ollama | `D:\Ollama\ollama.exe` | 本地模型服务；已发现 `deepseek-r1:7b` |
| Xilinx Vivado | `D:\Xilinx\Vivado\2023.2` | FPGA / HLS 项目使用 |
| Xilinx Vitis | `D:\Xilinx\Vitis\2023.2` | FPGA / 嵌入式项目使用 |
| Xilinx Vitis HLS | `D:\Xilinx\Vitis_HLS\2023.2` | HLS 项目使用 |
| Docker | 未发现命令 | 需要使用时重新确认是否安装 |

## Shell 使用策略

- 读写中文 Markdown 文档时，优先使用 PowerShell 7：`C:\Program Files\PowerShell\7\pwsh.exe`。
- 执行普通 Windows 管理命令、服务检查、简单文件查看时，可以使用 Windows PowerShell。
- 原生 Windows PowerShell 中文显示可能乱码；如果输出内容需要准确阅读，改用 PowerShell 7 或调整编码。
- PowerShell 7 在部分命令、权限、长期服务启动场景下可能报错；遇到问题时改用 Windows PowerShell、CMD、项目脚本或请求升级权限。
- 长期运行服务优先用 `Start-Process cmd /k ...`，并按项目文档记录日志位置。

## Git 使用策略

- Git 查询类命令可以直接运行，例如 `git status`、`git diff`、`git log`。
- Git 提交、打 tag、推送、合并远程分支默认需要用户确认。
- 当前环境中 Git 推送通常需要升级权限或正常本机权限；不要在受限沙盒中反复尝试推送。

## 环境使用规则

- 运行命令前，优先读取项目内的 `README.md`、`.codex/commands.md` 和构建配置。
- 如果项目指定了工具版本，以项目配置为准。
- 如果项目没有指定工具版本，使用本文件中的本机默认工具。
- 涉及全局安装、修改系统环境变量、写入用户目录之外的位置时，必须先说明原因并等待确认。
- Java 全栈项目如果涉及 MySQL、Redis、MinIO、Kafka、Elasticsearch、Ollama、Spring Boot、Vue 前端启动，按需读取 `user-rules/environments/java-fullstack.md`，并优先参考 `D:\JAVA-code\simple-auth\项目环境启动指南.md`。
- 本地 AI / RAG 项目如果需要模型服务，可使用 Ollama + `deepseek-r1:7b`，默认地址通常是 `http://localhost:11434/v1`；启动长期服务前先确认。
- 需要 Maven 本地仓库时，优先使用项目内 `.m2/repository`，避免受限环境写入用户目录失败。

## FPGA / Xilinx 环境

- 仅在 FPGA、Vivado、Vitis、Vitis HLS、PYNQ、板卡项目中读取详细环境。
- 详细信息见 `user-rules/environments/fpga-xilinx.md`。

## 待补充信息

- Docker Desktop 或其他容器环境是否安装。
- yarn 是否需要作为前端默认包管理器。
- MySQL 客户端命令路径。
- Vivado / Vitis / Vitis HLS 命令行初始化脚本的推荐调用方式。
- 常用代理端口、DashScope / DeepSeek 等 API key 的本机注入方式。
