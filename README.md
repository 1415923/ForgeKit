# ForgeKit

English documentation: [README.en.md](README.en.md)

ForgeKit 是一套轻量级 AI 工程交付工具包，用来把 Codex、Claude Code 等 AI 编程工具约束在可审查、可验证、可交接的项目流程里。

它不生成业务框架代码，也不替你部署系统。ForgeKit 只在项目本地生成一层“AI 交付工作区”：入口文件、项目边界、共享 skills、风险分级 change 工件、治理文档、检查脚本和可选 agent 配置模板。

## 为什么需要 ForgeKit

AI 写代码越来越快，但项目真正容易失控的地方通常不是“能不能写”，而是：

- AI 不知道项目边界，误改业务仓库或旧文档。
- 需求、任务、实现、验证和交接记录断链。
- 中高风险变更缺少 proposal、tasks、verification、review。
- Codex、Claude Code 等工具各读各的上下文，事实不一致。
- 代码做完了，但没人能快速确认“改了什么、怎么验证、还有什么风险”。

ForgeKit 的目标就是把这些交付约束固定到项目里，让 AI 能在同一个可检查流程下推进工作。

## 适合与不适合

适合：

- 新项目启动：先澄清目标、边界、技术栈和验证方式，再让 AI 写代码。
- 接手已有项目：先从 README、脚本、构建文件和旧文档中提取事实，而不是先猜技术栈。
- 中高风险变更：要求 proposal / tasks / verification / review，必要时增加 design / ship / retro。
- 多 AI 工具协作：让 Codex、Claude Code 共用同一套项目事实、命令、skills 和交付规则。

不适合：

- 作为业务框架脚手架。
- 自动安装依赖、启动服务、部署或发布。
- 默认启用 hook、MCP、memory、多 agent runtime 或外部账号集成。
- 自动创建 issue / PR、commit、tag 或 push。

## 快速开始

### 1. 生成项目工作区

推荐统一入口。它会自动判断目标目录应初始化、无需更新、生成升级计划，还是进入 legacy adoption：

```powershell
python .\scripts\forgekit-project.py --target "D:\projects\my-app-workspace"
```

默认确认是 No；非交互环境只展示计划，显式 `--yes` 才执行初始化或 `apply --safe`。未安装但非空的目录需要额外使用 `--force-init`，已有文件仍不会被覆盖。

需要显式选择 Mode、stack 或 Native Agent Adapter 时，可以使用底层初始化入口：

Windows PowerShell：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 -TargetPath "D:\projects\my-app-workspace" -ProjectName "my-app" -Mode Standard -NativeAgentAdapter all
```

Ubuntu / macOS：

```bash
./scripts/init-project-template.sh --target-path "$HOME/projects/my-app-workspace" --project-name "my-app" --mode Standard --native-agent-adapter all
```

生成后的目录是内外两层：

```text
my-app-workspace/        # 外层：ForgeKit 治理、AI 入口、.forgekit、.codex、scripts
  my-app/                # 内层：真实业务代码和 Git 仓库
