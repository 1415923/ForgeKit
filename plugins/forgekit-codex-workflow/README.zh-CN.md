# ForgeKit Codex Workflow Plugin 中文说明

这个 plugin 用于把 ForgeKit 的 Codex 工作流分发给团队成员，目标是让新用户安装后能获得一致的项目初始化、接手审查、代码审查、发布检查和安全审查能力。

## 包含内容

- `skills/`：项目初始化、初始化问答填充、既有项目接手、代码审查、发布检查、安全审查等稳定 skill。
- `scripts/init-project-template.ps1`：从 plugin 资产生成项目模板。
- `scripts/validate-plugin-assets.ps1`：检查 plugin 分发包是否完整。
- `scripts/detect-local-toolchain.ps1`：只读检测本地工具链。
- `scripts/run-harness-check.ps1`：只读检查生成项目的 harness 入口。
- `assets/project-template/`：生成项目时使用的基础模板。
- `assets/templates/`：Java、Vue、React、Python、Node、C#/.NET、Go、Laravel、Rust、Flutter、C++、Kotlin、Swift、Rails、R、FPGA 等技术栈模板。
- `assets/docs/`：安装、升级、安全和真实项目试用反馈说明。

## 不包含内容

- 不包含 `user-rules/`，因为这里通常有个人电脑路径、权限偏好和本机环境。
- 不包含外部开发记录目录 `document/`。
- 不包含凭据、token、私有服务地址或部署自动化。
- 不默认启用 hook。
- 不默认启用 MCP。
- 不自动执行 issue、PR、部署、tag、push 等外部写操作。

## 初始化项目

在 plugin 目录下运行初始化脚本。这个脚本会把 ForgeKit 的基础模板复制到目标项目目录，并按你选择的技术栈把模板放到目标项目的 `.codex/stacks/<stack>/` 下。

通用命令格式：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 `
  -TargetPath "<你的项目绝对路径>" `
  -ProjectName "<项目名称>" `
  -Stacks <技术栈1>,<技术栈2>
```

参数说明：

- `-TargetPath`：必填。要初始化的项目目录，建议使用绝对路径。
- `-ProjectName`：可选但建议填写。会写入 `.codex/init.generated.md`。
- `-Stacks`：可选。要加入的技术栈模板，多个值用英文逗号分隔。
- `-Force`：可选。覆盖已有模板文件。首次初始化普通项目时不要加。

可选技术栈：

- `java-springboot`：Java Spring Boot 后端。
- `vue`：Vue/Vite 前端。
- `react`：React 前端。
- `python-fastapi`：Python FastAPI 服务。
- `node-express`：Node.js / Express 后端。
- `csharp-dotnet`：C#/.NET、ASP.NET Core、Worker Service。
- `go-service`：Go API、CLI、微服务、后台任务。
- `php-laravel`：Laravel 后台、业务 CRUD、API 服务。
- `rust-cli-service`：Rust CLI、系统工具、高性能服务。
- `flutter-dart`：Flutter 跨端 App、移动端、Web、桌面。
- `cpp-cmake`：C++ 库、CLI、算法模块、CMake 工程。
- `kotlin-spring`：Kotlin 后端、Spring Boot、Ktor 原型。
- `swift-ios`：iOS 原生 App、SwiftUI、UIKit。
- `ruby-rails`：Rails Web、后台系统、API-only Rails。
- `r-data-analysis`：R 数据分析、报表、Shiny、可复现项目。
- `fpga-vivado-vitis`：FPGA、Vivado、Vitis、Vitis HLS 项目。

常见示例：

Java + Vue 前后端项目：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 `
  -TargetPath "D:\JAVA-code\my-business-app" `
  -ProjectName "my-business-app" `
  -Stacks java-springboot,vue
```

Python FastAPI 项目：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 `
  -TargetPath "D:\projects\my-api" `
  -ProjectName "my-api" `
  -Stacks python-fastapi
```

烟测示例：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 `
  -TargetPath "D:\tmp\forgekit-plugin-smoke" `
  -ProjectName "forgekit-plugin-smoke" `
  -Stacks java-springboot,vue
```

生成后进入目标项目，从 `AGENTS.md` 开始让 Codex 读取上下文。

## 验证 plugin 分发包

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-plugin-assets.ps1
```

这个检查会确认：

- plugin manifest 存在且版本正确。
- 必要 skills 存在。
- 模板资产存在。
- 安装、升级、安全和反馈说明存在。
- 没有把 `user-rules/`、外部 `document/` 或 `.git/` 打包进去。

## 推荐试用流程

1. 先运行 `validate-plugin-assets.ps1`。
2. 用 `init-project-template.ps1` 生成一个 `D:\tmp` 烟测项目。
3. 在烟测项目运行 `scripts/run-harness-check.ps1`。
4. 可选运行 `scripts/detect-local-toolchain.ps1`，只记录结果，不安装工具。
5. 确认生成项目从 `AGENTS.md`、`docs/代码库地图.md`、`docs/Codex下一步工作单.md` 开始工作。
6. 把真实项目试用结果记录到外部开发记录，再决定是否回灌到模板。

## 真实项目反馈

真实项目试用时，优先记录：

- 项目类型和技术栈。
- plugin 是否能安装或加载。
- 初始化脚本是否能生成项目模板。
- 哪些 skill 真正有用。
- 哪些说明导致困惑或上下文过重。
- 哪些验证命令通过或失败。
- 缺少哪些本地工具。
- 项目最终判断为 Suitable、Conditional 还是 Custom。

详细格式见 `assets/docs/feedback.md`。

## 安全边界

这个 plugin 是分发包，不是自动化开关。安装后仍然需要用户确认高风险动作。启用 command、hook、MCP、CI、issue tracker 或部署集成前，先阅读生成项目里的 `governance/team-agent-rollout.md`。

## v0.9.1 说明

plugin 顶层 `skills/` 和 `assets/project-template/.agents/skills/` 会有重复，这是刻意设计：

- 顶层 `skills/` 用于让 Codex 在安装 plugin 后发现这些能力。
- `assets/project-template/.agents/skills/` 用于让生成出来的项目自包含，不依赖 plugin 继续存在。
