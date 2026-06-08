# 脚本

## init-project-template.ps1

把 `project-template/` 初始化到目标项目目录，复制项目初始化问答表，并按需复制技术栈模板到目标项目的 `.codex/stacks/`。

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
| `TargetPath` | 是 | 目标项目目录 |
| `ProjectName` | 否 | 写入 `.codex/project.md` 的项目名 |
| `Stacks` | 否 | 技术栈模板列表，支持 `java-springboot,vue` 形式 |
| `Upgrade` | 否 | 安全升级已有项目；补缺失文件并生成 `.codex/upgrade-report.md` |
| `ExportUpgradeTemplates` | 否 | 升级时把新版模板副本导出到 `.codex/upgrade-templates/` 供 diff/合并 |
| `Force` | 否 | 覆盖已有文件；默认不覆盖 |

### 安全策略

- 默认不覆盖已有文件。
- 升级旧项目时使用 `-Upgrade`，不要使用 `-Force`。
- 已有文件如果和新版模板不同，会进入 `.codex/upgrade-report.md`，不会自动覆盖。
- 需要查看新版模板内容时，加 `-ExportUpgradeTemplates`。
- `.codex/init.generated.md` 和 `.claude/init.generated.md` 已存在时默认跳过，避免覆盖旧项目初始化记录。
- 问答表复制到 `.codex/questionnaires/init-questionnaire.md`。
- 技术栈模板复制到 `.codex/stacks/<stack>/`，不会自动混入全局规则。
- 复制后需要人工或 Codex 根据项目情况把必要内容合并到 `.codex/commands.md`、`.codex/style.md` 等文件。
