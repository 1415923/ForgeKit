# Agent Entry Contract

本文件是 Codex 与 Claude 入口始终生效的共享安全、事实和授权合同的唯一规范来源。入口文件只应用这些规则；具体任务流程仍由命中的 Skill、governance 或 reference 拥有。

## Project and Write Boundary

先从 `.forgekit/project-boundary.yml` 确认 ForgeKitRoot、ProjectRoot、managed docs root 和写入策略。读取和写入都必须留在用户给出的项目边界与任务范围内；不得把工具包根、业务项目、外部证据目录或真实用户项目相互混用。

## Evidence and No Fabrication

结论必须来自可定位的文件、命令或用户事实。证据不足时明确标记未知、假设或 `TODO_REVIEW`；不得把推测、一次未验证输出或缺失的外部状态写成项目事实。

## Audit Default

审计、检查、评估、诊断和规划默认只读。发现问题只授权报告问题，不自动授权修复、回填文档或执行后续动作。

## Bounded Local Authorization

用户明确要求修复、修改、实现或更新，并给出本地范围时，允许在该范围内执行可回滚写入和必要验证。清晰的局部授权无需用同义问题重复确认；它也不得扩张到未声明路径、外部系统或不可逆动作。

## External and Irreversible Actions

外部、不可逆、破坏性或越界操作必须获得针对具体目标和影响的明确授权。commit、push、tag、release、部署、生产变更、删除重要数据和权限或凭据变更不由普通本地写入授权隐含许可。

## Minimum Evidence-Based Writeback

写回遵循来源优先和最小必要原则：只持久化完成当前授权任务所需、且有证据支持的事实。按文档职责选择唯一目标，不复制完整对话、长工具输出或未经验证的推理，也不把业务事实写入 governance 模板。

## Skill Routing

先使用与当前意图和项目状态匹配的项目本地 Skill，再按需读取其直接引用的细则。通用路由只决定加载哪个任务流程，不授予写入、外部或不可逆操作；每个 Skill 的具体触发、不触发和平台适配语义仍由该 Skill 自身拥有。
