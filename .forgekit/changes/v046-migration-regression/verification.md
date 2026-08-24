AcceptanceStatus: maker-verified

# ForgeKit v0.46.0 Stage D Verification

执行日期：2026-08-24。

## Acceptance evidence

| Contract | Result | Evidence |
| --- | --- | --- |
| Exact predecessor / payload | PASS | `from=0.45.0`, `to=0.46.0`, 35 replace + 3 remove；baseline 与 tag、incoming 与 current template 逐字节校验 |
| Stock / missing | PASS | stock replacements、stock loop removal、missing README/no lock fixtures |
| Custom / unknown | PASS | byte preservation、classification、manual packet；unknown baseline 不猜测 |
| README | PASS | absent remains absent；custom 和 legacy stock byte-preserved；`replace-template` 不触碰 README；lock 不再 claim README |
| Current Truth | PASS | active task fixture 不创建 risk/testing facts，不修改 task board |
| Root / layout | PASS | fresh in-place + legacy-nested apply；legacy outer/inner same topology；inner 无第二个 `.forgekit`；ambiguous no-write |
| CurrentWriteScope | PASS | dry-run read-only；`--yes` 才显示 upgrade apply authorization |
| Rollback | PASS | fault injected after state write；完整 file/directory inventory、custom、lock 与 state 恢复 upgrade-start bytes |
| Idempotency | PASS | second apply reports no migration and tree stays identical |
| Checker compatibility | PASS | current checker legacy/canonical fields；workspace `not-enabled`/`runtime-error`/summary/path markers；exit semantics |
| Legacy loop guard | PASS | migrated workspace checker retains `loop-operations.md` compatibility guard |
| Version boundary | PASS | boundary remains old created-with；state becomes 0.46 in fixture；no VERSION MISMATCH；repo VERSION remains 0.45.0 |

## Actual commands

- `python -B -m unittest tests.test_stage_d_migration -v` — PASS，13 tests。
- `python -B -m unittest tests.test_upgrade_review_packets -v` — PASS，11 tests；因 managed sandbox 对系统 temp 的权限限制，使用批准的 unsandboxed test execution。
- `python -B -m unittest tests.test_stage_b_entry_migration.StageBMigrationBehaviorTests tests.test_stage_b_entry_migration.StageBProductionDiscoveryTests -v` — PASS，13 tests。
- `python -B scripts/update-template-manifest.py check --repo-root .` — PASS。
- `python -B -m py_compile scripts/forgekit-upgrade.py project-template/scripts/forgekit-upgrade.py scripts/update-template-manifest.py scripts/validate-stage-b-entry-migration.py tests/test_stage_d_migration.py` — PASS。
- `python -B scripts/smoke-test.py --repo-root .` — expected fail-fast：`Missing required paths: usage.html`；未运行后续 smoke，未恢复/修改该文件。
- `powershell -ExecutionPolicy Bypass -File .\\scripts\\validate-template.ps1 -SkipSkillValidation` — 90 秒无输出，复现已知高 CPU/静默限制，随后人工中止；不据此宣称 PASS/FAIL。
- `git diff --check`（排除两个逐字节保留的 v0.45 `loop-blueprint.md` baseline）— PASS；两个排除文件均与 `v0.45.0:project-template/docs/loop-blueprint.md` 哈希一致，其历史尾随空格未被“修复”。

## Limitations

- full smoke 被 unrelated user deletion `usage.html` 在入口阻止。
- full validator 在有限 90 秒窗口内无输出；Stage D 未新增 validator-of-validator。
- 未迁移或写入任何真实项目。

以上 limitations 是 Stage D maker 当时的 evidence boundary，不能改写为 Stage D full PASS。Stage E 另行取得并分级记录：targeted PASS、release-consistency PASS、基于当前 candidate snapshot 的 pristine/full smoke PASS、不带 skip 的 `validate-template.ps1` PASS，以及真实 dirty worktree 因 unstaged `D usage.html` 的 `KNOWN_UNRELATED_FAILURE`。该补充关闭 NB-D-01 的最终报告风险，但不改变 Stage D 历史证据标签。