```

如果已有业务代码，把整个业务项目放进内层 `my-app/`。如果是新项目，源码、测试、业务 README 和构建文件也都放在内层。

只在内层 `my-app/` 初始化 Git、commit 和 push，避免把外层 ForgeKit 治理文档和配置推送到业务仓库。

### 2. 在外层启动 AI 工具

Codex：

```powershell
cd D:\projects\my-app-workspace
codex
```

Claude Code：

```powershell
cd D:\projects\my-app-workspace
claude
```

### 3. 发送启动消息

Codex：

```text
请读取 AGENTS.md，并优先使用项目内 .agents/skills/project-init/SKILL.md，按 ForgeKit 流程帮我初始化这个项目。不要读取用户级或系统级 project-init 路径。
```

Claude Code：

```text
请读取 CLAUDE.md，并优先使用项目内 .agents/skills/project-init/SKILL.md，按 ForgeKit 流程帮我初始化这个项目。不要读取用户级或系统级 project-init 路径。
```

`-NativeAgentAdapter all` 只生成 Claude Code / Codex 可审查的原生 agent 配置模板，不代表 runtime 已经注册成功。首次真实使用时，仍要按 `.forgekit/docs/native-agent-adapter.md` 验证是否确实调用到 `forgekit-*` agent。

## 升级已有 ForgeKit 项目

推荐仍使用统一入口：

```bash
python scripts/forgekit-project.py --target <project-root>
```

它会先展示 ProjectRoot、已安装版本、工具版本和检测动作。版本落后时自动调用 check + plan，只有交互输入 `y/yes` 或显式 `--yes` 才调用 `apply --safe`。

v0.36.0 起，新项目使用 Versioned Migration Upgrade Model；以下命令保留为高级入口：

```bash
python scripts/forgekit-upgrade.py check --repo-root <project>
python scripts/forgekit-upgrade.py plan --repo-root <project>
python scripts/forgekit-upgrade.py apply --safe --repo-root <project>
```

- `check`：检查 `.forgekit/state.json` 和迁移资格，不写文件。
- `plan`：输出一屏可读的迁移计划，不写文件。
- `apply --safe`：只执行 migration 中明确标记为 safe 的动作；不做三方 merge，不改 business docs，不自动提交。

升级如果更新了 AGENTS / CLAUDE / rules、skills 或 agents，当前会话只用于 checkpoint 和收口；新任务请新开会话或重启工具，不要假设磁盘文件更新后旧会话会自动重载。

只有 v0.36.0 及以后初始化、且具有 `.forgekit/state.json` 的项目支持该模型。v0.35.x 及更早项目应按“接手既有项目”处理：先盘点当前事实，再由用户确认 adoption 边界。

## 项目维护

v0.39.0 增加 Project Maintenance Operations 和 Unified Project Bootstrap。安装、初始化、更新或同步优先使用 `forgekit-project.py` 自动分流；其他维护动作按 `intent -> plan -> confirm/apply -> summary/index` 推进。

## 第一性原理与对抗式审查

v0.40.0 增加两个按风险触发的审查协议：复杂问题先从事实、假设和约束推导最小正确机制；高风险变更收口前主动寻找失败路径。它们不强制用于 typo 或低风险小改动，也不替代独立代码审查。

常用说法：

```text
从第一性原理出发，重新分析这个 bug 的根因。
对这个功能做一次对抗式审查，专门找失败路径。
```

```text
我更新了外层 ForgeKit，帮这个项目同步一下。
这个阶段结束了，帮我归档成 capsule。
帮我生成维护计划，不要直接 apply。
```

升级同步复用上面的 `forgekit-upgrade.py check / plan / apply --safe`。阶段归档使用 `scripts/archive-capsule.py plan`，确认后才运行 `apply --confirm`；归档不是删除，apply 会生成 capsule summary、items log 和 `.forgekit/archive/index.md`，不会整理旧 archive 或修改 business docs。

## 工作流

ForgeKit 推荐把项目推进拆成一条可追溯链路：

```text
source -> task -> change -> verification -> review -> work-log / changelog / handoff
```

日常使用时通常按这个顺序：

1. 把需求、反馈、bug、技术债或调研发现先记到 `.forgekit/docs/task-intake.md`。
2. 只有可执行任务才进入 `.forgekit/docs/task-board.md`。
3. 根据风险创建 `.forgekit/changes/<change-id>/` 下的变更工件。
4. 实现后记录验证结果。
5. 代码变更使用 Independent Code Review Protocol，区分 Maker 与独立只读 Reviewer。
6. 在阶段边界、上下文压缩/清空前、子 agent 返回关键结论后做最小 Context Checkpoint。
7. 更新 work-log、changelog 或 handoff，方便中断恢复和交接。

风险分级对应的建议工件：

| 风险 | 建议工件 |
| --- | --- |
| low | proposal / verification / review |
| medium | proposal / tasks / verification / review |
| high | proposal / design / tasks / verification / review / ship |

`retro` 只在重大变更、事故、失败交付或团队明确要求时使用。

## 生成内容概览

| 路径 | 用途 |
| --- | --- |
| `AGENTS.md` | Codex 项目入口 |
| `CLAUDE.md` | Claude Code 项目入口 |
| `.agents/skills/` | 项目自包含 skills |
| `.forgekit/project-boundary.yml` | ForgeKitRoot、ProjectRoot、managed docs root、change root 和写入策略 |
| `.forgekit/docs/` | 管理文档：项目事实、任务、验证、交接、工具链等 |
| `.forgekit/changes/` | 中高风险变更的 proposal / design / tasks / verification / review 等工件 |
| `.codex/` | Codex 项目命令、version gates、可选 agent 配置 |
| `governance/` | AI Engineering Loop 等治理说明 |
| `scripts/` | 初始化、检查、升级、归档和 hook 安装脚本 |

业务已有 `docs/` 默认是 read-mostly 证据源。AI 可以读取和引用，但不应默认把 ForgeKit 治理模板写入业务 docs。

## 核心能力

| 能力 | 作用 |
| --- | --- |
| Boundary-first workspace | 明确外层治理目录和内层业务仓库，降低误写风险 |
| Source-first task intake | 先记录来源，再判断是否形成可执行任务 |
| Risk-based change artifacts | 按风险控制 proposal、tasks、verification、review、design、ship 的数量 |
| Managed docs responsibility | 规定每类文档什么时候读、写什么、不写什么 |
| Report-only checks | 生成 doc-health、source-trace、handoff 等报告，不自动修复或提交 |
| Native Agent Adapter | 可选生成 Codex / Claude Code 原生 agent 配置模板 |
| Independent Code Review Protocol | 独立只读 reviewer、最小上下文包和 pass / needs-fix / manual-review gate |
| Context Continuity Protocol | 把关键结论 checkpoint 到正确文档，避免长会话、压缩、清空或委派后丢失工程状态 |
| Project Maintenance Operations | 将 upgrade sync、Archive Capsule、checkpoint、handoff 和报告路由到先计划、后确认、再总结的维护流程 |

## 常用命令

模板仓库检查：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-template.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\validate-plugin-assets.ps1
```

