# Ruby Rails 命令示例

```powershell
ruby -v
bundle install
bin/rails test
bundle exec rspec
bin/rails routes
bin/rails db:migrate:status
```

## Local validation / 局部验证优先级

```powershell
bin/rails test
bundle exec rspec
bin/rails routes
bin/rails db:migrate:status
```

注意：

- `bundle install` 会下载依赖，先确认网络和 gem source。
- `bin/rails db:migrate`、seed、queue worker、scheduler 会影响外部状态，必须先确认。
- 多数据库、缓存、Active Storage 和 Action Cable 需要真实环境或替代环境。
- 部署、credentials 编辑、master key、云存储配置前必须确认。
