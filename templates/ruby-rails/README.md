# Ruby Rails 模板

适用于 Rails Web、后台系统、传统 MVC、快速业务产品、API-only Rails 和成熟 Rails 接手项目。

不适用于第一版就处理非 Rails Ruby、复杂引擎化 monolith 拆分或大型遗留升级；这些需要先做接手审计。

## Codex 启动建议

- 推荐启动目录：包含 `Gemfile`、`config/application.rb` 和 `bin/rails` 的项目根目录。
- 初始化前必须确认：Rails 版本；传统 MVC 还是 API-only；Minitest 还是 RSpec；数据库、队列、缓存和部署方式。
- 优先阅读：`config/routes.rb`、`app/controllers`、`app/models`、`app/jobs`、`db/migrate`、`test/` 或 `spec/`。
- Ignore guidance / 避免默认读取：`tmp/`、`log/`、`vendor/bundle/`、`node_modules/`、上传文件、构建产物。

## 符号搜索 / LSP

- 优先使用 Ruby LSP / Solargraph / RubyMine 识别类、路由、模型和调用关系。
- CLI 中按 route、controller、model、migration、job、mailer、policy、service 搜索。
- 常用关键词：`Rails.application.routes.draw`、`ApplicationController`、`ApplicationRecord`、`ActiveJob`、`ActionCable`、`ActiveStorage`、`RSpec`。
- 修改 migration、Active Job、Action Cable、Active Storage、多数据库或缓存配置前，先确认环境和影响。

## 局部验证

- 修改业务逻辑：运行相关 Minitest/RSpec。
- 修改路由或 controller：检查 routes 和请求测试。
- 修改 migration/seed：先确认数据库环境。
- 修改队列、缓存、存储或 Action Cable：确认外部服务和部署进程。
