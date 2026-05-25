# PHP Laravel 模板

适用于 Laravel 后台管理、内容系统、电商、业务 CRUD、API 服务和中小企业 Web 项目。

不适用于第一版就处理非 Laravel PHP 遗留系统、WordPress、Symfony 或大型多租户改造；这些需要单独模板或接手审计。

## Codex 启动建议

- 推荐启动目录：包含 `artisan`、`composer.json` 和 `.env.example` 的 Laravel 项目根目录。
- 初始化前必须确认：Blade、Livewire、Inertia、API-only 还是 Vue/React 前端；数据库、队列、缓存和部署方式。
- 优先阅读：`routes/`、`app/Http/Controllers`、`app/Models`、`database/migrations`、`config/`、`tests/`、`resources/`。
- Ignore guidance / 避免默认读取：`vendor/`、`node_modules/`、`storage/logs/`、`bootstrap/cache/`、上传文件、构建产物。

## 符号搜索 / LSP

- 优先使用 Intelephense / PHPStorm 索引确认类、路由、模型和服务引用。
- CLI 中按 route、controller、model、migration、job、event、policy、request 搜索。
- 常用关键词：`Route::`、`Controller`、`Model`、`FormRequest`、`Job`、`Policy`、`Migration`、`php artisan`。
- 修改 migration、queue、scheduler、auth、policy 或 storage 前，先确认环境和影响范围。

## 局部验证

- 修改业务逻辑：运行相关 PHPUnit/Pest 测试。
- 修改路由或接口：检查 `route:list` 和接口测试。
- 修改 migration/seed：先用预演或测试库确认。
- 修改前端资源：确认 npm/pnpm/bun 方案后再安装或构建。
