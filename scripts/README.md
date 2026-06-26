# 脚本

## init-project-template.ps1

把 `project-template/` 初始化到目标项目目录，复制项目初始化问答表，并按需复制技术栈模板到目标项目的 `.codex/stacks/`。

推荐一条命令完成初始化和 Native Agent Adapter 生成：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 `
  -TargetPath "D:\projects\demo-api-workspace" `
  -ProjectName "demo-api" `
  -NativeAgentAdapter all
```

`TargetPath` 是外层 ForgeKit 治理工作空间；`ProjectName` 会创建同名内层代码目录。业务源码和 Git 仓库放在内层，ForgeKit 文档和 AI 配置留在外层。

## upgrade-forgekit.ps1 / upgrade-forgekit.sh

对已有项目执行 guided upgrade。它只生成 `.forgekit/upgrade/upgrade-plan.md`、`.forgekit/upgrade/upgrade-actions.md`、`.forgekit/upgrade/upgrade-inventory.json` 和候选模板，不覆盖项目文件。

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\upgrade-forgekit.ps1 -ProjectPath "D:\projects\demo-api"
```

```bash
./scripts/upgrade-forgekit.sh --project-path "$HOME/projects/demo-api"
```

## generate-native-agent-adapter.ps1 / .sh / .py

兼容入口：单独生成 Native Agent Adapter 配置模板。新项目不推荐走这条旧路径，优先用 `init-project-template.ps1 -NativeAgentAdapter all` 一次完成。该脚本只写入 Claude Code / Codex 可审查配置，不启动 agent、不执行 loop、不创建 worktree、不 merge、commit、push 或 PR。

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\generate-native-agent-adapter.ps1 -Target all -ProjectRoot "D:\projects\demo-api" -DryRun
```

```bash
python3 scripts/generate-native-agent-adapter.py --target codex --project-root ./demo --dry-run
```

## check-codex-native-agents.py

只读检查 Codex native agent 配置和运行时观测证据，输出 `.forgekit/codex-native-agent-report.md`。`SchemaStatus: pass` 只说明 `.codex/agents/*.toml` 和 `.codex/config.toml` 结构齐全，不代表 Codex runtime 已注册；只有显式观察到 `forgekit-*` 被调用，才能记录为 native 可用。

```powershell
python scripts\check-codex-native-agents.py --repo-root . --observed-agent default,explorer,worker
```

## validate-template.ps1

检查模板结构、治理文档、技术栈模板、项目级 skills 和常见文档漂移。

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-template.ps1
```

如果本机没有 skill 校验脚本，可以跳过外部 skill 校验：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-template.ps1 -SkipSkillValidation
```

### 示例

Java 后端：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 `
  -TargetPath "D:\projects\demo-api" `
  -ProjectName "demo-api" `
  -Stacks java-springboot
```

Java + Vue：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 `
  -TargetPath "D:\projects\demo-fullstack" `
  -ProjectName "demo-fullstack" `
  -Stacks java-springboot,vue
```

FPGA：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 `
  -TargetPath "D:\projects\fpga-demo" `
  -ProjectName "fpga-demo" `
  -Stacks fpga-vivado-vitis
```

### 参数

| 参数 | 必填 | 说明 |
| --- | --- | --- |
| `TargetPath` | 是 | 外层 ForgeKit 治理工作空间 |
| `ProjectName` | 否 | 项目名；填写后会创建同名内层代码目录，并写入 boundary 的 `project_root` |
| `Stacks` | 否 | 技术栈模板列表，支持 `java-springboot,vue` 形式 |
| `NativeAgentAdapter` | 否 | 初始化时生成原生 agent 配置模板：`none`、`claude-code`、`codex`、`all`；默认 `none` |
| `Upgrade` | 否 | 兼容旧升级入口；新项目升级优先使用 `upgrade-forgekit.ps1` / `.sh` |
| `ExportUpgradeTemplates` | 否 | 兼容参数；guided upgrade 会导出候选模板到 `.forgekit/upgrade/candidates/<version>/` |
| `Force` | 否 | 覆盖已有文件；默认不覆盖 |

### 安全策略

- 默认不覆盖已有文件。
- 升级旧项目时优先使用 `upgrade-forgekit.ps1` / `.sh`，不要使用 `-Force`。
- guided upgrade 会进入 `.forgekit/upgrade/`，不会自动覆盖、合并、迁移、写 lock 或提交。
- `.codex/init.generated.md` 和 `.claude/init.generated.md` 已存在时默认跳过，避免覆盖旧项目初始化记录。
- 问答表复制到 `.codex/questionnaires/init-questionnaire.md`。
- 技术栈模板复制到 `.codex/stacks/<stack>/`，不会自动混入全局规则。
- 复制后需要人工或 Codex 根据项目情况把必要内容合并到 `.codex/commands.md`、`.codex/style.md` 等文件。
