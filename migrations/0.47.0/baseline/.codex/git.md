# 项目 Git 规则

## 分支策略

- 主分支：待补充
- 开发分支：待补充
- 功能分支：`feature/<short-name>`
- 修复分支：`fix/<short-name>`
- 发布分支：`release/<version>`

## Commit 规范

使用 Conventional Commits：

```text
feat: 增加功能
fix: 修复问题
docs: 更新文档
style: 调整格式
refactor: 重构代码
test: 增加或修改测试
chore: 调整构建、依赖或工具配置
```

## 提交前要求

- `git status` 已检查。
- `git diff` 已检查。
- 已检查 `.forgekit/docs/code-ownership.md`，Critical 或 Unknown 区域变更已有必要评审或人工确认。
- 测试或构建已运行，或记录未运行原因。
- 文档已同步。
- 不包含密钥、密码、令牌、个人路径等敏感信息。

## 发布版本

- 版本号规则：待补充
- Tag 规则：待补充
- 发布说明来源：`.forgekit/docs/changelog.md`
