# 问答表

问答表用于把项目启动阶段的信息一次性收集清楚，减少后续反复追问。

## 使用方式

1. 新项目先复制 `project-template/`。
2. 根据项目技术栈选择 `templates/<stack>/`。
3. 填写 [init-questionnaire.md](./init-questionnaire.md)。
4. 让 Codex 使用 `project-bootstrap-fill` 根据问答表补齐 `.codex/` 和 `docs/`。

## 设计原则

- 问题分层，先问项目目标，再问技术细节。
- 不要求所有问题一次答完；未知项保留 `待补充`。
- 技术栈只选择项目实际需要的模板，避免无关规则进入上下文。
