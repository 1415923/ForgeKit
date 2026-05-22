# Vue 命令示例

```powershell
node --version
npm --version
pnpm --version
npm install
npm run dev
npm run build
npm run lint
npm run typecheck
```

注意：

- `npm install` / `pnpm install` 会下载依赖并修改 lockfile，先确认。
- `npm run dev` 是长期运行服务，Vite 在受限环境中可能 `spawn EPERM`，失败时用正常本机权限启动。
