# Node Express 项目规则补充

## 代码结构

```text
src/
├─ routes/
├─ controllers/
├─ services/
├─ repositories/
├─ middlewares/
├─ schemas/
└─ utils/
```

## 开发规则

- Route 只定义路径和中间件组合。
- Controller 处理请求边界。
- Service 处理业务逻辑。
- Repository 处理数据访问。
- 输入校验使用项目已有 schema 工具。
- 错误处理中间件统一返回错误结构。
- 配置和密钥使用环境变量。

## 测试

- 业务逻辑使用单元测试。
- API 使用 supertest 或项目已有工具。
- 鉴权、权限、输入校验需要覆盖异常路径。
