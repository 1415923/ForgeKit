# Java Spring Boot 项目规则补充

## 适用范围

- Spring Boot 后端。
- Java Web API。
- Maven 或 Gradle 构建。
- 常见中间件：MySQL、Redis、Kafka、MinIO、Elasticsearch、Ollama / DeepSeek。

## 代码结构

优先遵循项目已有结构。新项目推荐：

```text
src/main/java/<base-package>/
├─ controller/
├─ service/
├─ service/impl/
├─ repository/ 或 mapper/
├─ entity/ 或 domain/
├─ dto/
├─ config/
├─ security/
├─ exception/
└─ common/
```

## 开发规则

- Controller 只处理 HTTP 边界和参数校验，不堆业务逻辑。
- Service 承载业务流程和事务边界。
- Repository/Mapper 只做数据访问。
- DTO、VO、Entity 不混用，除非项目已有明确约定。
- 配置项使用 `application.yml` 或环境变量，不硬编码密钥。
- 数据库访问使用参数化查询、ORM 或 MyBatis 安全参数绑定。
- 涉及事务时明确事务边界和异常回滚行为。

## 配置与中间件

- 本地开发环境依赖应写入 `.codex/commands.md` 或专项启动文档。
- MySQL、Redis、Kafka、MinIO、Elasticsearch、Ollama / DeepSeek 等长期服务启动前先确认。
- 本地 DeepSeek 模型默认通过 Ollama 使用，例如 `deepseek-r1:7b` 和 `http://localhost:11434/v1`。
- 不在沙盒内反复启动长期服务。
- Maven 本地仓库优先使用项目内 `.m2/repository`，避免用户目录权限问题。

## 测试

- 核心业务逻辑优先写单元测试。
- Controller 建议用 MockMvc 或等价工具验证请求/响应。
- Repository/Mapper 变化需要覆盖 SQL 或数据访问路径。
- 中间件相关逻辑如果无法集成测试，需要写清楚替代验证方式。
