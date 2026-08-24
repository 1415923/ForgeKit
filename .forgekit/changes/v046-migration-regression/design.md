# ForgeKit v0.46.0 Stage D Migration Design

## Authority

优先级保持为 Frozen Plan r2、Stage A approved semantics、Stage B consumers、Stage C runtime、Stage D migration/regression。本设计只描述 migration wiring，不改变上游语义。

## Existing framework reuse

- 继续使用 `migrations/<to>/migration.json` 与 `project-template/migrations/<to>/migration.json` 双镜像。
- 继续使用 exact `from -> to` chain；本轮 predecessor 为 `0.45.0`，不引入 family wildcard 或任意历史 shortcut。
- replacement 继续使用 `replace_file_if_baseline_matches`；baseline 字节锚定 `v0.45.0`，incoming 字节锚定 approved Stage B/C template。
- custom/unknown 继续进入 `.forgekit/reports/upgrade-review-needed.*` 和既有 packet root。

## Minimal extensions

1. `remove_file_if_baseline_matches` 是同一 action dispatcher 的 baseline-safe removal：exact stock 可删除并先生成 rollback packet；missing 为 no-op；custom/unknown 强制 manual preserve，即使全局 policy 是 `replace-template`。
2. apply transaction 在写前捕获有限、内存中的 upgrade-start snapshots。任一异常恢复 action targets、reports、template-lock、state 及本次创建的空父目录；不创建永久 rollback root/registry。
3. migration descriptor 的 `template_lock.retire_targets` 只驱动既有 lock metadata 收敛。README 不是 action target；lock absent 时保持 absent，invalid lock 在任何 migration write 前停止。

## Version and root semantics

- `.forgekit/state.json` 在成功末尾更新为 `0.46.0`。
- `.forgekit/project-boundary.yml` 不修改；其 created-with version 可保持旧值。
- unified entry 继续拥有 outer/inner exact topology discovery、CurrentWriteScope 和 ambiguous C4 stop；low-level migration 不新增 root discovery。
- repo `VERSION` 与 project-template state 在 Stage D 均保持 `0.45.0`。fresh v0.46 测试只使用临时 toolkit metadata fixture。

## Managed delta

payload 共 38 个 actions：35 个 replacement、3 个 stock-only loop removal。business README、current fact owners、scratch/archive/history 均不在 action targets 中。
