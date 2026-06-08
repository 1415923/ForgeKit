# 版本推进闸门

本规则用于防止项目每个版本只堆功能、堆文件，而不做架构复盘和复用整理。

## 强制规则

- 项目进入大规模开发前，必须先完成 `docs/project-plan.md` 和 `docs/version-roadmap.md` 的第一版。
- 每个大版本结束后，必须安排一个 review/refactor 中版本。
- review/refactor 中版本未完成时，不允许直接进入下一个大版本。
- 如果用户要求跳过中版本，Codex 必须提醒风险，并要求人工明确确认。

## 大版本定义

大版本通常指：

- `v0.1.0` 到 `v0.2.0`
- `v1.0.0` 到 `v1.1.0`
- 新增主要业务模块、核心能力、硬件能力或部署形态

## 中版本定义

中版本通常指：

- `v0.1.1`
- `v0.2.1`
- `v1.1.1`

中版本目标不是新增大功能，而是：

- review
- refactor
- documentation
- testing
- architecture cleanup

## Codex 行为要求

当用户要求开始下一个大版本时，先检查：

1. `docs/version-roadmap.md`
2. `docs/changelog.md`
3. 当前 `git diff` / `git status`
4. 上一个中版本 review/refactor 是否完成

如果缺少 review/refactor 结论，回复应包括：

- 当前不建议直接推进下一个大版本。
- 缺少哪些闸门材料。
- 建议先启动哪个中版本。
- 需要人工确认才能跳过。

## 允许跳过的条件

只有用户明确说明以下内容后，才可以跳过：

- 为什么跳过。
- 风险由谁承担。
- 后续在哪个版本补 review/refactor。
- 是否允许短期技术债。
