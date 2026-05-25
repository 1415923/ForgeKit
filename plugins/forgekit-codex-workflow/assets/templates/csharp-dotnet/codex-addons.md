# C# .NET 项目规则补充

## 代码结构

```text
src/
├─ Api/
├─ Application/
├─ Domain/
├─ Infrastructure/
└─ Worker/
tests/
```

## 开发规则

- 不要强制套用分层；先识别项目已有结构。
- API 边界只处理 HTTP、认证授权、请求响应和错误映射。
- 业务逻辑放 service/application 层或项目已有等价位置。
- 配置通过 options/environment/secret store 注入，不硬编码密钥。
- DI 注册、middleware 顺序、认证授权策略修改前先查启动链路。
- EF Core migration 和数据库脚本必须记录影响范围。

## 测试

- 默认先识别项目使用 xUnit、NUnit 还是 MSTest。
- 核心业务逻辑应有单元测试。
- API 行为用集成测试或最小 endpoint 测试验证。
- 外部服务、数据库和消息队列用 mock、testcontainer 或测试环境前先确认。
