# Go Service 模板

适用于 Go HTTP API、CLI、微服务、网关、后台任务和基础设施工具。

不适用于第一版就处理大型 monorepo、多 `go.work` 工作区或复杂 Cgo/跨平台二进制发布；这些需要单独确认。

## Codex 启动建议

- 推荐启动目录：包含 `go.mod` 的模块根目录。
- 初始化前必须确认：HTTP 服务、CLI、后台任务还是库；是否多模块；依赖和部署方式。
- 优先阅读：`go.mod`、`cmd/`、`internal/`、`pkg/`、`api/`、`config/`、`*_test.go`。
- Ignore guidance / 避免默认读取：`bin/`、`dist/`、`vendor/`、覆盖率文件、生成产物、大日志。

## 符号搜索 / LSP

- 优先使用 gopls 识别接口实现、引用、导入和类型。
- CLI 中按 handler、service、repository、interface、struct、method、route 搜索。
- 常用关键词：`http.Handler`、`context.Context`、`func main`、`cobra.Command`、`sql.DB`、`grpc`、`go test`。
- 修改 goroutine、context、timeout、channel、错误传播前，先查调用链和测试。

## 局部验证

- 修改单个包：运行该包测试。
- 修改公共接口：运行依赖包测试和 `go test ./...`。
- 修改并发、网络或数据库代码：优先补充 timeout/cancel/error 测试。
- `go mod tidy` 会改依赖文件，执行前确认。
