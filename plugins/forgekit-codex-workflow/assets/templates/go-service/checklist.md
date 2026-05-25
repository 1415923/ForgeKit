# Go Service 检查清单

- [ ] 已确认项目类型：HTTP、CLI、后台任务或库。
- [ ] 包边界清楚，没有强行过度分层。
- [ ] context、timeout、cancel 和错误传播已检查。
- [ ] goroutine、channel、共享状态没有明显泄漏或竞态。
- [ ] `go.mod` / `go.sum` 变更已确认。
- [ ] 核心包有测试或替代验证。
- [ ] 构建、部署、配置和运行参数已同步文档。
