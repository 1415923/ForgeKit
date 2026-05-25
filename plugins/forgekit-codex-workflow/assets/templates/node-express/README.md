# Node Express 模板

适用于 Node.js 后端、Express API 和轻量服务。

## Codex 启动建议

- 推荐启动目录：包含 `package.json` 的 Node 服务根目录。
- 优先阅读：`src/app.*`、`src/server.*`、`src/routes`、`src/controllers`、`src/services`、`src/middleware`、`src/models`、`tests/`。
- Ignore guidance / 避免默认读取：`node_modules/`、`dist/`、`build/`、`coverage/`、日志文件、上传文件。

## 符号搜索 / LSP

- TypeScript 项目优先使用 TypeScript language server；JavaScript 项目优先查 JSDoc、路由和测试。
- CLI 中按 route path、controller、service、middleware、model、env key 搜索。
- 常用关键词：`express()`、`Router()`、`.get(`、`.post(`、`.use(`、`middleware`、`req`、`res`、`next`、`zod`、`joi`。
- 修改中间件、鉴权、错误处理或数据库模型前，先查全局挂载点和调用链。

## 局部验证

- 修改路由：运行相关 API 测试。
- 修改中间件或错误处理：运行集成测试或最小请求测试。
- 修改 TypeScript 类型：运行 typecheck、lint、test。
- 启动 dev server 前确认，因为它是长期运行服务。

本机环境参考：

- Node.js：`D:\nodejs\node.exe`
- npm：`D:\nodejs\npm.ps1`
- pnpm：`C:\Users\32390\AppData\Roaming\npm\pnpm.ps1`
