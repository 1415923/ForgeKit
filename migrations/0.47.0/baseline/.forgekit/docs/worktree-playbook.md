# Worktree 手册

用途：定义 Git worktree 在并行任务、实验分支和 AI 多会话协作中的安全、可审查用法。

本文只是指南，不是 worktree runner、scheduler、agent 编排系统、自动 merge 流程、自动 PR 流程或无人值守自动化。

## 什么时候使用

以下情况可以考虑 worktree：

- 两个任务必须并行推进，不能共享同一个脏工作区
- 实验需要隔离的分支和目录
- Maker 和 Checker 需要同一仓库的不同视角
- 高风险重构需要方便和 base branch 对比
- 多个 AI 或人工会话需要避免互相覆盖文件

## 什么时候不要使用

以下情况不要使用 worktree：

- 当前任务很小，可以安全地在主工作区完成
- 仓库里有未审查的脏改动
- base branch 不清楚
- 分支命名、清理方式或验证负责人不清楚
- 涉及 secrets、deploy、CI、migration 或生产操作，且没有用户明确确认
- 用户没有明确要求创建或使用 worktree

## 命名约定

推荐模式：

- Worktree path: `../<repo-name>-wt/<change-id-or-topic>`
- Branch name: `work/<change-id-or-topic>`

示例：

- `../my-app-wt/20260616-search-refactor`
- `work/20260616-search-refactor`

名称要短、范围明确。模板文档里不要写用户名、密钥、含私密信息的 ticket 原文或本机绝对路径。

## 创建前检查清单

创建 worktree 前，先确认并说明：

- 用户明确要求使用 worktree
- 源工作区 `git status --short` 干净
- base branch
- worktree path
- branch name
- allowed paths
- forbidden paths
- validation command
- cleanup plan
- Maker、Checker 或两者是否使用 worktree

任何一项不清楚，都先停止并询问。

## 推荐命令

查看状态：

```bash
git status --short
git branch --show-current
git worktree list
```

用户明确确认后创建隔离 worktree：

```bash
git worktree add -b work/<topic> ../<repo-name>-wt/<topic> <base-branch>
```

检查隔离 worktree：

```bash
cd ../<repo-name>-wt/<topic>
git status --short
```

只有用户明确确认后，才删除完成的 worktree：

```bash
git worktree remove ../<repo-name>-wt/<topic>
```

只有用户明确确认后，才删除分支：

```bash
git branch -d work/<topic>
```

不要自动 merge、push、删除分支、移除 worktree、创建 PR 或启动 agent。

## Maker / Checker 用法

Maker 可以使用 worktree 实现有范围的变更，避免干扰主工作区。

Checker 可以使用独立 worktree 或主工作区审查干净 diff、验证证据、风险和文档同步。

Worktree 不能替代 Maker / Checker 证据。worktree path、branch、validation command 和发现的问题应记录在 `.forgekit/changes/<change-id>/review.md` 或 `.forgekit/docs/work-log.md`。

## 清理

清理前先记录：

- 最终状态
- 验证结果
- 修改文件
- 变更是已合并、放弃还是仍待处理
- 剩余 branch 和 worktree path
- 下一负责人或下一步

清理必须显式确认。不要自动移除 worktree、删除分支、merge、push 或创建 PR。

## 安全规则

- 除非用户明确要求，不要创建 worktree。
- 创建前确认源工作区干净。
- 创建前说明 base branch、worktree path、branch name、allowed paths、validation command 和 cleanup plan。
- 不要用 worktree 绕过禁止路径。
- 不要把 secrets 或本机私有路径写入管理文档。
- 不要自动 merge、push、删除分支、移除 worktree、创建 PR 或启动 agent。
- 结果写入 `.forgekit/docs/work-log.md` 或对应 change review。
