# Java Spring Boot 模板

适用于 Java 后端、Spring Boot、Maven/Gradle、MySQL/Redis/Kafka/MinIO/Elasticsearch 等项目。

仅在项目确实是 Java 后端或 Java 全栈项目时加载。

## Codex 启动建议

- 推荐启动目录：包含 `pom.xml` 或 `build.gradle` 的后端模块根目录。
- 多模块项目先读取根 `pom.xml` / `settings.gradle`，再进入具体业务模块。
- 优先阅读：`src/main/java`、`src/main/resources`、`src/test/java`、数据库 migration、项目 README。
- Ignore guidance / 避免默认读取：`target/`、`build/`、`.idea/`、日志文件、上传文件、生成代码目录。

## 符号搜索 / LSP

- IDEA 项目可借助 IDE 索引确认类、接口、方法调用关系。
- CLI 中优先用类名、接口名、Controller 路由、Service 名、Repository/Mapper 名搜索。
- 常用关键词：`@RestController`、`@RequestMapping`、`@GetMapping`、`@PostMapping`、`@Service`、`@Repository`、`@Transactional`、`Mapper`、`Entity`、`DTO`。
- 修改公共接口、实体、数据库访问或事务边界前，先查调用方和测试。

## 局部验证

- 修改单个类：优先运行对应测试类或模块测试。
- 修改接口：补查 controller/service/repository 链路，并运行相关集成测试。
- 修改配置：运行最小启动或配置加载测试；长期服务启动前确认。
- 修改依赖：先确认网络和权限，再运行依赖解析或模块构建。

本机环境参考：

- JDK：`D:\JAVA\jdk-17`
- Maven：`D:\JetBrains\IntelliJ IDEA 2025.2\plugins\maven\lib\maven3\bin\mvn.cmd`
- Gradle：`D:\gradle\gradle-9.5.1\bin\gradle.bat`
- Java 全栈启动经验：`D:\JAVA-code\simple-auth\项目环境启动指南.md`
- 本地 Ollama / DeepSeek：`D:\Ollama\ollama.exe`，模型 `deepseek-r1:7b`
