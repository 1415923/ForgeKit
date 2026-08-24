# ForgeKit v0.46.0 Stage D Migration Proposal

## 状态

Stage: D — Migration and Regression
MakerStatus: ready-for-check
ReleaseStatus: not-authorized

## 目标

在不重新设计 Stage A/B/C 的前提下，复用现有 versioned migration、baseline guard、review packet 和 unified entry，实现精确的 `0.45.0 -> 0.46.0` 安全幂等升级。

## 范围

- 为 Stage B/C 已批准的 managed consumers 和 checker runtime 提供 baseline-guarded replacement。
- 对三个 retired loop docs 执行 stock-only removal；custom/unknown 始终 preserve/manual。
- 从旧 template-lock ownership 中退休 business README 和三个 loop docs，不改 README 字节。
- 让异常 apply 恢复完整 upgrade-start state，包括 managed targets、reports、template-lock 和 state。
- 使用 repo-local synthetic fixtures 验证 fresh、upgrade、topology、rollback、idempotency 和 machine compatibility。

## 非目标

- 不迁移真实项目，不移动 layout，不猜 root，不清理 scratch/archive/shadow。
- 不生成 risk、testing、traceability、authority、task 或 plan 事实。
- 不修改 `usage.html`，不 bump `VERSION`，不进入 Stage E，不 release/commit/push/tag。
- 不新增 Skill、checker、protocol、registry、state 或 migration framework。
