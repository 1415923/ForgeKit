# Java Spring Boot 命令示例

按项目实际情况选择，不要机械复制。

## Maven

```powershell
mvn -version
mvn test
mvn -Dtest=ClassNameTest test
mvn -pl module-name test
mvn package
mvn "-Dmaven.repo.local=.m2\repository" test
mvn "-Dmaven.repo.local=.m2\repository" spring-boot:run
```

## Gradle

```powershell
gradle --version
gradle test
gradle test --tests "*ClassNameTest"
gradle :module-name:test
gradle build
gradle bootRun
```

## Local validation / 局部验证优先级

```powershell
mvn -Dtest=ClassNameTest test
mvn -pl module-name -Dtest=ClassNameTest test
mvn -pl module-name package -DskipTests
gradle :module-name:test --tests "*ClassNameTest"
```

## 服务检查

```powershell
Get-Service MySQL95
Get-Service Redis
Test-NetConnection -ComputerName localhost -Port 3306
Test-NetConnection -ComputerName localhost -Port 6379
Test-NetConnection -ComputerName localhost -Port 9092
Test-NetConnection -ComputerName localhost -Port 9200
Test-NetConnection -ComputerName localhost -Port 11434
Test-NetConnection -ComputerName localhost -Port 8081
```

## 注意

- `spring-boot:run`、`bootRun` 属于长期运行服务，执行前确认。
- `mvn dependency:*`、首次构建、依赖下载可能需要网络或升级权限。
- `ollama list` 可用于查看本地模型；`ollama serve` 是长期运行服务，执行前确认。
- 优先运行局部测试；只有跨模块、依赖或发布前变更才运行全量构建。
