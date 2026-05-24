# Python FastAPI 模板

适用于 Python API 服务、FastAPI、脚本服务和轻量后端。

## Codex 启动建议

- 推荐启动目录：包含 `pyproject.toml`、`requirements.txt` 或 `app/` 的 API 模块根目录。
- 优先阅读：`app/main.py`、`app/api`、`app/routers`、`app/services`、`app/models`、`app/schemas`、`tests/`。
- Ignore guidance / 避免默认读取：`.venv/`、`__pycache__/`、`.pytest_cache/`、`dist/`、大型数据文件、模型权重。

## 符号搜索 / LSP

- 优先使用 Pyright / Pylance / Jedi 识别类型、引用和导入问题。
- CLI 中按 router、path operation、service 函数、Pydantic schema、SQLAlchemy model 搜索。
- 常用关键词：`FastAPI(`、`APIRouter`、`@router.get`、`@router.post`、`BaseModel`、`Depends`、`Session`、`pytest`。
- 修改依赖注入、数据库 session 或 schema 前，先查接口和测试。

## 局部验证

- 修改单个函数：运行相关 pytest。
- 修改接口：运行 API 测试或最小 TestClient 测试。
- 修改类型或 schema：运行 type check、pytest、compileall。
- 启动 `uvicorn --reload` 前确认，因为它是长期运行服务。

本机环境参考：

- Python：`D:\anaconda3\python.exe`
- Python Launcher：`C:\WINDOWS\py.exe`
