# 项目命令

记录本项目常用命令。Codex 执行命令前应优先查看本文件。

## 环境准备

```powershell
# 待补充
```

环境地址、依赖服务、配置来源和权限边界记录在 `.forgekit/docs/environment-matrix.md`。

## 安装依赖

```powershell
# 待补充
```

## 本地开发

```powershell
# 待补充
```

## 测试

```powershell
# 待补充
```

## 构建

```powershell
# 待补充
```

## 格式化与静态检查

```powershell
# 待补充
```

## Codex Harness 检查

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-harness-check.ps1
```

## 本地工具链检测

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\detect-local-toolchain.ps1
```

## 文档同步检查

Windows PowerShell：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check-doc-sync.ps1
```

Ubuntu / macOS：

```bash
./scripts/check-doc-sync.sh
```

默认只提示不阻断；如果团队确认要作为 hook 阻断，可使用：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check-doc-sync.ps1 -Strict
```

```bash
./scripts/check-doc-sync.sh --strict
```

## 安装可选 Hooks

Windows PowerShell：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-hooks.ps1 -Profile docs-warn -Target git
```

Ubuntu / macOS：

```bash
./scripts/install-hooks.sh --profile docs-warn --target git
```

查看状态：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-hooks.ps1 -Status
```

```bash
./scripts/install-hooks.sh --status
```

卸载：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-hooks.ps1 -Uninstall
```

```bash
./scripts/install-hooks.sh --uninstall
```

## 数据库迁移

```powershell
# 待补充
```

## 部署

```powershell
# 待补充
```

部署命令默认需要用户确认后再执行。
发布流水线、制品、验证和回滚步骤记录在 `.forgekit/docs/release-pipeline.md`。
