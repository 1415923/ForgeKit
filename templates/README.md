# 技术栈模板

本目录用于按技术栈拆分项目规则，避免每个项目都加载无关内容。

## 使用原则

新项目初始化时，先复制 `project-template/`，再按实际技术栈选择一个或多个 `templates/<stack>/` 中的内容。

不要把所有技术栈模板一次性复制到项目中。只复制当前项目需要的部分。

## 模板清单

| 模板 | 适用项目 | 典型内容 |
| --- | --- | --- |
| `java-springboot/` | Java 后端、Spring Boot、Maven/Gradle | 后端分层、配置、数据库、中间件、测试 |
| `vue/` | Vue、Vite、前端管理端 | npm/pnpm、组件、路由、状态、接口代理 |
| `react/` | React、Vite/Next 风格前端 | 组件、hooks、状态、路由、测试 |
| `python-fastapi/` | Python API、FastAPI、脚本服务 | 虚拟环境、依赖、API、pytest |
| `node-express/` | Node.js 后端、Express API | npm/pnpm、路由、中间件、测试 |
| `csharp-dotnet/` | C#/.NET、ASP.NET Core、Worker Service | SDK、DI、配置、EF Core、测试、发布 |
| `go-service/` | Go HTTP API、CLI、微服务、后台任务 | Go modules、包边界、context、并发、测试 |
| `php-laravel/` | Laravel 后台、业务 CRUD、API 服务 | Composer、Artisan、migration、队列、测试 |
| `rust-cli-service/` | Rust CLI、系统工具、高性能服务 | Cargo、错误处理、clippy、测试、发布 |
| `flutter-dart/` | Flutter 跨端 App、移动端、Web、桌面 | Dart、状态管理、平台权限、测试、签名 |
| `cpp-cmake/` | C++ 库、CLI、算法模块、嵌入式配套 | CMake、编译器、ABI、CTest、依赖 |
| `kotlin-spring/` | Kotlin 后端、Spring Boot、Ktor 原型 | 协程、Gradle Kotlin DSL、JPA、测试 |
| `swift-ios/` | iOS 原生 App、SwiftUI、UIKit | Xcode、签名、权限、测试、发布 |
| `ruby-rails/` | Rails Web、后台系统、API-only Rails | MVC、migration、队列、缓存、测试 |
| `r-data-analysis/` | R 数据分析、科研脚本、报表、Shiny | renv、数据、随机种子、报告、可复现 |
| `fpga-vivado-vitis/` | FPGA、Vivado、Vitis、Vitis HLS | HLS、综合、仿真、板卡、脚本 |

## 推荐加载方式

| 项目类型 | 建议加载 |
| --- | --- |
| Java 单体后端 | `project-template/` + `templates/java-springboot/` |
| Java + Vue 前后端 | `project-template/` + `templates/java-springboot/` + `templates/vue/` |
| React 前端 | `project-template/` + `templates/react/` |
| Python API | `project-template/` + `templates/python-fastapi/` |
| Node 后端 | `project-template/` + `templates/node-express/` |
| C# 企业 API / Worker | `project-template/` + `templates/csharp-dotnet/` |
| Go 服务 / CLI | `project-template/` + `templates/go-service/` |
| Laravel 后台 / API | `project-template/` + `templates/php-laravel/` |
| Rust CLI / Service | `project-template/` + `templates/rust-cli-service/` |
| Flutter 跨端 App | `project-template/` + `templates/flutter-dart/` |
| C++ CMake 工程 | `project-template/` + `templates/cpp-cmake/` |
| Kotlin 后端 | `project-template/` + `templates/kotlin-spring/` |
| Swift iOS App | `project-template/` + `templates/swift-ios/` |
| Rails Web / API | `project-template/` + `templates/ruby-rails/` |
| R 数据分析 / Shiny | `project-template/` + `templates/r-data-analysis/` |
| FPGA / HLS 项目 | `project-template/` + `templates/fpga-vivado-vitis/` |

## 脚本加载方式

可以使用根目录脚本初始化：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 `
  -TargetPath "D:\projects\demo" `
  -ProjectName "demo" `
  -Mode Standard
```

初始化时可以不选择技术栈。方案访谈或现有项目扫描确认后，再把技术栈模板复制到目标项目：

```text
.codex/stacks/<stack>/
```

这样 Codex 可以按需读取，不必把所有技术栈规则混入主规则。

## 文件约定

每个技术栈模板尽量包含：

- `README.md`：何时使用该模板。
- `codex-addons.md`：追加到项目 `.codex/` 的规则。
- `commands.md`：该技术栈常用命令示例。
- `checklist.md`：该技术栈开发检查清单。
- `docs-notes.md`：文档编写提示。

复制到具体项目后，可以把这些内容合并进项目的 `.codex/` 和 `docs/`，也可以保留为独立技术栈说明。
