# Stage C Checker Consumer Audit

审计日期：2026-08-24
范围：Stage C 修改 checker 前的活动 v0.45 runtime、模板投影、smoke 断言与 validator。

## Current-doc checker consumers

- `scripts/archive-capsule.py` 及其相同的模板副本使用 `--json` 执行 checker。它们把命令退出码 `2` 视为 checker runtime failure，读取 `status`、`active_tasks`、`blocking_count`、`warning_count` 和 `findings[].severity/code/message`，并以 `blocking_count` 控制 archive apply/postflight。
- `scripts/forgekit-project.py` 原先不带 `--json` 执行 checker，在统一入口输出中保留 checker stdout，并按返回码 `1`、`2` 给出提示；它不读取 finding 字段。Stage C 将该入口改为读取 additive canonical 字段，同时保留 checker 人类可读 stdout 与旧聚合字段。
- `scripts/smoke-test.py` 读取命令返回码及人类可读 stdout 中的 `Status`、`Active tasks` 和 finding code，也覆盖 archive-capsule 的旧 JSON consumer 路径。
- `scripts/validate-template.ps1` 检查 root/template 字节一致性、脚本存在性与源码标记，不在 runtime 读取 checker JSON。
- `project-template/scripts/check-current-docs-integrity.py` 是生成项目投影。历史 migration 副本仅作为兼容性证据，不是 Stage C runtime 修改目标。

## Workspace checker consumers

- 活动仓库脚本中没有发现读取 workspace checker JSON 的 parser；公开的 `--json` 接口仍是必须保持的兼容面。
- `scripts/smoke-test.py` 读取返回码及 `passed`、`warning`、`blocking`、`not-enabled` 等 stdout 标记，也检查 finding code、`WorkspaceRoot`、strict 行为和 `--require-enabled`。
- `scripts/bootstrap-project-capsule.py` 只把 checker 命令作为下一步提示输出，不读取其结果。
- `scripts/validate-template.ps1` 检查 root/template 字节一致性、CLI/源码标记和脚本存在性。
- `project-template/scripts/check-workspace-integrity.py` 是生成项目投影。历史 migration/baseline 副本在 Stage C 保持不变。

## Compatibility boundary

- current-doc 顶层继续保留 `status`、`mode`、`repo_root`、`active_tasks`、`blocking_count`、`warning_count`、`findings` 和 restoration guidance。
- workspace 继续保留 `status`、`workspace_root`、`summary`、`adoption_guidance`、finding `path`、`not-enabled`、`runtime-error` 以及既有 status/code/stdout 标记。
- finding 的 `severity=blocking|warning` 只作为旧 disposition 保留。新增的 canonical gate authority 是 `blocking`；`blocking_count` 从 `blocking=true` 计算，`warning_count` 统计 non-blocking findings。
- strict 命令失败以及 checker input/runtime failure 都不得把某个 project finding 改写成 `blocking=true`。

## Legacy loop filename guard

四个活动 runtime 命中位于 root/template 两份 `check-workspace-integrity.py` 和两份 `bootstrap-project-capsule.py`。每处 `loop-operations.md` 都只存在于 forbidden capsule filename set，用于拒绝 legacy full-protocol 文件副本；这些代码不会读取、路由、安装该文档，也不把它当作 semantic owner。因此保留这些 guard，继续保护旧项目。
