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

## 归档计划 Dry Run

只生成或覆盖 `.forgekit/archive-plan.md`，不移动文件、不改状态、不改链接、不写 current docs、不写 business docs、不改 lock、不提交。

```powershell
python .\scripts\archive-changes.py --dry-run
```

```bash
python3 ./scripts/archive-changes.py --dry-run
```

Reference check 只读取 dry-run plan 中的候选项，生成 `.forgekit/archive-reference-report.md`，不移动、不改链接。

```powershell
python .\scripts\archive-changes.py --reference-check --plan .forgekit/archive-plan.md
```

```bash
python3 ./scripts/archive-changes.py --reference-check --plan .forgekit/archive-plan.md
```

Sync check 只读取 dry-run plan 中的候选项，检查 `review.md` 中的结构化同步字段，生成 `.forgekit/current-docs-sync-report.md`，不修改 current docs、business docs、archive plan、template-lock，也不移动文件。

```powershell
python .\scripts\archive-changes.py --sync-check --plan .forgekit/archive-plan.md
```

```bash
python3 ./scripts/archive-changes.py --sync-check --plan .forgekit/archive-plan.md
```

Smart check 只综合 dry-run plan、reference report 和 sync report 的机器字段，生成 `.forgekit/smart-archive-report.md`，不移动、不改链接、不改 current docs、不改 business docs、不改 lock。

```powershell
python .\scripts\archive-changes.py --smart-check --plan .forgekit/archive-plan.md --reference-report .forgekit/archive-reference-report.md --sync-report .forgekit/current-docs-sync-report.md
```

```bash
python3 ./scripts/archive-changes.py --smart-check --plan .forgekit/archive-plan.md --reference-report .forgekit/archive-reference-report.md --sync-report .forgekit/current-docs-sync-report.md
```

Apply 需要先人工 review plan，并且必须显式确认。工作区除 `.forgekit/archive-plan.md` 外不干净时会拒绝执行。

```powershell
python .\scripts\archive-changes.py --apply --plan .forgekit/archive-plan.md --confirm
```

```bash
python3 ./scripts/archive-changes.py --apply --plan .forgekit/archive-plan.md --confirm
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
