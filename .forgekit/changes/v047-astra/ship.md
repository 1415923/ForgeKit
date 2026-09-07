# 交付状态

范围：0.47.0 实现、后续迁移修复及中英文使用说明。用户已确认结果，并授权完成两份 README 和 CHANGELOG 后提交、推送当前 ForgeKit 仓库；提交目标为 main / origin。未请求创建版本标签或托管平台 Release。

此前用户另行授权的指定项目文档整理与 ForgeKit 升级已经完成，证据见 ownership-repair-design.md。业务项目文件、本机合并材料与日志不属于本次 ForgeKit 提交；`user-rules/reviewed-upgrades/` 按忽略规则保持本地。

交付检查已完成：当前版本与插件 metadata 一致；migration／template 镜像一致；独立审查、仓库门禁与生成 smoke 通过，结果见 verification.md。

升级使用 ForgeKitRoot 的 forgekit-project.py 统一入口。真实冲突停止整次 apply；写入失败逐项恢复，恢复不完整时使用错误中指出的 rollback.json，先核对文件后恢复，不直接重试覆盖现场。

若实际项目升级修改入口、Skill 或 agent，旧会话只做最小 checkpoint 与收口，新任务启动新会话。

尚未声明：GPT-6 Astra 成功率、token／时间收益，Claude／Codex 真实加载效果，Linux／macOS 原生实测。对应模型测试方案见 tests/skill-behavior/ASTRA-EVALUATION.md。
