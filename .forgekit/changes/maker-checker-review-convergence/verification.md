# 验证

## Frozen Acceptance Matrix

| ID | Contract | Positive case | Rejection case | Evidence |
| --- | --- | --- | --- | --- |
| A01 | proposal 冻结四类边界 | medium/high change 可填写四项 | 未声明阶段不得被 review pass 隐式授权 | 模板与协议检查 |
| A02 | 每个 acceptance ID 映射真实路径 | 正式入口与测试路径一致 | 只测 helper、正式入口绕过合同 | verification 模板与提示词检查 |
| A03 | 首审 blocker 有限分类 | 冻结合同违例或 Critical consequence 阻塞 | token、额外日志等矩阵外加固自动阻塞 | 协议/review skill 检查 |
| A04 | 复审默认限定范围 | Closed/Partially closed/Still open | 复审重新开放架构要求 | review 模板与协议检查 |
| A05 | 修复循环可收敛 | 一轮修复后通过或回设计 | 第三、第四轮无界小补丁 | 工程循环检查 |
| A06 | 三个角色短提示词可复制 | Maker/首审/复审均完整简短 | 依赖每轮长提示词 | usage playbook 检查 |
| A07 | low risk 保持轻量 | low risk 可不建完整矩阵 | 所有小改动被强制大型规范 | 风险规则检查 |
| A08 | 新建项目直接获得规则 | init 后模板包含新协议 | 新项目缺模板或提示词 | generated smoke |
| A09 | 定制项目不被覆盖 | baseline 相同自动更新 | 不同内容被安全 apply 覆盖 | migration smoke |
| A10 | dry-run 可解释更新 | 展示 safe/review-needed/non-goals | 隐式授权 commit/smoke/full execution | migration plan 输出 |
| A11 | 模板结构一致 | validate-template 通过 | manifest/checksum/version 不一致 | validate-template.ps1 |
| A12 | 禁止项目特定术语泄漏 | 通用模板不含来源项目术语 | 任一禁用术语出现 | rg 检查 |
| A13 | 新旧项目都能发现规则 | 新项目入口直接包含；v0.43.2 AGENTS 路由到受管协议 | 文件升级但 Agent 无读取入口 | init、baseline 与 migration smoke |
| A14 | 普通升级保持单命令交互 | 同一 controller 完成 preview/apply/manual merge/summary | 要求普通用户退出后执行第二条命令；取消产生写入 | unified controller、PTY/state-flow smoke |

## 未授权验证

- 不向真实业务项目 apply 升级。
- 不运行真实训练、真实 smoke 或完整执行。

## 结果

- A01-A07: 模板、协议、AGENTS 入口和三个短提示词已由静态检查覆盖。
- A08: `D:\tmp\forgekit-maker-checker-0440` 新项目初始化成功，并包含新模板、协议和 0.44.0 migration。
- A09-A10: 0.43.2 dry-run 同时观察到 baseline-matched proposal 为 `SAFE`、定制/不同内容为 `REVIEW-NEEDED`，且 plan 为 report-only、未写文件。
- A11: `powershell -ExecutionPolicy Bypass -File .\scripts\validate-template.ps1` 通过。
- A02/A09/A10 durable regression: `python .\scripts\smoke-test.py` 通过；标准 suite 通过统一入口验证全 baseline safe apply、定制 target 保留、state/feature 前进、migration mirror 和 rerun no-op。
- A12: 通用模板、入口和 0.44.0 migration 的禁用项目术语扫描无匹配。
- A13: 新项目 AGENTS 包含冻结/复审短规则；v0.43.2 baseline AGENTS 已指向 `.forgekit/docs/maker-checker-protocol.md`。升级 plan 与结果汇总提供可直接合并的三行 AGENTS 入口，不覆盖项目定制。
- A14: 标准 smoke 以一次 unified controller 调用完成 0.43.2 preview + manual-merge apply + 汇总；验证自动更新、本地保留、incoming/diff、version/feature、业务文件/真实 change 不变和 rerun no-op。abort controller 与交互初始取消均验证零写入；POSIX PTY 分支覆盖同会话 diff 选择，Windows 覆盖等价 controller state flow。

## 修复过的验证缺口

- 首次 dry-run 拒绝了 `changes/_template/...` 和根级 `AGENTS.md` target。现将 change target 修正为 `.forgekit/changes/...`，并取消根级 AGENTS 自动迁移；已有项目通过受管治理文档和 review instructions 获得规则，项目定制入口不被自动覆盖。
- 首次 migration snapshot 多出工具包装换行，导致 baseline checksum 不匹配。已重建快照；旧 proposal baseline SHA-256 与 v0.43.2 模板哈希一致。
- 独立首审指出人工 dry-run 未形成耐久 orchestration 回归。已将 0.44.0 clean/customized 两类真实升级场景加入 `scripts/smoke-test.py`，并修正版本升级后暴露的旧 smoke fixture 硬编码。
- 发布前审计发现复审例外过窄、结果汇总不足和 abort 写 review report。已在既有协议/入口内修正，并将项目内高级升级脚本作为第十个 baseline-guarded 迁移文件。
- 独立发布审查进一步发现交互 `[a]` 与显式 abort policy 是两个分支；交互分支仍写报告。已删除该写入，并用直接调用交互控制器、伪造 TTY/input 的跨平台回归验证 state、target 和 reports 均不变。
