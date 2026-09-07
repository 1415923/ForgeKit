# ForgeKit 日常用法

读者：项目使用者。需要选用工作流时读取；这里不存业务事实，也不新增执行授权。

| 目标 | 提示词或入口 |
| --- | --- |
| 安装、初始化、更新、同步 | 在 ForgeKitRoot 使用 `python scripts/forgekit-project.py --target <ProjectRoot>` |
| 实现任务 | 请完成 `<目标>`，范围为 `<范围>`，验收为 `<结果>`；运行相关验证并修复本次引入的失败 |
| 接手项目 | 请使用 $project-assessment 的 takeover 分支只读盘点现状 |
| 评估适用性 | 请使用 $project-assessment 的 adoption 分支评估是否适用 |
| 初始化填充 | 请使用 $document-backfill 的 bootstrap 分支填充有证据的占位 |
| 事实回填 | 请使用 $document-backfill 的 facts 分支回填 `<事实领域>` |
| 高影响规划 | 请使用 $large-change-planning 冻结范围、验收与回滚 |
| 独立代码审查 | 请使用 $code-review；fresh reviewer 只读审查，self-review 不代替独立门禁 |
| 安全／发布检查 | 按真实意图使用 $security-review 或 $release-check，不自动修复或发布 |
| 保存与恢复 | 按 work-session-checkpoint 保存确认结论、证据、阻断范围和下一步 |
| 维护和归档 | 读取 project-maintenance；plan、确认、apply、summary/index，归档不是删除 |
| current docs 断链 | 读取 current-docs-integrity，检查 Source/Task；有事实依据才恢复 |
| 多项目 | 读取 scoped-docs；workspace-map 是显式启用的机器入口 |
| 显式连续推进 | bounded-auto-loop-policy；普通任务完成不要求启用 loop |
| worktree 或 native agents | 按需读取 worktree-playbook、native-agent-adapter |

正常实现授权覆盖相关可逆本地工作。高影响方案与必要独立审查仍适用；commit、push、tag、发布、部署和破坏性动作需要具体授权。
事实只写到 document-responsibility 指定的 owner；无新事实不填表。未确认信息保留 TODO_REVIEW，不把 report 当作 current truth。

<!-- forgekit:section s-c6168d65b15a -->
## 定制与升级

Markdown 隐藏标记标识模板章节和用户区。用户仍直接编辑 Markdown；用户区自动保留，受管区修改参与三方合并。
0.47 结构迁移自动处理常规填写、追加内容及 AGENTS 规则。真实冲突集中显示并阻止整个应用；不会把未完成合并报告为升级成功。升级后新开会话。
旧 Skill 名称 project-bootstrap-fill、handover-review、project-suitability 在 0.47.x 可显式调用。

<!-- forgekit:user begin -->
<!-- forgekit:user end -->
