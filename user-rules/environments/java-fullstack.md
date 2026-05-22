# 用户级环境补充：Java 全栈

仅在 Java / Spring Boot / Vue / 中间件项目中读取。

## 参考文档

- `D:\JAVA-code\simple-auth\项目环境启动指南.md`

## 常见服务与端口

| 服务 | 端口 | 启动/检查方式 | 备注 |
| --- | --- | --- | --- |
| MySQL | 3306 | Windows 服务 `MySQL95` | 当前服务存在且可自动启动 |
| Redis | 6379 | Windows 服务 `Redis` 或 `D:\Redis\redis-server.exe` | 注意 `redis-cli` 只是客户端 |
| MinIO API | 9090 | `D:\minio_server_data\bin\minio.exe` | 推荐正常本机权限启动 |
| MinIO Console | 9000 | 同上 | 控制台地址通常是 `http://127.0.0.1:9000` |
| Kafka | 9092 | simple-auth 项目脚本 `scripts\start-kafka-kraft.bat` | KRaft 推荐方式 |
| Kafka Controller | 9093 | KRaft 模式 | 开发环境使用 |
| Elasticsearch | 9200 | `D:\elasticsearch-8.10.0\bin\elasticsearch.bat` | 需要常驻运行 |
| Ollama / DeepSeek | 11434 | `ollama serve` | 本地模型服务；已发现模型 `deepseek-r1:7b` |
| Spring Boot 示例后端 | 8081 | Maven 启动 | 具体项目以配置为准 |
| Vite 示例前端 | 5173 | `npm run dev` | 具体项目以配置为准 |

## 使用规则

- 长期服务启动前先确认。
- Maven 本地仓库优先使用项目内 `.m2/repository`。
- simple-auth 类项目优先参考专项启动指南，不凭记忆启动中间件。
- 本地 DeepSeek 走 Ollama 时通常不需要 API key；如果切到 DeepSeek 官方 API，再设置 `DEEPSEEK_API_KEY`。
