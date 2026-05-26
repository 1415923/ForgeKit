# Node Express 命令示例

```powershell
node --version
npm --version
npm install
npm run dev
npm test
npm test -- --runInBand
npm run lint
npm run typecheck
npm run build
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
- `npm run dev` 是长期运行服务，先确认。
- 优先跑 typecheck/lint/相关测试；发布前或配置变更后再跑 build。
