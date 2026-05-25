# Kotlin Spring 命令示例

```powershell
java -version
gradle --version
./gradlew test
./gradlew build
mvn test
mvn package
```

## Local validation / 局部验证优先级

```powershell
./gradlew test
./gradlew build
mvn test
```

注意：

- `./gradlew build`、`mvn package` 会解析依赖，先确认网络和仓库源。
- 数据库 migration、seed、真实服务启动和部署前必须确认。
- 协程 dispatcher、线程池、连接池和事务边界变化需要额外验证。
- 不默认安装 JDK、Gradle、Maven 或修改全局配置。
