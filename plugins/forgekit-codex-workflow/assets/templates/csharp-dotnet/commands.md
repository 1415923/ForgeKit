# C# .NET 命令示例

```powershell
dotnet --info
dotnet restore
dotnet build
dotnet test
dotnet format --verify-no-changes
```

## Local validation / 局部验证优先级

```powershell
dotnet test
dotnet build
dotnet format --verify-no-changes
```

注意：

- `dotnet restore` 会联网下载依赖，先确认。
- EF Core `database update`、migration apply、seed 会改数据库，必须先确认目标环境。
- `dotnet run`、Worker Service、Windows 服务是长期运行进程，先确认。
- 发布、容器镜像、IIS/Windows Service 安装属于外部动作，执行前确认。
