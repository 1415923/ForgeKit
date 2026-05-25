# Ruby Rails 项目规则补充

## 代码结构

```text
app/
config/
db/
test/
spec/
```

## 开发规则

- Rails 约定优先，不强行加入额外分层。
- 先识别项目使用 Minitest 还是 RSpec，不默认迁移测试框架。
- Model、Controller、Job、Mailer、Policy、Service 对应职责要清楚。
- migration、credentials、queue、cache、storage、Action Cable 属于高风险区域。
- 多数据库、分片、只读库和后台任务不能凭默认想象修改。

## 测试

- 默认先运行项目已有测试命令。
- 请求、权限、表单、model validation 和关键业务流程优先覆盖。
- system tests、Capybara、浏览器驱动和外部服务运行前先确认环境。
