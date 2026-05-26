# Python FastAPI 项目规则补充

## 代码结构

```text
app/
├─ api/
├─ core/
├─ models/
├─ schemas/
├─ services/
├─ repositories/
└─ tests/
```

## 开发规则

- API 路由只处理 HTTP 边界。
- Pydantic schema 用于请求和响应结构。
- 业务逻辑放 service。
- 数据访问放 repository。
- 配置通过环境变量或配置文件注入，不硬编码密钥。
- 异步代码注意阻塞调用和连接池。

## 测试

- 核心业务逻辑使用 pytest。
- API 可使用 TestClient 或 httpx。
- 数据库和外部服务需要 mock 或测试容器时先确认环境。
