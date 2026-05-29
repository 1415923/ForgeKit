# Hooks 示例

本文记录可选 hook 设计。Opt-in only：默认不启用任何 hook；启用前必须确认权限、噪音、误阻断和维护成本。

新增或升级 hook 前，先阅读 `.codex/automation-decision.md`。Hook 只适合固定、低风险、可解释、可跳过的检查；需要 AI 判断或方案取舍的工作应做成 skill 或保留人工确认。

## Hook 分级

| 等级 | 说明 | 示例 | 默认策略 |
| --- | --- | --- | --- |
| H0 | 只提示，不阻断 | 提醒更新任务看板、版本记录 | 可试用 |
| H1 | 本地只读检查 | 检查文件是否存在、规则是否引用 | 可选 |
| H2 | 本地验证 | lint、typecheck、测试 | 需确认耗时 |
| H3 | 外部系统只读 | 读取 issue、PR、CI 状态 | 需确认网络和凭据 |
| H4 | 外部系统写操作 | 创建 issue、更新 PR、触发部署 | 默认禁用 |

## 推荐 Hook 候选

| 触发点 | 动作 | 目的 | 风险 |
| --- | --- | --- | --- |
| 提交前 | 运行模板自检或项目 lint | 防止明显漂移 | 耗时、误阻断 |
| 会话开始 | 运行 `scripts/run-harness-check.ps1` | 提前发现入口文件缺失 | 小项目可能觉得多余 |
| 初始化后 | 运行 `scripts/detect-local-toolchain.ps1` | 辅助填写本地工具链检查 | 结果可能不完整 |
| 大任务开始前 | 检查 `docs/探索报告.md` 和 `docs/实施计划.md` 是否存在 | 阻止直接大改 | 小任务误判 |
| 发布前 | 检查版本记录、任务状态、测试记录 | 强化 release gate | 规则过严 |
| 安全敏感变更 | 提醒安全审查和依赖审查 | 减少遗漏 | 需要准确识别 |
| 文档修改后 / 提交前 | 运行 `scripts/check-doc-sync.ps1` 或 `scripts/check-doc-sync.sh` | 提醒相关文档、过期描述和版本记录原因 | 可能有噪音，默认只提示 |

## 一键启用

ForgeKit 默认不启用 hook。需要时先用 warning 模式安装 Git hook：

Windows PowerShell：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-hooks.ps1 -Profile docs-warn -Target git
```

Ubuntu / macOS：

```bash
./scripts/install-hooks.sh --profile docs-warn --target git
```

确认噪音可接受后，再切换严格模式：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-hooks.ps1 -Profile docs-strict -Target git
```

```bash
./scripts/install-hooks.sh --profile docs-strict --target git
```

查看状态或卸载：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-hooks.ps1 -Status
powershell -ExecutionPolicy Bypass -File .\scripts\install-hooks.ps1 -Uninstall
```

```bash
./scripts/install-hooks.sh --status
./scripts/install-hooks.sh --uninstall
```

`-Target claude` 和 `-Target codex` 目前只输出说明，不直接改全局配置。不同 CLI 的生命周期 hook 加载规则仍在变化；跨工具最稳的是先使用 Git hook。

## 安全边界

- 不在 hook 中写入凭据。
- 不默认联网。
- 不默认触发部署、push、tag、issue/PR 写操作。
- 长耗时 hook 应可手动跳过，并记录跳过原因。
- hook 失败信息必须说明如何修复，不输出大段日志。

## 示例伪命令

```powershell
# H1: template validation
powershell -ExecutionPolicy Bypass -File .\scripts\validate-template.ps1

# H1: generated project harness check
powershell -ExecutionPolicy Bypass -File .\scripts\run-harness-check.ps1

# H1: local toolchain detection
powershell -ExecutionPolicy Bypass -File .\scripts\detect-local-toolchain.ps1

# H1: document sync check, warn only
powershell -ExecutionPolicy Bypass -File .\scripts\check-doc-sync.ps1

# H1: document sync check, strict mode for opt-in hooks
powershell -ExecutionPolicy Bypass -File .\scripts\check-doc-sync.ps1 -Strict

# H1: document sync check on Ubuntu / macOS, warn only
./scripts/check-doc-sync.sh

# H1: document sync check on Ubuntu / macOS, strict mode for opt-in hooks
./scripts/check-doc-sync.sh --strict

# H2: project test placeholder
# Replace with project-specific test command in .codex/commands.md
```

## 手动 Git Hook 示例

通常不需要手写，优先使用 `scripts/install-hooks.*`。如果需要手动安装，可以参考下面内容。

Windows PowerShell 项目：

```powershell
New-Item -ItemType Directory -Force .git\hooks
@'
powershell -ExecutionPolicy Bypass -File .\scripts\check-doc-sync.ps1
exit 0
'@ | Set-Content .git\hooks\pre-commit -Encoding ASCII
```

Ubuntu / macOS 项目：

```bash
mkdir -p .git/hooks
cat > .git/hooks/pre-commit <<'EOF'
#!/usr/bin/env bash
./scripts/check-doc-sync.sh
exit 0
EOF
chmod +x .git/hooks/pre-commit
```

确认噪音可接受后，再把命令改为 `-Strict` 或 `--strict`。