```bash
bash scripts/smoke-test.sh
python3 scripts/update-template-manifest.py --check --repo-root .
```

生成项目内检查：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-harness-check.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\check-doc-sync.ps1
```

```bash
./scripts/check-doc-sync.sh
```

这些脚本只做检查、复制模板或安装本地 opt-in hook；不会自动安装依赖、启动服务、部署、commit、tag 或 push。


## 可选功能

### Native Agent Adapter

Native Agent Adapter 会把 ForgeKit 的 loop、maker-checker、verification 协议导出为 Codex / Claude Code 可审查的原生 agent 配置模板。

它只生成配置，不执行 loop，不启动 agent，不做 runner、dispatcher、worktree 自动化、merge、commit、push 或 PR。

### Hooks

ForgeKit 默认不启用 hook。需要文档同步提醒时，可以安装 opt-in Git hook：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-hooks.ps1 -Profile docs-warn -Target git
```

```bash
./scripts/install-hooks.sh --profile docs-warn --target git
```

`docs-warn` 只提示不阻断；团队确认噪音可接受后再使用 `docs-strict`。

### Change Archiving

ForgeKit 把当前事实和历史过程分开：

- 当前事实：`.forgekit/docs/`
- 活跃或刚完成的变更：`.forgekit/changes/`
- 历史变更：`.forgekit/archive/changes/YYYY/`

常用归档入口：

```bash
python3 scripts/archive-changes.py --dry-run
python3 scripts/archive-changes.py --smart-check --plan .forgekit/archive-plan.md --reference-report .forgekit/archive-reference-report.md --sync-report .forgekit/current-docs-sync-report.md
python3 scripts/archive-changes.py --smart-apply --report .forgekit/smart-archive-report.md --confirm
```

`--smart-apply` 要求 Git clean 且显式 `--confirm`，只移动报告中标记为 `auto_archive_candidate` 的 change。

## 与 ECC 的边界

ECC 更像 AI 编程工具增强套件，覆盖 commands、hooks、memory、MCP、多 agent、安全工具和跨工具适配。

ForgeKit 的职责更窄：约束具体项目的交付流程，让 AI 工具更可靠地接手项目现场。

两者可以共存：ECC 增强 AI 工具，ForgeKit 约束项目工作区。

## 版本提示

完整版本历史请查看 CHANGELOG.md。
