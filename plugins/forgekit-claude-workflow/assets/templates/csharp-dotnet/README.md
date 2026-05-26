# C# .NET 模板

适用于 ASP.NET Core API、企业后端、Worker Service、Windows 服务和内部工具。

不适用于第一版就处理 MAUI、Unity、复杂桌面客户端或大型遗留 .NET Framework 迁移；这些项目需要单独确认运行时和发布方式。

## Codex 启动建议

- 推荐启动目录：包含 `.sln`、`.csproj` 或 `global.json` 的解决方案/项目根目录。
- 初始化前必须确认：API 还是 Worker/服务；Minimal APIs 还是 Controller；数据库和 ORM；目标 .NET SDK；测试框架。
- 优先阅读：`*.sln`、`*.csproj`、`Program.cs`、`appsettings*.json`、`Controllers/`、`Services/`、`Data/`、`Tests/`。
- Ignore guidance / 避免默认读取：`bin/`、`obj/`、`.vs/`、日志、发布产物、用户上传文件。

## 符号搜索 / LSP

- 优先借助 Visual Studio、Rider、C# Dev Kit 或 OmniSharp 的索引确认引用。
- CLI 中按 Controller、endpoint、service、interface、DbContext、migration、options class 搜索。
- 常用关键词：`MapGet`、`MapPost`、`ControllerBase`、`IServiceCollection`、`DbContext`、`IOptions`、`BackgroundService`、`ILogger`。
- 修改 public API、DI 注册、EF Core migration、配置绑定或认证授权前，先查调用方和测试。

## 局部验证

- 修改业务逻辑：优先运行相关测试项目或过滤测试。
- 修改 API：运行 controller/minimal API 测试，检查 OpenAPI/路由变化。
- 修改 EF Core migration：先确认数据库环境，优先使用 dry-run/script。
- 修改依赖：先确认网络和 NuGet 源，再运行 restore/build。
