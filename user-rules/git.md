# 用户级规则：Git

用于定义跨项目复用的 Git 工作习惯。

## 基本原则

- 使用本机安装的 Git。
- 修改前先查看 `git status`，识别已有改动。
- 不回滚用户已有改动，除非用户明确要求。
- 提交前查看 `git diff`，确认只包含本次任务相关变更。
- 不自动 `push`，除非用户明确要求。

## Commit Message

默认使用 Conventional Commits：

```text
feat: add user login flow
fix: handle empty upload file
docs: update api contract
refactor: simplify order calculation
test: add payment service tests
chore: update build config
```

中文项目也可以使用英文类型加中文描述：

```text
feat: 增加订单导出功能
fix: 修复空文件上传报错
docs: 更新接口文档
```

## 分支命名

推荐格式：

```text
feature/<short-name>
fix/<short-name>
docs/<short-name>
release/<version>
```

## 提交前检查

- 工作区没有无关修改混入。
- 测试或构建已运行，或明确说明未运行原因。
- 文档已同步更新。
- 版本更新记录已补充，若本次变更属于可见功能、接口、部署或行为变化。
