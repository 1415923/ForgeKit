# 本地工具链检查

本文记录当前项目可用的 LSP、lint、test、build 和局部验证能力。它描述项目事实，不替代用户级环境规则。

## 使用规则

- 新项目初始化后，按实际技术栈填写。
- 接手既有项目时，先验证已有命令，不要直接改构建体系。
- 缺失工具先记录为风险或技术债，不要默认安装。
- 安装依赖、启动长期服务、连接外部服务、执行部署前必须确认。
- 可先运行 `scripts/detect-local-toolchain.ps1` 生成检测报告，再把相关事实合并到本文。

## 技术栈入口

| 技术栈 | 推荐启动目录 | LSP / 符号能力 | 局部验证命令 | 状态 | 备注 |
| --- | --- | --- | --- | --- | --- |
| Java Spring Boot | 包含 `pom.xml` 或 `build.gradle` 的后端模块 | IDEA / Java LSP / Maven or Gradle project model | `mvn -Dtest=ClassNameTest test` / `gradle test --tests "*ClassNameTest"` | 待验证 | 待补充 |
| Vue | 包含 `package.json` 和 `vite.config.*` 的前端模块 | Vue language server / TypeScript server | `npm run typecheck` / `npm run lint` / `npm run test` | 待验证 | 待补充 |
| React | 包含 `package.json` 的前端模块 | TypeScript server | `npm run typecheck` / `npm run lint` / `npm test` | 待验证 | 待补充 |
| Python FastAPI | 包含 `pyproject.toml`、`requirements.txt` 或 `app/` 的 API 模块 | Pyright / Pylance / Jedi | `python -m pytest -k keyword` / `python -m compileall app` | 待验证 | 待补充 |
| Node Express | 包含 `package.json` 的 Node 服务模块 | TypeScript server / ESLint | `npm run typecheck` / `npm run lint` / `npm test` | 待验证 | 待补充 |
| FPGA Vivado/Vitis | 硬件工程根目录或脚本目录 | Vivado/Vitis project scripts / Tcl / HLS top | `vitis_hls -f scripts/csim.tcl` / `vivado -mode batch -source scripts/check_project.tcl` | 待验证 | 待补充 |

## 忽略规则建议

| 类型 | 路径示例 | Codex 默认处理 |
| --- | --- | --- |
| 前端依赖 | `node_modules/` | 不读取，不手改 |
| Java 构建产物 | `target/`、`build/` | 不读取，不手改 |
| Python 缓存 | `.venv/`、`__pycache__/`、`.pytest_cache/` | 不读取，不手改 |
| 前端产物 | `dist/`、`coverage/` | 不读取，不手改 |
| FPGA 产物 | `.runs/`、`.cache/`、`.hw/`、`*.bit`、`*.xsa` | 不读取，大文件先询问 |
| 日志和上传文件 | `logs/`、`uploads/` | 默认不读取，必要时先说明目的 |

## 验证记录

| 日期 | 技术栈 | 命令 | 结果 | 备注 |
| --- | --- | --- | --- | --- |
| 待补充 | 待补充 | 待补充 | 待补充 | 待补充 |

## 可执行检测

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\detect-local-toolchain.ps1
```

如需保存报告：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\detect-local-toolchain.ps1 -OutputPath .\docs\local-toolchain.detected.md
```

检测结果只作为事实输入。安装缺失工具、启用 LSP、启动依赖服务或修改系统配置前，必须先确认。
