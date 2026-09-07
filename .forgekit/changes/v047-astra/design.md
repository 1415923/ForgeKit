# 0.47 设计与边界

用户已批准 Astra-first、双平台兼容、激进合并 Skill／文档以及同文件 Markdown 分区。实现不修改模型设置，也不调用模型进行迁移。

## 内容

- 主要能力从九个收敛为七个；三个旧名称保留为显式别名。bootstrap/facts 与 adoption/takeover 的长说明分别按分支加载。
- AGENTS／CLAUDE 保留授权、证据、按需导航、完成和恢复。Claude 适配器去掉固定问卷与反复确认。
- context-continuity 合并到 work-session-checkpoint；local-toolchain 合并到 testing；workflow-router 合并到 usage-playbook；旧 .codex project/scope/rules 按显式 owner 映射退休。task-intake、task-board、work-log 的职责保持独立。
- 用户仍直接编辑 Markdown。H2 稳定标记与 user region 为迁移提供边界；代码围栏内的标题不参与拆分。

## 升级

1. 统一入口定位真实治理根、当前版本和精确版本链，调用低层 JSON plan。
2. 计划阶段只读。整条链在内存中顺序执行，记录输入哈希、动作、保留来源和集中冲突。
3. 逐文件 ancestry 优先考虑有效锁记录、可精确匹配的历史模板和该版本基线。发布标签的基线按内容哈希去重压缩；既有 migration 包保持原样。
4. 非重叠编辑合并；入口中的纯新增规则搬入用户区。旧规则被修改、重复章节、无法确认的基线或重叠编辑需要明确解决，不能自动猜测事实。
5. 搬迁更新 Markdown 链接和精确路径代码片段；代码围栏保持不透明。自定义文档根和 change_root 按 boundary 映射。
6. apply 绑定已审阅计划哈希并复查输入；先写恢复备份，再写受影响文件和锁，最后写 state 与实际结果报告。失败逐项恢复，单项恢复失败也继续其余恢复并保留备份。

## 不扩展的范围

不覆盖业务 README、不自动拆分多项目事实、不更改现有项目布局、不升级真实业务项目，不执行 commit／push／发布。旧会话在规则升级后只做 checkpoint 和收口。

实际 Astra 行为和收益仍为 NEEDS_TEST。静态减量、隔离 runner 测试和迁移 smoke 不构成模型性能证据。
