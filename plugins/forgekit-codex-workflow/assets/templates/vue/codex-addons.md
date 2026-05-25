# Vue 项目规则补充

## 代码结构

优先遵循项目已有结构。新项目推荐：

```text
src/
├─ api/
├─ assets/
├─ components/
├─ composables/
├─ router/
├─ stores/
├─ views/
└─ utils/
```

## 开发规则

- 页面级组件放 `views/`，可复用组件放 `components/`。
- API 请求集中放 `api/`。
- 状态管理遵循项目已有 Pinia/Vuex 或组合式状态方案。
- 不在组件中硬编码后端地址，使用环境变量或 Vite proxy。
- 表单、权限、路由守卫、错误提示按项目统一约定实现。
- UI 组件和样式遵循已有设计系统。

## 测试与验证

- 修改组件后至少运行 lint、typecheck 或 build 中的一项。
- 修改路由、权限、登录态时需要手动或 E2E 验证关键流程。
- `npm run dev` / `pnpm dev` 是长期服务，先确认后执行。
