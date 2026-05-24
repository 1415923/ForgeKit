# Vue 模板

适用于 Vue、Vite、前端管理端、前后端分离项目。

仅在项目包含 Vue 前端时加载。

## Codex 启动建议

- 推荐启动目录：包含 `package.json` 和 `vite.config.*` 的前端模块根目录。
- 优先阅读：`src/router`、`src/views`、`src/pages`、`src/components`、`src/stores`、`src/api`、`env` 示例。
- Ignore guidance / 避免默认读取：`node_modules/`、`dist/`、`coverage/`、`.vite/`、构建产物和大图片资源。

## 符号搜索 / LSP

- 优先使用 TypeScript / Vue language server 的类型错误和引用关系。
- CLI 中按页面路由、组件名、store 名、接口函数名、后端 API 路径搜索。
- 常用关键词：`createRouter`、`routes`、`defineProps`、`defineEmits`、`ref(`、`computed(`、`watch(`、`pinia`、`axios`、`fetch`。
- 修改组件前先找使用方；修改接口封装前先找页面调用方。

## 局部验证

- 修改组件或页面：运行类型检查、lint 和相关单测。
- 修改路由：检查导航、权限守卫和页面懒加载。
- 修改接口代理或环境变量：运行构建或最小 dev server 验证；长期服务启动前确认。

本机环境参考：

- Node.js：`D:\nodejs\node.exe`
- npm：`D:\nodejs\npm.ps1`
- pnpm：`C:\Users\32390\AppData\Roaming\npm\pnpm.ps1`
