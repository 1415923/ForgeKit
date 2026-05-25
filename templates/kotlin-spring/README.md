# Kotlin Spring 模板

适用于 Kotlin 后端、Spring Boot Kotlin、Ktor 原型服务和 JVM 后端模块。

不适用于第一版就混合 Android、Compose Multiplatform 或复杂 Java 迁移；这些需要单独确认模块边界和运行时。

## Codex 启动建议

- 推荐启动目录：包含 `build.gradle.kts`、`pom.xml` 或 `settings.gradle.kts` 的模块/项目根目录。
- 初始化前必须确认：Spring Boot Kotlin 还是 Ktor；Gradle Kotlin DSL 还是 Maven；是否使用协程；数据库和测试框架。
- 优先阅读：`build.gradle.kts`、`pom.xml`、`src/main/kotlin`、`src/main/resources`、`src/test/kotlin`、migration。
- Ignore guidance / 避免默认读取：`build/`、`target/`、`.gradle/`、`.idea/`、日志、生成代码。

## 符号搜索 / LSP

- 优先使用 IntelliJ IDEA / Kotlin LSP 识别引用、nullability、协程和 Java 互操作问题。
- CLI 中按 controller、route、service、repository、configuration、entity、data class 搜索。
- 常用关键词：`@SpringBootApplication`、`@RestController`、`suspend`、`CoroutineScope`、`Dispatcher`、`data class`、`JpaRepository`、`Ktor`。
- 修改协程、事务、JPA entity、nullability 或 Java interop 前，先查调用方和测试。

## 局部验证

- 修改业务逻辑：运行相关 Gradle/Maven 测试。
- 修改协程或异步路径：确认 dispatcher、scope、timeout、cancel 和结构化并发。
- 修改 JPA entity 或 migration：先确认数据库环境。
- 修改构建脚本：先确认 Gradle/Maven 版本和网络依赖。
