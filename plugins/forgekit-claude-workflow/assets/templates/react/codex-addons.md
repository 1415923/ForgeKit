# React 项目规则补充

## 代码结构

```text
src/
├─ api/
├─ assets/
├─ components/
├─ hooks/
├─ pages/
├─ routes/
├─ stores/
└─ utils/
```

## 开发规则

- 页面放 `pages/`，复用组件放 `components/`。
- 自定义 hooks 放 `hooks/`，避免在组件中堆复杂副作用。
- API 请求集中管理。
- 状态管理遵循项目已有方案。
- 不硬编码服务地址和密钥。
- 表单、权限、路由、错误态和加载态要完整。

## 测试与验证

- UI 变化至少运行 build、lint、typecheck 或相关测试。
- 关键交互变化需要手动或 E2E 验证。
