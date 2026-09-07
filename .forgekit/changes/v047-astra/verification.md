# 0.47 验证记录

日期：2026-09-07。范围：本仓库工作区与 D:\tmp 下的隔离 fixture。证据用途：实现回归及 SMOKE，不是模型收益声明。

| 验证 | 结果与证据 |
| --- | --- |
| 必需 PowerShell 门禁 | 最近一轮 `powershell -ExecutionPolicy Bypass -File .\scripts\validate-template.ps1`，exit 0；288 项中 281 通过、7 项跳过；124.194 秒；entry-resolution-gate.log。其余初版记录保留各自证据范围 |
| 当前 migration | 12 个测试方法通过，含真实 v0.36、v0.43、v0.43.1、v0.44 tag 的子场景；historical-tests.log |
| 合并与事务 | 14 项覆盖非重叠／重叠、BOM／CRLF、围栏、章节重排、冲突零写入、过期计划、硬链接、备份顺序和回滚故障；包含在最终门禁 |
| 当前契约反向测试 | 8 项通过，验证别名隐式策略、审查写入反转、主路由缺失、payload 漂移、版本、LF 与 references 缺失；release-gate.log |
| 插件与 manifest | validate-plugin-assets.ps1、validate-v047.py、投影 check 均 exit 0；24 个投影文件及当前 migration 镜像一致 |
| 行为场景清单 | test-skill-behavior.py validate：37 个场景通过 schema 检查；真实模型执行仍 NEEDS_TEST |
| 生成项目 | Windows PowerShell 初始化、业务 README 保留、schema 2 lock、退休路径、harness、current docs 和 workspace checker 均通过；最终门禁包含 smoke |
| 全新检出 | LF、CRLF 两种 clone 的字节及属性检查、生成 smoke 均通过；移除 Markdown LF 属性的 mutation 正确失败；fresh-clone.log |
| 独立审查 | blocker-recheck pass；审查范围、SHA256 与 12＋2 个只读重放场景见 review.md |
| 差异卫生 | git diff --check 通过；旧 migration 包无 tracked diff；仅新增 0.47 包；未提交源仓库 |

历史精确文本／固定数量测试通过本地 Git 对象固定到 v0.46：它们验证旧契约，不能当作当前行为证据。当前行为由 test_v047_*、test_structured_upgrade、当前 runner、投影和生成 smoke 覆盖。7 个跳过项属于旧版本递归门禁编排 canary，当前门禁不重入旧门禁。

fresh-clone 的临时提交为 `478fd4d8da4a2d529cdcb46fb9a9049e4ec8e0f4`，只存在于隔离测试仓库。其后最终门禁覆盖了 JSON current 输出和 PowerShell 编码修正；未将该快照冒充最后工作区逐字节快照。

实测静态文件大小：AGENTS 从 4,831 降至 2,366 bytes；CLAUDE 从 5,027 降至 2,459 bytes。该数据只描述入口字节数，不代表 token、响应时间或成功率收益。

## 限制

- 未执行 GPT-6 Astra／Codex／Claude 真实模型 A/B；没有对应客户端加载、工具 trace、token 或耗时结论。
- 生成项目的原生执行平台为 Windows；Linux／macOS 脚本保留兼容实现，但本轮没有原生平台实测。
- 初版与前两次报告修复仅使用副本。后续用户明确要求按第一性原理修复后，已对指定项目完成入口所有权整理和实际 ForgeKit 升级；范围与证据见 ownership-repair-design.md。未操作生产业务数据。

详细运行输出的 .log 文件为本地验证材料，按仓库规则忽略；本记录与测试代码保存可复现结论，不复制长日志。

## 整份定制入口复现

默认整份改写仍停止。修复首个差异行号的误导提示，并加入显式保留材料；本轮新增 5 个合并/事务测试和 2 个真实统一 CLI 测试。覆盖项目/版本/迁移/输入/候选绑定、重复或越界目标、未使用条目、删改原规则、嵌套用户区、后续引用改写、计划后材料和项目变化。首次受限沙箱测试因临时目录写权限失败，在获准的 D:\tmp 临时目录环境重新执行 21 个结构化引擎测试全部通过；完整门禁结果如上。

报告项目只读预检为 0.46.0 → 0.47.0，113 个动作、2 份项目事实文档保留、零冲突。统一入口 `--entry-resolutions` + `--dry-run` exit 0；逐个核对迁移输入哈希未变。真实项目仍为 0.46.0。

复制受管迁移输入到独立临时副本，实际低层 CLI `apply --safe --plan-hash --entry-resolutions` exit 0，副本到 0.47.0。最终 AGENTS 与可审阅候选逐字节相同，原入口完整正文保留；rollback 原入口字节与真实原文件一致。业务源码、生产程序及数据不在执行范围。

本地材料（已 gitignore，不分发）：`user-rules/reviewed-upgrades/autumn-v047/` 中的 resolution.json、AGENTS.candidate.md、preflight.json、preflight-cli.txt、verification.json。候选 SHA-256：`d969d1b8d3bdecb7fb32091c05b1522b4155df49cb7857068ba6ad380930dfde`。独立语义与拒绝路径复核见 review.md 最新补充。
