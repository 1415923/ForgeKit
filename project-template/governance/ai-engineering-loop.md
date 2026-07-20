# AI Engineering Loop

ForgeKit turns AI coding into a lightweight engineering loop:

1. Clarify the work.
2. Size the risk.
3. Create just enough reviewable change artifacts.
4. Implement with small, scoped edits.
5. Verify, review, ship, and record what changed.

ForgeKit does not replace the framework, CI, issue tracker, or architecture process. It provides project-local prompts, skills, templates, and checks so AI agents work inside visible engineering boundaries.

## Risk Levels

| Risk | Typical work | Required workflow |
| --- | --- | --- |
| low | Single-file fix, copy edit, local test adjustment, no public behavior or data impact | Clarify if needed, edit surgically, run relevant validation, summarize result. A `.forgekit/changes/<id>/` folder is optional. |
| medium | Multi-file change, small feature, template/script change, user-visible flow, documentation structure change | Create `.forgekit/changes/<id>/proposal.md`, `tasks.md`, `verification.md`, and `review.md`; confirm the plan before implementation. |
| high | Architecture change, migration, security/permission change, cross-platform script, public template contract, deployment or compatibility risk | Create `proposal.md`, `design.md`, `tasks.md`, `verification.md`, `review.md`, and `ship.md`; confirm the design before implementation. `retro.md` is recommended after completion. |

风险按客观影响判断，不按文件数或模块数计分。每次用一段简短说明覆盖：不可逆性、公共合同、持久数据或迁移、身份权限与秘密、外部动作、跨仓库协调、回滚难度、部署影响、验证能力以及事实不确定性。

- 本地、可逆、无公共合同或持久状态影响且可完整验证的机械变更可为低风险，即使涉及多个文件。
- 单文件权限策略、schema migration、公共 API、模板升级或发布规则至少为中风险。
- 生产数据、身份与密钥、不可回滚发布、破坏性外部动作或当前无法可靠验证的关键结论属于高风险。
- 用户授权只解决“是否允许执行”，不会降低数据、权限、兼容、部署或回滚的客观风险。

maker-checker、独立 code review 和 change artifact 由中高风险或明确 gate 触发；低风险改动不因代码或文件数量自动升级。推荐使用：`Risk: <level> — <主要影响>; rollback <难度>; verification <能力或缺口>.`

## Change Metadata

Each `.forgekit/changes/<id>/proposal.md` should start with ASCII metadata:

```text
Status: draft
Risk: medium
Created: YYYY-MM-DD
Owner: <name>
Reason: <short reason>
```

If `Risk:` is missing, treat the change as needing review before coding.

## Freeze Before Implementation

For medium and high risk changes, confirm the proposal's scope, trust boundary, non-goals, and stage authorization before implementation. Freeze a risk-proportional acceptance matrix in `verification.md`; each ID needs a positive case, a key rejection case, and evidence from the real entry or orchestration path. Low risk changes may keep the lightweight flow.

Changing a frozen contract returns the change to design/acceptance. Do not smuggle a larger contract into review findings.

## Review Convergence

The first independent review checks the frozen contract and may also block a newly discovered issue only when it can cause data leakage or contamination, wrong training/evaluation/checkpoint behavior, artifact overwrite, unauthorized work through the formal entry point, false success, or clearly untrustworthy conclusions. Other matrix-external hardening, observability, style, abstraction, or defense against a developer deliberately calling an internal helper is a follow-up unless the frozen trust boundary says otherwise.

After one normal maker fix round, re-review defaults to the previous blocking findings and marks each Closed, Partially closed, or Still open. A regression introduced by that fix may still block when it violates the frozen contract or causes a real Critical consequence. Unrelated new suggestions are follow-ups. Do not reopen architecture review or expand the trust boundary. If several Major findings remain after the normal fix round, return to design to simplify, split, or refactor instead of extending an indefinite patch loop.

Review pass authorizes only the stage named in the proposal. `ready-for-commit`, `ready-for-minimal-real-smoke`, and `ready-for-full-execution` are separate decisions.

## Completion

- Do not stop at "tests passed" for medium or high risk changes.
- Record verification results in `verification.md`.
- Record review notes and residual risk in `review.md`.
- For high risk changes, record release and rollback notes in `ship.md`.
- Use `retro.md` only when the change was high risk, major, surprising, or explicitly requested.
