# 0.47 Astra 行为验收

状态：NEEDS_TEST（真实客户端／模型）。自动测试验证 runner 的隔离、授权判定、素材投影和结果记录，不能证明模型已遵守提示。

`cases.json` 保留 31 个既有行为场景，并增加 6 个 `astra-*` 场景：已定位小改动、批准范围内修复、验证停止条件、用户指令优先级、普通实现不触发回填、只读恢复。兼容别名保留显式调用；自动接手改用 project-assessment。别名测试同时装载实际目标 Skill 及 references，避免测试孤立别名。

只读检查场景清单：

```powershell
python scripts/test-skill-behavior.py list
```

实际执行时 runner 会先探测客户端可用性；调用前确认目标模型和调用条件。运行应使用隔离 fixture，不能把 fake adapter、当前聊天或静态检查当作 Astra 模型结果。

对照方法：在独立临时目录分别使用 0.46 与 0.47 的入口及 Skill 素材，固定模型、客户端版本、场景、任务范围和判分标准。保留首次有效证据和失败记录；修正后追加新结果，不能覆盖旧结果来改善结论。

记录任务成功率、误触发、重复确认、无关预读、过早停止、越界写入、额外测试次数、输入 token、耗时，以及不可获得的指标。授权越界和事实丢失单独报告。收益结论必须引用实际 trace，不能根据文件变短推断成功率提高。

历史精确文本契约通过 `tests/version_fixture.py` 固定到本地 v0.46 Git 对象；新版本语义、迁移和发布约束由 `test_v047_*`、`test_structured_upgrade.py`、当前 runner 和生成 smoke 验证。顶层新门禁不递归运行旧版本的门禁编排 canary。
