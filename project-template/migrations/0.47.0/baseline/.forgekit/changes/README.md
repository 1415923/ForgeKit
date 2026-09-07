# 变更工件

生成项目中，这些材料默认安装到 `.forgekit/changes/`。只有变更需要可审查工程工件时才使用。

按风险等级的最低要求：

| Risk | 必需文件 |
| --- | --- |
| low | 默认不要求 change folder，除非用户要求。 |
| medium | `proposal.md`、`tasks.md`、`verification.md`、`review.md` |
| high | `proposal.md`、`design.md`、`tasks.md`、`verification.md`、`review.md`、`ship.md` |

高风险或重大变更后建议写 `retro.md`，但不是每个变更都必须写。

Change ID 应短且稳定，例如 `20260608-add-payment-callback`。

生命周期状态记录在 `proposal.md`：

| Status | 含义 |
| --- | --- |
| `draft` | 正在讨论，尚未确认实施。 |
| `active` | 已确认并正在执行。 |
| `done` | 已实现并验证，稳定结论应该已经同步到 `.forgekit/docs/`；此状态只提示该 change 可以考虑归档。 |
| `archived` | 历史材料；不是活跃 change，也不会按活跃工作检查。 |

已完成变更必须把稳定结论同步回当前态文档。不要把当前项目事实只留在 change folder 里。
