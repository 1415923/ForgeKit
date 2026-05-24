# React 命令示例

```powershell
node --version
npm --version
pnpm --version
npm install
npm run dev
npm run build
npm run lint
npm run typecheck
npm test
```

## Local validation / 局部验证优先级

```powershell
npm run typecheck
npm run lint
npm test -- --runInBand
npm run build
```

注意：

- 安装依赖先确认。
- dev server 先确认，必要时用正常本机权限启动。
- 优先跑 typecheck/lint/相关测试；路由、构建配置或依赖变更后再跑 build。
