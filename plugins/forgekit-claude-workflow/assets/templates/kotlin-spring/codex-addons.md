# Kotlin Spring 项目规则补充

## 代码结构

```text
src/main/kotlin/
src/main/resources/
src/test/kotlin/
```

## 开发规则

- 先区分 Spring Boot Kotlin 和 Ktor，不把两套架构混用。
- Kotlin nullability、data class、sealed class 和 Java interop 变化要谨慎。
- JPA entity 不一定适合普通 `data class`，先看项目约定。
- 协程必须明确 dispatcher、scope、timeout、cancel 和异常传播。
- Gradle Kotlin DSL 与 Maven 项目分开处理，不自动迁移构建系统。

## 测试

- 默认先识别 JUnit、Kotest、MockK、Spring Boot Test 等实际方案。
- 核心业务逻辑需要单元测试或替代验证。
- Web、数据库、协程和事务路径优先补集成测试。
