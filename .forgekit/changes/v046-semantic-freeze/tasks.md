# ForgeKit v0.46.0 Staged Tasks

## 当前状态

Stage A-D 已独立批准。Stage E maker 已完成 release-candidate 收口，当前只等待 fresh read-only independent review；发布 side effects 仍未授权。

| ID | Task | Status | Evidence / gate |
| --- | --- | --- | --- |
| SA-01 | 调查现有 change/design workflow 与 v0.45 artifacts，确定 Stage A 落点。 | Done | 复用 high-risk proposal/design/tasks/verification/review/ship 套件。 |
| SA-02 | 冻结 neutral ownership、Execution/Effect/Formal、finding、Current Truth、authority、layout、README、artifact/scratch 与 non-goals。 | Done | `proposal.md` + `design.md`。 |
| SA-03 | 完整冻结 A1～A9 / B1～B12。 | Done | `verification.md`。 |
| SA-04 | 吸收 BF-01～BF-04 closure，并把 NF-01～NF-03 指派到批准的后续 stage/owner。 | Done | `review.md`。 |
| SA-05 | 执行有限 Stage A consistency/scope checks。 | Done | `verification.md` Actual checks 全部 PASS。 |
| SA-06 | Fresh read-only independent review Stage A representation。 | Done | 正式状态 `STAGE_A_APPROVED`。 |

## Stage B — Protocol and Selective Consumer Convergence (`DONE`)

- 先修改三个 neutral owners，再只修改有真实 semantic delta 的 Skills/docs/native/Claude consumers。
- 必须先收敛全部 active loop/review consumers，移除 every-run mandatory review 与 severity-implies-blocking，才能从 fresh surface 删除三个旧 loop docs。
- Current-doc consumers 收敛为 fact-triggered population + closure writeback。
- `project-maintenance.md` 承载一次性 cleanup plan，不新增 taxonomy/database。
- 停止条件：global invariant 仍由 specific Skill 隐式拥有、同一语义有多个 canonical owner、active loop consumer inventory 未闭合，或 consumer 仍从 active task 推导 mandatory population。

## Stage C — Consumer Audit, Checkers and Unified Init (`DONE`)

- 修改 checker 前先刷新 JSON/stdout/exit consumer inventory，并保持 additive compatibility。
- 实现 canonical finding fields、strict/Blocking 解耦、unified layout、existing root discovery、fresh README ownership 收敛。
- 不新增 persisted root、root registry、checker schema registry 或新 checker。
- 停止条件：需要 breaking machine interface、nearest-ancestor guess、静默改变 noninteractive layout，或 fresh install 仍拥有 business README。

## Stage D — Migration and Regression (`DONE`)

- 只在 Stage B/C 通过后创建和验证 0.45→0.46 安全幂等 migration 与批准矩阵回归。
- 不猜 root、不覆盖 user-owned 文件、不自动补事实、不删除历史资产、不做 destructive cleanup、不触碰 unrelated worktree change。

## Stage E — User Docs and Release Validation (`READY_FOR_INDEPENDENT_REVIEW`)

- 更新批准的用户文档与 release validation；release-check 只评估真实 v0.46 candidate。
- 任一 acceptance category 或 checker/CLI compatibility evidence 不完整时停止。
- `VERSION`、current-version projections、用户文档与 CHANGELOG 已收敛到 0.46.0；完整证据见 `verification.md`。
- tag、push、publish、GitHub release 与 deployment 未执行，且只有 Stage E independent review PASS 后才可由用户另行授权。
