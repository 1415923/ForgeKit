# 代码库地图

读者：AI 和接手人员。定位不明、模块入口变化或接手时使用。仅记录搜索入口，不记录任务流水或完整架构。

| 区域 | 搜索起点 | 关键入口 | 验证位置 |
| --- | --- | --- | --- |
| 业务实现 | 待补充 | 待补充 | testing.md |
| 测试 | 待补充 | 待补充 | testing.md |
| 业务文档 | docs/ | 用户自有，按任务读取 | 原项目命令 |

已知目标时直接读取相关文件及调用边界。仅加载选择的 `.codex/stacks/<stack>/`。当前任务依次引用 task-intake、task-board、work-log；不默认读取全量文档。
事实归属见 document-responsibility；保存和恢复见 work-session-checkpoint；操作示例见 usage-playbook。修改入口或验证方法时最小更新本表及 testing。
多项目仅在 workspace-map 已显式启用时解析命中的 project capsule；不自动拆分。忽略依赖、构建和缓存，敏感值不回显。

<!-- forgekit:user begin -->
<!-- forgekit:user end -->
