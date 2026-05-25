# PHP Laravel 项目规则补充

## 代码结构

```text
app/
routes/
database/
resources/
config/
tests/
```

## 开发规则

- 先识别项目是 Blade、Livewire、Inertia、API-only 还是前后端分离。
- Controller 保持 HTTP 边界清晰，复杂业务放 service/action/job。
- FormRequest、Policy、Middleware、Event/Listener 变化要同步测试和文档。
- migration 和 seed 是数据库变更，执行前确认环境。
- 队列、缓存、session、文件存储和邮件发送都属于外部依赖。

## 测试

- 默认先识别项目使用 PHPUnit 还是 Pest。
- Feature test 覆盖路由、权限、表单和关键业务流程。
- 数据库测试前确认 sqlite、测试库或容器策略。
- 前端资源变化需要运行对应构建或页面验证。
