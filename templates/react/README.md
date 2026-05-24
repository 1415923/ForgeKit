# React 模板

适用于 React、Vite、前端应用、管理端或组件型前端项目。

仅在项目包含 React 前端时加载。

## Codex 启动建议

- 推荐启动目录：包含 `package.json` 的 React 前端模块根目录。
- 优先阅读：`src/routes`、`src/pages`、`src/components`、`src/hooks`、`src/store`、`src/api`、`vite.config.*` 或框架配置。
- Ignore guidance / 避免默认读取：`node_modules/`、`dist/`、`build/`、`coverage/`、`.next/`、大图片资源。

## 符号搜索 / LSP

- 优先使用 TypeScript language server 的类型错误和引用关系。
- CLI 中按组件名、hook 名、路由、store/action、接口函数名搜索。
- 常用关键词：`createBrowserRouter`、`Routes`、`Route`、`useEffect`、`useMemo`、`useCallback`、`useState`、`zustand`、`redux`、`axios`、`fetch`。
- 修改共享组件、hook 或状态管理前，先查所有引用方。

## 局部验证

- 修改组件：运行相关测试、typecheck、lint。
- 修改路由或状态管理：运行构建或关键页面测试。
- 修改 API client：查页面调用方，并验证错误处理和 loading 状态。
