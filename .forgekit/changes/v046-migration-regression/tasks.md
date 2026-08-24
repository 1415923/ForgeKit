# ForgeKit v0.46.0 Stage D Tasks

| ID | Task | Status | Evidence |
| --- | --- | --- | --- |
| SD-01 | 核对 Git boundary、Frozen Plan、Stage A artifacts 与 Stage B/C commits。 | Done | `git status --short`; `git log --oneline --decorate -6` |
| SD-02 | 调查 migration runner、baseline、packet、lock、rollback、state/version 和 smoke fixtures。 | Done | existing `forgekit-upgrade.py`, `upgrade_review_packets.py`, manifest/update scripts and tests |
| SD-03 | 实现精确 `0.45.0 -> 0.46.0` payload 与双镜像。 | Done | `migrations/0.46.0/**`; template mirror |
| SD-04 | 实现 stock-only loop removal、README lock retirement 和 exact failure rollback。 | Done | existing upgrader extensions |
| SD-05 | 覆盖 stock/custom/unknown/missing/README/current facts/idempotency/rollback。 | Done | `tests/test_stage_d_migration.py` |
| SD-06 | 覆盖 fresh layouts、legacy outer/inner、ambiguous root、scope 和 checker compatibility。 | Done | `tests/test_stage_d_migration.py` |
| SD-07 | 运行 targeted regression、manifest、compile、diff/scope checks。 | Done | `verification.md` |
| SD-08 | Fresh independent read-only review。 | Pending | 本轮不以 self-review 满足 independent gate |

Stage E、release、commit、push、tag 均未授权。
