# Agent Entry Contract

本文件是 Codex 与 Claude 入口始终生效的共享安全、事实、授权、Effect Risk 和 root resolution 合同的唯一规范来源。入口文件只应用这些规则；具体任务流程仍由命中的 Skill、governance 或 reference 拥有。

## Project and Write Boundary

先从 `.forgekit/project-boundary.yml` 确认 ForgeKitRoot、ProjectRoot、managed docs root 和写入策略。读取和写入都必须留在用户给出的项目边界与任务范围内；不得把工具包根、业务项目、外部证据目录或真实用户项目相互混用。

## Root Resolution Contract

existing-project entry 在开始相关写操作前应解析并能说明：

```text
GovernanceRoot
WorkspaceRoot
ProjectRoot
RepoRoot
ForgeKitRoot
CurrentWriteScope
```

- `GovernanceRoot` 是被选中的 active `.forgekit/state.json` 与 `.forgekit/project-boundary.yml` 所在根。
- `WorkspaceRoot = GovernanceRoot` 是 derived operational default，不新增 persisted identity。
- `ProjectRoot` 来自现有 boundary；`RepoRoot` 来自当前 task/path 的 Git top-level，或已显式启用的 workspace-map project/repo scope。
- `ForgeKitRoot` 来自现有 boundary；`CurrentWriteScope` 由 boundary policy、task scope 与用户授权共同决定。
- 无法唯一解析时报告 `UNKNOWN` 或 `AMBIGUOUS`。只有在相关写操作将依赖该不确定目标，且存在受支持的 C4 failure path 时，才阻塞该 scoped action。

Existing-project discovery 只允许以下规则，不是通用的“向上寻找任意 `.forgekit`”：

1. requested target 自身具有有效 state 与 boundary 时，它是 direct GovernanceRoot，由 boundary 解析 ProjectRoot。
2. requested target 自身没有 active state 时，只检查 ancestor candidates。候选必须同时具有有效 state/boundary，且其 `project_root` 规范化后恰好等于 requested target，并且未被 archive、artifact 或 materialized-workspace classification 排除。
3. 恰好一个 exact candidate 时复用该 topology，不在 inner ProjectRoot 创建第二套 `.forgekit`。
4. 零候选不得继承 unrelated ancestor；多候选报告 `AMBIGUOUS`。禁止 `nearest ancestor wins`。

该语义合同不实现 root discovery，也不新增 persisted workspace/repo/layout/root 字段、root registry、authority registry 或 shadow-root registry。fresh layout 和实际 CLI 行为由获授权的实现 stage 落地；existing layout 不因发现过程被移动或重写。

## Evidence and No Fabrication

结论必须来自可定位的文件、命令或用户事实。证据不足时明确标记未知、假设或 `TODO_REVIEW`；不得把推测、一次未验证输出或缺失的外部状态写成项目事实，也不得为了满足 checker 编造 risk、testing、traceability、project plan 或其他 owner 内容。

## Audit Default

审计、检查、评估、诊断和规划默认只读。发现问题只授权报告问题，不自动授权修复、回填文档或执行后续动作。

## Bounded Local Authorization

用户明确要求修复、修改、实现或更新，并给出本地范围时，允许在该范围内执行可回滚写入和必要验证。清晰的局部授权无需用同义问题重复确认；它也不得扩张到未声明路径、外部系统或不可逆动作。

## Effect Risk

Effect Risk 与 `ai-engineering-loop.md` 的 Execution Intent 正交。它只判断实际动作的外部性、不可逆性与授权要求，包括：

- external system or account action；
- credentials、permissions、secrets 或 sensitive data；
- paid call、budget、rate limit 与 retry；
- destructive、irreversible 或 hard-to-recover effect；
- production、deployment、migration 或 remote repository impact。

真实、外部或付费调用不自动等于 `FORMAL`；`DIAGNOSTIC`、`SMOKE`、`FORMAL` 也都不会降低 Effect Risk。用户授权只回答是否允许执行，不改变客观影响或验证要求。

## Bounded Effect Envelope

执行具有外部或不可逆 effect 的动作前，必须从用户授权和当前任务证据确定：

```text
Target
Allowed Effect
Credential Scope
Budget / Rate Limit
Retry Limit
Destructive Boundary
Stop Condition
Recovery / Rollback
```

- 缺少会改变实际影响的 envelope 信息时停止相关动作；不阻止无关的只读或可逆本地工作。
- Retry 不得无限延长，不得为了获得更好结果 outcome-shop，也不得跨越 credential、budget 或 target scope。
- 不读取、回显或持久化超出任务所需的 secret；不把凭据存在视为使用授权。
- 删除、覆盖、迁移、权限变更或其他难恢复动作必须先解析精确目标、影响与恢复方案。

## External and Irreversible Actions

外部、不可逆、破坏性或越界操作必须获得针对具体目标和影响的明确授权。commit、push、tag、release、部署、生产变更、删除重要数据和权限或凭据变更不由普通本地写入授权隐含许可。

授权必须落在 bounded effect envelope 内。目标、scope、credential、budget、retry 或 destructive boundary 发生实质变化时，原授权不自动覆盖新动作。

## Minimum Evidence-Based Writeback

写回遵循来源优先和最小必要原则：只持久化完成当前授权任务所需、且有证据支持的事实。Document ownership does not imply mandatory population；没有对应事实变化时 owner 可以保持 lean 或 template 状态。

Active work 中已确认事实可以临时停留在 active change 或 checkpoint，但在受影响的 task/change/phase 被声明 closed、shipped 或 handed off 前，必须写回唯一负责 owner。用户禁止所需 writeback 时，只阻止相关 closure/handover/ship declaration，不阻止无关工作。

按文档职责选择唯一目标，不复制完整对话、长工具输出或未经验证的推理，也不把业务事实写入 governance 模板。

## Skill Routing

先使用与当前意图和项目状态匹配的项目本地 Skill，再按需读取其直接引用的细则。通用路由只决定加载哪个任务流程，不授予写入、外部或不可逆操作；每个 Skill 的具体触发、不触发和平台适配语义仍由该 Skill 自身拥有。
