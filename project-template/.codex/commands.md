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

## 文档健康报告

只生成或覆盖 `.forgekit/doc-health-report.md`，用于汇总 managed docs 是否过长、重复、职责错位或违反 workflow-router 边界。它是 report-only，不自动瘦身、不归档、不修改 current docs 或 business docs。

```powershell
python .\scripts\doc-health-report.py --project-root .
```

```bash
python3 ./scripts/doc-health-report.py --project-root .
```

## 来源追溯报告

只生成或覆盖 `.forgekit/source-trace-report.md`，用于检查“原始来源 -> 需求事实 -> 任务拆解 -> change/实现 -> 验证记录 -> work-log/changelog 状态”的链路是否断裂。它是 report-only，不自动补 Source ID、不修改 task-intake / requirements / task-board / work-log / changelog。

```powershell
python .\scripts\source-trace-report.py --project-root .
```

```bash
python3 ./scripts/source-trace-report.py --project-root .
```

## Review-Ready Handoff Package

只生成或覆盖 `.forgekit/handoff-package.md`，用于把阶段成果整理成给领导、reviewer 或测试可读的交付包。它是 report-only，不自动修复 doc-health/source-trace 问题，不修改 current docs、business docs、任务状态、Git、PR 或 worktree。

```powershell
python .\scripts\handoff-package.py --project-root .
```

```bash
python3 ./scripts/handoff-package.py --project-root .
```

按单个 change 生成时，只写 `.forgekit/changes/<change-id>/handoff.md`：

```powershell
python .\scripts\handoff-package.py --project-root . --change-id <change-id>
```

```bash
python3 ./scripts/handoff-package.py --project-root . --change-id <change-id>
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

Smart apply 只读取 `.forgekit/smart-archive-report.md` 中 `Smart-Status: auto_archive_candidate` 的条目。必须显式确认，且工作区除 smart report 本身外不干净时会拒绝执行；它只移动 `.forgekit/changes/<change-id>` 到 `.forgekit/archive/changes/YYYY/<change-id>`，并把归档后 `proposal.md` 的 `Status: done` 改为 `Status: archived`。

```powershell
python .\scripts\archive-changes.py --smart-apply --report .forgekit/smart-archive-report.md --confirm
```

```bash
python3 ./scripts/archive-changes.py --smart-apply --report .forgekit/smart-archive-report.md --confirm
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
