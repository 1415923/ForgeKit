# v0.47.0：Astra 精简与结构化迁移

状态：用户已批准实施；不包含 commit、push、发布或真实业务项目升级。

依据：OpenAI GPT-6 Astra model guidance（https://developers.openai.com/api/docs/guides/latest-model）及 Eric Provencher 原文（https://x.com/pvncher/status/2095991462416490862），规划会话已完整阅读正文。

目标：七个主要 Skill、三个显式兼容入口；减少重复规则与预读链；同文件 Markdown 分区；旧基线、本地内容和新版模板的确定性迁移。正常填写文档和追加 AGENTS 规则自动保留；真实冲突停止整个应用。

授权范围：本仓库模板、Skills、平台适配、脚本、测试、配置、migration、说明及本变更工件。usage.html 的已有删除纳入退休。保留双平台，不修改用户模型设置。

高影响原因：迁移改变持久文档和入口，必须验证内容保存、边界、冲突与回滚，并进行独立只读审查。自检不替代独立审查。

验收：A1 stock 升级；A2 常规定制自动迁移；A3 搬迁覆盖及引用完整；A4 冲突零写入；A5 并发修改与失败回滚；A6 幂等；A7 历史链及布局；A8 Skill 与别名；A9 轻量执行及高风险边界；A10 manifest、生成 smoke 和版本一致性。

实施顺序：迁移机制及测试 → 内容收敛 → migration 与生成验证 → 独立审查及收口。整个已批准实现阶段可连续推进，扩大授权或真实冲突时才重新决策。
