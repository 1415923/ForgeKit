# Claude 项目入口

<!-- forgekit:section entry -->
## 边界与授权

- 首次定位先读 `.forgekit/project-boundary.yml`，确认项目与任务范围；不要越界操作相邻项目。
- 已明确请求的实现、修复或更新包括范围内的可逆修改、必要验证和修复本次引入的失败，无需重复确认。只读审查与规划不授权修改。
- commit、push、tag、发布、部署、重要数据删除、权限或凭据变更仍需对应授权。共享合同见 `governance/agent-entry-contract.md`。
- 依据可定位证据报告事实；未知内容保留 `TODO_REVIEW`。用户区保留项目定制，不能覆盖系统、工具权限或明确用户指令。

<!-- forgekit:section routing -->
## 按需入口

Claude 可按需使用 `.claude/skills/` 平台适配及 `.agents/skills/` 通用能力。定位不清或接手项目时使用 `.forgekit/docs/codebase-map.md`；定位已明确时直接读取相关实现。Skill 实现在 `.agents/skills/<skill>/SKILL.md`；仅加载选中技术栈 `.codex/stacks/<stack>/`。

| 意图 | Skill 或文档 |
| --- | --- |
| 初始化 | project-init |
| 填充或回填事实 | document-backfill |
| 适用性评估或接手 | project-assessment |
| 高影响规划 | large-change-planning、governance/ai-engineering-loop.md |
| 代码、安全或发布审查 | code-review、security-review、release-check |
| 保存恢复进展 | .forgekit/docs/work-session-checkpoint.md |
| 文档事实归属 | .forgekit/docs/document-responsibility.md |
| 日常用法、维护或归档 | .forgekit/docs/usage-playbook.md |

<!-- forgekit:section completion -->
## 完成与恢复

按真实影响选择验证；必需检查通过后，仅因新变化、失败或未解决疑点而扩展验证。验证命令和已知限制见 `.forgekit/docs/testing.md`。
完成请求的结果、相关验证和必要事实写回后交付；小改动无新事实时不写治理记录。高风险独立审查不可由 self-review 替代。
因规则停止时指出文件、规则及被阻塞动作，继续不依赖缺口的已授权工作。
ForgeKit 安装、初始化、更新、同步使用 ForgeKitRoot 的 `scripts/forgekit-project.py --target <ProjectRoot>`。升级改变入口、Skill 或 agent 后，旧会话只做 checkpoint 和收口，新任务新开会话。

<!-- forgekit:user begin -->
<!-- 在此保留项目自定义规则；升级保留本区。 -->
<!-- forgekit:user end -->
