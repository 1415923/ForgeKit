# Agent Harness

本文定义本项目如何让 Codex 在有限上下文内稳定工作。它不是新的治理层，而是告诉 Codex 先读什么、怎么找代码、什么时候停止编码并回到方案确认。

## 目标

- 让 `AGENTS.md` 成为短入口，只负责路由和边界。
- 让 `.forgekit/docs/codebase-map.md` 成为代码搜索起点。
- 让 `.codex/stacks/` 只按技术栈加载，不跨栈污染。
- 让治理文档按任务读取，不默认全量加载。
- 让大任务先探索、计划、确认，再编码。

## 上下文加载顺序

1. 读取 `AGENTS.md`，判断任务类型和禁止动作。
2. 读取 `.forgekit/docs/codebase-map.md`，定位相关模块、入口文件和验证命令。
3. 读取 `.codex/project.md`、`.codex/scope.md`、`.codex/commands.md` 中与任务相关的部分。
4. 只读取相关 `.codex/stacks/<stack>/`。
5. 只读取当前任务需要的治理文件。
6. 如果信息仍不足，先用搜索和用户访谈补齐，不要猜测。

## Agentic Search 规则

在写代码前，Codex 应先建立最小事实集：

- 用文件名搜索找到入口。
- 用符号、类名、接口名、路由、表名、命令名搜索定位实现。
- 读取调用方和被调用方，确认行为边界。
- 检查测试、构建、启动命令是否存在。
- 对不确定项写成问题或假设，不直接编码。

常用搜索对象：

| 目标 | 优先查找 |
| --- | --- |
| 后端接口 | controller、route、handler、service、repository、schema、migration |
| 前端页面 | route、page、view、component、store、api client |
| 数据模型 | entity、model、dto、migration、schema、mapper |
| 配置和启动 | package scripts、pom、gradle、docker、env example、README |
| 测试 | test、spec、fixtures、mock、e2e |

## AGENTS 分层规则

- 根 `AGENTS.md` 控制全项目共性，建议保持在 200 行以内。
- 子目录可以增加自己的 `AGENTS.md`，只描述该目录特有规则。
- 不要在 `AGENTS.md` 中复制长治理文档、长提示词或技术栈细节。
- 稳定流程放进 skill；技术栈细节放进 `.codex/stacks/`；版本和风险放进 `.forgekit/docs/`。
- 每 3 到 6 个月，或每个大版本 review/refactor gate，检查一次 AGENTS 是否过长、重复或过时。

## 编码前停止条件

出现以下情况时，Codex 应停止直接编码，先输出问题、探索结果或方案：

- 当前版本范围、验收标准或 Definition of Ready 不清楚。
- 需要跨多个模块、数据库、外部 API、部署链路或权限模型。
- 现有架构边界不清楚，修改可能影响上下游服务。
- 找不到可运行的测试、构建或局部验证命令。
- 用户要求进入下一个大版本，但上一个 review/refactor gate 未完成。

## 输出要求

探索或初始化阶段优先输出：

- 已确认事实。
- 关键缺口。
- 风险和假设。
- 推荐下一步。
- 是否允许进入编码。

实现阶段优先输出：

- 修改了什么。
- 如何验证。
- 哪些风险仍需人工确认。
