# 独立审查

ReviewType: independent
ReviewMode: blocker-recheck
Reviewer: migration_review（只读上下文）
ReviewDecision: pass

最终复核的 structured_upgrade.py SHA256：`40A31EEE334B84EC7B3FF7AC08E83F53D8B5977C441B839C59CA6E68EE49BAE2`。

已修复并关闭：硬链接越界写入、回滚遇到首个恢复错误就中断、备份顺序、自定义 change_root、旧 README 锁条目、列表／通配版本链、stable ID 与 user region 的连续搬迁、纯插入及换行差异、旧 runtime 升级后的逐文件 ancestry。

独立证据：真实 v0.36／v0.43／v0.45／v0.46 标签分别测试末尾追加、新 H2、章节内插入，共 12/12；自定义文本保留，user region 一个，AGENTS 小于 5 KB，没有旧模板整套规则回流。旧 runtime v0.45→v0.46 后再迁移 v0.47 的 stock 与有效旧锁＋新增 H2 两例均 ready、零冲突。

审查使用只读内存计划，没有应用真实业务项目。自动化应用与失败恢复证据由当前回归和 smoke 提供；独立审查不替代实际模型验收。

## 整份定制入口的显式合并复核

ReviewType: independent；Reviewer: migration_review；ReviewDecision: pass。范围为本轮新增材料绑定、完整原文保留机制与指定项目候选，非全项目业务审查。

原 AGENTS 原始字节在候选中恰好出现一次；新模板用户区外内容不变。候选文件、材料正文及计划输出一致。项目强制启动顺序、canonical repo 路由、生产边界兼容；build、部署、生产 DATA、Scheduler、凭据等单独授权要求完整保留。

实际项目默认计划仍因入口冲突停止；带材料为 ready、零冲突。独立只读负向验证 8/8 拒绝错误绑定或删改候选；计划后材料变化、错误 plan hash 均在检查项目输入前拒绝。未发现具体阻断缺陷。真实项目未写入；副本实际 apply 与完整门禁使用主代理的明确证据，未冒充审查者重跑。

审查 SHA-256：

- 候选：`d969d1b8d3bdecb7fb32091c05b1522b4155df49cb7857068ba6ad380930dfde`
- scripts/structured_upgrade.py：`2E24F27DDE28B3E2BAE13A3753479F511B4C56A75317C4524121A13B23096487`
- scripts/forgekit-project.py：`015E6F73EBA8F101B0361CA180678E64475CE785B277B375BFA6D1FC2ABAAEAC`
- scripts/forgekit-upgrade.py：`7471DD2A3F290BCE93338D04E7482A2DB87E0AB57B3EFC9A2A93FC322CD1B67F`
