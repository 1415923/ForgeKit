# Archive Capsule 策略

## Archive is not deletion

归档是保留可追溯历史，不是删除。被归档内容不再作为 current truth，但必须能通过索引、摘要和原路径记录找回。

## Capsule structure

```text
.forgekit/archive/
  index.md
  YYYY/
    YYYY-MM/
      YYYY-MM-DD-<slug>/
        archive-summary.md
        archived-items.md
        items/
          changes/
          reports/
```

脚本只移动计划中确认的 `.forgekit/changes/**` 或 `.forgekit/` 下允许的生成报告。它不移动 `.forgekit/docs/**`、business docs、state、lock、upgrade 文件或旧 archive。

## Archive index

`.forgekit/archive/index.md` 是历史检索入口。每次 apply 新增一条 Date、Archive ID、Phase / Version、Reason、Summary path 和 Key links 记录。默认先读 index，不读全量 archive。

## Archive summary

`archive-summary.md` 记录归档原因、范围、关键决策、完成事项、验证证据、风险和关联 ID。计划无法证明的字段写 `TODO_REVIEW`，不得编造。

## Archived items log

`archived-items.md` 逐项记录 `from`、`to`、`type`、`reason`、`status` 和 `notes`。它是移动审计记录，不替代 current docs 或 Git 历史。

## Date / phase naming

默认路径为 `.forgekit/archive/YYYY/YYYY-MM/YYYY-MM-DD-<slug>/`。`slug` 来自 `--name`；未提供名称时使用 `phase-close`，并在计划中提示可在 apply 前重建计划调整名称。

## Legacy archive handling

旧 archive 保持原位。v0.39 不扫描、不重排、不改写、不删除 legacy archive，也不会把它重新当作 current truth。

## Plan / apply boundary

`plan` 只覆盖 `.forgekit/archive-capsule-plan.md`，不移动文件。`apply` 必须显式 `--confirm`，只消费计划中 `Archive-Status: candidate` 的条目；计划字段异常、来源变化、目标冲突或路径越界时停止，不做部分猜测。
