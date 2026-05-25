# Go Service 项目规则补充

## 代码结构

```text
cmd/
internal/
pkg/
api/
configs/
tests/
```

## 开发规则

- 不要把 Java 式分层强套到 Go；先尊重现有包边界。
- `internal/` 有可见性语义，不当作普通目录。
- 所有外部请求、数据库访问和 goroutine 应有 context、timeout 或取消路径。
- 错误必须显式处理，避免忽略返回值。
- 公共包 API 要保持小而稳定，避免泄漏内部实现。

## 测试

- 基线使用标准库 `go test`。
- 表驱动测试适合核心业务和解析逻辑。
- 并发代码、全局状态、缓存和网络路径优先考虑 race test。
- 外部服务和数据库测试前确认环境或使用替身。
