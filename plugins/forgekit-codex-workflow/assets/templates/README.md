# 技术栈模板

本目录用于按技术栈拆分项目规则，避免每个项目都加载无关内容。

## 使用原则

新项目初始化时，先复制 `project-template/`，再按实际技术栈选择一个或多个 `templates/<stack>/` 中的内容。

不要把所有技术栈模板一次性复制到项目中。只复制当前项目需要的部分。

## 模板清单

| 模板 | 适用项目 | 典型内容 |
| --- | --- | --- |
| `java-springboot/` | Java 后端、Spring Boot、Maven/Gradle | 后端分层、配置、数据库、中间件、测试 |
| `vue/` | Vue、Vite、前端管理端 | npm/pnpm、组件、路由、状态、接口代理 |
| `react/` | React、Vite/Next 风格前端 | 组件、hooks、状态、路由、测试 |
| `python-fastapi/` | Python API、FastAPI、脚本服务 | 虚拟环境、依赖、API、pytest |
| `node-express/` | Node.js 后端、Express API | npm/pnpm、路由、中间件、测试 |
| `fpga-vivado-vitis/` | FPGA、Vivado、Vitis、Vitis HLS | HLS、综合、仿真、板卡、脚本 |

## 推荐加载方式

| 项目类型 | 建议加载 |
| --- | --- |
| Java 单体后端 | `project-template/` + `templates/java-springboot/` |
| Java + Vue 前后端 | `project-template/` + `templates/java-springboot/` + `templates/vue/` |
| React 前端 | `project-template/` + `templates/react/` |
| Python API | `project-template/` + `templates/python-fastapi/` |
| Node 后端 | `project-template/` + `templates/node-express/` |
| FPGA / HLS 项目 | `project-template/` + `templates/fpga-vivado-vitis/` |

## 脚本加载方式

可以使用根目录脚本初始化：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-project-template.ps1 `
  -TargetPath "D:\JAVA-code\demo" `
  -ProjectName "demo" `
  -Stacks java-springboot,vue
```

脚本会把技术栈模板复制到目标项目：

```text
.codex/stacks/<stack>/
```

这样 Codex 可以按需读取，不必把所有技术栈规则混入主规则。

## 文件约定

每个技术栈模板尽量包含：

- `README.md`：何时使用该模板。
- `codex-addons.md`：追加到项目 `.codex/` 的规则。
- `commands.md`：该技术栈常用命令示例。
- `checklist.md`：该技术栈开发检查清单。
- `docs-notes.md`：文档编写提示。

复制到具体项目后，可以把这些内容合并进项目的 `.codex/` 和 `docs/`，也可以保留为独立技术栈说明。
